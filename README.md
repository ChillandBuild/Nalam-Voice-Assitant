# நலம் Nalam 🩺

**India's Intelligent Medical Voice Assistant**

> *"Nalam" (நலம்) means "Wellbeing" in Tamil.*  
> Built by a Tamil Nadu student to bring healthcare to every Indian state.

---

## What It Does

A user speaks patient symptoms in **their own language** — Nalam speaks back the triage result **in the same language**. No reading required.

```
🎙️ User speaks symptoms (any Indian language)
   ↓ Sarvam Saaras v3 (Speech → Text)
   ↓ Sarvam Mayura (Auto-translate → English)
   ↓ WHO IMNCI Rule Engine (Triage assessment)
   ↓ Groq Llama 3.3 70B (Clinical explanation)
   ↓ Sarvam Mayura (English → Her language)
   ↓ Sarvam Bulbul v3 (Text → Speech)
🔊 Nalam speaks result back to the user
```

### Triage Levels

| Level | Meaning | Action |
|-------|---------|--------|
| 🔴 RED | Emergency | Take to hospital **immediately** |
| 🟡 YELLOW | Needs attention | Visit PHC within **48 hours** |
| 🟢 GREEN | Home care | Monitor at home with advice |

---

## Supported Languages

Hindi, Tamil, Telugu, Bengali, Marathi, Kannada, Malayalam, Gujarati, Punjabi, Odia — and English.

---

## Setup

### 1. Clone & Install

```bash
cd Nalam
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit the `.env` file:

```env
SARVAM_API_KEY=your_sarvam_key_here
GROQ_API_KEY=your_groq_key_here
```

### 3. Run

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Project Structure

```
Nalam/
├── app.py              → Streamlit UI (voice + text input)
├── voice_input.py      → Microphone recording → WAV
├── sarvam_stt.py       → Sarvam Saaras v3: Speech → Text
├── sarvam_translate.py → Sarvam Mayura: Translation
├── sarvam_tts.py       → Sarvam Bulbul v3: Text → Speech
├── triage_engine.py    → WHO IMNCI rule engine
├── explainer.py        → Groq Llama 3.3 70B explanations
├── rules/
│   └── imnci_rules.py  → WHO IMNCI symptom rules
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Voice I/O | Sarvam AI (Saaras v3 + Bulbul v3) |
| Translation | Sarvam AI (Mayura) |
| Clinical Logic | WHO IMNCI rules (Python) |
| Explanations | Groq (Llama 3.3 70B) |
| Web UI | Streamlit |
| Audio | sounddevice + scipy |

---

## Key Differentiator

- User **speaks** in their language
- Nalam **speaks back** in the same language
- **No reading required** — works for everyone
- Covers **all of India** — 10+ languages, auto-detected

---

*Built with ❤️ from Tamil Nadu for healthcare across India.*
