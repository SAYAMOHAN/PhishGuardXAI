from flask import Blueprint, request, jsonify

from services.database_service import save_user_report


report_bp = Blueprint("report", __name__)


# --------------------------------------------------
# Submit User Report
# --------------------------------------------------

@report_bp.route("/report", methods=["POST"])
def report():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON data is required"
        }), 400

    url = data.get("url")
    reason = data.get("reason")

    if not url:
        return jsonify({
            "error": "URL is required"
        }), 400

    try:

        report_id = save_user_report(
            url=url,
            reason=reason
        )

        return jsonify({
            "message": "URL reported successfully",
            "report_id": report_id,
            "url": url,
            "reason": reason,
            "status": "PENDING"
        }), 201

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
