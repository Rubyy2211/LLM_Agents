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
CORPUS_DIR     = Path(os.getenv("CORPUS_DIR", "./base_conocimiento"))
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
    from adapters.retriever.hybrid_retriever import HybridRetriever
    from adapters.parser.document_loader import obtener_todos_los_chunks_del_disco
    from adapters.llm.ollama_llm import OllamaLLM
    from domain.chatbot_service import ChatbotService
 
    embedder = OllamaEmbedder(
        base_url=OLLAMA_URL,
        model=EMBED_MODEL,
        verify_ssl=VERIFY_SSL,
    )
    # 2. Inicializamos el recuperador Semántico base (Chroma)
    base_chroma_retriever = ChromaRetriever(
        embedder=embedder,
        collection_name=COLLECTION,
        chroma_path=CHROMA_PATH,
    )
    
    # 3. Leemos los textos planos del disco para alimentar al motor Léxico (BM25)
    chunks_del_disco = obtener_todos_los_chunks_del_disco(CORPUS_DIR)
    
    # 4. Construimos el verdadero Retriever Híbrido combinando ambos mundos
    hybrid_retriever = HybridRetriever(
        chroma_retriever=base_chroma_retriever,
        todos_los_chunks=chunks_del_disco,
        k=8,         # Número de chunks que queremos pasarle al LLM
        alpha=0.45   # Balance de peso (0.45 Semántica Chroma / 0.55 Léxica BM25)
    )
 
    if llm_backend == "poligpt":
        from adapters.llm.poligpt_llm import PoliGPTLLM
        model = llm_model or "poligpt"
        llm = PoliGPTLLM(base_url=POLIGPT_URL, api_key=POLIGPT_KEY, model=model)
    else:
        from adapters.llm.ollama_llm import OllamaLLM
        model = llm_model or LLM_MODEL
        llm = OllamaLLM(base_url=OLLAMA_URL, model=model, verify_ssl=VERIFY_SSL)
 
    service = ChatbotService(llm=llm, retriever=hybrid_retriever)
    return service, hybrid_retriever