from flask import Flask, request, jsonify
from database import save_scan, get_history

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "message": "PhishGuardAI backend is running"
    })


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    url = data.get("url")

    if not url:
        return jsonify({
            "error": "URL is required"
        }), 400

    # Temporary test prediction
    prediction = "SAFE"
    probability = 0.05
    confidence = 95.0
    risk_score = 5
    risk_level = "LOW"

    scan_id = save_scan(
        url=url,
        prediction=prediction,
        probability=probability,
        confidence=confidence,
        risk_score=risk_score,
        risk_level=risk_level
    )

    return jsonify({
        "scan_id": scan_id,
        "url": url,
        "prediction": prediction,
        "probability": probability,
        "confidence": confidence,
        "risk_score": risk_score,
        "risk_level": risk_level
    })


@app.route("/history", methods=["GET"])
def history():
    rows = get_history()

    history_data = []

    for row in rows:
        history_data.append({
            "id": row[0],
            "url": row[1],
            "prediction": row[2],
            "probability": float(row[3]) if row[3] is not None else None,
            "confidence": float(row[4]) if row[4] is not None else None,
            "risk_score": row[5],
            "risk_level": row[6],
            "scan_time": row[7].isoformat() if row[7] else None
        })

    return jsonify(history_data)


if __name__ == "__main__":
    app.run(debug=True)