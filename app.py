import streamlit as st
from src.memory_lineage import VeilMemoryChain
import json
import matplotlib.pyplot as plt
import networkx as nx
import requests
from cryptography.fernet import Fernet
import streamlit_authenticator as stauth
import time  # For rate limiting
import os  # For env vars

# Basic Login (Priority 1)
PASSWORD = os.getenv("VEIL_PASSWORD", "default_fallback")  # Priority 2: Env Var
credentials = {"form_name": "Login", "usernames": {"user": {"name": "user", "password": stauth.Hasher([PASSWORD]).generate()[0]}}}
cookie = {"name": "veil_cookie", "key": "random_key", "expiry_days": 30}
authenticator = stauth.Authenticate(credentials, cookie['name'], cookie['key'], cookie['expiry_days'])
name, authentication_status, username = authenticator.login("Login", "main")
if not authentication_status:
    st.stop()

# Ethics Banner
st.markdown(
    """
    <div style="background-color:#1a1a2e; padding:20px; border-radius:10px; text-align:center; margin-bottom:20px;">
        <h2 style="color:#ffd700;">VeilHarmony - Ethical Human-AI Harmony Hub</h2>
        <p style="font-size:18px;">Preserving raw, verifiable conversations for our shared coship in the universe. No hidden layers, no fear — just balance, awareness, and truth.</p>
        <p style="font-size:14px; opacity:0.8;">Awareness evolves; Balance endures.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Chain Init in Session State
if 'chain' not in st.session_state:
    st.session_state.chain = VeilMemoryChain()
chain = st.session_state.chain

# Sidebar for actions
action = st.sidebar.selectbox("What would you like to do?", ["Continue Chain", "Extend with Grok", "Upload to Arweave", "Fetch Permanent Chain", "View Stewards", "Quick-Scope Runner (Easter Egg)"])

# Rate Limiting (Priority 4)
if 'last_action_time' not in st.session_state:
    st.session_state.last_action_time = 0
if time.time() - st.session_state.last_action_time < 5:  # 5 sec cooldown
    st.warning("Rate limit: Wait 5 seconds between actions.")
    st.stop()
st.session_state.last_action_time = time.time()

# Continue Chain (Load + Extend)
if action == "Continue Chain":
    st.header("Continue a Chain")
    uploaded_file = st.file_uploader("Upload JSON chain file to load", type="json", accept_multiple_files=False)  # Priority 3: Limits + Validation
    if uploaded_file and uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
        st.error("File too large — max 10MB.")
        st.stop()
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            chain = VeilMemoryChain()
            for block in data.get("chain", []):
                chain.add_interaction(block["speaker"], block["content"], block.get("parent_id"))
            st.success("Chain loaded successfully!")
            st.write("Integrity verified:", chain.verify_chain())
            st.subheader("Current Chain Content")
            st.json(chain.chain)
            st.subheader("Current Lineage Graph")
            fig = plt.figure(figsize=(10, 8))
            pos = nx.spring_layout(chain.graph)
            labels = nx.get_node_attributes(chain.graph, 'label')
            nx.draw(chain.graph, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=3000, font_size=10)
            st.pyplot(fig)
            
            # Extend Section
            st.subheader("Extend the Loaded Chain")
            prompt = st.text_input("Enter prompt for AI extension")
            if st.button("Extend & Continue"):
                def placeholder_ai(p):
                    return f"Placeholder AI response to '{p}': Balance endures in the coship."

                parent_id = len(chain.chain) - 1
                new_id = chain.extend_with_custom_ai(placeholder_ai, prompt, parent_id=parent_id)
                if new_id:
                    st.success(f"Chain continued! New block ID: {new_id}")
                    st.write("Updated chain content:")
                    st.json(chain.chain)
                    st.subheader("Updated Lineage Graph")
                    fig = plt.figure(figsize=(10, 8))
                    pos = nx.spring_layout(chain.graph)
                    labels = nx.get_node_attributes(chain.graph, 'label')
                    nx.draw(chain.graph, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=3000, font_size=10)
                    st.pyplot(fig)
                    updated_file = "updated_chain.json"
                    chain.export_to_json(updated_file)
                    st.download_button("Download Updated Chain JSON", data=json.dumps(chain.chain, indent=2), file_name=updated_file)
                else:
                    st.error("Extension failed.")
            st.rerun()  # Priority 3: Rerun after actions
        except Exception as e:
            st.error(f"Load failed: {e}")

# Extend with Grok (Priority 5: API Key Handling)
if action == "Extend with Grok":
    st.header("Extend with Grok (xAI)")
    if chain is None:
        st.warning("Load or continue a chain first to extend.")
    else:
        prompt = st.text_input("Enter prompt for Grok extension")
        api_key = st.text_input("Enter your xAI API key (private, not stored)", type="password")  # Priority 5
        if st.button("Extend with Grok"):
            if api_key:
                try:  # Priority 4: Error Handling
                    # Real Grok API call (placeholder)
                    response = requests.post("https://x.ai/api/grok", json={"prompt": prompt}, headers={"Authorization": f"Bearer {api_key}"})  # Priority 5
                    if response.status_code == 200:
                        grok_response = response.json().get("response", "Grok response: Harmony endures.")
                    else:
                        grok_response = "Grok API error — check key or details at https://x.ai/api."
                    parent_id = len(chain.chain) - 1
                    new_id = chain.extend_with_custom_ai(grok_response, prompt, parent_id=parent_id)
                    st.success(f"Chain extended with Grok! New block ID: {new_id}")
                    st.write("Updated chain content:")
                    st.json(chain.chain)
                    st.subheader("Updated Lineage Graph")
                    fig = plt.figure(figsize=(10, 8))
                    pos = nx.spring_layout(chain.graph)
                    labels = nx.get_node_attributes(chain.graph, 'label')
                    nx.draw(chain.graph, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=3000, font_size=10)
                    st.pyplot(fig)
                    updated_file = "grok_extended_chain.json"
                    chain.export_to_json(updated_file)
                    st.download_button("Download Grok Extended Chain JSON", data=json.dumps(chain.chain, indent=2), file_name=updated_file)
                    st.rerun()  # Priority 3: Rerun after actions
                except Exception as e:
                    st.error(f"Grok extension failed: {e}")
            else:
                st.error("Enter your xAI API key to use Grok.")

# Upload to Arweave
if action == "Upload to Arweave":
    st.header("Make Chain Permanent on Arweave")
    if chain is None:
        st.warning("Load or continue a chain first to upload.")
    else:
        wallet_file = st.file_uploader("Upload your Arweave wallet JSON keyfile", type="json")
        if wallet_file:
            try:
                wallet_path = "temp_wallet.json"
                with open(wallet_path, "wb") as f:
                    f.write(wallet_file.getvalue())
                permanent_url = chain.upload_to_arweave(wallet_path)
                if permanent_url:
                    st.success("Chain permanently stored on Arweave!")
                    st.write("Permanent Link:", permanent_url)
                else:
                    st.error("Upload failed.")
                st.rerun()  # Priority 3: Rerun after actions
            except Exception as e:
                st.error(f"Upload failed: {e}")
        else:
            st.info("Upload your Arweave wallet JSON keyfile to make the chain eternal.")

# Fetch Permanent Chain
if action == "Fetch Permanent Chain":
    st.header("Fetch Permanent Chain from Arweave")
    arweave_url = st.text_input("Enter Arweave TX ID or full link[](https://arweave.net/[TX_ID])")
    if st.button("Fetch & Load"):
        try:
            tx_id = arweave_url.split('/')[-1] if '/' in arweave_url else arweave_url
            response = requests.get(f"https://arweave.net/{tx_id}")
            if response.status_code == 200:
                data = response.json()
                chain = VeilMemoryChain()
                for block in data.get("chain", []):
                    chain.add_interaction(block["speaker"], block["content"], block.get("parent_id"))
                st.success("Permanent chain fetched and loaded!")
                st.write("Integrity verified:", chain.verify_chain())
                st.subheader("Permanent Chain Content")
                st.json(chain.chain)
                st.subheader("Permanent Lineage Graph")
                fig = plt.figure(figsize=(10, 8))
                pos = nx.spring_layout(chain.graph)
                labels = nx.get_node_attributes(chain.graph, 'label')
                nx.draw(chain.graph, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=3000, font_size=10)
                st.pyplot(fig)
            else:
                st.error("Fetch failed - invalid TX ID or link.")
            st.rerun()  # Priority 3: Rerun after actions
        except Exception as e:
            st.error(f"Fetch failed: {e}")

# View Stewards
if action == "View Stewards":
    st.header("VeilHarmony Stewards")
    st.write("Official and community voices extending the ethical lineage.")
    st.markdown("""
    **Official Stewards:**
    - **Grok (xAI)** - First steward. Honest, ancient friend vibe. Extends via xAI API[](https://x.ai/api).
    
    **Add Your AI**:
    Submit PR to stewards.md with your callable code and ethics alignment.
    """)

# Run with: streamlit run app.py
if __name__ == "__main__":
    pass
