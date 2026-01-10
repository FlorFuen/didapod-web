import streamlit as st
import edge_tts
import asyncio
import os
import speech_recognition as sr
from deep_translator import GoogleTranslator
from pydub import AudioSegment

# --- 1. CONFIGURACIÓN E INTERFAZ LUXURY ---
st.set_page_config(page_title="DIDAPOD - DidactAI", page_icon="🎙️", layout="centered")

# URL de tu logo en PostImages
URL_LOGO = "https://i.postimg.cc/1z07Pqqf/logo.png"
# 3. ENCABEZADO CON LOGO
try:
    img = Image.open("logo.png")
    col_l, col_r = st.columns([1, 4])
    with col_l:
        st.image(img, width=120)
    with col_r:
        st.markdown('<p class="main-title">DIDAPOD</p>', unsafe_allow_html=True)
        st.write("<p style='color: #94a3b8;'>Powered by DidactAI</p>", unsafe_allow_html=True)
except:
    st.markdown('<p class="main-title">DIDAPOD by DidactAI</p>', unsafe_allow_html=True)

st.write("---")


st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }}
    
    /* DISEÑO DE LOS BOTONES GRANDES */
    .stButton>button, .stDownloadButton>button {{ 
        background-color: #7c3aed !important; 
        color: white !important; 
        border-radius: 12px !important; 
        padding: 20px !important; 
        font-weight: 800 !important; 
        width: 100% !important; 
        border: 2px solid #a78bfa !important;
        font-size: 18px !important;
        text-transform: uppercase;
        margin-bottom: 10px;
    }}
    
    /* CAJA DE RESULTADO */
    .result-card {{ 
        background: rgba(255, 255, 255, 0.05); 
        padding: 30px; 
        border-radius: 20px; 
        border: 1px solid #7c3aed; 
        text-align: center;
        margin-top: 20px;
    }}
    
    .main-title {{ color: white; font-size: 42px; font-weight: 800; margin: 0; }}
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

# --- 3. ENCABEZADO CON LOGO ---
col_logo, col_txt = st.columns([1, 4])
with col_logo:
    st.image(URL_LOGO, width=100)
with col_txt:
    st.markdown('<p class="main-title">DIDAPOD PRO</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8; font-size:18px;">Powered by DidactAI-US</p>', unsafe_allow_html=True)

# --- 4. PROCESAMIENTO ---
target_lang = st.selectbox("Select Target Language:", ["English", "Spanish", "French"])
up_file = st.file_uploader("Upload podcast", type=["mp3", "wav"])

if up_file:
    st.audio(up_file)
    if st.button("🚀 START AI DUBBING"):
        try:
            with st.status("🤖 Processing...", expanded=True) as status:
                with open("temp.mp3", "wb") as f: f.write(up_file.getbuffer())
                audio = AudioSegment.from_file("temp.mp3")
                # Cortes de 40 seg para evitar errores
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
            
            # --- ZONA DE RESULTADO FINAL ---
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='color:white;'>✅ YOUR PODCAST IS READY</h2>", unsafe_allow_html=True)
            
            # Botón de Escuchar (Usando un Expander estilizado como botón)
            with st.expander("▶️ CLICK HERE TO LISTEN BEFORE DOWNLOADING"):
                st.audio("result.mp3")
            
            st.write("") # Espacio
            
            # Botón de Descarga
            with open("result.mp3", "rb") as f:
                st.download_button("📥 DOWNLOAD FINAL FILE", f, "didapod_result.mp3")
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e: st.error(f"Error: {e}")

st.markdown("<br><hr><center><small style='color:#94a3b8;'>© 2026 DidactAI-US</small></center>", unsafe_allow_html=True)


