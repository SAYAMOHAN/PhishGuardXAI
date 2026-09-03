from flask import Blueprint, jsonify, request

from services.database_service import get_scan_history


history_bp = Blueprint("history", __name__)


# --------------------------------------------------
# Scan History
# --------------------------------------------------

@history_bp.route("/history", methods=["GET"])
def history():

    rows = get_scan_history()

    # --------------------------------------------------
    # Get optional filters from URL
    # --------------------------------------------------

    search = request.args.get("search", "").strip().lower()
    prediction_filter = request.args.get("prediction", "").strip().upper()
    risk_filter = request.args.get("risk_level", "").strip().upper()

    history_data = []

    for row in rows:

        url = row[1]
        prediction = row[2]
        risk_level = row[6]

        # --------------------------------------------------
        # Search filter
        # Searches inside the scanned URL
        # --------------------------------------------------

        if search and search not in url.lower():
            continue

        # --------------------------------------------------
        # Prediction filter
        # Example: ?prediction=PHISHING
        # --------------------------------------------------

        if prediction_filter and prediction != prediction_filter:
            continue

        # --------------------------------------------------
        # Risk level filter
        # Example: ?risk_level=CRITICAL
        # --------------------------------------------------

        if risk_filter and risk_level != risk_filter:
            continue

        # --------------------------------------------------
        # Add matching scan
        # --------------------------------------------------

        history_data.append({

            "id": row[0],

            "url": row[1],

            "prediction": row[2],

            "probability": (
                float(row[3])
                if row[3] is not None
                else None
            ),

            "confidence": (
                float(row[4])
                if row[4] is not None
                else None
            ),

            "risk_score": row[5],

            "risk_level": row[6],

            "threat_intelligence": row[7],

            "scan_time": (
                row[8].isoformat()
                if row[8]
                else None
            )
        })

    return jsonify(history_data), 200
