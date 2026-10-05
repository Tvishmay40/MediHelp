"""
app.py
------
ONLY job of this file: HTTP routes. Receives the uploaded prescription photo,
hands the raw bytes to gemini_service.py, and returns JSON to the frontend.
"""

import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

import gemini_service

load_dotenv()

app = Flask(__name__)
CORS(app)  # allow the frontend (different port/origin) to call this API

MAX_UPLOAD_MB = 10
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/analyze")
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image file received. Field name must be 'image'."}), 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"error": "Empty file."}), 400

    image_bytes = image_file.read()
    mime_type = image_file.mimetype or "image/jpeg"

    try:
        result = gemini_service.extract_medicines(image_bytes, mime_type)
    except RuntimeError as exc:
        # e.g. missing API key
        return jsonify({"error": str(exc)}), 500
    except ValueError as exc:
        # e.g. Gemini didn't return parseable JSON
        return jsonify({"error": str(exc)}), 502
    except Exception as exc:  # last-resort guard for a prototype
        return jsonify({"error": f"Unexpected error: {exc}"}), 500

    return jsonify(result), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
