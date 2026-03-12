"""
Agent 3 — RED Case Escalation

When triage = RED, this agent automatically:
1. Generates a structured patient handoff note for the PHC doctor (via Groq)
2. Sends an SMS alert to the configured PHC phone number (via Twilio)
3. Logs the escalation with full details

If Twilio credentials are not set → logs locally only, never crashes.
"""

import os
import json
import time
from datetime import datetime, timezone
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
PHC_PHONE_NUMBER = os.getenv("PHC_PHONE_NUMBER")

HANDOFF_PROMPT = """Create a brief structured patient handoff note for a Primary Health Centre doctor.
Symptoms reported: {symptoms_english}
Triage level: RED — immediate attention needed
Reported in language: {detected_language}

Format:
PATIENT HANDOFF — NALAM ALERT
Time: {timestamp}
Symptoms: [bullet points]
Urgency: IMMEDIATE
Reported via: Nalam Voice Triage System
Action needed: [what PHC doctor should prepare for]

Keep it under 100 words. Clinical and clear."""


def escalate_red_case(symptoms_english: str,
                      symptoms_original_language: str,
                      triage_decision: str,
                      explanation: str,
                      detected_language: str,
                      twilio_client=None,
                      phc_phone_number: str = None) -> dict:
    """
    Auto-escalate RED triage cases.

    Only runs if triage_decision == "RED". Returns immediately for
    YELLOW or GREEN cases.

    Args:
        symptoms_english: Patient symptoms translated to English.
        symptoms_original_language: Symptoms in the original language.
        triage_decision: "RED", "YELLOW", or "GREEN".
        explanation: The final explanation text.
        detected_language: Language code of the original input.
        twilio_client: Optional pre-initialised Twilio client.
        phc_phone_number: PHC phone number to alert. Falls back to env var.

    Returns:
        {
            'escalated': True/False,
            'sms_sent': True/False,
            'handoff_note': generated text or None,
            'timestamp': ISO timestamp,
            'error': None or error message,
            'time_taken': seconds
        }
    """
    start_time = time.time()
    timestamp = datetime.now(timezone.utc).isoformat()

    result = {
        "escalated": False,
        "sms_sent": False,
        "handoff_note": None,
        "timestamp": timestamp,
        "error": None,
        "time_taken": 0,
    }

    # ── Only escalate RED cases ─────────────────────────
    if triage_decision.upper() != "RED":
        result["error"] = f"No escalation needed — triage is {triage_decision}"
        result["time_taken"] = round(time.time() - start_time, 3)
        return result

    result["escalated"] = True

    # ── Step 1: Generate handoff note via Groq ──────────
    handoff_note = _generate_handoff_note(symptoms_english, detected_language, timestamp)
    result["handoff_note"] = handoff_note

    # ── Step 2: Send SMS via Twilio ─────────────────────
    target_number = phc_phone_number or PHC_PHONE_NUMBER
    sms_sent = _send_sms_alert(
        symptoms_english, detected_language, timestamp, target_number, twilio_client
    )
    result["sms_sent"] = sms_sent

    if not sms_sent:
        result["error"] = "SMS not sent — Twilio not configured or send failed (logged locally)"

    # ── Step 3: Log escalation ──────────────────────────
    _log_escalation(
        timestamp=timestamp,
        triage=triage_decision,
        symptoms=symptoms_english,
        language=detected_language,
        sms_sent=sms_sent,
        phc_number=target_number,
        handoff_note=handoff_note,
    )

    result["time_taken"] = round(time.time() - start_time, 3)
    return result


def _generate_handoff_note(symptoms_english: str, detected_language: str,
                           timestamp: str) -> str:
    """Generate a structured handoff note via Groq."""
    if not GROQ_API_KEY:
        # Fallback handoff note without Groq
        return (
            f"PATIENT HANDOFF — NALAM ALERT\n"
            f"Time: {timestamp}\n"
            f"Symptoms: {symptoms_english}\n"
            f"Urgency: IMMEDIATE\n"
            f"Reported via: Nalam Voice Triage System\n"
            f"Language: {detected_language}\n"
            f"Action needed: Prepare for immediate patient assessment."
        )

    try:
        client = Groq(api_key=GROQ_API_KEY)

        prompt = HANDOFF_PROMPT.format(
            symptoms_english=symptoms_english,
            detected_language=detected_language,
            timestamp=timestamp,
        )

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=200,
        )

        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        # Fallback if Groq fails
        return (
            f"PATIENT HANDOFF — NALAM ALERT\n"
            f"Time: {timestamp}\n"
            f"Symptoms: {symptoms_english}\n"
            f"Urgency: IMMEDIATE\n"
            f"Reported via: Nalam Voice Triage System\n"
            f"Language: {detected_language}\n"
            f"Action needed: Prepare for immediate patient assessment.\n"
            f"Note: Auto-generated (Groq unavailable: {e})"
        )


def _send_sms_alert(symptoms_english: str, detected_language: str,
                    timestamp: str, phc_number: str,
                    twilio_client=None) -> bool:
    """Send SMS alert to PHC. Returns True if sent, False otherwise."""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER]):
        return False

    if not phc_number or phc_number == "+91XXXXXXXXXX":
        return False

    try:
        if twilio_client is None:
            from twilio.rest import Client
            twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message_body = (
            f"🔴 NALAM RED ALERT\n"
            f"Time: {timestamp}\n"
            f"Symptoms: {symptoms_english}\n"
            f"Language: {detected_language}\n"
            f"Action: Prepare for immediate patient arrival\n"
            f"— Sent by Nalam Triage System"
        )

        twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_FROM_NUMBER,
            to=phc_number,
        )
        return True

    except Exception as e:
        print(f"Twilio SMS failed: {e}")
        return False


def _log_escalation(timestamp: str, triage: str, symptoms: str,
                    language: str, sms_sent: bool, phc_number: str,
                    handoff_note: str):
    """Log the escalation to escalation_log.json."""
    log_entry = {
        "timestamp": timestamp,
        "triage": triage,
        "symptoms": symptoms,
        "language": language,
        "sms_sent": sms_sent,
        "phc_number": phc_number or "not_configured",
        "handoff_note": handoff_note,
    }

    log_path = os.path.join(os.path.dirname(__file__), "escalation_log.json")
    try:
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                logs = json.load(f)
        else:
            logs = []
        logs.append(log_entry)
        with open(log_path, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception:
        pass  # Never crash the app over logging

    # Also log to centralized agent_logs.json
    agent_log = {
        "agent": "escalation",
        "timestamp": timestamp,
        "triage": triage,
        "symptoms": symptoms,
        "sms_sent": sms_sent,
        "escalated": True,
    }

    agent_log_path = os.path.join(os.path.dirname(__file__), "agent_logs.json")
    try:
        if os.path.exists(agent_log_path):
            with open(agent_log_path, "r") as f:
                logs = json.load(f)
        else:
            logs = []
        logs.append(agent_log)
        with open(agent_log_path, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception:
        pass


# ── Quick self-test ─────────────────────────────────────
if __name__ == "__main__":
    print("Testing escalation agent...")

    # Test RED case (SMS will fail gracefully without real Twilio creds)
    test_red = escalate_red_case(
        symptoms_english="Child has difficulty breathing and convulsions",
        symptoms_original_language="குழந்தைக்கு சுவாசிப்பதில் சிரமம் மற்றும் வலிப்பு",
        triage_decision="RED",
        explanation="Take the child to the hospital immediately.",
        detected_language="ta-IN",
    )
    print(f"Escalated: {test_red['escalated']}")
    print(f"SMS sent: {test_red['sms_sent']}")
    print(f"Handoff note:\n{test_red['handoff_note']}")
    print(f"Time taken: {test_red['time_taken']}s")

    print("\n--- Testing GREEN case (should skip) ---")
    test_green = escalate_red_case(
        symptoms_english="Mild cold and runny nose",
        symptoms_original_language="லேசான சளி",
        triage_decision="GREEN",
        explanation="Give rest and fluids.",
        detected_language="ta-IN",
    )
    print(f"Escalated: {test_green['escalated']}")
