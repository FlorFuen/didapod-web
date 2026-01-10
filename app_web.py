import streamlit as st
import edge_tts
import asyncio
import os
import speech_recognition as sr
from deep_translator import GoogleTranslator
from pydub import AudioSegment

# --- 1. CONFIGURACIÓN Y ESTILO VISUAL ---
st.set_page_config(page_title="DIDAPOD - DidactAI", page_icon="🎙️", layout="centered")

st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }}
    
    /* DISEÑO DEL BOTÓN "CLICK HERE" (MODO BOTÓN MORADO) */
    .stExpander {{ 
        background-color: #7c3aed !important; 
        border: 2px solid white !important; 
        border-radius: 12px !important;
        margin-bottom: 15px;
    }}
    /* Esto obliga a que el texto "CLICK HERE" sea BLANCO y GRANDE */
    .stExpander summary span p {{ 
        color: white !important; 
        font-weight: 800 !important; 
        font-size: 20px !important;
        text-transform: uppercase;
    }}
    .stExpander summary {{ color: white !important; }}

    /* BOTONES DE ACCIÓN (START Y DOWNLOAD) */
    .stButton>button, .stDownloadButton>button {{ 
        background-color: #7c3aed !important; 
        color: white !important; 
        border-radius: 12px !important; 
        padding: 18px !important; 
        font-weight: 800 !important; 
        width: 100% !important; 
        border: 2px solid white !important;
    }}
    
    .main-title {{ color: white; font-size: 40px; font-weight: 800; margin: 0; }}
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

# --- 3. ENCABEZADO (CON LOGO LOCAL) ---
col_logo, col_txt = st.columns([1, 4])
with col_logo:
    # Verificamos si logo.png existe en tu carpeta de GitHub
    if os.path.exists("logo.png"):
        st.image("logo.png", width=110)
    else:
        st.markdown("<h1 style='margin:0;'>🎙️</h1>", unsafe_allow_html=True)

with col_txt:
    st.markdown('<p class="main-title">DIDAPOD PRO</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8; font-size:16px; margin:0;">Enterprise Dubbing by DidactAI-US</p>', unsafe_allow_html=True)

st.write("---")

# --- 4. LÓGICA DE PROCESAMIENTO ---
target_lang = st.selectbox("Select Target Language:", ["English", "Spanish", "French"])
up_file = st.file_uploader("Upload podcast", type=["mp3", "wav"])

if up_file:
    st.audio(up_file)
    if st.button("🚀 START AI DUBBING"):
        try:
            with st.status("🤖 Processing...", expanded=True) as status:
                with open("temp.mp3", "wb") as f: f.write(up_file.getbuffer())
                audio = AudioSegment.from_file("temp.mp3")
                # Fragmentos para evitar errores de saturación
                chunks = [audio[i:i + 40000] for i in range(0, len(audio), 40000)]
                
                final_audio = AudioSegment.empty()
                r = sr.Recognizer()
                codes = {"English": "en", "Spanish": "es", "French": "fr"}
                voice_m = {"English": "en-US-EmmaMultilingualNeural", "Spanish": "es-ES-ElviraNeural", "French": "fr-FR-DeniseNeural"}

                for i, chunk in enumerate(chunks):
                    st.write(f"🔄 Processing segment {i+1}/{len(chunks)}...")
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
            
            # --- ZONA DE RESULTADO ESTILIZADA ---
            st.markdown("<div style='background: rgba(255,255,255,0.05); padding: 25px; border-radius: 20px; border: 1px solid #7c3aed;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center; color:white;'>✅ PODCAST READY</h3>", unsafe_allow_html=True)
            
            # AQUÍ EL BOTÓN DE ESCUCHA CON EL ESTILO QUE PEDISTE
            with st.expander("▶️ CLICK HERE TO LISTEN BEFORE DOWNLOADING"):
                st.audio("result.mp3")
            
            st.write("") 
            
            # BOTÓN DE DESCARGA
            with open("result.mp3", "rb") as f:
                st.download_button("📥 DOWNLOAD FINAL FILE", f, "didapod_result.mp3")
            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e: st.error(f"Error: {e}")

st.markdown("<br><hr><center><small style='color:#94a3b8;'>© 2026 DidactAI-US</small></center>", unsafe_allow_html=True)



