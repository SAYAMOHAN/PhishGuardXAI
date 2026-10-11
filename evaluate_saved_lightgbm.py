
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)

DATA_PATH = "datasets/processed/processed_phishing_urls.csv"
MODEL_PATH = "models/lightgbm/lightgbm_model.pkl"

FEATURES = [
    "URL_Length",
    "No_of_Dots",
    "No_of_Hyphens",
    "No_of_Digits",
    "Has_HTTPS",
    "No_of_Slashes",
    "No_of_Underscores",
    "No_of_QuestionMarks",
    "No_of_EqualSigns",
    "No_of_At",
    "Has_IP",
]

print("Loading processed dataset...")
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=FEATURES + ["Label"])

X = df[FEATURES]
y = df["Label"].astype(int)

_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

print("Loading existing model (no training)...")
model = joblib.load(MODEL_PATH)

probabilities = model.predict_proba(X_test)[:, 1]

print("\nSaved LightGBM model evaluation")
print("Test rows:", len(y_test))

for threshold in [0.30, 0.40, 0.50, 0.60]:
    predictions = (probabilities >= threshold).astype(int)
    print(f"\nThreshold: {threshold:.2f}")
    print(f"Accuracy:  {accuracy_score(y_test, predictions):.4f}")
    print(f"Precision: {precision_score(y_test, predictions, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(y_test, predictions, zero_division=0):.4f}")
    print(f"F1-score:  {f1_score(y_test, predictions, zero_division=0):.4f}")

print("\nConfusion matrix at threshold 0.30:")
print(confusion_matrix(y_test, (probabilities >= 0.30).astype(int), labels=[0, 1]))
print("\nClassification report at threshold 0.30:")
print(classification_report(
    y_test,
    (probabilities >= 0.30).astype(int),
    target_names=["Legitimate", "Phishing"],
    zero_division=0,
))
