from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import streamlit as st
from config import build_service
from domain.entities import Question

# --- Configuración de página ---
st.set_page_config(
    page_title="Asistente DNI Valencia",
    page_icon="🤝",
    layout="centered",
)

# --- Inicializar servicio (singleton por sesión) ---
@st.cache_resource
def get_service():
    service, _ = build_service(llm_backend="ollama")
    return service

# --- UI ---
st.title("🤝 Asistente DNI Valencia")
st.caption("Pregúntame sobre la asociación Damos Nuestra Ilusión — desayunos solidarios, RESIS, COLES y más.")

# Inicializar variables de estado
if "messages" not in st.session_state:
    st.session_state.messages = []
if "click_question" not in st.session_state:
    st.session_state.click_question = None

# Mostrar historial completo acumulado
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "fuentes" in msg:
            with st.expander("📂 Fuentes consultadas"):
                for f in msg["fuentes"]:
                    st.markdown(f"- `{f}`")
            if "metricas" in msg and msg["metricas"]:
                m = msg["metricas"]
                cols = st.columns(4)
                cols[0].metric("Modelo", m.get("modelo", "?"))
                cols[1].metric("Latencia", f"{m.get('latencia_s', '?')}s")
                cols[2].metric("Tokens/s", m.get("tokens_per_sec", "?"))
                cols[3].metric("Tokens out", m.get("output_tokens", "?"))

# Capturar entrada: Puede venir de la caja de chat o del trigger de los botones
pregunta_usuario = st.chat_input("¿En qué puedo ayudarte?")

# Si se pulsó un botón en el sidebar, recuperamos esa pregunta
if st.session_state.click_question:
    pregunta_usuario = st.session_state.click_question
    st.session_state.click_question = None  # Consumir el trigger inmediatamente

# --- Procesamiento de la Pregunta ---
if pregunta_usuario:
    # 1. Mostrar y guardar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": pregunta_usuario})
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)

    # 2. Obtener respuesta del Agente RAG
    with st.chat_message("assistant"):
        with st.spinner("Buscando en el corpus DNI..."):
            try:
                service = get_service()
                q = Question(text=pregunta_usuario)
                answer = service.answer(q)

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

                # Guardar respuesta en el historial de sesión
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer.text,
                    "fuentes": list(answer.sources),
                    "metricas": dict(answer.metricas),
                })

            except Exception as e:
                error_msg = f"Error al consultar el agente: {e}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                })

# --- Sidebar con información y ejemplos ---
with st.sidebar:
    st.header("ℹ️ Sobre este asistente")
    st.markdown("""
    Este asistente usa un sistema **RAG** (Retrieval-Augmented Generation)
    para responder preguntas sobre la asociación DNI Valencia.

    **Corpus**: 16 documentos oficiales de DNI  
    **Modelo**: qwen2.5:3b (Ollama local)  
    **Embeddings**: nomic-embed-text  
    **Vector store**: ChromaDB  
    **Arquitectura**: Hexagonal (banda 10)
    """)

    st.divider()
    st.markdown("**Preguntas de ejemplo:**")
    ejemplos = [
        "¿Qué es DNI?",
        "¿Cómo me apunto a los desayunos?",
        "¿En qué se diferencian RESIS y COLES?",
        "¿Cuántos voluntarios tiene DNI?",
        "¿Cuánto cuesta el alquiler en Valencia?",
    ]
    for ejemplo in ejemplos:
        if st.button(ejemplo, use_container_width=True):
            # En vez de añadir el mensaje nosotros, activamos el trigger y recargamos
            st.session_state.click_question = ejemplo
            st.rerun()

    st.divider()
    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.click_question = None
        st.rerun()