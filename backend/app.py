from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])


@app.route("/")
def home():
    return jsonify({"message": "LexPredict backend is running!"})


@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "LexPredict API"
    })


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    if not data.get("case_type") or not data.get("case_description"):
        return jsonify({
            "error": "Please provide case_type and case_description"
        }), 400

    return jsonify({
        "message": "Case received successfully",
        "case_type": data["case_type"],
        "prediction": None,
        "status": "model_not_connected",
        "note": "A trained prediction model is not connected yet."
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
