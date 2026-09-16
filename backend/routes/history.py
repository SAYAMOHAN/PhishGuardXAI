from flask import Blueprint, jsonify

from services.database_service import get_scan_history


history_bp = Blueprint("history", __name__)


# --------------------------------------------------
# Scan History
# --------------------------------------------------

@history_bp.route("/history", methods=["GET"])
def history():

    try:

        rows = get_scan_history()

        history_data = []

        for row in rows:

            history_data.append({
                "id": row[0],
                "url": row[1],
                "prediction": row[2],
                "probability": float(row[3]),
                "confidence": float(row[4]),
                "risk_score": row[5],
                "risk_level": row[6],
                "threat_intelligence": row[7],
                "shap_evidence": (
                    float(row[8])
                    if row[8] is not None
                    else None
                ),
                "model_disagreement": (
                    float(row[9])
                    if row[9] is not None
                    else None
                ),
                "scan_time": (
                    row[10].isoformat()
                    if row[10] is not None
                    else None
                )
            })

        return jsonify(history_data), 200


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
