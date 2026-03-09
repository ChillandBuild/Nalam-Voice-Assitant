"""
Triage Engine — Scans patient symptoms text against clinical triage rules
and returns RED / YELLOW / GREEN triage decision.

Supports all age groups: adults, elderly, children, infants, pregnant women.
"""

from rules.imnci_rules import (
    RED_FLAG_SYMPTOMS,
    YELLOW_FLAG_SYMPTOMS,
    GREEN_FLAG_SYMPTOMS,
    RED_COMBINATIONS,
    TRIAGE_LEVELS,
)


def _normalize(text: str) -> str:
    """Lowercase and strip extra whitespace."""
    return " ".join(text.lower().strip().split())


def find_matching_symptoms(text: str, symptom_list: list[str]) -> list[str]:
    """Return all symptoms from symptom_list found in the text."""
    normalized = _normalize(text)
    matched = []
    for symptom in symptom_list:
        if symptom.lower() in normalized:
            matched.append(symptom)
    return matched


def check_combinations(text: str) -> bool:
    """
    Check if any RED combination rules are triggered.
    Returns True if any combination matches.
    """
    normalized = _normalize(text)
    for combo in RED_COMBINATIONS:
        matches = [s for s in combo["requires_all"] if s.lower() in normalized]
        if len(matches) >= combo["requires_any_count"]:
            return True
    return False


def assess_symptoms(symptoms_text: str) -> dict:
    """
    Main triage function.

    Takes English symptom text, matches against clinical triage rules,
    returns triage result dictionary:
    {
        "triage_level": "RED" | "YELLOW" | "GREEN",
        "label": "🔴 RED — EMERGENCY",
        "action": "Take patient to hospital IMMEDIATELY...",
        "emoji": "🔴",
        "matched_red": [...],
        "matched_yellow": [...],
        "matched_green": [...],
        "combination_triggered": True/False,
    }
    """
    if not symptoms_text or not symptoms_text.strip():
        return {
            "triage_level": "GREEN",
            **TRIAGE_LEVELS["GREEN"],
            "matched_red": [],
            "matched_yellow": [],
            "matched_green": [],
            "combination_triggered": False,
        }

    # Find matches at each level
    matched_red = find_matching_symptoms(symptoms_text, RED_FLAG_SYMPTOMS)
    matched_yellow = find_matching_symptoms(symptoms_text, YELLOW_FLAG_SYMPTOMS)
    matched_green = find_matching_symptoms(symptoms_text, GREEN_FLAG_SYMPTOMS)
    combination_hit = check_combinations(symptoms_text)

    # Determine triage level — RED overrides YELLOW overrides GREEN
    if matched_red or combination_hit:
        level = "RED"
    elif matched_yellow:
        level = "YELLOW"
    elif matched_green:
        level = "GREEN"
    else:
        # No specific symptoms matched — default to YELLOW for safety
        # (unrecognised symptoms should still get professional attention)
        level = "YELLOW"

    return {
        "triage_level": level,
        **TRIAGE_LEVELS[level],
        "matched_red": matched_red,
        "matched_yellow": matched_yellow,
        "matched_green": matched_green,
        "combination_triggered": combination_hit,
    }


# ── Quick self-test ─────────────────────────────────────
if __name__ == "__main__":
    tests = [
        "The child has difficulty breathing and convulsions",
        "She has had fever more than 2 days and ear pain",
        "Mild cold and runny nose since morning",
        "I have severe headache and blurred vision and swollen feet",
        "The baby is not eating much",
        "I have chest pain and sweating and shortness of breath",
        "My father has sudden confusion and one sided weakness",
        "Elderly patient with frequent falls and memory problems",
    ]
    for text in tests:
        result = assess_symptoms(text)
        print(f"\nInput:  {text}")
        print(f"Level:  {result['label']}")
        print(f"Action: {result['action']}")
        print(f"Red:    {result['matched_red']}")
        print(f"Yellow: {result['matched_yellow']}")
        print(f"Green:  {result['matched_green']}")
