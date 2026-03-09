"""
Sarvam Saaras v3 — Speech-to-Text

Sends a WAV audio file to Sarvam's STT API.
Returns transcript text + auto-detected language code.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
STT_URL = "https://api.sarvam.ai/speech-to-text"


def speech_to_text(audio_file_path: str) -> dict:
    """
    Send an audio file to Sarvam Saaras v3 for transcription.

    Args:
        audio_file_path: Path to the WAV audio file.

    Returns:
        {
            "transcript": "patient symptom text",
            "language_code": "ta-IN",
            "success": True
        }
        On error:
        {
            "transcript": "",
            "language_code": "",
            "success": False,
            "error": "error message"
        }
    """
    if not SARVAM_API_KEY:
        return {
            "transcript": "",
            "language_code": "",
            "success": False,
            "error": "SARVAM_API_KEY not set in .env file",
        }

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
    }

    try:
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "file": (os.path.basename(audio_file_path), audio_file, "audio/wav"),
            }
            data = {
                "model": "saaras:v3",
            }

            response = requests.post(
                STT_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=30,
            )

        if response.status_code == 200:
            result = response.json()
            return {
                "transcript": result.get("transcript", ""),
                "language_code": result.get("language_code", ""),
                "success": True,
            }
        else:
            return {
                "transcript": "",
                "language_code": "",
                "success": False,
                "error": f"API error {response.status_code}: {response.text}",
            }

    except FileNotFoundError:
        return {
            "transcript": "",
            "language_code": "",
            "success": False,
            "error": f"Audio file not found: {audio_file_path}",
        }
    except Exception as e:
        return {
            "transcript": "",
            "language_code": "",
            "success": False,
            "error": f"STT request failed: {str(e)}",
        }


# ── Quick self-test ─────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        result = speech_to_text(sys.argv[1])
        print(f"Transcript: {result['transcript']}")
        print(f"Language:   {result['language_code']}")
        print(f"Success:    {result['success']}")
        if not result["success"]:
            print(f"Error:      {result['error']}")
    else:
        print("Usage: python sarvam_stt.py <path_to_audio.wav>")
