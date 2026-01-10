import streamlit as st
import edge_tts
import asyncio
import os
import base64
import speech_recognition as sr
from deep_translator import GoogleTranslator
from pydub import AudioSegment

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="DIDAPOD - DidactAI", page_icon="🎙️", layout="centered")

# Función para convertir el logo a código base64 para que no falle la ruta
def get_base64_logo(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_data = get_base64_logo("logo.png")

# --- 2. ESTILO CSS PARA FORZAR COLORES ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a !important; }
    
    /* BOTÓN DE ESCUCHA (EXPANDER) FORZADO A MORADO Y BLANCO */
    .stExpander { 
        background-color: #7c3aed !important; 
        border: 2px solid white !important; 
        border-radius: 15px !important;
    }
    .stExpander summary, .stExpander summary * { 
        color: white !important; 
        font-weight: 900 !important; 
        font-size: 20px !important;
        text-transform: uppercase !important;
    }
    .stExpander svg { fill: white !important; }

    /* BOTONES DE ACCIÓN */
    .stButton>button, .stDownloadButton>button { 
        background-color: #7c3aed !important; 
        color: white !important; 
        border-radius: 12px !important; 
        padding: 20px !important; 
        font-weight: 800 !important; 
        width: 100% !important; 
        border: 1px solid white !important;
    }
    
    h1, h2, h3, label, p, span { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    with st.form("login"):
        u, p = st.text_input("User"), st.text_input("Pass", type="password")
        if st.form_submit_button("Login"):
            if u == "admin" and p == "didactai2026":
                st.session_state["auth"] = True
                st.rerun()
    st.stop()

# --- 4. ENCABEZADO CON HTML PURO (LOGO GARANTIZADO) ---
if logo_data:
    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{logo_data}" width="100" style="margin-right: 20px; border-radius: 10px;">
            <div>
                <h1 style="margin:0; font-size: 40px;">DIDAPOD PRO</h1>
                <p style="margin:0; color: #94a3b8 !important;">Powered by DidactAI-US</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<h1>🎙️ DIDAPOD PRO</h1>", unsafe_allow_html=True)

st.write("---")

# --- 5. PROCESAMIENTO ---
target_lang = st.selectbox("Select Target Language:", ["English", "Spanish", "French"])
up_file = st.file_uploader("Upload podcast", type=["mp3", "wav"])

if up_file:
    st.audio(up_file)
    if st.button("🚀 START AI DUBBING"):
        try:
            with st.status("🤖 Processing...", expanded=True) as status:
                with open("temp.mp3", "wb") as f: f.write(up_file.getbuffer())
                audio = AudioSegment.from_file("temp.mp3")
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
            
            # --- ZONA DE RESULTADO CON BOTONES PRO ---
            st.markdown("<div style='background: rgba(255,255,255,0.05); padding: 25px; border-radius: 20px; border: 1px solid #7c3aed;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center;'>✅ PODCAST READY</h3>", unsafe_allow_html=True)
            
            # Botón de Escucha Forzado
            with st.expander("▶️ CLICK HERE TO LISTEN BEFORE DOWNLOADING"):
                st.audio("result.mp3")
            
            st.write("")
            with open("result.mp3", "rb") as f:
                st.download_button("📥 DOWNLOAD FINAL FILE", f, "didapod_result.mp3")
            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e: st.error(f"Error: {e}")

st.markdown("<br><hr><center><small style='color:#94a3b8;'>© 2026 DidactAI-US</small></center>", unsafe_allow_html=True)
