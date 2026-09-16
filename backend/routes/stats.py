from flask import Blueprint, jsonify

from services.database_service import get_scan_statistics


stats_bp = Blueprint("stats", __name__)


# --------------------------------------------------
# Dashboard Statistics
# --------------------------------------------------

@stats_bp.route("/stats", methods=["GET"])
def statistics():

    try:

        stats = get_scan_statistics()

        return jsonify(stats), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
