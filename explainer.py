"""
Clinical Explainer — Groq Llama 3.3 70B

Takes English symptoms + triage level and generates a simple
2-sentence explanation for the ASHA worker.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """You are a clinical assistant for ASHA workers in India.
You will be given patient symptoms and a triage decision (RED, YELLOW, or GREEN).

Write exactly 2 sentences in simple English:
1. Why this triage level was given
2. Exactly what the ASHA worker should do next

Rules:
- Keep it very simple. No medical jargon.
- Use short sentences.
- Be direct and actionable.
- Do not use bullet points or numbering in your response.
- Write as if speaking to a village health worker."""


def generate_explanation(
    symptoms_english: str,
    triage_level: str,
    matched_symptoms: list[str] | None = None,
) -> dict:
    """
    Generate a clinical explanation using Groq Llama 3.3 70B.

    Args:
        symptoms_english: Patient symptoms in English.
        triage_level: "RED", "YELLOW", or "GREEN".
        matched_symptoms: Optional list of matched keywords.

    Returns:
        {
            "explanation": "2-sentence explanation",
            "success": True
        }
        On error returns fallback explanation.
    """
    if not GROQ_API_KEY:
        return _fallback_explanation(triage_level)

    matched_str = ""
    if matched_symptoms:
        matched_str = f"\nKey symptoms identified: {', '.join(matched_symptoms)}"

    user_prompt = (
        f"Patient symptoms: {symptoms_english}\n"
        f"{matched_str}\n"
        f"Triage decision: {triage_level}\n\n"
        f"Give your 2-sentence explanation."
    )

    try:
        client = Groq(api_key=GROQ_API_KEY)

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=150,
        )

        explanation = chat_completion.choices[0].message.content.strip()
        return {
            "explanation": explanation,
            "success": True,
        }

    except Exception as e:
        print(f"Groq API error: {e}")
        return _fallback_explanation(triage_level)


def _fallback_explanation(triage_level: str) -> dict:
    """Return a safe fallback if Groq API fails."""
    fallbacks = {
        "RED": (
            "The patient has serious danger signs that need emergency care. "
            "Take the patient to the nearest hospital immediately, do not wait."
        ),
        "YELLOW": (
            "The patient has symptoms that need a doctor's attention soon. "
            "Take the patient to the Primary Health Centre within 1-2 days."
        ),
        "GREEN": (
            "The patient has mild symptoms that can be managed at home. "
            "Give home care, keep the patient comfortable, and watch for any worsening."
        ),
    }

    return {
        "explanation": fallbacks.get(triage_level, fallbacks["YELLOW"]),
        "success": True,
    }


# ── Quick self-test ─────────────────────────────────────
if __name__ == "__main__":
    result = generate_explanation(
        "Child has high fever for 3 days and is not eating well",
        "YELLOW",
        ["high fever", "not eating well"],
    )
    print(f"Explanation: {result['explanation']}")
    print(f"Success: {result['success']}")
