import os
import joblib
import pandas as pd
import shap


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "lightgbm",
    "lightgbm_model.pkl"
)

FEATURE_NAMES = [
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

# --------------------------------------------------
# 2. Load model
# --------------------------------------------------

model = joblib.load(MODEL_PATH)

# --------------------------------------------------
# 4. Verify model and features
# --------------------------------------------------

if len(FEATURE_NAMES) != model.n_features_in_:
    raise ValueError(
        f"Feature mismatch: model expects "
        f"{model.n_features_in_} features, but "
        f"{len(FEATURE_NAMES)} feature names were found."
    )


# --------------------------------------------------
# 5. Create SHAP explainer
# --------------------------------------------------

explainer = shap.TreeExplainer(model)


print("XAI Engine loaded successfully")
print("Model features:", model.n_features_in_)
print("Feature names:", len(FEATURE_NAMES))
# --------------------------------------------------
# 6. Analyze a feature vector
# --------------------------------------------------

def analyze_lightgbm(features):
    """
    Run LightGBM prediction and generate SHAP-based explanation.

    Parameters:
        features: list, numpy array, or dictionary containing 27 features

    Returns:
        Dictionary containing prediction, probabilities,
        confidence, risk, and SHAP feature contributions.
    """

    # Convert dictionary input into the correct feature order
    
    # Convert a URL string into the 11 features expected by LightGBM.
    if isinstance(features, str):
        from backend.feature_extractor import extract_features

        features = extract_features(features)

    if isinstance(features, dict):
        features = [features[name] for name in FEATURE_NAMES]

    # Ensure exactly 11 values are supplied.
    if len(features) != len(FEATURE_NAMES):
        raise ValueError(
            f"Expected {len(FEATURE_NAMES)} features, "
            f"but received {len(features)}."
        )

    X = pd.DataFrame([features], columns=FEATURE_NAMES)


    # --------------------------------------------------
    # Prediction probability
    # --------------------------------------------------

    probabilities = model.predict_proba(X)[0]

    phishing_probability = float(probabilities[1])
    legitimate_probability = float(probabilities[0])

    # --------------------------------------------------
    # Prediction
    # --------------------------------------------------

    prediction = int(model.predict(X)[0])

    if prediction == 1:
        prediction_label = "Phishing"
    else:
        prediction_label = "Legitimate"

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------

    confidence = max(
        phishing_probability,
        legitimate_probability
    )

    # --------------------------------------------------
    # SHAP values
    # --------------------------------------------------

    shap_values = explainer.shap_values(X)

    # Handle different SHAP output formats
    if isinstance(shap_values, list):
        shap_for_phishing = shap_values[1][0]
    else:
        shap_for_phishing = shap_values[0]

    # --------------------------------------------------
    # Create feature contribution list
    # --------------------------------------------------

    contributions = []

    for feature, value, shap_value in zip(
        FEATURE_NAMES,
        features,
        shap_for_phishing
    ):
        contributions.append({
            "feature": feature,
            "value": float(value),
            "shap_value": float(shap_value)
        })

    # Sort by absolute SHAP importance
    contributions.sort(
        key=lambda x: abs(x["shap_value"]),
        reverse=True
    )

    # Top 5 features
    top_features = contributions[:5]

    # --------------------------------------------------
    # SHAP evidence
    # --------------------------------------------------

    total_abs_shap = sum(
        abs(item["shap_value"])
        for item in contributions
    )

    if total_abs_shap > 0:
        shap_evidence = sum(
            abs(item["shap_value"])
            for item in top_features
        ) / total_abs_shap
    else:
        shap_evidence = 0.0

    # --------------------------------------------------
    # Risk level
    # --------------------------------------------------

    if phishing_probability >= 0.75:
        risk = "High"
    elif phishing_probability >= 0.40:
        risk = "Medium"
    else:
        risk = "Low"

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------

    return {
        "prediction": prediction_label,
        "prediction_value": prediction,
        "phishing_probability": phishing_probability,
        "legitimate_probability": legitimate_probability,
        "confidence": confidence,
        "risk": risk,
        "shap_evidence": float(shap_evidence),
        "shap_top_features": top_features
    }