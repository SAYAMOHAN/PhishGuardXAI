from flask import Flask, jsonify

from routes.prediction import prediction_bp
from routes.history import history_bp
from routes.stats import stats_bp
from routes.recent_phishing import recent_phishing_bp
from routes.report import report_bp
from routes.reports import reports_bp


app = Flask(__name__)


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.route("/")
def home():

    return jsonify({
        "message": "PhishGuardAI backend is running"
    })


# --------------------------------------------------
# Register Routes
# --------------------------------------------------

app.register_blueprint(prediction_bp)

app.register_blueprint(history_bp)

app.register_blueprint(stats_bp)

app.register_blueprint(recent_phishing_bp)

app.register_blueprint(report_bp)

app.register_blueprint(reports_bp)


# --------------------------------------------------
# Run Server
# --------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)
