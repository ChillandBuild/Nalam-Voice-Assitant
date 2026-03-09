"""
Voice Input — Microphone Recording

Records audio from the microphone using sounddevice
and saves as a WAV file for the Sarvam STT API.
"""

import io
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as write_wav


def record_audio(duration: int = 10, sample_rate: int = 16000) -> bytes:
    """
    Record audio from the default microphone.

    Args:
        duration: Recording duration in seconds (default 10).
        sample_rate: Sample rate in Hz (default 16000, good for speech).

    Returns:
        WAV file content as bytes.
    """
    print(f"🎙️ Recording for {duration} seconds...")

    # Record audio
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
    )
    sd.wait()  # Wait until recording is done

    print("✅ Recording complete!")

    # Convert to WAV bytes
    wav_buffer = io.BytesIO()
    write_wav(wav_buffer, sample_rate, audio_data)
    wav_bytes = wav_buffer.getvalue()

    return wav_bytes


def save_audio_to_file(audio_bytes: bytes, file_path: str = "temp_recording.wav"):
    """Save audio bytes to a WAV file."""
    with open(file_path, "wb") as f:
        f.write(audio_bytes)
    return file_path


# ── Quick self-test ─────────────────────────────────────
if __name__ == "__main__":
    audio = record_audio(duration=5)
    path = save_audio_to_file(audio)
    print(f"Audio saved to: {path}")
    print(f"Size: {len(audio)} bytes")
