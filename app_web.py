import streamlit as st
import edge_tts
import asyncio
import os
import speech_recognition as sr
from deep_translator import GoogleTranslator
from pydub import AudioSegment

# --- 1. CONFIGURACIÓN Y ESTILO AGRESIVO ---
st.set_page_config(page_title="DIDAPOD - DidactAI", page_icon="🎙️", layout="centered")

# URL DIRECTA DEL LOGO
URL_LOGO = "https://i.postimg.cc/1z07Pqqf/logo.png"

st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }}
    
    /* FORZAR TEXTO BLANCO EN TODO EL EXPANDER */
    .stExpander {{ 
        background-color: #7c3aed !important; 
        border: 2px solid white !important; 
        border-radius: 10px !important;
    }}
    .stExpander * {{ 
        color: white !important; 
        font-weight: bold !important; 
    }}
    
    /* ESTILO PARA EL LOGO */
    .header-box {{
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
    }}
    .logo-img {{
        width: 100px;
        margin-right: 20px;
        filter: drop-shadow(0px 0px 5px rgba(124, 58, 237, 0.5));
    }}
    .title-text {{
        color: white;
        font-size: 38px;
        font-weight: 800;
        margin: 0;
    }}
    
    label, .stMarkdown p {{ color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    with st.form("login"):
        u, p = st.text_input("User"), st.text_input("Pass", type="password")
        if st.form_submit_button("Login"):
            if u == "admin" and p == "didactai2026":
                st.session_state["auth"] = True
                st.rerun()
    st.stop()

# --- 3. ENCABEZADO (HTML PURO PARA EL LOGO) ---
st.markdown(f"""
    <div class="header-box">
        <img src="{URL_LOGO}" class="logo-img">
        <div>
            <p class="title-text">DIDAPOD PRO</p>
            <p style="color:#94a3b8; margin:0;">Enterprise Dubbing by DidactAI-US</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. PROCESAMIENTO (MODO CASCADA) ---
target_lang = st.selectbox("Select Target Language:", ["English", "Spanish", "French"])
up_file = st.file_uploader("Upload podcast", type=["mp3", "wav"])

if up_file:
    st.audio(up_file)
    if st.button("🚀 START AI DUBBING"):
        try:
            with st.status("🤖 Processing...", expanded=True) as status:
                with open("temp.mp3", "wb") as f: f.write(up_file.getbuffer())
                audio = AudioSegment.from_file("temp.mp3")
                # Fragmentos de 40 seg para evitar error de 5000 chars
                chunks = [audio[i:i + 40000] for i in range(0, len(audio), 40000)]
                
                final_audio = AudioSegment.empty()
                r = sr.Recognizer()
                codes = {"English": "en", "Spanish": "es", "French": "fr"}
                voice_m = {"English": "en-US-EmmaMultilingualNeural", "Spanish": "es-ES-ElviraNeural", "French": "fr-FR-DeniseNeural"}

                for i, chunk in enumerate(chunks):
                    st.write(f"🔄 Segment {i+1}/{len(chunks)}...")
                    chunk.export("c.wav", format="wav")
                    with sr.AudioFile("c.wav") as src:
                        try:
                            text = r.recognize_google(r.record(src), language="es-ES")
                            trans = GoogleTranslator(source='auto', target=codes[target_lang]).translate(text)
                            asyncio.run(edge_tts.Communicate(trans, voice_m[target_lang]).save(f"v{i}.mp3"))
                            final_audio += AudioSegment.from_file(f"v{i}.mp3")
                            os.remove(f"v{i}.mp3")
                        except: continue
                
                final_audio.export("result.mp3", format="mp3")
                status.update(label="Complete!", state="complete")
            
            st.balloons()
            
            # --- ZONA DE RESULTADO ---
            st.markdown("### ✅ Your Podcast is Ready")
            
            # Usamos un truco de estilo para que el texto sea blanco sí o sí
            with st.expander("▶️ CLICK HERE TO LISTEN BEFORE DOWNLOADING"):
                st.audio("result.mp3")
            
            st.markdown("<br>", unsafe_allow_html=True)
            with open("result.mp3", "rb") as f:
                st.download_button("📥 DOWNLOAD FINAL FILE", f, "didapod_result.mp3")

        except Exception as e: st.error(f"Error: {e}")

st.markdown("<br><hr><center><small style='color:#94a3b8;'>© 2026 DidactAI-US</small></center>", unsafe_allow_html=True)

