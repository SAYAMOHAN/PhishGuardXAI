
from pathlib import Path
import json
import random

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    set_seed,
)

SEED = 42
MODEL_NAME = "google-bert/bert-base-uncased"
DATA_PATH = Path("dataset/phishing_dataset.csv.csv")
OUTPUT_DIR = Path("models/bert/saved_model")
METRICS_PATH = Path("models/bert/evaluation_metrics.json")

# Small initial run to check the pipeline on CPU.
MAX_ROWS = 4000
MAX_LENGTH = 96

set_seed(SEED)
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH.resolve()}")

# Load and clean without modifying the original CSV.
df = pd.read_csv(DATA_PATH, encoding="latin-1")
df = df.dropna(subset=["URL", "Label"]).copy()
df["URL"] = df["URL"].astype(str).str.strip()
df["Label"] = df["Label"].astype(str).str.strip().str.lower()
df = df[df["Label"].isin(["good", "bad"])].copy()
df = df[df["URL"] != ""]

# Remove URLs whose labels conflict.
label_counts = df.groupby("URL")["Label"].nunique()
conflicting_urls = label_counts[label_counts > 1].index
df = df[~df["URL"].isin(conflicting_urls)].copy()

# Deduplicate URLs before splitting to prevent URL leakage.
df = df.drop_duplicates(subset=["URL"], keep="first")
df["target"] = df["Label"].map({"good": 0, "bad": 1}).astype(int)

if df["target"].nunique() != 2:
    raise ValueError("Expected both legitimate and phishing labels.")

# A stratified subset for the initial pipeline test.
if len(df) > MAX_ROWS:
    df, _ = train_test_split(
        df,
        train_size=MAX_ROWS,
        random_state=SEED,
        stratify=df["target"],
    )

train_df, temp_df = train_test_split(
    df,
    test_size=0.30,
    random_state=SEED,
    stratify=df["target"],
)

val_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    random_state=SEED,
    stratify=temp_df["target"],
)

print("Dataset rows:", len(df))
print("Train/validation/test:", len(train_df), len(val_df), len(test_df))
print("Label convention: good=0, bad=1")
print("Device: CPU")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

class URLDataset(torch.utils.data.Dataset):
    def __init__(self, frame):
        self.urls = frame["URL"].tolist()
        self.labels = frame["target"].tolist()

    def __len__(self):
        return len(self.urls)

    def __getitem__(self, index):
        encoded = tokenizer(
            self.urls[index],
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
            return_tensors="pt",
        )
        item = {key: value.squeeze(0) for key, value in encoded.items()}
        item["labels"] = torch.tensor(self.labels[index], dtype=torch.long)
        return item

train_dataset = URLDataset(train_df)
val_dataset = URLDataset(val_df)
test_dataset = URLDataset(test_df)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2,
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    probabilities = torch.softmax(torch.tensor(logits), dim=1).numpy()[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    return {
        "accuracy": accuracy_score(labels, predictions),
        "precision": precision_score(labels, predictions, zero_division=0),
        "recall": recall_score(labels, predictions, zero_division=0),
        "f1": f1_score(labels, predictions, zero_division=0),
        "roc_auc": roc_auc_score(labels, probabilities),
    }

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

training_args = TrainingArguments(
    output_dir="models/bert/checkpoints",
    num_train_epochs=1,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=2,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="no",
    logging_steps=25,
    report_to="none",
    use_cpu=True,
    dataloader_num_workers=0,
    seed=SEED,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()

# Evaluate once on the held-out test set.
test_output = trainer.predict(test_dataset)
test_metrics = compute_metrics(
    (test_output.predictions, test_output.label_ids)
)

test_metrics["confusion_matrix"] = confusion_matrix(
    test_output.label_ids,
    (torch.softmax(
        torch.tensor(test_output.predictions), dim=1
    ).numpy()[:, 1] >= 0.5).astype(int),
).tolist()

test_metrics["test_rows"] = len(test_df)
test_metrics["training_rows"] = len(train_df)
test_metrics["validation_rows"] = len(val_df)
test_metrics["seed"] = SEED
test_metrics["max_length"] = MAX_LENGTH
test_metrics["note"] = (
    "Small-subset pipeline test; not final full-dataset results."
)

trainer.save_model(str(OUTPUT_DIR))
tokenizer.save_pretrained(str(OUTPUT_DIR))

METRICS_PATH.write_text(
    json.dumps(test_metrics, indent=2),
    encoding="utf-8",
)

print("\nHeld-out test metrics:")
print(json.dumps(test_metrics, indent=2))
print(f"\nModel saved to: {OUTPUT_DIR.resolve()}")
print(f"Metrics saved to: {METRICS_PATH.resolve()}")
