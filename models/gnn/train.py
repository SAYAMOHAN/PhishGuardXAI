
from pathlib import Path
import json
import random

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "models" / "gnn" / "data"
OUTPUT_DIR = ROOT / "models" / "gnn" / "saved_model"
SEED = 42
EPOCHS = 30
HIDDEN_CHANNELS = 16
LEARNING_RATE = 0.01

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


def make_features(df):
    """Create URL-only features without using labels."""
    urls = df["URL"].fillna("").astype(str)
    hosts = df["hostname"].fillna("").astype(str)

    features = pd.DataFrame(index=df.index)
    features["url_length"] = urls.str.len()
    features["dot_count"] = urls.str.count(r"\.")
    features["hyphen_count"] = urls.str.count("-")
    features["digit_count"] = urls.str.count(r"\d")
    features["slash_count"] = urls.str.count("/")
    features["question_count"] = urls.str.count(r"\?")
    features["equals_count"] = urls.str.count("=")
    features["at_count"] = urls.str.count("@")
    features["https"] = urls.str.lower().str.startswith("https://").astype(int)
    features["hostname_length"] = hosts.str.len()
    features["subdomain_parts"] = hosts.str.count(r"\.")
    features["ip_address"] = hosts.str.fullmatch(
        r"(?:\d{1,3}\.){3}\d{1,3}"
    ).astype(int)

    return features.replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy(
        dtype=np.float32
    )


class URLGCN(nn.Module):
    def __init__(self, input_channels, hidden_channels=16):
        super().__init__()
        self.conv1 = GCNConv(input_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(hidden_channels, 2)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.dropout(x)
        x = self.conv2(x, edge_index).relu()
        return self.classifier(x)


def main():
    nodes_path = DATA_DIR / "url_nodes.csv"
    edges_path = DATA_DIR / "edge_index.csv"

    if not nodes_path.exists() or not edges_path.exists():
        raise FileNotFoundError(
            "Graph files missing. Run models/gnn/build_graph.py first."
        )

    nodes = pd.read_csv(nodes_path)
    edges = pd.read_csv(edges_path)

    # Labels: good=0, bad=1
    y = nodes["label_id"].to_numpy(dtype=np.int64)
    groups = nodes["hostname"].astype(str).to_numpy()

    # Hold out complete hostnames, then split the remaining hostnames.
    outer_split = GroupShuffleSplit(
        n_splits=1, test_size=0.20, random_state=SEED
    )
    trainval_idx, test_idx = next(
        outer_split.split(nodes, y, groups=groups)
    )

    inner_split = GroupShuffleSplit(
        n_splits=1, test_size=0.20, random_state=SEED
    )
    train_rel, val_rel = next(
        inner_split.split(
            nodes.iloc[trainval_idx],
            y[trainval_idx],
            groups=groups[trainval_idx],
        )
    )
    train_idx = trainval_idx[train_rel]
    val_idx = trainval_idx[val_rel]

    # Verify that hostname groups do not overlap across splits.
    train_hosts = set(groups[train_idx])
    val_hosts = set(groups[val_idx])
    test_hosts = set(groups[test_idx])
    assert train_hosts.isdisjoint(val_hosts)
    assert train_hosts.isdisjoint(test_hosts)
    assert val_hosts.isdisjoint(test_hosts)

    # Fit feature scaling on training nodes only.
    raw_features = make_features(nodes)
    scaler = StandardScaler()
    scaler.fit(raw_features[train_idx])
    x = scaler.transform(raw_features).astype(np.float32)

    # Retain only edges within each split. This prevents message passing
    # across train/validation/test boundaries.
    src = edges["source"].to_numpy(dtype=np.int64)
    dst = edges["target"].to_numpy(dtype=np.int64)

    split_id = np.full(len(nodes), -1, dtype=np.int8)
    split_id[train_idx] = 0
    split_id[val_idx] = 1
    split_id[test_idx] = 2

    same_split = split_id[src] == split_id[dst]
    src = src[same_split]
    dst = dst[same_split]
    edge_index = torch.tensor(
        np.vstack([src, dst]), dtype=torch.long
    )

    # Add self-loops for nodes without usable neighbors.
    self_nodes = np.arange(len(nodes), dtype=np.int64)
    edge_index = torch.cat(
        [
            edge_index,
            torch.tensor(
                np.vstack([self_nodes, self_nodes]), dtype=torch.long
            ),
        ],
        dim=1,
    )

    device = torch.device("cpu")
    data = Data(
        x=torch.tensor(x, dtype=torch.float32),
        edge_index=edge_index,
        y=torch.tensor(y, dtype=torch.long),
    ).to(device)

    train_mask = torch.zeros(len(nodes), dtype=torch.bool)
    val_mask = torch.zeros(len(nodes), dtype=torch.bool)
    test_mask = torch.zeros(len(nodes), dtype=torch.bool)
    train_mask[train_idx] = True
    val_mask[val_idx] = True
    test_mask[test_idx] = True

    model = URLGCN(data.num_node_features, HIDDEN_CHANNELS).to(device)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=LEARNING_RATE, weight_decay=5e-4
    )
    criterion = nn.CrossEntropyLoss()

    best_val_f1 = -1.0
    best_state = None
    best_epoch = 0

    for epoch in range(1, EPOCHS + 1):
        model.train()
        optimizer.zero_grad()
        logits = model(data.x, data.edge_index)
        loss = criterion(logits[train_mask], data.y[train_mask])
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_logits = model(data.x, data.edge_index)[val_mask]
            val_probs = val_logits.softmax(dim=1)[:, 1].cpu().numpy()
            
            val_true = y[val_idx]

            # Select a threshold using validation data only.
            candidate_thresholds = [
                0.20, 0.25, 0.30, 0.35, 0.40,
                0.45, 0.50, 0.55, 0.60, 0.65, 0.70
            ]

            threshold_results = []
            for threshold in candidate_thresholds:
                val_pred = (val_probs >= threshold).astype(int)
                score = f1_score(
                    val_true, val_pred, zero_division=0
                )
                threshold_results.append((score, threshold))

            val_f1, val_threshold = max(threshold_results)


        print(
            f"Epoch {epoch:02d}/{EPOCHS} | "
            f"loss={loss.item():.4f} | val_f1={val_f1:.4f}"
        )

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_epoch = epoch
            best_threshold = val_threshold
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }

    if best_state is None:
        raise RuntimeError("Training did not produce a model checkpoint.")

    model.load_state_dict(best_state)
    model.eval()

    with torch.no_grad():
        test_probs = model(data.x, data.edge_index)[test_mask]
        test_probs = test_probs.softmax(dim=1)[:, 1].cpu().numpy()

    test_true = y[test_idx]
    test_pred = (test_probs >= best_threshold).astype(int)

    metrics = {
        "model": "URL GCN",
        "selected_threshold": float(best_threshold),
        "seed": SEED,
        "nodes": int(len(nodes)),
        "directed_edges_before_split_filter": int(len(edges)),
        "train_nodes": int(len(train_idx)),
        "validation_nodes": int(len(val_idx)),
        "test_nodes": int(len(test_idx)),
        "train_unique_hostnames": int(len(train_hosts)),
        "validation_unique_hostnames": int(len(val_hosts)),
        "test_unique_hostnames": int(len(test_hosts)),
        "best_epoch": int(best_epoch),
        "best_validation_f1": float(best_val_f1),
        "test_accuracy": float(accuracy_score(test_true, test_pred)),
        "test_precision": float(
            precision_score(test_true, test_pred, zero_division=0)
        ),
        "test_recall": float(
            recall_score(test_true, test_pred, zero_division=0)
        ),
        "test_f1": float(
            f1_score(test_true, test_pred, zero_division=0)
        ),
        "test_roc_auc": float(roc_auc_score(test_true, test_probs))
        if len(np.unique(test_true)) == 2
        else None,
        "test_confusion_matrix": confusion_matrix(
            test_true, test_pred, labels=[0, 1]
        ).tolist(),
        "note": (
            "Experimental URL GCN; hostname-grouped split; "
            "edges crossing splits removed; CPU training."
        ),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "decision_threshold": float(best_threshold),
            "input_channels": data.num_node_features,
            "hidden_channels": HIDDEN_CHANNELS,
            "feature_names": [
                "url_length", "dot_count", "hyphen_count", "digit_count",
                "slash_count", "question_count", "equals_count", "at_count",
                "https", "hostname_length", "subdomain_parts", "ip_address",
            ],
            "scaler_mean": scaler.mean_.tolist(),
            "scaler_scale": scaler.scale_.tolist(),
            "seed": SEED,
        },
        OUTPUT_DIR / "url_gcn.pt",
    )

    metrics_path = OUTPUT_DIR / "evaluation_metrics.json"
    metrics_path.write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    print("\nTest metrics:")
    print(json.dumps(metrics, indent=2))
    print(f"\nSaved model: {OUTPUT_DIR / 'url_gcn.pt'}")
    print(f"Saved metrics: {metrics_path}")


if __name__ == "__main__":
    main()
