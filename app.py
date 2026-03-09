"""
நலம் (Nalam) — India's Voice Health Assistant for ASHA Workers

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
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }

    /* Title styling */
    .main-title {
        text-align: center;
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5, #00d2ff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 3s ease infinite;
        margin-bottom: 0;
        padding-top: 1rem;
    }

    @keyframes gradient-shift {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    .subtitle {
        text-align: center;
        color: #a0aec0;
        font-size: 1.1rem;
        margin-top: -0.5rem;
        margin-bottom: 2rem;
        letter-spacing: 0.5px;
    }

    /* Triage cards */
    .triage-card {
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        animation: fadeIn 0.6s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .triage-red {
        background: linear-gradient(135deg, rgba(220,38,38,0.25), rgba(153,27,27,0.15));
        border-left: 5px solid #ef4444;
        box-shadow: 0 4px 20px rgba(239,68,68,0.2);
    }

    .triage-yellow {
        background: linear-gradient(135deg, rgba(234,179,8,0.25), rgba(161,98,7,0.15));
        border-left: 5px solid #eab308;
        box-shadow: 0 4px 20px rgba(234,179,8,0.2);
    }

    .triage-green {
        background: linear-gradient(135deg, rgba(34,197,94,0.25), rgba(21,128,61,0.15));
        border-left: 5px solid #22c55e;
        box-shadow: 0 4px 20px rgba(34,197,94,0.2);
    }

    .triage-level {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .triage-action {
        font-size: 1.15rem;
        color: #e2e8f0;
        line-height: 1.6;
    }

    .triage-explanation {
        font-size: 1rem;
        color: #cbd5e1;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.1);
        line-height: 1.6;
    }

    /* Info boxes */
    .info-box {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .info-label {
        color: #64748b;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.3rem;
    }

    .info-value {
        color: #f1f5f9;
        font-size: 1.05rem;
    }

    /* Record button */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }

    /* Pipeline step indicator */
    .pipeline-step {
        display: inline-block;
        background: rgba(59,130,246,0.15);
        color: #93c5fd;
        border-radius: 8px;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        font-size: 0.85rem;
        border: 1px solid rgba(59,130,246,0.2);
    }

    .pipeline-step.done {
        background: rgba(34,197,94,0.15);
        color: #86efac;
        border-color: rgba(34,197,94,0.2);
    }

    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
        margin: 2rem 0;
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Matched symptoms pills */
    .symptom-pill {
        display: inline-block;
        background: rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        margin: 0.15rem;
        font-size: 0.85rem;
        color: #e2e8f0;
        border: 1px solid rgba(255,255,255,0.1);
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
    '<div class="subtitle">India\'s Voice Health Assistant for ASHA Workers</div>',
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
    st.markdown("**Built for:** ASHA Workers across India")
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
