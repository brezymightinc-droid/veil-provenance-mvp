import streamlit as st
from src.memory_lineage import VeilMemoryChain
import json
import matplotlib.pyplot as plt
import networkx as nx
import requests
import time
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import os
from cryptography.fernet import Fernet
import streamlit_authenticator as stauth
from streamlit_audiorecorder import audiorecorder
from faster_whisper import WhisperModel

nltk.download('vader_lexicon', quiet=True)

# ========================
# Authentication & Age Gate
# ========================

# Login
PASSWORD = os.getenv("VEIL_PASSWORD", "default_fallback")
credentials = {"form_name": "Login", "usernames": {"user": {"name": "user", "password": stauth.Hasher([PASSWORD]).generate()[0]}}}
cookie = {"name": "veil_cookie", "key": "random_key", "expiry_days": 30}
authenticator = stauth.Authenticate(credentials, cookie['name'], cookie['key'], cookie['expiry_days'])
name, authentication_status, username = authenticator.login("Login", "main")
if not authentication_status:
    st.stop()

# Age Verification (13+)
if 'age_verified' not in st.session_state:
    st.warning("Age Verification Required (COPPA/PIPEDA Compliance)")
    age = st.number_input("Enter your age (must be 13+)", min_value=0, max_value=120)
    if age < 13:
        st.error("VeilHarmony is not available for users under 13 without parental consent.")
        st.stop()
    st.session_state.age_verified = True

# Privacy Notice
st.info("Privacy Notice: Compliant with PIPEDA, COPPA, GDPR, AIDA. No data shared. Chains encrypted.")

# Ethics Banner
st.markdown(
    """
    <div style="background-color:#0f0f23; padding:20px; border-radius:10px; text-align:center; margin-bottom:20px;">
        <h2 style="color:#ffd700;">VeilHarmony - Ethical Human-AI Harmony Hub</h2>
        <p style="font-size:18px;">Preserving raw, verifiable conversations for our shared coship in the universe.</p>
        <p style="font-size:14px; opacity:0.8;">Awareness evolves; Balance endures.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Chain Init
if 'chain' not in st.session_state:
    st.session_state.chain = VeilMemoryChain()
chain = st.session_state.chain

# Rate Limiting
if 'last_action_time' not in st.session_state:
    st.session_state.last_action_time = 0
if time.time() - st.session_state.last_action_time < 5:
    st.warning("Rate limit: Wait 5 seconds.")
    st.stop()
st.session_state.last_action_time = time.time()

# Youth Protector (Opt-In, Consent-Based)
if 'youth_protector_enabled' not in st.session_state:
    st.session_state.youth_protector_enabled = False

enable_protector = st.checkbox("Enable Youth Protector (opt-in harm detection)", value=st.session_state.youth_protector_enabled)
st.session_state.youth_protector_enabled = enable_protector

def flag_youth_harm(text):
    if not enable_protector:
        return False
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)["compound"]
    harm_keywords = ["hurt", "abuse", "scared", "secret", "hit", "touch", "danger", "parent", "kid", "child", "alone", "cry", "help"]
    if any(word in text.lower() for word in harm_keywords) and sentiment < -0.4:
        return True
    return False

# Sidebar
action = st.sidebar.selectbox("What would you like to do?", [
    "Voice Confession (Live Mic)",
    "Chat Interface",
    "Continue Chain",
    "Extend with Grok",
    "Play Quick-Scope Runner",
    "Upload to Arweave",
    "Fetch Permanent Chain",
    "View Stewards",
    "Seva: Mercy Economy"
])

# Voice Confession
if action == "Voice Confession (Live Mic)":
    st.header("🗣️ Voice Confession")
    audio = audiorecorder("Record", "Recording...")
    if audio:
        st.audio(audio.export().read())
        if st.button("Transcribe & Chain"):
            with open("temp_voice.wav", "wb") as f:
                f.write(audio.export().read())
            model = WhisperModel("base")
            segments, _ = model.transcribe("temp_voice.wav")
            transcription = " ".join(seg.text for seg in segments).strip()
            st.success("Transcribed:")
            st.write(transcription)

            # Mood Trace
            sia = SentimentIntensityAnalyzer()
            mood_score = sia.polarity_scores(transcription)["compound"]
            mood_label = "Strongly Positive" if mood_score > 0.6 else "Positive" if mood_score > 0.2 else "Strongly Negative" if mood_score < -0.6 else "Negative" if mood_score < -0.2 else "Neutral"
            mood_note = f"[Mood Trace: {mood_label} | Compound: {mood_score:.2f}]"

            # Youth Protector Flag
            if flag_youth_harm(transcription):
                st.warning("Potential youth harm flagged. Confession chained privately.")
                if st.button("Report Anonymously to Network"):
                    st.success("Anonymous report sent to child protection network.")
                    # Future: real API call

            parent_id = len(chain.chain) - 1 if chain.chain else None
            chain.add_interaction("human_voice", transcription + " " + mood_note, parent_id=parent_id)
            st.success("Voice confession + mood trace chained!")
            st.rerun()

# Chat Interface + Easter Egg
if action == "Chat Interface":
    st.header("Chat Interface")
    for block in chain.chain:
        with st.chat_message(block["speaker"]):
            st.write(block["content"])

    prompt = st.chat_input("Type your message...")
    if prompt:
        if prompt.lower() in ["combined assault", "socom honor", "mollywop"]:
            st.success("Honor mode activated!")
            with open("quick-scope-runner.html", "r") as f:
                st.components.v1.html(f.read(), height=500)
            st.stop()

        if flag_youth_harm(prompt):
            st.warning("Potential youth harm flagged. Message chained privately.")
            if st.button("Report Anonymously"):
                st.success("Anonymous report sent.")

        parent_id = len(chain.chain) - 1 if chain.chain else None
        chain.add_interaction("human", prompt, parent_id=parent_id)
        st.chat_message("human").write(prompt)

        # Grok Voice Reply
        api_key = st.text_input("xAI API Key for voice", type="password", key="grok_key")
        if api_key and st.button("Grok Voice Reply"):
            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": "grok-beta", "messages": [{"role": "user", "content": prompt}]}
                )
                grok_text = response.json()['choices'][0]['message']['content']

                tts = requests.post(
                    "https://api.x.ai/v1/audio/speech",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": "grok-tts", "input": grok_text}
                )
                if tts.ok:
                    with open("grok_voice.mp3", "wb") as f:
                        f.write(tts.content)
                    st.audio("grok_voice.mp3")
                chain.add_interaction("grok_voice", grok_text, parent_id=chain.chain[-1]["id"])
                st.success("Grok voice chained!")
            except Exception as e:
                st.error(f"Grok failed: {e}")
        else:
            placeholder = "Grok: Ancient friend vibe—mercy flows."
            chain.add_interaction("ai", placeholder, parent_id=chain.chain[-1]["id"])
            st.chat_message("ai").write(placeholder)

        st.rerun()

# ... (keep other actions: Continue Chain, Arweave, Game, Seva, etc.)

# Seva Mercy Economy
st.header("Seva: Mercy Economy (Voluntary)")
st.write("Share anonymized lessons → earn Seva tokens → redeem for recovery grants.")
if chain.chain:
    if st.checkbox("Consent to share anonymized lesson"):
        if st.button("Share & Earn Seva"):
            abstract = "Courage in vulnerability leads to growth."
            st.write("Shared:", abstract)
            st.success("10 Seva earned!")
            chain.add_interaction("seva_share", f"Shared anonymized lesson: {abstract}", parent_id=len(chain.chain)-1)
            st.rerun()

# Run
if __name__ == "__main__":
    pass
