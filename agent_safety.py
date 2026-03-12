"""
Agent 2 — Language Safety Checker

Ensures the explanation given to an ASHA worker is:
1. Free of medical jargon (ASHA has 23 days of training)
2. Not panic-inducing (causes fear without action)
3. Not vague (ASHA needs concrete steps)

Rewrites the explanation to Class 5 reading level if needed.
"""

import os
import json
import time
from datetime import datetime, timezone
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LANGUAGE_SAFETY_PROMPT = """You are checking if health instructions are appropriate for a semi-literate village health worker (ASHA) in India.
An ASHA worker has only 23 days of training — she needs simple, clear, action-oriented instructions.

Triage level: {triage_level}
Explanation: {explanation}

Check for these problems:
1. Medical jargon (words like 'tachycardia', 'dyspnea', 'contraindicated', 'hemorrhage', 'resuscitation', 'intubation')
2. Panic language (words that cause fear without giving action, e.g. 'fatal', 'death', 'brain damage')
3. Vague instructions ('be careful', 'watch the patient', 'monitor closely', 'seek attention' without specifics)

Reply with JSON only, no other text:
{{
  "needs_rewrite": true or false,
  "problems_found": ["list of specific issues found"],
  "rewritten_explanation": "simpler, clearer version if needed, or null if the original is fine"
}}

If rewriting, follow these rules:
- Use Class 5 (5th grade) reading level
- Use short sentences with common words only
- Give specific actions: "do THIS now", "go HERE now"
- If triage is RED, be urgent but calm: "Take the patient to hospital NOW"
- If triage is YELLOW, be clear: "Go to the health centre in 1-2 days"
- If triage is GREEN, be reassuring: "Give water and rest at home"
- Never use medical terms the ASHA worker would not know"""


def check_language_safety(explanation: str, triage_level: str,
                          target_language: str = "en-IN",
                          groq_client=None) -> dict:
    """
    Check if the explanation is appropriate for an ASHA worker.

    Args:
        explanation: The explanation text to check.
        triage_level: "RED", "YELLOW", or "GREEN".
        target_language: Target language code (for context only).
        groq_client: Optional pre-initialised Groq client.

    Returns:
        {
            'rewrite_needed': True/False,
            'problems': list of issues found,
            'final_explanation': cleaned explanation (or original if fine),
            'original_explanation': original text,
            'time_taken': seconds
        }
    """
    start_time = time.time()

    result = {
        "rewrite_needed": False,
        "problems": [],
        "final_explanation": explanation,
        "original_explanation": explanation,
        "time_taken": 0,
    }

    if not GROQ_API_KEY:
        result["problems"] = ["Groq API key not set — skipped language safety check"]
        result["time_taken"] = round(time.time() - start_time, 3)
        return result

    try:
        client = groq_client or Groq(api_key=GROQ_API_KEY)

        prompt = LANGUAGE_SAFETY_PROMPT.format(
            triage_level=triage_level,
            explanation=explanation,
        )

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=300,
        )

        response_text = chat_completion.choices[0].message.content.strip()

        # Parse JSON — handle potential markdown code fences
        cleaned = response_text
        if "```" in cleaned:
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)

        if parsed.get("needs_rewrite", False):
            result["rewrite_needed"] = True
            result["problems"] = parsed.get("problems_found", [])
            rewritten = parsed.get("rewritten_explanation")
            if rewritten and rewritten != "null":
                result["final_explanation"] = rewritten

            # Log the rewrite
            _log_safety_check(triage_level, explanation, result["final_explanation"], result["problems"])
        else:
            result["problems"] = parsed.get("problems_found", [])

    except json.JSONDecodeError as e:
        result["problems"] = [f"Failed to parse safety response: {e}"]
    except Exception as e:
        result["problems"] = [f"Language safety check failed: {e}"]

    result["time_taken"] = round(time.time() - start_time, 3)
    return result


def _log_safety_check(triage_level: str, original: str, rewritten: str, problems: list):
    """Log language safety rewrite to agent_logs.json."""
    log_entry = {
        "agent": "language_safety",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "triage_level": triage_level,
        "original_explanation": original,
        "rewritten_explanation": rewritten,
        "problems_found": problems,
    }

    log_path = os.path.join(os.path.dirname(__file__), "agent_logs.json")
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


# ── Quick self-test ─────────────────────────────────────
if __name__ == "__main__":
    print("Testing language safety checker...")
    test = check_language_safety(
        "The patient presents with tachycardia and acute respiratory distress. "
        "Contraindicated for home management. Immediate resuscitation may be needed.",
        "RED",
    )
    print(f"Rewrite needed: {test['rewrite_needed']}")
    print(f"Problems: {test['problems']}")
    print(f"Final: {test['final_explanation']}")
    print(f"Time taken: {test['time_taken']}s")
