
from pathlib import Path
from urllib.parse import urlparse
import ipaddress
import re

import pandas as pd


# Resolve paths relative to the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "dataset" / "phishing_dataset.csv.csv"
OUTPUT_DIR = PROJECT_ROOT / "models" / "gnn" / "data"

MAX_ROWS = 100_000
RANDOM_SEED = 42


def normalize_url(value):
    """Normalize a URL enough to extract its hostname safely."""
    value = str(value).strip()
    if not value:
        return None

    candidate = value if "://" in value else "http://" + value

    try:
        parsed = urlparse(candidate)
        host = (parsed.hostname or "").lower().rstrip(".")
        if not host or "." not in host:
            return None
        return host
    except (ValueError, TypeError):
        return None


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH, encoding="latin-1")
    df = df.dropna(subset=["URL", "Label"]).copy()
    df["URL"] = df["URL"].astype(str).str.strip()
    df["Label"] = df["Label"].astype(str).str.strip().str.lower()
    df = df[df["Label"].isin(["good", "bad"])]
    df = df[df["URL"] != ""]

    # Remove URLs whose labels conflict.
    label_counts = df.groupby("URL")["Label"].nunique()
    conflicting_urls = set(label_counts[label_counts > 1].index)
    df = df[~df["URL"].isin(conflicting_urls)]

    # Remove duplicate URLs before sampling.
    df = df.drop_duplicates(subset=["URL"]).reset_index(drop=True)

    if len(df) > MAX_ROWS:
        df = df.sample(n=MAX_ROWS, random_state=RANDOM_SEED)
        df = df.reset_index(drop=True)

    df["hostname"] = df["URL"].map(normalize_url)

    # Keep URLs for which a hostname can be extracted.
    df = df.dropna(subset=["hostname"]).reset_index(drop=True)

    # Encode labels: good=0, bad=1.
    df["label_id"] = df["Label"].map({"good": 0, "bad": 1}).astype("int64")

    # Each URL is a node. URLs sharing a hostname are connected.
    # Edges are structural only; labels are not used to create edges.
    host_groups = df.groupby("hostname").indices
    edges = set()

    for indices in host_groups.values():
        indices = list(map(int, indices))
        if len(indices) < 2:
            continue

        # Connect adjacent nodes in each hostname group to limit edge growth.
        for left, right in zip(indices[:-1], indices[1:]):
            edges.add((left, right))
            edges.add((right, left))

    # Save a compact, reproducible graph representation.
    nodes_path = OUTPUT_DIR / "url_nodes.csv"
    edges_path = OUTPUT_DIR / "edge_index.csv"
    summary_path = OUTPUT_DIR / "graph_summary.txt"

    df[["URL", "hostname", "Label", "label_id"]].to_csv(
        nodes_path, index=False, encoding="utf-8"
    )

    pd.DataFrame(sorted(edges), columns=["source", "target"]).to_csv(
        edges_path, index=False
    )

    summary = [
        "PhishGuard AI URL graph",
        f"Dataset: {DATA_PATH.name}",
        f"Random seed: {RANDOM_SEED}",
        f"Maximum rows configured: {MAX_ROWS}",
        f"Nodes: {len(df)}",
        f"Directed edges: {len(edges)}",
        f"Unique hostnames: {df['hostname'].nunique()}",
        f"Legitimate nodes (good=0): {(df['label_id'] == 0).sum()}",
        f"Phishing nodes (bad=1): {(df['label_id'] == 1).sum()}",
        "Edge rule: adjacent URLs sharing an identical hostname",
        "Labels are not used to construct edges.",
    ]

    summary_path.write_text("\n".join(summary) + "\n", encoding="utf-8")

    print("\n".join(summary))
    print(f"\nSaved nodes: {nodes_path}")
    print(f"Saved edges: {edges_path}")
    print(f"Saved summary: {summary_path}")


if __name__ == "__main__":
    main()
