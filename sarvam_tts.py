"""
Sarvam Bulbul v3 — Text-to-Speech

Converts text to spoken audio in any supported Indian language.
Returns raw audio bytes (WAV format).
"""

import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
TTS_URL = "https://api.sarvam.ai/text-to-speech"

# Speaker options by gender
SPEAKERS = {
    "female": "anushka",
    "male": "arvind",
}


def text_to_speech(
    text: str,
    target_language_code: str = "ta-IN",
    speaker: str = "anushka",
) -> dict:
    """
    Convert text to speech using Sarvam Bulbul v3.

    Args:
        text: The text to convert to speech.
        target_language_code: Language code (e.g. "ta-IN", "hi-IN").
        speaker: Speaker voice name ("anushka" or "arvind").

    Returns:
        {
            "audio_bytes": b"...",  # raw audio data
            "success": True
        }
        On error:
        {
            "audio_bytes": b"",
            "success": False,
            "error": "error message"
        }
    """
    if not SARVAM_API_KEY:
        return {
            "audio_bytes": b"",
            "success": False,
            "error": "SARVAM_API_KEY not set in .env file",
        }

    if not text or not text.strip():
        return {
            "audio_bytes": b"",
            "success": False,
            "error": "No text provided for speech synthesis",
        }

    headers = {
        "Content-Type": "application/json",
        "api-subscription-key": SARVAM_API_KEY,
    }

    # Sarvam TTS has a character limit per chunk, so we split if needed
    # Max ~500 chars per request is safe
    chunks = _split_text(text, max_chars=500)
    all_audio = b""

    for chunk in chunks:
        payload = {
            "inputs": [chunk],
            "target_language_code": target_language_code,
            "speaker": speaker,
            "model": "bulbul:v3",
        }

        try:
            response = requests.post(
                TTS_URL,
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                audios = result.get("audios", [])
                if audios:
                    # Sarvam returns base64 encoded audio
                    audio_b64 = audios[0]
                    all_audio += base64.b64decode(audio_b64)
                else:
                    return {
                        "audio_bytes": b"",
                        "success": False,
                        "error": "No audio returned from API",
                    }
            else:
                return {
                    "audio_bytes": b"",
                    "success": False,
                    "error": f"API error {response.status_code}: {response.text}",
                }

        except Exception as e:
            return {
                "audio_bytes": b"",
                "success": False,
                "error": f"TTS request failed: {str(e)}",
            }

    return {
        "audio_bytes": all_audio,
        "success": True,
    }


def _split_text(text: str, max_chars: int = 500) -> list[str]:
    """Split text into chunks at sentence boundaries."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""

    sentences = text.replace("।", ".").replace("。", ".").split(".")
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(current) + len(sentence) + 2 <= max_chars:
            current = f"{current}. {sentence}" if current else sentence
        else:
            if current:
                chunks.append(current + ".")
            current = sentence

    if current:
        chunks.append(current + ".")

    return chunks if chunks else [text]


# ── Quick self-test ─────────────────────────────────────
if __name__ == "__main__":
    result = text_to_speech(
        "இந்த குழந்தைக்கு காய்ச்சல் உள்ளது. உடனடியாக மருத்துவமனைக்கு செல்லவும்.",
        target_language_code="ta-IN",
        speaker="anushka",
    )
    if result["success"]:
        with open("test_output.wav", "wb") as f:
            f.write(result["audio_bytes"])
        print("Audio saved to test_output.wav")
    else:
        print(f"Error: {result['error']}")
