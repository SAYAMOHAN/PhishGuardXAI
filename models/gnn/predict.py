
from pathlib import Path
from urllib.parse import urlparse
import ipaddress
import re

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch_geometric.nn import GCNConv


ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_PATH = ROOT / "models" / "gnn" / "saved_model" / "url_gcn.pt"


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


def _features(url):
    """Keep the feature order identical to the training script."""
    value = str(url).strip()
    candidate = value if "://" in value else "http://" + value

    try:
        host = (urlparse(candidate).hostname or "").lower().rstrip(".")
    except ValueError:
        host = ""

    is_ip = 0
    try:
        ipaddress.ip_address(host)
        is_ip = 1
    except ValueError:
        pass

    return np.array([[
        len(value),
        value.count("."),
        value.count("-"),
        sum(ch.isdigit() for ch in value),
        value.count("/"),
        value.count("?"),
        value.count("="),
        value.count("@"),
        int(value.lower().startswith("https://")),
        len(host),
        host.count("."),
        is_ip,
    ]], dtype=np.float32)


_checkpoint = torch.load(
    CHECKPOINT_PATH,
    map_location="cpu",
    weights_only=True,
)

_model = URLGCN(
    input_channels=_checkpoint["input_channels"],
    hidden_channels=_checkpoint["hidden_channels"],
)
_model.load_state_dict(_checkpoint["model_state_dict"])
_model.eval()

_MEAN = np.asarray(_checkpoint["scaler_mean"], dtype=np.float32)
_SCALE = np.asarray(_checkpoint["scaler_scale"], dtype=np.float32)
_THRESHOLD = float(_checkpoint["decision_threshold"])


def predict_gnn(url: str) -> float:
    """
    Return the model's phishing probability for a URL.

    IMPORTANT: this uses a single-node graph with a self-loop.
    It is an integration approximation, not the graph evaluation setup.
    """
    raw = _features(url)
    scale = np.where(_SCALE == 0, 1.0, _SCALE)
    scaled = (raw - _MEAN) / scale

    x = torch.tensor(scaled, dtype=torch.float32)
    edge_index = torch.tensor([[0], [0]], dtype=torch.long)

    with torch.no_grad():
        logits = _model(x, edge_index)
        probability = torch.softmax(logits, dim=1)[0, 1].item()

    return float(probability)


def predict_gnn_label(url: str) -> dict:
    probability = predict_gnn(url)
    return {
        "phishing_probability": probability,
        "threshold": _THRESHOLD,
        "prediction": int(probability >= _THRESHOLD),
        "inference_mode": "single_node_self_loop_approximation",
    }


if __name__ == "__main__":
    samples = [
        "https://www.wikipedia.org/",
        "http://paypal.com.security-check.example/login",
    ]

    for sample in samples:
        print(sample)
        print(predict_gnn_label(sample))
