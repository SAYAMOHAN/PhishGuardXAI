"""
=============================================================================
PhishGuard AI - Improved LightGBM Model Trainer
Notebook Section: DATASET VERIFICATION AND LightGBM IMPROVEMENT
=============================================================================
Feature Set (26 Advanced Features):
1. URL_Length               2. No_of_Dots               3. No_of_Hyphens
4. No_of_Digits             5. Has_HTTPS                6. No_of_Slashes
7. No_of_Underscores        8. No_of_QuestionMarks      9. No_of_EqualSigns
10. No_of_At                11. Has_IP                 12. Domain_Length
13. Subdomain_Count         14. Path_Length            15. Query_Length
16. Fragment_Length         17. Path_Depth             18. Digit_Ratio
19. Special_Character_Count 20. Suspicious_Keyword_Count 21. Shortening_Service
22. Punycode_Indicator      23. Port_Presence          24. Double_Slash_Redirect
25. WWW_Indicator           26. IP_Address_Indicator   27. URL_Entropy

LightGBM Hyperparameters:
n_estimators=200, learning_rate=0.05, num_leaves=31, random_state=42
=============================================================================
"""

import os
import re
import math
import time
import pickle
import numpy as np
import pandas as pd
from urllib.parse import urlparse
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

try:
    from lightgbm import LGBMClassifier
    HAS_LIGHTGBM = True
except ImportError:
    from sklearn.ensemble import HistGradientBoostingClassifier
    HAS_LIGHTGBM = False

# Paths configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH_ALT = os.path.join(BASE_DIR, "dataset", "phishing_dataset.csv.csv")
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "phishing_dataset.csv")

MODEL_DIR = os.path.join(BASE_DIR, "backend", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "phishing_model.pkl")

# Suspicious words commonly found in phishing URLs
SUSPICIOUS_KEYWORDS = [
    "login", "signin", "verify", "verification", "secure",
    "account", "update", "confirm", "banking", "password",
    "credential", "wallet", "paypal", "free", "bonus",
    "recover", "authentication", "authorize"
]

# Common URL shortening services
SHORTENING_SERVICES = [
    "bit.ly", "tinyurl.com", "goo.gl", "t.co",
    "ow.ly", "is.gd", "buff.ly", "adf.ly",
    "bit.do", "cutt.ly", "shorturl.at"
]


def extract_improved_features_single(url_raw):
    """
    Extracts 26 features matching Cell 47 / Cell 60 of notebook.
    """
    url = str(url_raw)
    url_lower = url.lower()
    
    # 1. Base URL features
    url_length = len(url)
    no_of_dots = url.count(".")
    no_of_hyphens = url.count("-")
    digit_count = sum(c.isdigit() for c in url)
    has_https = 1 if "https" in url_lower else 0
    no_of_slashes = url.count("/")
    no_of_underscores = url.count("_")
    no_of_questionmarks = url.count("?")
    no_of_equalsigns = url.count("=")
    no_of_at = url.count("@")
    has_ip = 1 if re.search(r'(\d{1,3}\.){3}\d{1,3}', url) else 0

    # 2. Parsed URL elements
    try:
        parsed_url = urlparse(url if re.match(r"^[a-zA-Z]+://", url) else "http://" + url)
        hostname = parsed_url.hostname or ""
        path = parsed_url.path or ""
        query = parsed_url.query or ""
        fragment = parsed_url.fragment or ""
    except Exception:
        hostname = path = query = fragment = ""

    domain_length = len(hostname)
    subdomain_count = max(0, hostname.count(".") - 1)
    path_length = len(path)
    query_length = len(query)
    fragment_length = len(fragment)
    path_depth = path.count("/")
    digit_ratio = (digit_count / url_length) if url_length > 0 else 0
    special_character_count = sum(not c.isalnum() for c in url)
    suspicious_keyword_count = sum(kw in url_lower for kw in SUSPICIOUS_KEYWORDS)
    shortening_service = int(any(srv in hostname.lower() for srv in SHORTENING_SERVICES))
    punycode_indicator = int("xn--" in hostname.lower())
    
    try:
        port_presence = int(parsed_url.port is not None)
    except Exception:
        port_presence = 0

    double_slash_redirect = int("//" in path)
    www_indicator = int(hostname.lower().startswith("www."))
    ip_address_indicator = int(bool(re.match(r"^(?:\d{1,3}\.){3}\d{1,3}$", hostname)))

    # Entropy
    freq = {}
    for c in url:
        freq[c] = freq.get(c, 0) + 1
    entropy = 0.0
    if url_length > 0:
        for count in freq.values():
            prob = count / url_length
            entropy -= prob * math.log2(prob)

    return [
        url_length, no_of_dots, no_of_hyphens, digit_count,
        has_https, no_of_slashes, no_of_underscores, no_of_questionmarks,
        no_of_equalsigns, no_of_at, has_ip,
        domain_length, subdomain_count, path_length, query_length,
        fragment_length, path_depth, digit_ratio, special_character_count,
        suspicious_keyword_count, shortening_service, punycode_indicator,
        port_presence, double_slash_redirect, www_indicator,
        ip_address_indicator, entropy
    ]


def extract_improved_features_dataframe(df):
    print("Extracting 27 improved features from URLs (Model 2)...")
    t0 = time.time()
    feature_rows = df['URL'].apply(extract_improved_features_single).tolist()
    X = np.array(feature_rows)
    print(f"Improved feature extraction completed in {time.time() - t0:.2f} seconds.")
    return X


FEATURE_NAMES = [
    "URL_Length", "No_of_Dots", "No_of_Hyphens", "No_of_Digits",
    "Has_HTTPS", "No_of_Slashes", "No_of_Underscores", "No_of_QuestionMarks",
    "No_of_EqualSigns", "No_of_At", "Has_IP",
    "Domain_Length", "Subdomain_Count", "Path_Length", "Query_Length",
    "Fragment_Length", "Path_Depth", "Digit_Ratio", "Special_Character_Count",
    "Suspicious_Keyword_Count", "Shortening_Service", "Punycode_Indicator",
    "Port_Presence", "Double_Slash_Redirect", "WWW_Indicator",
    "IP_Address_Indicator", "URL_Entropy"
]


def train_and_save_model():
    print("=" * 70)
    print(" Starting Notebook Improved LightGBM Training (Model 2)")
    print("=" * 70)

    target_csv = DATASET_PATH_ALT if os.path.exists(DATASET_PATH_ALT) else DATASET_PATH
    if not os.path.exists(target_csv):
        print(f"Error: Dataset CSV file not found at {target_csv}")
        return

    print(f"Loading dataset: {target_csv}...")
    df = pd.read_csv(target_csv, encoding='latin-1')
    
    df.columns = ['URL', 'Label']
    df = df.dropna(subset=['URL', 'Label']).reset_index(drop=True)
    df = df.drop_duplicates()
    print(f"Dataset loaded: {len(df):,} total unique URL entries.")

    df['Label'] = df['Label'].astype(str).str.lower().apply(lambda l: 1 if 'bad' in l or 'phish' in l or '1' in l else 0)

    print(f"Training on full dataset: {len(df):,} total URL samples...")
    X = extract_improved_features_dataframe(df)
    y = df['Label'].values

    # Train / Test Split (80% Train, 20% Test, stratify)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

    print("Training Improved LightGBM (Model 2) with Notebook Hyperparameters...")
    if HAS_LIGHTGBM:
        model = LGBMClassifier(
            random_state=42,
            n_estimators=200,
            learning_rate=0.05,
            num_leaves=31,
            verbose=-1,
            min_child_samples=2
        )
    else:
        model = HistGradientBoostingClassifier(random_state=42, max_iter=200, learning_rate=0.05)

    t_train0 = time.time()
    model.fit(X_train, y_train)
    print(f"LightGBM Model 2 fitted in {time.time() - t_train0:.2f} seconds.")

    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print("\n" + "-" * 40)
    print("--- IMPROVED LIGHTGBM MODEL (MODEL 2) RESULTS ---")
    print(f"   Accuracy  : {acc * 100:.2f}%")
    print(f"   Precision : {prec * 100:.2f}%")
    print(f"   Recall    : {rec * 100:.2f}%")
    print(f"   F1-Score  : {f1 * 100:.2f}%")
    print(f"   Tested on : {len(X_test):,} validation URLs")
    print("-" * 40 + "\n")

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({
            "model": model,
            "feature_names": FEATURE_NAMES,
            "accuracy": acc,
            "trained_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }, f)

    print(f"Trained model weights successfully saved to:\n   {MODEL_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    train_and_save_model()
