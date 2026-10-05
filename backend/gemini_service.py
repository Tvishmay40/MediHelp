"""
gemini_service.py
------------------
ONLY job of this file: talk to the Gemini API and turn its answer into a
clean Python list of medicines. No Flask, no routing, no file handling here.
"""

import os
import json
import re
import google.generativeai as genai

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# The prompt is written to force Gemini to return ONLY JSON, nothing else.
PROMPT = """You are a medical prescription reading assistant.
You will be shown a photo of a doctor's prescription (handwritten or printed).

Read it carefully and extract every medicine mentioned.

Respond with ONLY valid JSON (no markdown, no backticks, no extra text),
in exactly this shape:

{
  "medicines": [
    {
      "name": "medicine name as best identified",
      "dose": "dose/strength if visible, else empty string",
      "frequency": "how often / when to take it, e.g. '1-0-1 after food', else empty string",
      "duration": "how many days/weeks if mentioned, else empty string",
      "confidence": "high | medium | low"
    }
  ],
  "notes": "any short warning, e.g. if the image is unclear or unreadable"
}

If you cannot find any medicines, return {"medicines": [], "notes": "explain why"}.
"""


def _configure():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add your key."
        )
    genai.configure(api_key=api_key)


def _extract_json(raw_text: str) -> dict:
    """Gemini sometimes wraps JSON in ```json fences — strip those before parsing."""
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned.strip(), flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned.strip()).strip()
    return json.loads(cleaned)


def extract_medicines(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """
    Takes raw image bytes from an uploaded prescription photo and returns:
    { "medicines": [ {name, dose, frequency, duration, confidence}, ... ], "notes": str }
    Raises RuntimeError / ValueError on failure — the caller (app.py) turns
    those into proper HTTP error responses.
    """
    _configure()

    model = genai.GenerativeModel(GEMINI_MODEL)

    response = model.generate_content(
        [
            PROMPT,
            {"mime_type": mime_type, "data": image_bytes},
        ]
    )

    raw_text = response.text or ""
    try:
        data = _extract_json(raw_text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(f"Gemini did not return valid JSON: {exc}\nRaw: {raw_text[:500]}")

    data.setdefault("medicines", [])
    data.setdefault("notes", "")
    return data
