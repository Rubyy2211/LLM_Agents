"""Construye el índice vectorial usando la arquitectura hexagonal.
 
Ejecución desde la raíz del repo:
    python scripts/build_index_hex.py
 
Tiempo estimado: 60-120 s para los 16 documentos DNI con nomic-embed-text.
"""
from __future__ import annotations
import sys
import time
from pathlib import Path
 
# Aseguramos imports desde la raíz
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
 
from config import build_service, CORPUS_DIR
from agente_rag.chunker import load_corpus, split_documents
 
 
def main() -> int:
    print(f"[build_index] corpus_dir  = {CORPUS_DIR}")
    print(f"[build_index] Cargando documentos...")
 
    docs = load_corpus(CORPUS_DIR)
    print(f"[build_index] {len(docs)} documentos cargados.")
 
    chunks = split_documents(docs, chunk_size=500, chunk_overlap=100)
    print(f"[build_index] {len(chunks)} chunks generados.")
 
    _, retriever = build_service(llm_backend="ollama")
 
    print(f"[build_index] Generando embeddings e indexando (puede tardar 1-2 min)...")
    t0 = time.time()
    n = retriever.build_index(chunks)
    elapsed = time.time() - t0
    print(f"[build_index] {n} chunks indexados en {elapsed:.1f}s.")
    print("[build_index] Índice listo. Ya puedes usar consultar.py")
    return 0
 
 
if __name__ == "__main__":
    raise SystemExit(main())