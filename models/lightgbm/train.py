import pandas as pd
import numpy as np
import re
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from lightgbm import LGBMClassifier


# 1. Load dataset
df = pd.read_csv("datasets/raw/phishing_site_urls.csv")


# 2. Data cleaning
df = df.dropna()
df = df.drop_duplicates()


# 3. Convert labels
df["Label"] = df["Label"].map({
    "good": 0,
    "bad": 1
})

df = df.dropna(subset=["Label"])
df["Label"] = df["Label"].astype(int)


# 4. Feature extraction

df["URL_Length"] = df["URL"].apply(len)
df["No_of_Dots"] = df["URL"].str.count(r"\.")
df["No_of_Hyphens"] = df["URL"].str.count("-")
df["No_of_Digits"] = df["URL"].str.count(r"\d")
df["Has_HTTPS"] = df["URL"].str.contains("https").astype(int)

df["No_of_Slashes"] = df["URL"].str.count("/")
df["No_of_Underscores"] = df["URL"].str.count("_")
df["No_of_QuestionMarks"] = df["URL"].str.count(r"\?")
df["No_of_EqualSigns"] = df["URL"].str.count("=")
df["No_of_At"] = df["URL"].str.count("@")


# Check IP address
def has_ip(url):
    pattern = r'(\d{1,3}\.){3}\d{1,3}'
    return 1 if re.search(pattern, url) else 0


df["Has_IP"] = df["URL"].apply(has_ip)


# 5. Select features

features = [
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
    "Has_IP"
]


X = df[features]
y = df["Label"]

import os

os.makedirs("datasets/processed", exist_ok=True)

df.to_csv(
    "datasets/processed/processed_phishing_urls.csv",
    index=False
)

print("Processed dataset saved")


# 6. Split data

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# 7. Train LightGBM

model = LGBMClassifier(random_state=42)

model.fit(X_train, y_train)


# 8. Evaluate

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))


# 9. Save model

joblib.dump(model, "models/lightgbm/lightgbm_model.pkl")

print("Model saved successfully")