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

PROJECT_ROOT = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# --------------------------------------------------
# Import the inference bridge
# --------------------------------------------------

from model_inference_bridge import predict_with_bert_gnn


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

    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must be a non-empty string")

    url = url.strip()

    # ----------------------------------------------
    # 1. Extract features
    # ----------------------------------------------

    features = extract_features(url)

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

    phishing_probability = float(probabilities[1])

    prediction_value = int(model.predict(X)[0])

    prediction = (
        "PHISHING" if prediction_value == 1 else "SAFE"
    )


    # ----------------------------------------------
    # 3. Confidence
    # ----------------------------------------------

    confidence = (
        phishing_probability * 100
        if prediction == "PHISHING"
        else (1 - phishing_probability) * 100
    )

    confidence_normalized = confidence / 100


    # ----------------------------------------------
    # 4. SHAP explanation and evidence
    # ----------------------------------------------

    explanation = explain_prediction(features)

    shap_evidence = calculate_shap_evidence(features)


    # ----------------------------------------------
    # 5. Real BERT and GNN inference
    # ----------------------------------------------

    # Raises an error if either model fails.
    # Do not silently substitute LightGBM probabilities.

    model_outputs = predict_with_bert_gnn(url)

    bert_probability = float(
        model_outputs["bert_probability"]
    )

    gnn_probability = float(
        model_outputs["gnn_probability"]
    )

    for name, probability in (
        ("BERT", bert_probability),
        ("GNN", gnn_probability),
        ("LightGBM", phishing_probability),
    ):
        if not 0.0 <= probability <= 1.0:
            raise ValueError(
                f"{name} returned an invalid probability"
            )


    # ----------------------------------------------
    # 6. Model disagreement
    # ----------------------------------------------

    model_disagreement = calculate_model_disagreement(
        bert_probability=bert_probability,
        lightgbm_probability=phishing_probability,
        gnn_probability=gnn_probability
    )


    # ----------------------------------------------
    # 7. Adaptive risk score
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
    # 8. Adaptive risk level
    # ----------------------------------------------

    adaptive_risk_level = determine_risk_level(
        risk_score=adaptive_risk_score,
        model_disagreement=model_disagreement,
        confidence=confidence_normalized
    )


    # ----------------------------------------------
    # 9. Prepare result
    # ----------------------------------------------

    return {
        "url": url,
        "prediction": prediction,
        "probability": phishing_probability,
        "lightgbm_probability": phishing_probability,
        "bert_probability": bert_probability,
        "gnn_probability": gnn_probability,
        "confidence": confidence,
        "confidence_normalized": confidence_normalized,
        "risk_score": round(adaptive_risk_score, 2),
        "risk_level": adaptive_risk_level,
        "shap_evidence": shap_evidence,
        "model_disagreement": model_disagreement,
        "explanation": explanation
    }
