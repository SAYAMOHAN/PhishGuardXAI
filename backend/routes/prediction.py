from flask import Blueprint, request, jsonify

from services.prediction_service import predict_url
from services.database_service import save_scan_result
from services.threat_intelligence_service import check_threat_intelligence


prediction_bp = Blueprint("prediction", __name__)


# --------------------------------------------------
# Predict URL
# --------------------------------------------------

@prediction_bp.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON data is required"
        }), 400

    url = data.get("url")

    if not url:
        return jsonify({
            "error": "URL is required"
        }), 400

    try:

        # ------------------------------------------
        # ML + SHAP prediction
        # ------------------------------------------

        result = predict_url(url)

        # ------------------------------------------
        # Threat Intelligence
        # ------------------------------------------

        threat_intelligence = check_threat_intelligence(url)

        result["threat_intelligence"] = threat_intelligence

        # ------------------------------------------
        # Save complete result to database
        # ------------------------------------------

        scan_id = save_scan_result(
            url=result["url"],
            prediction=result["prediction"],
            probability=result["probability"],
            confidence=result["confidence"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            threat_intelligence=threat_intelligence
        )

        result["scan_id"] = scan_id

        return jsonify(result), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# --------------------------------------------------
# Scan Endpoint
# --------------------------------------------------

@prediction_bp.route("/scan", methods=["POST"])
def scan():

    return predict()
