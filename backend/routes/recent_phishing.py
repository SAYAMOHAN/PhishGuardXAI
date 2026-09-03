from flask import Blueprint, jsonify, request

from services.database_service import get_recent_phishing_scans


recent_phishing_bp = Blueprint(
    "recent_phishing",
    __name__
)


# --------------------------------------------------
# Recent Phishing Scans
# --------------------------------------------------

@recent_phishing_bp.route(
    "/recent-phishing",
    methods=["GET"]
)
def recent_phishing():

    try:

        # Get requested number of records
        limit = request.args.get(
            "limit",
            default=10,
            type=int
        )

        # Keep the limit within a safe range
        if limit < 1:
            limit = 1

        if limit > 50:
            limit = 50

        rows = get_recent_phishing_scans(limit)

        phishing_data = []

        for row in rows:

            phishing_data.append({

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

        return jsonify(phishing_data), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
