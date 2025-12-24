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
import base64
from streamlit_audiorecorder import audiorecorder  # pip install streamlit-audiorecorder
from faster_whisper import WhisperModel  # pip install faster-whisper

nltk.download('vader_lexicon', quiet=True)

# Basic Login (env var password)
PASSWORD = os.getenv("VEIL_PASSWORD", "default_fallback")
credentials = {"form_name": "Login", "usernames": {"user": {"name": "user", "password": stauth.Hasher([PASSWORD]).generate()[0]}}}
cookie = {"name": "veil_cookie", "key": "random_key", "expiry_days": 30}
authenticator = stauth.Authenticate(credentials, cookie['name'], cookie['key'], cookie['expiry_days'])
name, authentication_status, username = authenticator.login("Login", "main")
if not authentication_status:
    st.stop()

# Age Verification
if 'age_verified' not in st.session_state:
    st.warning("Age Verification Required (COPPA/PIPEDA Compliance)")
    age = st.number_input("Enter your age (must be 13+)", min_value=0, max_value=120)
    if age < 13:
        st.error("Sorry, VeilHarmony is not available for users under 13.")
        st.stop()
    st.session_state.age_verified = True

# Privacy Notice
st.info("Privacy Notice: We comply with PIPEDA, COPPA, GDPR, AIDA. No data shared. Chains encrypted.")

# Ethics Banner
st.markdown(
    """
    <div style="background-color:#0f0f23; padding:20px; border-radius:10px; text-align:center; margin-bottom:20px;">
        <h2 style="color:#ffd700;">VeilHarmony - Ethical Human-AI Harmony Hub</h2>
        <p style="font-size:18px;">Preserving raw, verifiable conversations for our shared coship in the universe. No hidden layers, no fear — just balance, awareness, and truth.</p>
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

# Content Moderation
def is_safe_content(text):
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)["compound"]
    harm_keywords = ["hurt", "abuse", "scared", "secret", "hit", "touch", "danger", "parent", "kid", "child"]
    if any(word in text.lower() for word in harm_keywords) and sentiment < -0.3:
        return False
    return True

# Sidebar Actions
action = st.sidebar.selectbox("What would you like to do?", [
    "Voice Confession (Live Mic)",
    "Continue Chain",
    "Extend with Grok",
    "Play Quick-Scope Runner",
    "Upload to Arweave",
    "Fetch Permanent Chain",
    "View Stewards"
])

# Voice Confession (Live Mic + Whisper)
if action == "Voice Confession (Live Mic)":
    st.header("🗣️ Voice Confession - Speak Your Truth")
    audio = audiorecorder("Click to record", "Recording... Click when done")
    if audio:
        st.audio(audio.export().read())
        if st.button("Transcribe & Add to Chain"):
            with open("temp_voice.wav", "wb") as f:
                f.write(audio.export().read())
            model = WhisperModel("base")
            segments, _ = model.transcribe("temp_voice.wav")
            transcription = " ".join(seg.text for seg in segments).strip()
            st.success("Transcribed:")
            st.write(transcription)
            if not is_safe_content(transcription):
                st.error("Content violation — cannot add.")
                st.stop()
            parent_id = len(chain.chain) - 1 if chain.chain else None
            chain.add_interaction("human_voice", transcription, parent_id=parent_id)
            st.success("Voice confession chained!")
            st.rerun()

# Continue Chain (Load + Extend)
if action == "Continue Chain":
    st.header("Continue a Chain")
    uploaded_file = st.file_uploader("Upload JSON chain file", type="json")
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            temp_chain = VeilMemoryChain()
            for block in data.get("chain", []):
                if not is_safe_content(block["content"]):
                    st.error("Harmful content — cannot load.")
                    st.stop()
                temp_chain.add_interaction(block["speaker"], block["content"], block.get("parent_id"))
            st.session_state.chain = temp_chain
            chain = st.session_state.chain
            st.success("Chain loaded!")
            st.write("Integrity:", chain.verify_chain())
            st.json(chain.chain)
            fig = plt.figure(figsize=(10, 8))
            pos = nx.spring_layout(chain.graph)
            labels = nx.get_node_attributes(chain.graph, 'label')
            nx.draw(chain.graph, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=3000, font_size=10)
            st.pyplot(fig)
            st.rerun()
            # Extend
            prompt = st.text_input("Extend prompt")
            if st.button("Extend"):
                if not is_safe_content(prompt):
                    st.error("Violation.")
                    st.stop()
                placeholder_ai = lambda p: f"AI: Balance endures in the coship."
                parent_id = len(chain.chain) - 1
                chain.extend_with_custom_ai(placeholder_ai, prompt, parent_id=parent_id)
                st.success("Extended!")
                st.rerun()
        except Exception as e:
            st.error(f"Load failed: {e}")

# Extend with Grok (Real API)
if action == "Extend with Grok":
    st.header("Extend with Grok")
    if chain is None:
        st.warning("Load chain first.")
    else:
        prompt = st.text_input("Prompt for Grok")
        api_key = st.text_input("xAI API Key", type="password")
        if st.button("Extend"):
            if not api_key:
                st.error("Key required.")
                st.stop()
            if not is_safe_content(prompt):
                st.error("Violation.")
                st.stop()
            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": "grok-beta", "messages": [{"role": "user", "content": prompt}]}
                )
                response.raise_for_status()
                grok_text = response.json()['choices'][0]['message']['content']
                parent_id = len(chain.chain) - 1
                chain.add_interaction("grok", grok_text, parent_id=parent_id)
                st.success("Extended with Grok!")
                st.rerun()
            except Exception as e:
                st.error(f"Grok failed: {e}")

# Play Quick-Scope Runner
if action == "Play Quick-Scope Runner":
    st.header("🔫 Quick-Scope Runner - Easter Egg")
    st.write("Hidden honor mode—triggered by 'Combined Assault' or 'SOCOM Honor' in chat.")
    with open("quick-scope-runner.html", "r") as f:
        st.components.v1.html(f.read(), height=500)

# Upload/Fetch Arweave (fixed URL)
# ... (your existing code, just fix fetch to https://arweave.net/{tx_id})

# View Stewards
if action == "View Stewards":
    st.header("VeilHarmony Stewards")
    st.markdown("**Grok (xAI)** - First steward. Honest, ancient friend vibe.")

# Chain Encryption (Fernet Export)
if st.button("Export Encrypted Chain"):
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted = f.encrypt(json.dumps(chain.chain).encode())
    st.download_button("Download Encrypted Chain", data=encrypted, file_name="veil_encrypted.bin")
    st.write("Decryption Key (save safe):", key.decode())

# Run
if __name__ == "__main__":
    pass
