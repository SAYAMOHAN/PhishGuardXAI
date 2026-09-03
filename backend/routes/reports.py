from flask import Blueprint, jsonify

from services.database_service import get_user_reports


reports_bp = Blueprint("reports", __name__)


# --------------------------------------------------
# Get User Reports
# --------------------------------------------------

@reports_bp.route("/reports", methods=["GET"])
def reports():

    try:

        rows = get_user_reports()

        reports_data = []

        for row in rows:

            reports_data.append({
                "id": row[0],
                "url": row[1],
                "reason": row[2],
                "status": row[3],
                "reported_at": (
                    row[4].isoformat()
                    if row[4]
                    else None
                )
            })

        return jsonify(reports_data), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
