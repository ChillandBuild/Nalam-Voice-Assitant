"""
Clinical Triage Rules — All Age Groups

Comprehensive symptom-based triage rules covering:
- Adults, elderly, children, infants, and pregnant women
- Based on WHO emergency triage guidelines and general clinical practice

Each rule set maps symptom keywords → triage level.
The triage engine scans patient text for these keywords.
"""

# ──────────────────────────────────────────────────────────
# RED FLAG — Immediate referral to hospital
# ──────────────────────────────────────────────────────────
RED_FLAG_SYMPTOMS = [
    # ── Breathing & Respiratory Emergencies ──
    "difficulty breathing",
    "fast breathing",
    "chest indrawing",
    "stridor",
    "not breathing",
    "unable to breathe",
    "breathless",
    "gasping",
    "choking",
    "severe asthma",
    "wheezing severely",
    "turning blue",
    "blue lips",
    "cyanosis",

    # ── Cardiac & Chest Emergencies ──
    "chest pain",
    "severe chest pain",
    "crushing chest pain",
    "chest tightness",
    "heart attack",
    "irregular heartbeat",
    "palpitations with fainting",
    "sudden collapse",

    # ── Neurological Danger Signs ──
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
    "sudden confusion",
    "slurred speech",
    "facial drooping",
    "one sided weakness",
    "sudden severe headache",
    "paralysis",
    "loss of consciousness",
    "fainting",
    "stroke symptoms",
    "stiff neck",
    "neck stiffness",
    "bulging fontanelle",

    # ── Severe Bleeding & Trauma ──
    "heavy bleeding",
    "uncontrolled bleeding",
    "bleeding wound",
    "deep wound",
    "severe injury",
    "head injury",
    "spinal injury",
    "fracture",
    "broken bone",
    "severe burn",
    "burn",
    "poisoning",
    "snake bite",
    "animal bite",
    "drowning",

    # ── Gastrointestinal Emergencies ──
    "vomiting everything",
    "vomits everything",
    "continuous vomiting",
    "persistent vomiting",
    "vomiting blood",
    "blood in stool",
    "bloody diarrhoea",
    "bloody diarrhea",
    "black stool",
    "severe abdominal pain",
    "rigid abdomen",

    # ── Feeding / Intake Danger Signs ──
    "unable to drink",
    "unable to eat",
    "unable to swallow",
    "not able to drink",
    "cannot drink",
    "refusing to eat",
    "refusing to feed",
    "unable to breastfeed",
    "not able to breastfeed",
    "cannot breastfeed",
    "stopped breastfeeding",

    # ── Severe Dehydration ──
    "sunken eyes",
    "skin pinch goes back slowly",
    "skin pinch very slowly",
    "not passing urine",
    "no urine",
    "dry mouth",
    "very thirsty",

    # ── Severe Malnutrition ──
    "severe malnutrition",
    "visible wasting",
    "very thin",
    "severe wasting",
    "marasmus",
    "kwashiorkor",
    "oedema both feet",
    "swelling both feet",

    # ── Pregnancy & Obstetric Emergencies ──
    "heavy bleeding in pregnancy",
    "heavy vaginal bleeding",
    "fits in pregnancy",
    "convulsions in pregnancy",
    "high blood pressure",
    "blurred vision",
    "severe headache",
    "heavy discharge",

    # ── Newborn / Infant Danger Signs ──
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

    # ── Allergic / Anaphylaxis ──
    "severe allergic reaction",
    "anaphylaxis",
    "throat swelling",
    "swollen tongue",
    "difficulty swallowing",
    "hives all over body",

    # ── Severe Infections ──
    "high fever with rash",
    "measles with complications",
    "dengue warning signs",
    "severe malaria",

    # ── Mental Health Emergency ──
    "suicidal thoughts",
    "self harm",
    "suicide attempt",
]

# ──────────────────────────────────────────────────────────
# YELLOW FLAG — Refer to health facility within 48 hours
# ──────────────────────────────────────────────────────────
YELLOW_FLAG_SYMPTOMS = [
    # ── Fever ──
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

    # ── Respiratory ──
    "mild fast breathing",
    "slightly fast breathing",
    "cough more than 3 weeks",
    "chronic cough",
    "persistent cough",
    "cough with phlegm",
    "night sweats",
    "cough with blood",
    "wheezing",
    "shortness of breath on exertion",

    # ── Ear / Nose / Throat ──
    "ear pain",
    "ear discharge",
    "ear infection",
    "pus from ear",
    "hearing problem",
    "sinus pain",
    "persistent sore throat",
    "difficulty swallowing food",
    "hoarse voice for weeks",

    # ── Gastrointestinal ──
    "diarrhoea more than 3 days",
    "diarrhea more than 3 days",
    "loose motions for days",
    "watery stool for days",
    "persistent diarrhoea",
    "persistent diarrhea",
    "abdominal pain for days",
    "bloating and pain",
    "blood in urine",
    "painful urination",
    "burning urination",
    "frequent urination",

    # ── Appetite & Weight ──
    "not eating well",
    "not eating properly",
    "poor appetite",
    "eating less",
    "reduced appetite",
    "loss of appetite",
    "weight loss",
    "unexplained weight loss",

    # ── Pain & Musculoskeletal ──
    "headache for days",
    "persistent headache",
    "joint pain",
    "body pain for days",
    "back pain for days",
    "severe back pain",
    "swollen joints",
    "joint swelling",
    "chest pain on exertion",
    "numbness",
    "tingling",

    # ── Skin & Eyes ──
    "skin infection",
    "boils",
    "abscess",
    "pus from wound",
    "wound not healing",
    "eye discharge",
    "red eyes",
    "eye infection",
    "spreading rash",
    "skin ulcer",

    # ── Pregnancy Concerns ──
    "mild swelling feet",
    "swollen feet",
    "swollen legs",
    "reduced fetal movement",
    "baby not moving",
    "less baby movement",
    "leaking fluid",
    "spotting",
    "mild bleeding",

    # ── Anaemia & General ──
    "pale palms",
    "pale eyes",
    "pale nails",
    "very tired",
    "always tired",
    "weakness",
    "dizziness",
    "feeling faint",
    "chronic fatigue",

    # ── Blood Sugar & Chronic ──
    "excessive thirst",
    "excessive urination",
    "slow healing wounds",
    "blurry vision",
    "unexplained weight gain",

    # ── Swelling & Lumps ──
    "swollen glands",
    "lump in body",
    "lump in breast",
    "painless lump",
    "mouth sores",
    "white patches in mouth",
    "thrush",

    # ── Mental Health ──
    "feeling depressed",
    "anxiety for weeks",
    "not sleeping for days",
    "mood changes",
    "memory problems",
    "confusion",

    # ── Elderly Specific ──
    "frequent falls",
    "unsteady walking",
    "sudden memory loss",
    "incontinence",
]

# ──────────────────────────────────────────────────────────
# GREEN FLAG — Monitor at home with advice
# ──────────────────────────────────────────────────────────
GREEN_FLAG_SYMPTOMS = [
    # ── Mild Fever ──
    "mild fever",
    "low fever",
    "slight fever",
    "fever today",
    "fever since morning",
    "low grade fever",

    # ── Mild Respiratory ──
    "mild cold",
    "runny nose",
    "sneezing",
    "mild cough",
    "dry cough",
    "slight cough",
    "blocked nose",
    "stuffy nose",
    "sore throat",
    "nasal congestion",

    # ── Mild Skin ──
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
    "dry skin",
    "dandruff",

    # ── Mild Gastrointestinal ──
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
    "mild bloating",

    # ── Normal Pregnancy Symptoms ──
    "normal pregnancy",
    "morning sickness",
    "mild nausea in pregnancy",
    "back pain in pregnancy",
    "leg cramps",
    "heartburn",
    "fatigue in pregnancy",

    # ── General Mild / Common ──
    "headache",
    "body pain",
    "muscle pain",
    "tiredness",
    "not sleeping well",
    "mild fatigue",
    "mild body pain",
    "minor eye redness",
    "watery eyes",
    "mild allergies",

    # ── Childhood-specific mild ──
    "teething",
    "fussiness",
    "crying more than usual",
    "diaper rash",
    "mild cold in baby",

    # ── Elderly mild ──
    "mild joint stiffness",
    "seasonal allergies",
    "mild back pain",
]


# ──────────────────────────────────────────────────────────
# Combination rules (RED flags when symptoms appear together)
# ──────────────────────────────────────────────────────────
RED_COMBINATIONS = [
    # Pre-eclampsia: severe headache + swollen feet + blurred vision
    {
        "name": "Pre-eclampsia signs",
        "requires_all": ["severe headache", "swollen feet", "blurred vision"],
        "requires_any_count": 2,
    },
    # Severe dehydration
    {
        "name": "Severe dehydration",
        "requires_all": ["sunken eyes", "skin pinch", "not passing urine"],
        "requires_any_count": 2,
    },
    # Meningitis signs
    {
        "name": "Meningitis signs",
        "requires_all": ["fever", "stiff neck", "not responding"],
        "requires_any_count": 2,
    },
    # Stroke signs
    {
        "name": "Stroke signs",
        "requires_all": ["facial drooping", "slurred speech", "one sided weakness"],
        "requires_any_count": 2,
    },
    # Heart attack signs
    {
        "name": "Heart attack signs",
        "requires_all": ["chest pain", "sweating", "shortness of breath"],
        "requires_any_count": 2,
    },
    # Diabetic emergency
    {
        "name": "Diabetic emergency",
        "requires_all": ["excessive thirst", "confusion", "fast breathing"],
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
        "action": "Visit the nearest health facility or doctor within 48 hours.",
        "emoji": "🟡",
    },
    "GREEN": {
        "label": "🟢 GREEN — HOME CARE",
        "action": "Monitor at home. Stay hydrated, rest well, and eat nutritious food. Come back if symptoms get worse.",
        "emoji": "🟢",
    },
}
