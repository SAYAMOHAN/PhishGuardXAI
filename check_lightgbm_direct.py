
import joblib
import pandas as pd

from backend.feature_extractor import extract_features, FEATURE_NAMES

model = joblib.load("models/lightgbm/lightgbm_model.pkl")

print("FEATURE ORDER MATCH:",
      list(model.booster_.feature_name()) == FEATURE_NAMES)

urls = [
    "https://www.wikipedia.org/",
    "http://paypal.com.security-check.example/login",
]

for url in urls:
    features = extract_features(url)

    X = pd.DataFrame(
        [[features[name] for name in FEATURE_NAMES]],
        columns=FEATURE_NAMES,
    )

    probabilities = model.predict_proba(X)[0]
    phishing_probability = probabilities[1]
    predicted_class = int(phishing_probability >= 0.30)

    print("\nURL:", url)
    print("FEATURES:", X.to_dict(orient="records")[0])
    print("MODEL CLASSES:", model.classes_.tolist())
    print("RAW PROBABILITIES:", probabilities.tolist())
    print("PREDICTED CLASS:", predicted_class)
    print("THRESHOLD USED: 0.30")
