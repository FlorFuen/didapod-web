import streamlit as st
import edge_tts
import asyncio
import os
import speech_recognition as sr
from deep_translator import GoogleTranslator
from pydub import AudioSegment

# --- 1. LUXURY INTERFACE ---
st.set_page_config(page_title="DIDAPOD - DidactAI", page_icon="🎙️", layout="centered")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
    .main-title { color: white; font-size: 40px; font-weight: 800; margin-bottom: 0px; }
    .sub-title { color: #94a3b8; font-size: 18px; margin-bottom: 30px; }
    .stButton>button { 
        background-color: #7c3aed !important; color: white !important; 
        border-radius: 10px; padding: 15px 30px; font-weight: bold; width: 100%; border: none;
    }
    /* Caja de Preview Mejorada */
    .preview-section { 
        background: rgba(124, 58, 237, 0.2); 
        padding: 25px; 
        border-radius: 15px; 
        margin-top: 25px; 
        border: 2px solid #7c3aed;
        text-align: center;
    }
    label, .stMarkdown p, .stSuccess, .stInfo { color: white !important; }
    h3 { color: #a78bfa !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN SYSTEM ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.markdown("<h2 style='color:white;'>🔐 Restricted Access</h2>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u == "admin" and p == "didactai2026":
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("Invalid credentials")
    st.stop()

# --- 3. BRANDING ---
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
with col2:
    st.markdown('<p class="main-title">DIDAPOD PRO</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Powered by DidactAI-US</p>', unsafe_allow_html=True)

target_lang = st.selectbox("Select Target Language:", ["English", "Spanish", "French"])
up_file = st.file_uploader("Upload podcast (MP3/WAV)", type=["mp3", "wav"])

if up_file:
    st.audio(up_file)
    if st.button("🚀 START AI DUBBING"):
        try:
            with st.status("🤖 Processing in Safe Cascade Mode...", expanded=True) as status:
                st.write("⏳ Step 1: Fragmenting audio...")
                with open("t.mp3", "wb") as f: f.write(up_file.getbuffer())
                
                audio = AudioSegment.from_file("t.mp3")
                chunk_ms = 40000 
                chunks = [audio[i:i + chunk_ms] for i in range(0, len(audio), chunk_ms)]
                
                final_podcast = AudioSegment.empty()
                r = sr.Recognizer()
                codes = {"English": "en", "Spanish": "es", "French": "fr"}
                voice_m = {"English": "en-US-EmmaMultilingualNeural", "Spanish": "es-ES-ElviraNeural", "French": "fr-FR-DeniseNeural"}

                for i, chunk in enumerate(chunks):
                    st.write(f"🔄 Processing segment {i+1}/{len(chunks)}...")
                    chunk.export("c.wav", format="wav")
                    with sr.AudioFile("c.wav") as src:
                        try:
                            text_es = r.recognize_google(r.record(src), language="es-ES")
                            text_en = GoogleTranslator(source='auto', target=codes[target_lang]).translate(text_es)
                            temp_v = f"v_{i}.mp3"
                            communicate = edge_tts.Communicate(text_en, voice_m[target_lang])
                            asyncio.run(communicate.save(temp_v))
                            final_podcast += AudioSegment.from_file(temp_v)
                            os.remove(temp_v)
                        except: continue

                final_podcast.export("final_result.mp3", format="mp3")
                status.update(label="Dubbing Complete!", state="complete")
            
            st.balloons()
            
            # --- SECCIÓN DE PREVIEW VISIBLE ---
            st.markdown('<div class="preview-section">', unsafe_allow_html=True)
            st.markdown("### ▶️ Preview your Dubbed Podcast")
            st.markdown("Listen to the result before downloading:")
            st.audio("final_result.mp3") # El reproductor ahora es 100% visible
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            with open("final_result.mp3", "rb") as f:
                st.download_button("📥 DOWNLOAD FULL PODCAST", f, "didapod_result.mp3")
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Technical detail: {e}")

# --- 4. INSTRUCTIONS ---
st.markdown("<br><hr><center><small style='color:#94a3b8;'>© 2026 DidactAI-US | AI Enterprise Solutions</small></center>", unsafe_allow_html=True)









