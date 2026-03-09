"""
Sarvam Mayura — Translation

Translates text between Indian languages and English
using Sarvam's translation API.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
TRANSLATE_URL = "https://api.sarvam.ai/translate"

# Supported language codes
SUPPORTED_LANGUAGES = {
    "hi-IN": "Hindi",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "bn-IN": "Bengali",
    "mr-IN": "Marathi",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "gu-IN": "Gujarati",
    "pa-IN": "Punjabi",
    "or-IN": "Odia",
    "en-IN": "English",
}


def translate_text(
    text: str,
    source_language_code: str = "auto",
    target_language_code: str = "en-IN",
) -> dict:
    """
    Translate text using Sarvam Mayura.

    Args:
        text: The text to translate.
        source_language_code: Source language code (e.g. "ta-IN"), or "auto".
        target_language_code: Target language code (e.g. "en-IN").

    Returns:
        {
            "translated_text": "translated output",
            "success": True
        }
        On error:
        {
            "translated_text": "",
            "success": False,
            "error": "error message"
        }
    """
    if not SARVAM_API_KEY:
        return {
            "translated_text": "",
            "success": False,
            "error": "SARVAM_API_KEY not set in .env file",
        }

    if not text or not text.strip():
        return {
            "translated_text": "",
            "success": False,
            "error": "No text provided for translation",
        }

    headers = {
        "Content-Type": "application/json",
        "api-subscription-key": SARVAM_API_KEY,
    }

    payload = {
        "input": text,
        "source_language_code": source_language_code,
        "target_language_code": target_language_code,
    }

    try:
        response = requests.post(
            TRANSLATE_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "translated_text": result.get("translated_text", ""),
                "success": True,
            }
        else:
            return {
                "translated_text": "",
                "success": False,
                "error": f"API error {response.status_code}: {response.text}",
            }

    except Exception as e:
        return {
            "translated_text": "",
            "success": False,
            "error": f"Translation request failed: {str(e)}",
        }


def to_english(text: str, source_language_code: str = "auto") -> dict:
    """Convenience: translate any Indian language → English."""
    return translate_text(text, source_language_code, "en-IN")


def from_english(text: str, target_language_code: str = "hi-IN") -> dict:
    """Convenience: translate English → any Indian language."""
    return translate_text(text, "en-IN", target_language_code)


def get_language_name(code: str) -> str:
    """Return human-readable language name for a code."""
    return SUPPORTED_LANGUAGES.get(code, code)


# ── Quick self-test ─────────────────────────────────────
if __name__ == "__main__":
    # Test English → Hindi
    result = to_english("मुझे बुखार है और सिर दर्द है")
    print(f"To English: {result}")

    result2 = from_english("The patient has fever and headache", "ta-IN")
    print(f"To Tamil:   {result2}")
