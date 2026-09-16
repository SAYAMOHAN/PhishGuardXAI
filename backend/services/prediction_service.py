import os
import sys
import joblib
import pandas as pd


# --------------------------------------------------
# Allow access to project root and backend files
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PROJECT_DIR = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)


# --------------------------------------------------
# Imports
# --------------------------------------------------

from feature_extractor import (
    extract_features,
    FEATURE_NAMES
)

from xai.shap_explainer import (
    explain_prediction,
    calculate_shap_evidence
)

from services.risk_engine import (
    calculate_model_disagreement,
    calculate_risk_score,
    determine_risk_level
)


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

print(
    "Prediction service: "
    "LightGBM model loaded successfully!"
)


# --------------------------------------------------
# Predict URL
# --------------------------------------------------

def predict_url(url):

    # ----------------------------------------------
    # 1. Extract features
    # ----------------------------------------------

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


    # ----------------------------------------------
    # 2. LightGBM prediction
    # ----------------------------------------------

    probabilities = model.predict_proba(X)[0]

    phishing_probability = float(
        probabilities[1]
    )

    prediction_value = int(
        model.predict(X)[0]
    )


    # ----------------------------------------------
    # 3. Prediction label
    # ----------------------------------------------

    if prediction_value == 1:
        prediction = "PHISHING"
    else:
        prediction = "SAFE"


    # ----------------------------------------------
    # 4. Confidence
    # ----------------------------------------------

    confidence = (
        phishing_probability * 100
        if prediction == "PHISHING"
        else (1 - phishing_probability) * 100
    )

    # Convert confidence to 0-1 scale
    confidence_normalized = confidence / 100


    # ----------------------------------------------
    # 5. Original LightGBM risk score
    # ----------------------------------------------

    lightgbm_risk_score = round(
        phishing_probability * 100
    )


    # ----------------------------------------------
    # 6. Original LightGBM risk level
    # ----------------------------------------------

    if lightgbm_risk_score >= 75:

        risk_level = "CRITICAL"

    elif lightgbm_risk_score >= 50:

        risk_level = "HIGH"

    elif lightgbm_risk_score >= 25:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"


    # ----------------------------------------------
    # 7. SHAP explanation
    # ----------------------------------------------

    explanation = explain_prediction(
        features
    )


    # ----------------------------------------------
    # 8. SHAP evidence
    # ----------------------------------------------

    shap_evidence = calculate_shap_evidence(
        features
    )


    # ----------------------------------------------
    # 9. Adaptive Risk Engine
    # ----------------------------------------------

    # TEMPORARY:
    # BERT and GNN probabilities will be replaced
    # with actual model outputs during final integration.

    bert_probability = phishing_probability

    gnn_probability = phishing_probability


    # ----------------------------------------------
    # 9A. Model disagreement
    # ----------------------------------------------

    model_disagreement = calculate_model_disagreement(
        bert_probability=bert_probability,
        lightgbm_probability=phishing_probability,
        gnn_probability=gnn_probability
    )


    # ----------------------------------------------
    # 9B. Adaptive Risk Score
    # ----------------------------------------------

    adaptive_risk_score = calculate_risk_score(
        bert_probability=bert_probability,
        lightgbm_probability=phishing_probability,
        gnn_probability=gnn_probability,
        shap_evidence=shap_evidence,
        confidence=confidence_normalized,
        model_disagreement=model_disagreement
    )


    # ----------------------------------------------
    # 9C. Adaptive Risk Level
    # ----------------------------------------------

    adaptive_risk_level = determine_risk_level(
        risk_score=adaptive_risk_score,
        model_disagreement=model_disagreement,
        confidence=confidence_normalized
    )


    # ----------------------------------------------
    # 10. Prepare result
    # ----------------------------------------------

    return {

        "url": url,

        "prediction": prediction,

        "probability": phishing_probability,

        "lightgbm_probability": phishing_probability,

        "confidence": confidence,

        "confidence_normalized": confidence_normalized,

        "risk_score": round(
            adaptive_risk_score,
            2
        ),

        "risk_level": adaptive_risk_level,

        "shap_evidence": shap_evidence,

        "model_disagreement": model_disagreement,

        "explanation": explanation

    }
