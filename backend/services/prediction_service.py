import os
import sys
import joblib
import pandas as pd

# Allow access to the project root and backend files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from feature_extractor import extract_features, FEATURE_NAMES
from xai.shap_explainer import explain_prediction


# --------------------------------------------------
# Load LightGBM model
# --------------------------------------------------

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "lightgbm",
    "lightgbm_model.pkl"
)

model = joblib.load(MODEL_PATH)

print("Prediction service: LightGBM model loaded successfully!")


# --------------------------------------------------
# Predict URL
# --------------------------------------------------

def predict_url(url):

    # Extract the same 11 features used by the trained model
    features = extract_features(url)

    # Keep exact feature order
    feature_values = [
        features[name]
        for name in FEATURE_NAMES
    ]

    X = pd.DataFrame(
        [feature_values],
        columns=FEATURE_NAMES
    )

    # Get probabilities
    probabilities = model.predict_proba(X)[0]

    phishing_probability = float(probabilities[1])

    # Get prediction
    prediction_value = int(model.predict(X)[0])

    if prediction_value == 1:
        prediction = "PHISHING"
    else:
        prediction = "SAFE"

    # Confidence
    confidence = (
        phishing_probability * 100
        if prediction == "PHISHING"
        else (1 - phishing_probability) * 100
    )

    # Risk score
    risk_score = round(phishing_probability * 100)

    # Risk level
    if risk_score >= 75:
        risk_level = "CRITICAL"
    elif risk_score >= 50:
        risk_level = "HIGH"
    elif risk_score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # Existing SHAP module
    explanation = explain_prediction(features)

    return {
        "url": url,
        "prediction": prediction,
        "probability": phishing_probability,
        "confidence": confidence,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "explanation": explanation
    }
