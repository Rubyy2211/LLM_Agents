"""Composition root — monta los adapters y devuelve el ChatbotService listo.
 
Este es el único sitio donde se toman decisiones de infraestructura:
qué LLM, qué embedder, qué retriever. Cambiar de Ollama a PoliGPT
es cambiar una línea aquí, sin tocar el dominio.
"""
from __future__ import annotations
import os
from pathlib import Path
 
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
 
# --- Lectura de settings ---
OLLAMA_URL     = os.getenv("OLLAMA_URL", "http://localhost:11434/api")
LLM_MODEL      = os.getenv("LLM_MODEL", "qwen2.5:3b")
EMBED_MODEL    = os.getenv("EMBED_MODEL", "nomic-embed-text")
VERIFY_SSL     = os.getenv("VERIFY_SSL", "true").lower() in {"1", "true", "yes"}
CHROMA_PATH    = Path(os.getenv("CHROMA_PATH", "./data/chroma"))
COLLECTION     = os.getenv("COLLECTION_NAME", "dni")
CORPUS_DIR     = Path(os.getenv("CORPUS_DIR", "./corpus"))
POLIGPT_URL    = os.getenv("POLIGPT_BASE_URL", "https://api.poligpt.upv.es/v1")
POLIGPT_KEY    = os.getenv("POLIGPT_API_KEY", "")
 
 
def build_service(llm_backend: str = "ollama", llm_model: str | None = None):
    """
    Construye y devuelve (chatbot_service, retriever) listos para usar.
 
    llm_backend: "ollama" | "poligpt"
    llm_model:   sobrescribe el modelo por defecto del backend elegido
    """
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
 
    from adapters.embedder.ollama_embedder import OllamaEmbedder
    from adapters.retriever.chroma_retriever import ChromaRetriever
    from adapters.llm.ollama_llm import OllamaLLM
    from domain.chatbot_service import ChatbotService
 
    embedder = OllamaEmbedder(
        base_url=OLLAMA_URL,
        model=EMBED_MODEL,
        verify_ssl=VERIFY_SSL,
    )
    retriever = ChromaRetriever(
        embedder=embedder,
        collection_name=COLLECTION,
        chroma_path=CHROMA_PATH,
    )
 
    if llm_backend == "poligpt":
        from adapters.llm.poligpt_llm import PoliGPTLLM
        model = llm_model or "poligpt"
        llm = PoliGPTLLM(base_url=POLIGPT_URL, api_key=POLIGPT_KEY, model=model)
    else:
        from adapters.llm.ollama_llm import OllamaLLM
        model = llm_model or LLM_MODEL
        llm = OllamaLLM(base_url=OLLAMA_URL, model=model, verify_ssl=VERIFY_SSL)
 
    service = ChatbotService(llm=llm, retriever=retriever)
    return service, retriever