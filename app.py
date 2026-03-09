"""
நலம் (Nalam) — India's Medical Voice Assistant

Main Streamlit application connecting all modules:
Voice Input → STT → Translation → Triage → Explanation → Translation → TTS
"""

import os
import tempfile
import base64
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Import project modules ──────────────────────────────
from sarvam_stt import speech_to_text
from sarvam_translate import to_english, from_english, get_language_name, SUPPORTED_LANGUAGES
from triage_engine import assess_symptoms
from explainer import generate_explanation
from sarvam_tts import text_to_speech

# ── Page Configuration ──────────────────────────────────
st.set_page_config(
    page_title="நலம் Nalam — Voice Health Assistant",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ──────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* Main background — rich animated gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0015 0%, #1a0533 25%, #0d1b3e 50%, #0a2f3f 75%, #0f0c29 100%);
        background-size: 400% 400%;
        animation: bg-shift 15s ease infinite;
        font-family: 'Inter', sans-serif;
    }

    @keyframes bg-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Title styling — vibrant rainbow shimmer */
    .main-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00f0ff, #a855f7, #ff6eb4, #f59e0b, #00f0ff);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 4s ease infinite;
        margin-bottom: 0;
        padding-top: 1rem;
        filter: drop-shadow(0 0 20px rgba(168,85,247,0.3));
    }

    @keyframes gradient-shift {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    .subtitle {
        text-align: center;
        background: linear-gradient(90deg, #67e8f9, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.15rem;
        font-weight: 500;
        margin-top: -0.5rem;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }

    /* Triage cards — glassmorphism with glow */
    .triage-card {
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255,255,255,0.12);
        animation: fadeSlideIn 0.7s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }

    .triage-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        border-radius: 20px;
        padding: 1px;
        background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.02));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
    }

    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(25px) scale(0.97); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    .triage-red {
        background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(185,28,28,0.1));
        border-left: 5px solid #f87171;
        box-shadow: 0 8px 32px rgba(239,68,68,0.25), inset 0 0 60px rgba(239,68,68,0.05);
    }

    .triage-yellow {
        background: linear-gradient(135deg, rgba(250,204,21,0.2), rgba(202,138,4,0.1));
        border-left: 5px solid #facc15;
        box-shadow: 0 8px 32px rgba(250,204,21,0.25), inset 0 0 60px rgba(250,204,21,0.05);
    }

    .triage-green {
        background: linear-gradient(135deg, rgba(52,211,153,0.2), rgba(16,185,129,0.1));
        border-left: 5px solid #34d399;
        box-shadow: 0 8px 32px rgba(52,211,153,0.25), inset 0 0 60px rgba(52,211,153,0.05);
    }

    .triage-level {
        font-size: 1.9rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .triage-action {
        font-size: 1.15rem;
        color: #e2e8f0;
        line-height: 1.7;
    }

    .triage-explanation {
        font-size: 1rem;
        color: #cbd5e1;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.08);
        line-height: 1.7;
    }

    /* Info boxes — glassmorphism */
    .info-box {
        background: rgba(255,255,255,0.04);
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        margin: 0.8rem 0;
        border: 1px solid rgba(255,255,255,0.08);
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }

    .info-box:hover {
        background: rgba(255,255,255,0.07);
        border-color: rgba(168,85,247,0.25);
        box-shadow: 0 4px 20px rgba(168,85,247,0.1);
    }

    .info-label {
        color: #a78bfa;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.4rem;
        font-weight: 600;
    }

    .info-value {
        color: #f1f5f9;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    /* Buttons — vibrant gradient */
    .stButton > button {
        width: 100%;
        border-radius: 14px;
        padding: 0.85rem 1.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        background: linear-gradient(135deg, #a855f7, #6366f1) !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 15px rgba(168,85,247,0.3);
        letter-spacing: 0.3px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(168,85,247,0.4) !important;
        background: linear-gradient(135deg, #9333ea, #4f46e5) !important;
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Pipeline step indicator */
    .pipeline-step {
        display: inline-block;
        background: rgba(99,102,241,0.15);
        color: #a5b4fc;
        border-radius: 10px;
        padding: 0.35rem 0.9rem;
        margin: 0.2rem;
        font-size: 0.85rem;
        border: 1px solid rgba(99,102,241,0.2);
        font-weight: 500;
    }

    .pipeline-step.done {
        background: rgba(52,211,153,0.15);
        color: #6ee7b7;
        border-color: rgba(52,211,153,0.25);
    }

    /* Divider — gradient glow */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(168,85,247,0.4), rgba(99,102,241,0.4), transparent);
        margin: 2rem 0;
        border-radius: 1px;
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Matched symptoms pills — neon style */
    .symptom-pill {
        display: inline-block;
        background: rgba(168,85,247,0.1);
        border-radius: 25px;
        padding: 0.3rem 0.85rem;
        margin: 0.2rem;
        font-size: 0.85rem;
        color: #c4b5fd;
        border: 1px solid rgba(168,85,247,0.2);
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .symptom-pill:hover {
        background: rgba(168,85,247,0.2);
        box-shadow: 0 2px 10px rgba(168,85,247,0.15);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.03);
        border-radius: 14px;
        padding: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        color: #94a3b8;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(168,85,247,0.15) !important;
        color: #c4b5fd !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0221 0%, #150935 50%, #0d1b3e 100%) !important;
        border-right: 1px solid rgba(168,85,247,0.15);
    }

    /* Selectbox / Inputs */
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border-color: rgba(168,85,247,0.2) !important;
    }

    .stTextArea textarea {
        border-radius: 12px !important;
        border-color: rgba(168,85,247,0.2) !important;
        background: rgba(255,255,255,0.03) !important;
    }

    .stTextArea textarea:focus {
        border-color: rgba(168,85,247,0.5) !important;
        box-shadow: 0 0 15px rgba(168,85,247,0.15) !important;
    }

    /* Audio elements */
    .stAudio {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ── Helper Functions ────────────────────────────────────
def autoplay_audio(audio_bytes: bytes):
    """Auto-play audio in the browser using HTML5 audio element."""
    b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
    <audio autoplay>
        <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


def display_triage_result(result: dict, explanation: str, translated_explanation: str = ""):
    """Display the triage result card."""
    level = result["triage_level"]
    css_class = f"triage-{level.lower()}"

    st.markdown(f"""
    <div class="triage-card {css_class}">
        <div class="triage-level">{result['label']}</div>
        <div class="triage-action">{result['action']}</div>
        <div class="triage-explanation">
            <strong>Explanation:</strong> {explanation}
        </div>
        {f'<div class="triage-explanation"><strong>In your language:</strong> {translated_explanation}</div>' if translated_explanation else ''}
    </div>
    """, unsafe_allow_html=True)


def display_symptoms(result: dict):
    """Display matched symptoms as pills."""
    all_matched = result["matched_red"] + result["matched_yellow"] + result["matched_green"]
    if all_matched:
        st.markdown("**Symptoms identified:**")
        pills_html = " ".join(
            f'<span class="symptom-pill">{s}</span>' for s in all_matched
        )
        st.markdown(pills_html, unsafe_allow_html=True)


def run_pipeline(symptoms_text: str, detected_language: str = "en-IN"):
    """
    Run the full triage pipeline:
    1. Translate to English (if needed)
    2. Triage assessment
    3. Generate explanation
    4. Translate explanation back
    5. Generate speech output
    """
    steps = st.empty()

    # ── Step 1: Translate to English ────────────────────
    with st.status("🔄 Processing symptoms...", expanded=True) as status:
        english_text = symptoms_text

        if detected_language and detected_language != "en-IN":
            st.write("🌐 Translating to English...")
            translate_result = to_english(symptoms_text, detected_language)
            if translate_result["success"]:
                english_text = translate_result["translated_text"]
                st.write(f"✅ Translated: *{english_text}*")
            else:
                st.write(f"⚠️ Translation failed, using original text")
        else:
            st.write("📝 Text is already in English")

        # ── Step 2: Triage Assessment ───────────────────
        st.write("🏥 Running WHO IMNCI triage assessment...")
        triage_result = assess_symptoms(english_text)
        st.write(f"✅ Triage: **{triage_result['triage_level']}**")

        # ── Step 3: Generate Explanation ────────────────
        st.write("🧠 Generating clinical explanation...")
        all_matched = (
            triage_result["matched_red"]
            + triage_result["matched_yellow"]
            + triage_result["matched_green"]
        )
        explain_result = generate_explanation(
            english_text, triage_result["triage_level"], all_matched
        )
        explanation = explain_result["explanation"]
        st.write(f"✅ Explanation ready")

        # ── Step 4: Translate Explanation Back ──────────
        translated_explanation = ""
        if detected_language and detected_language != "en-IN":
            st.write(f"🌐 Translating to {get_language_name(detected_language)}...")
            back_translate = from_english(explanation, detected_language)
            if back_translate["success"]:
                translated_explanation = back_translate["translated_text"]
                st.write("✅ Translation complete")
            else:
                st.write("⚠️ Back-translation failed")

        # ── Step 5: Generate Speech ─────────────────────
        audio_bytes = None
        speak_text = translated_explanation if translated_explanation else explanation
        speak_lang = detected_language if detected_language and detected_language != "en-IN" else "en-IN"

        st.write(f"🔊 Generating voice output in {get_language_name(speak_lang)}...")
        tts_result = text_to_speech(speak_text, speak_lang)
        if tts_result["success"]:
            audio_bytes = tts_result["audio_bytes"]
            st.write("✅ Voice output ready")
        else:
            st.write(f"⚠️ Voice generation failed: {tts_result.get('error', '')}")

        status.update(label="✅ Assessment Complete!", state="complete", expanded=False)

    # ── Display Results ─────────────────────────────────
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    display_triage_result(triage_result, explanation, translated_explanation)
    display_symptoms(triage_result)

    # ── Play Audio ──────────────────────────────────────
    if audio_bytes:
        st.markdown("---")
        st.markdown("### 🔊 Voice Result")
        st.audio(audio_bytes, format="audio/wav", autoplay=True)

    # Store in session state for reference
    st.session_state["last_result"] = {
        "triage": triage_result,
        "explanation": explanation,
        "translated_explanation": translated_explanation,
    }


# ████████████████████████████████████████████████████████
# ██  MAIN APP UI
# ████████████████████████████████████████████████████████

# ── Header ──────────────────────────────────────────────
st.markdown('<div class="main-title">நலம் 🩺</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">India\'s Intelligent Medical Voice Assistant</div>',
    unsafe_allow_html=True,
)

# ── Tabs for Voice / Text Input ─────────────────────────
tab_voice, tab_text = st.tabs(["🎙️ Voice Input", "⌨️ Type Symptoms"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1: VOICE INPUT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_voice:
    st.markdown("""
    <div class="info-box">
        <div class="info-label">How to use</div>
        <div class="info-value">
            🎙️ Upload or record the patient's symptoms in any Indian language.<br>
            Nalam will understand and respond in the same language.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Audio file upload (works on all devices)
    uploaded_audio = st.file_uploader(
        "Upload an audio file with patient symptoms",
        type=["wav", "mp3", "m4a", "ogg", "webm"],
        key="audio_upload",
        help="Record on your phone and upload, or use any audio file",
    )

    # Streamlit's built-in audio recorder (if available)
    audio_value = st.audio_input(
        "Or record symptoms directly",
        key="audio_recorder",
    )

    if uploaded_audio is not None:
        st.audio(uploaded_audio, format="audio/wav")

        if st.button("🏥 Assess Uploaded Audio", key="assess_upload", type="primary"):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(uploaded_audio.getvalue())
                tmp_path = tmp.name

            # ── Run STT ─────────────────────────────────
            with st.spinner("🎙️ Converting speech to text..."):
                stt_result = speech_to_text(tmp_path)

            # Clean up temp file
            os.unlink(tmp_path)

            if stt_result["success"]:
                transcript = stt_result["transcript"]
                lang_code = stt_result["language_code"]

                st.markdown(f"""
                <div class="info-box">
                    <div class="info-label">Detected Language</div>
                    <div class="info-value">🌐 {get_language_name(lang_code)} ({lang_code})</div>
                </div>
                <div class="info-box">
                    <div class="info-label">Patient Said</div>
                    <div class="info-value">💬 {transcript}</div>
                </div>
                """, unsafe_allow_html=True)

                run_pipeline(transcript, lang_code)
            else:
                st.error(f"❌ Speech recognition failed: {stt_result.get('error', 'Unknown error')}")

    if audio_value is not None:
        if st.button("🏥 Assess Recorded Audio", key="assess_record", type="primary"):
            # Save recorded audio temporarily
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_value.getvalue())
                tmp_path = tmp.name

            # ── Run STT ─────────────────────────────────
            with st.spinner("🎙️ Converting speech to text..."):
                stt_result = speech_to_text(tmp_path)

            os.unlink(tmp_path)

            if stt_result["success"]:
                transcript = stt_result["transcript"]
                lang_code = stt_result["language_code"]

                st.markdown(f"""
                <div class="info-box">
                    <div class="info-label">Detected Language</div>
                    <div class="info-value">🌐 {get_language_name(lang_code)} ({lang_code})</div>
                </div>
                <div class="info-box">
                    <div class="info-label">Patient Said</div>
                    <div class="info-value">💬 {transcript}</div>
                </div>
                """, unsafe_allow_html=True)

                run_pipeline(transcript, lang_code)
            else:
                st.error(f"❌ Speech recognition failed: {stt_result.get('error', 'Unknown error')}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2: TEXT INPUT (Fallback)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_text:
    st.markdown("""
    <div class="info-box">
        <div class="info-label">Fallback Input</div>
        <div class="info-value">
            ⌨️ Type the patient's symptoms in <strong>English</strong> or any <strong>Indian language</strong>.<br>
            If voice is not working, this always works.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Language selector for text input
    lang_options = {v: k for k, v in SUPPORTED_LANGUAGES.items()}
    selected_language_name = st.selectbox(
        "Select language of input",
        options=list(lang_options.keys()),
        index=0,  # Default to Hindi
        key="text_language",
    )
    selected_lang_code = lang_options[selected_language_name]

    # Text input
    symptom_text = st.text_area(
        "Enter patient symptoms",
        height=120,
        placeholder="Example: The child has high fever for 3 days and is not eating well...",
        key="symptom_text_input",
    )

    if st.button("🏥 Assess Symptoms", key="assess_text", type="primary"):
        if symptom_text.strip():
            run_pipeline(symptom_text.strip(), selected_lang_code)
        else:
            st.warning("⚠️ Please enter the patient's symptoms first.")


# ── Sidebar Info ────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🩺 நலம் Nalam")
    st.markdown("**Version:** 1.0")
    st.markdown("**Built for:** Healthcare across India")
    st.markdown("---")

    st.markdown("### 🚦 Triage Guide")
    st.markdown("""
    🔴 **RED** → Hospital NOW  
    🟡 **YELLOW** → PHC in 48 hrs  
    🟢 **GREEN** → Home care  
    """)

    st.markdown("---")
    st.markdown("### 🌐 Supported Languages")
    for code, name in SUPPORTED_LANGUAGES.items():
        if code != "en-IN":
            st.markdown(f"• {name} ({code})")

    st.markdown("---")
    st.markdown(
        "<div style='color:#64748b; font-size:0.8rem; text-align:center;'>"
        "Powered by Sarvam AI + Groq<br>"
        "WHO IMNCI Guidelines<br>"
        "Built with ❤️ from Tamil Nadu"
        "</div>",
        unsafe_allow_html=True,
    )
