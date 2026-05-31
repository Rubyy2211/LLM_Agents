"""Frontend Streamlit del Agente RAG DNI.

Ejecución desde la raíz del repo:
    streamlit run adapters/web/streamlit_ui.py

Extras implementados:
- Frontend Streamlit funcional (+1.5)
- AWS Rekognition: sube foto y verifica contra corpus DNI (+1.5)
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from config import build_service
from domain.entities import Question

# --- Configuración de página ---
st.set_page_config(
    page_title="Asistente DNI Valencia",
    page_icon="🤝",
    layout="centered",
)

# --- Singletons ---
@st.cache_resource
def get_service():
    service, _ = build_service(llm_backend="ollama")
    return service

@st.cache_resource
def get_rekognition():
    try:
        from adapters.web.rekognition_adapter import RekognitionAdapter
        return RekognitionAdapter()
    except Exception:
        return None

# --- Título ---
st.title("🤝 Asistente DNI Valencia")
st.caption("Pregúntame sobre la asociación Damos Nuestra Ilusión — desayunos solidarios, RESIS, COLES y más.")

# --- Estado de sesión ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "click_question" not in st.session_state:
    st.session_state.click_question = None

# --- Pestañas ---
tab_chat, tab_foto = st.tabs(["💬 Chat", "📷 Verificar foto"])

# ==================== PESTAÑA CHAT ====================
with tab_chat:

    # Historial
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("fuentes"):
                with st.expander("📂 Fuentes consultadas"):
                    for f in msg["fuentes"]:
                        st.markdown(f"- `{f}`")
                if msg.get("metricas"):
                    m = msg["metricas"]
                    cols = st.columns(4)
                    cols[0].metric("Modelo", m.get("modelo", "?"))
                    cols[1].metric("Latencia", f"{m.get('latencia_s', '?')}s")
                    cols[2].metric("Tokens/s", m.get("tokens_per_sec", "?"))
                    cols[3].metric("Tokens out", m.get("output_tokens", "?"))

    # Capturar entrada: chat_input o botón del sidebar
    pregunta_usuario = st.chat_input("¿En qué puedo ayudarte?")
    if st.session_state.click_question:
        pregunta_usuario = st.session_state.click_question
        st.session_state.click_question = None

    # Procesar pregunta
    if pregunta_usuario:
        st.session_state.messages.append({"role": "user", "content": pregunta_usuario})
        with st.chat_message("user"):
            st.markdown(pregunta_usuario)

        with st.chat_message("assistant"):
            with st.spinner("Buscando en el corpus DNI..."):
                try:
                    service = get_service()
                    answer = service.answer(Question(text=pregunta_usuario))
                    st.markdown(answer.text)
                    with st.expander("📂 Fuentes consultadas"):
                        for f in answer.sources:
                            st.markdown(f"- `{f}`")
                    if answer.metricas:
                        m = answer.metricas
                        cols = st.columns(4)
                        cols[0].metric("Modelo", m.get("modelo", "?"))
                        cols[1].metric("Latencia", f"{m.get('latencia_s', '?')}s")
                        cols[2].metric("Tokens/s", m.get("tokens_per_sec", "?"))
                        cols[3].metric("Tokens out", m.get("output_tokens", "?"))
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer.text,
                        "fuentes": list(answer.sources),
                        "metricas": dict(answer.metricas),
                    })
                except Exception as e:
                    msg = f"Error al consultar el agente: {e}"
                    st.error(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg})

# ==================== PESTAÑA FOTO ====================
with tab_foto:
    st.subheader("📷 Verificar contenido de una foto contra el corpus DNI")
    st.markdown("""
    Sube una foto de un **cartel, horario impreso o post de Instagram** de DNI.
    AWS Rekognition extraerá el texto y el agente verificará si coincide con
    el corpus oficial.
    """)

    uploaded = st.file_uploader(
        "Sube una imagen (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded is not None:
        st.image(uploaded, caption="Imagen subida", use_container_width=True)

        if st.button("🔍 Extraer texto y verificar", type="primary"):
            with st.spinner("Extrayendo texto con AWS Rekognition..."):
                try:
                    rek = get_rekognition()
                    if rek is None:
                        st.error("Rekognition no disponible. Comprueba AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY en .env")
                    else:
                        image_bytes = uploaded.read()
                        texto_extraido = rek.extract_text(image_bytes)

                        if not texto_extraido:
                            st.warning("No se detectó texto en la imagen.")
                        else:
                            st.success("✅ Texto extraído por Rekognition:")
                            st.code(texto_extraido)

                            st.info("🔎 Verificando contra el corpus oficial de DNI...")
                            pregunta = (
                                f"He visto esta información en una imagen: '{texto_extraido}'. "
                                f"¿Es correcta según el corpus oficial de DNI? "
                                f"¿Coincide con los horarios, lugares y datos oficiales?"
                            )
                            service = get_service()
                            answer = service.answer(Question(text=pregunta))

                            st.subheader("📋 Verificación del agente:")
                            st.markdown(answer.text)
                            with st.expander("📂 Fuentes consultadas"):
                                for f in answer.sources:
                                    st.markdown(f"- `{f}`")

                except Exception as e:
                    st.error(f"Error con Rekognition: {e}")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("ℹ️ Sobre este asistente")
    st.markdown("""
    Sistema **RAG** sobre el corpus oficial de DNI Valencia.

    **Corpus**: 16 documentos DNI  
    **Modelo**: qwen2.5:3b (Ollama local)  
    **Embeddings**: nomic-embed-text  
    **Vector store**: ChromaDB  
    **Arquitectura**: Hexagonal (banda 10)  
    **Extra**: AWS Rekognition (verificación de fotos)
    """)

    st.divider()
    st.markdown("**Preguntas de ejemplo:**")
    for ejemplo in [
        "¿Qué es DNI?",
        "¿Cómo me apunto a los desayunos?",
        "¿En qué se diferencian RESIS y COLES?",
        "¿Cuántos voluntarios tiene DNI?",
        "¿Cuánto cuesta el alquiler en Valencia?",
    ]:
        if st.button(ejemplo, use_container_width=True):
            st.session_state.click_question = ejemplo
            st.rerun()

    st.divider()
    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.click_question = None
        st.rerun()