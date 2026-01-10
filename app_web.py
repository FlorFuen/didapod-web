import streamlit as st
import edge_tts
import asyncio
import os
from deep_translator import GoogleTranslator
from pydub import AudioSegment
import speech_recognition as sr

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="DIDAPOD - DidactAI", page_icon="🎙️", layout="centered")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
    .main-title { color: white; font-size: 40px; font-weight: 800; margin-bottom: 0px; }
    .sub-title { color: #94a3b8; font-size: 18px; margin-bottom: 30px; }
    .stButton>button { 
        background-color: #7c3aed !important; color: white !important; 
        border-radius: 10px; padding: 15px 30px; font-weight: bold; width: 100%; 
    }
    label, .stMarkdown p { color: white !important; } /* Corrección de contraste */
    </style>
    """, unsafe_allow_html=True)

# --- 2. SISTEMA DE PRIVACIDAD ---
def login():
    if "auth" not in st.session_state: st.session_state["auth"] = False
    if st.session_state["auth"]: return True

    st.markdown("<h2 style='color:white;'>🔐 Acceso DidactAI</h2>", unsafe_allow_html=True)
    with st.form("login"):
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            if user == "admin" and pw == "didactai2026": # CAMBIA TU CLAVE AQUÍ
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("Credenciales incorrectas")
    return False

if login():
    # --- 3. CABECERA (JERARQUÍA VISUAL) ---
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=80)
    with col2:
        st.markdown('<p class="main-title">DIDAPOD</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Powered by DidactAI-US</p>', unsafe_allow_html=True)

    # --- 4. INDICADOR DE PASOS ---
    st.markdown("### 🗺️ Flujo de Trabajo")
    c1, c2, c3, c4 = st.columns(4)
    c1.info("1. Subir")
    c2.info("2. Idioma")
    c3.info("3. Doblar")
    c4.info("4. List")

    # --- 5. CONFIGURACIÓN DEL PROYECTO ---
    st.markdown("---")
    idioma = st.selectbox("Idioma de destino:", ["Inglés (EE.UU.)", "Español", "Francés"])
    
    uploaded_file = st.file_uploader("Formatos soportados: MP3, WAV", type=["mp3", "wav"])

    if uploaded_file:
        st.success("✅ Audio listo")
        st.audio(uploaded_file) # Previsualización (Confianza)

        if st.button("🚀 INICIAR DOBLAJE IA"):
            try:
                with st.status("🤖 Procesando audio...", expanded=True) as status:
                    # Guardar temporal
                    with open("temp.mp3", "wb") as f: f.write(uploaded_file.read())
                    
                    st.write("🎙️ Transcribiendo y Traduciendo...")
                    # Lógica simplificada de traducción (aquí iría tu bloque de speech_recognition)
                    texto_original = "Texto detectado en el podcast..." 
                    texto_traducido = GoogleTranslator(source='auto', target='en').translate(texto_original)
                    
                    st.write("🔊 Generando voz de IA (Emma)...")
                    communicate = edge_tts.Communicate(texto_traducido, "en-US-EmmaMultilingualNeural")
                    asyncio.run(communicate.save("output.mp3"))
                    
                    status.update(label="¡Doblaje Completado!", state="complete")
                
                st.balloons()
                with open("output.mp3", "rb") as f:
                    st.download_button("📥 Descargar Podcast Doblado", f, "podcast_didactai.mp3")
            
            except Exception as e:
                st.error(f"Hubo un detalle técnico: {e}")

    # --- 6. PIE DE PÁGINA ---
    st.markdown("<br><hr><center><small style='color:#94a3b8;'>© 2026 DidactAI-US | Soluciones de IA</small></center>", unsafe_allow_html=True)
