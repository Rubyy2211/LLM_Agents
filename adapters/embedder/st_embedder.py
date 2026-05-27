"""Adapter embedder → sentence-transformers (sin Ollama)."""
from __future__ import annotations

from sentence_transformers import SentenceTransformer


class STEmbedder:
    """Implementa EmbedderPort estructuralmente usando sentence-transformers."""
 
    def __init__(self, model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> None:
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model)
 
    def embed(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()