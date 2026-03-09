"""
WHO IMNCI (Integrated Management of Neonatal and Childhood Illness) Rules
Encoded as Python data structures for the Nalam triage engine.

Each rule set maps symptom keywords → triage level.
The triage engine scans patient text for these keywords.
"""

# ──────────────────────────────────────────────────────────
# RED FLAG — Immediate referral to hospital
# ──────────────────────────────────────────────────────────
RED_FLAG_SYMPTOMS = [
    # Breathing danger signs
    "difficulty breathing",
    "fast breathing",
    "chest indrawing",
    "stridor",
    "not breathing",
    "unable to breathe",
    "breathless",
    "gasping",

    # Feeding danger signs
    "unable to drink",
    "unable to breastfeed",
    "not able to drink",
    "not able to breastfeed",
    "cannot drink",
    "cannot breastfeed",
    "refusing to feed",
    "stopped breastfeeding",

    # Vomiting danger signs
    "vomiting everything",
    "vomits everything",
    "continuous vomiting",
    "persistent vomiting",

    # Neurological danger signs
    "convulsions",
    "fits",
    "seizures",
    "seizure",
    "lethargic",
    "unconscious",
    "not responding",
    "unresponsive",
    "drowsy",
    "limp",
    "not waking up",
    "bulging fontanelle",

    # Severe malnutrition
    "severe malnutrition",
    "visible wasting",
    "very thin",
    "severe wasting",
    "marasmus",
    "kwashiorkor",
    "oedema both feet",
    "swelling both feet",

    # Pregnancy danger signs
    "severe headache",
    "blurred vision",
    "heavy bleeding",
    "heavy discharge",
    "fits in pregnancy",
    "convulsions in pregnancy",
    "high blood pressure",
    "severe abdominal pain",

    # Newborn danger signs
    "cold to touch",
    "yellow skin",
    "jaundice",
    "yellow eyes",
    "umbilical redness",
    "umbilical pus",
    "baby not breathing",
    "blue baby",
    "very small baby",
    "premature",

    # Dehydration danger signs
    "sunken eyes",
    "skin pinch goes back slowly",
    "skin pinch very slowly",
    "not passing urine",
    "no urine",
    "dry mouth",
    "very thirsty",
    "blood in stool",
    "bloody diarrhoea",

    # Other critical signs
    "stiff neck",
    "severe chest pain",
    "poisoning",
    "snake bite",
    "animal bite",
    "burn",
    "severe burn",
    "drowning",
    "severe injury",
    "deep wound",
    "bleeding wound",
    "high fever with rash",
    "measles with complications",
]

# ──────────────────────────────────────────────────────────
# YELLOW FLAG — Refer to PHC within 48 hours
# ──────────────────────────────────────────────────────────
YELLOW_FLAG_SYMPTOMS = [
    # Fever
    "fever more than 2 days",
    "fever for 3 days",
    "fever for 4 days",
    "fever for 5 days",
    "high fever",
    "persistent fever",
    "recurring fever",
    "fever with chills",
    "fever not going down",
    "fever and shivering",

    # Ear problems
    "ear pain",
    "ear discharge",
    "ear infection",
    "pus from ear",
    "hearing problem",

    # Prolonged diarrhoea
    "diarrhoea more than 3 days",
    "diarrhea more than 3 days",
    "loose motions for days",
    "watery stool for days",
    "persistent diarrhoea",
    "persistent diarrhea",

    # Feeding problems
    "not eating well",
    "not eating properly",
    "poor appetite",
    "eating less",
    "reduced appetite",
    "loss of appetite",
    "weight loss",

    # Mild breathing
    "mild fast breathing",
    "slightly fast breathing",
    "cough more than 3 weeks",
    "chronic cough",
    "persistent cough",
    "cough with phlegm",
    "night sweats",
    "cough with blood",

    # Pregnancy concerns
    "mild swelling feet",
    "swollen feet",
    "swollen legs",
    "reduced fetal movement",
    "baby not moving",
    "less baby movement",
    "leaking fluid",
    "spotting",
    "mild bleeding",

    # Anaemia signs
    "pale palms",
    "pale eyes",
    "pale nails",
    "very tired",
    "always tired",
    "weakness",
    "dizziness",
    "feeling faint",

    # Skin and eyes
    "skin infection",
    "boils",
    "abscess",
    "pus from wound",
    "wound not healing",
    "eye discharge",
    "red eyes",
    "eye infection",

    # Urinary
    "painful urination",
    "burning urination",
    "frequent urination",
    "blood in urine",

    # Other
    "headache for days",
    "persistent headache",
    "joint pain",
    "body pain for days",
    "swollen glands",
    "mouth sores",
    "white patches in mouth",
    "thrush",
]

# ──────────────────────────────────────────────────────────
# GREEN FLAG — Monitor at home with advice
# ──────────────────────────────────────────────────────────
GREEN_FLAG_SYMPTOMS = [
    # Mild fever
    "mild fever",
    "low fever",
    "slight fever",
    "fever today",
    "fever since morning",
    "low grade fever",

    # Mild respiratory
    "mild cold",
    "runny nose",
    "sneezing",
    "mild cough",
    "dry cough",
    "slight cough",
    "blocked nose",
    "stuffy nose",
    "sore throat",

    # Mild skin
    "minor skin rash",
    "mild rash",
    "small rash",
    "itching",
    "minor itching",
    "heat rash",
    "prickly heat",
    "insect bite",
    "minor cut",
    "minor wound",
    "small wound",

    # Mild GI
    "mild diarrhoea",
    "mild diarrhea",
    "loose motions",
    "loose motion",
    "stomach ache",
    "stomach pain",
    "mild stomach pain",
    "gas",
    "indigestion",
    "acidity",
    "constipation",
    "vomiting once",
    "nausea",

    # Normal pregnancy
    "normal pregnancy",
    "morning sickness",
    "mild nausea in pregnancy",
    "back pain in pregnancy",
    "leg cramps",
    "heartburn",
    "fatigue in pregnancy",

    # General mild
    "headache",
    "body pain",
    "muscle pain",
    "tiredness",
    "not sleeping well",
    "teething",
    "fussiness",
    "crying more than usual",
    "diaper rash",
    "minor eye redness",
]


# ──────────────────────────────────────────────────────────
# Combination rules (RED flags when symptoms appear together)
# ──────────────────────────────────────────────────────────
RED_COMBINATIONS = [
    # Pregnancy: severe headache + swollen feet + blurred vision → pre-eclampsia
    {
        "name": "Pre-eclampsia signs",
        "requires_all": ["severe headache", "swollen feet", "blurred vision"],
        "requires_any_count": 2,  # at least 2 of 3 present
    },
    # Dehydration: sunken eyes + skin pinch + not passing urine
    {
        "name": "Severe dehydration",
        "requires_all": ["sunken eyes", "skin pinch", "not passing urine"],
        "requires_any_count": 2,
    },
    # Meningitis signs: fever + stiff neck + not responding
    {
        "name": "Meningitis signs",
        "requires_all": ["fever", "stiff neck", "not responding"],
        "requires_any_count": 2,
    },
]


# ──────────────────────────────────────────────────────────
# Triage level descriptions
# ──────────────────────────────────────────────────────────
TRIAGE_LEVELS = {
    "RED": {
        "label": "🔴 RED — EMERGENCY",
        "action": "Take patient to hospital IMMEDIATELY. Do not wait.",
        "emoji": "🔴",
    },
    "YELLOW": {
        "label": "🟡 YELLOW — NEEDS ATTENTION",
        "action": "Take patient to Primary Health Centre (PHC) within 48 hours.",
        "emoji": "🟡",
    },
    "GREEN": {
        "label": "🟢 GREEN — HOME CARE",
        "action": "Monitor at home. Give ORS if diarrhoea. Keep child warm. Breastfeed frequently. Come back if symptoms get worse.",
        "emoji": "🟢",
    },
}
