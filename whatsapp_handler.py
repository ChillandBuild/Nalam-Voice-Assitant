import os
import requests
import uuid
import subprocess
from dotenv import load_dotenv
from twilio.rest import Client

from sarvam_stt import speech_to_text
from triage_engine import assess_symptoms
from explainer import generate_explanation
from sarvam_translate import from_english
from sarvam_tts import text_to_speech

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

def download_twilio_media(media_url: str, save_path: str):
    """Download media from Twilio, using HTTP auth."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        raise ValueError("Twilio credentials not set")
    
    response = requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed to download media: {response.status_code}")

def convert_audio_to_wav(input_path: str, output_path: str):
    """Convert audio format to standard WAV using FFmpeg."""
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"Error converting audio to WAV: {e}")
        # Fallback to copy if ffmpeg fails
        import shutil
        shutil.copy(input_path, output_path)

def send_twilio_message(to: str, body: str, media_url: str = None):
    """Send text or media message via Twilio REST API."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("Error: Twilio credentials not set")
        return

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    kwargs = {
        "from_": TWILIO_WHATSAPP_FROM,
        "to": to,
        "body": body
    }
    if media_url:
        kwargs["media_url"] = [media_url]

    try:
        client.messages.create(**kwargs)
        print(f"✅ Sent message to {to}")
    except Exception as e:
        print(f"❌ Failed to send Twilio message: {e}")

def process_whatsapp_message(sender: str, body: str, num_media: int, media_url: str, media_type: str, base_url: str):
    """Main background processor for incoming WhatsApp messages."""
    print(f"📬 Received message from {sender} - Media: {num_media}")
    
    if num_media == 0 or not media_url:
        # No audio provided
        send_twilio_message(
            sender, 
            "Hello from Nalam 🩺! Please send an audio voice note explaining the patient's symptoms."
        )
        return

    # Create temporary files
    tracking_id = str(uuid.uuid4())
    raw_audio_path = f"tmp_{tracking_id}.ogg"
    wav_audio_path = f"tmp_{tracking_id}.wav"
    output_audio_name = f"reply_{tracking_id}.wav"
    output_audio_path = os.path.join("static", output_audio_name)
    
    try:
        # 1. Download audio from Twilio media URL
        download_twilio_media(media_url, raw_audio_path)
        
        # 2. Convert raw audio to WAV (Sarvam API expectation)
        convert_audio_to_wav(raw_audio_path, wav_audio_path)
        
        # 3. Send to Sarvam STT -> get text + language
        stt_result = speech_to_text(wav_audio_path)
        if not stt_result["success"]:
            send_twilio_message(sender, f"Sorry, I couldn't understand the audio. ({stt_result.get('error')})")
            return
            
        transcript = stt_result["transcript"]
        lang_code = stt_result["language_code"] or "en-IN"
        
        # Send an immediate text acknowledgment so user knows we are processing
        send_twilio_message(sender, f"🩺 Understood: \"{transcript}\"\n\nProcessing clinical triage...")

        # 4. Run through triage engine -> get English assessment
        triage_result = assess_symptoms(transcript)
        triage_level_label = triage_result["label"]
        
        # 5. Get English explanation
        all_matched = triage_result["matched_red"] + triage_result["matched_yellow"] + triage_result["matched_green"]
        explain_result = generate_explanation(transcript, triage_result["triage_level"], all_matched)
        explanation_en = explain_result["explanation"]
        
        # 6. Translate explanation back to native language
        if lang_code != "en-IN":
            trans_result = from_english(explanation_en, lang_code)
            final_explanation = trans_result.get("translated_text", explanation_en) if trans_result["success"] else explanation_en
        else:
            final_explanation = explanation_en
            
        # Compile text reply
        text_reply = f"{triage_level_label}\n\n{final_explanation}"
        
        # 7. Generate Audio Reply via Sarvam TTS
        tts_result = text_to_speech(final_explanation, target_language_code=lang_code)
        
        if tts_result["success"]:
            # Save audio to static folder
            with open(output_audio_path, "wb") as f:
                f.write(tts_result["audio_bytes"])
            
            # 8. Send text reply AND audio reply via Twilio
            # Provide public URL pointing to our generated static audio
            public_audio_url = f"{base_url}/static/{output_audio_name}"
            
            # Send text + media response
            send_twilio_message(sender, text_reply, media_url=public_audio_url)
        else:
            # TTS failed, send text only
            send_twilio_message(sender, text_reply)
            send_twilio_message(sender, "⚠️ Voice response generation failed.")

    except Exception as e:
        print(f"❌ Error processing WhatsApp message: {e}")
        send_twilio_message(sender, "⚠️ An error occurred while processing your request.")
    finally:
        # Cleanup temporary audio files
        for temp_file in [raw_audio_path, wav_audio_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
