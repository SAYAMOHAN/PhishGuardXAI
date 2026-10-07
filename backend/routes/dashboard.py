from flask import Blueprint, jsonify

from services.database_service import (
    get_scan_statistics,
    get_recent_phishing_scans,
    get_user_reports
)


dashboard_bp = Blueprint("dashboard", __name__)


# --------------------------------------------------
# Threat Intelligence Dashboard
# --------------------------------------------------

@dashboard_bp.route("/dashboard", methods=["GET"])
def dashboard():

    try:

        # ------------------------------------------
        # Statistics
        # ------------------------------------------

        statistics = get_scan_statistics()


        # ------------------------------------------
        # Recent phishing scans
        # ------------------------------------------

        recent_rows = get_recent_phishing_scans(
            limit=10
        )

        recent_phishing = []

        for row in recent_rows:

            recent_phishing.append({
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


        # ------------------------------------------
        # User reports
        # ------------------------------------------

        report_rows = get_user_reports()

        reports = []

        for row in report_rows:

            reports.append({
                "id": row[0],
                "url": row[1],
                "reason": row[2],
                "status": row[3],
                "reported_at": (
                    row[4].isoformat()
                    if row[4] is not None
                    else None
                )
            })


        # ------------------------------------------
        # Combined dashboard response
        # ------------------------------------------

        return jsonify({
            "statistics": statistics,
            "recent_phishing": recent_phishing,
            "reports": reports
        }), 200


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
