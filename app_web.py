import streamlit as st
import os

# Configuración básica
st.set_page_config(page_title="RECOV DIDAPOD")

st.title("🎙️ MODO RECUPERACIÓN DIDAPOD")

st.write("### 1. Estado de Conexión")
st.success("Si puedes leer esto, GitHub y Streamlit ya están conectados de nuevo.")

st.write("### 2. Verificación de Archivos")
archivos = os.listdir('.')
st.write("Archivos encontrados en el servidor:", archivos)

if "logo.png" in archivos:
    st.success("✅ 'logo.png' detectado correctamente.")
else:
    st.error("⚠️ No encuentro 'logo.png'. Asegúrate de que el nombre sea exacto (todo en minúsculas).")

st.write("### 3. Prueba de Librerías")
try:
    import edge_tts
    import pydub
    st.success("✅ Librerías (edge-tts, pydub) cargadas.")
except Exception as e:
    st.error(f"❌ Error de librerías: {e}")
    st.info("Revisa que tu archivo 'requirements.txt' tenga los nombres bien escritos.")


