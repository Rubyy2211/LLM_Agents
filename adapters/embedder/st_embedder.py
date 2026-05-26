"""Adapter embedder → sentence-transformers (sin Ollama)."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    # Import for type checkers only; avoid runtime import issues if package isn't installed.
    from sentence_transformers import SentenceTransformer  # pragma: no cover
else:
    try:
        from sentence_transformers import SentenceTransformer
    except Exception:  # pragma: no cover
        SentenceTransformer = None  # type: ignore


class STEmbedder:
    """Embedder adapter using sentence-transformers if available."""

    def __init__(self, model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> None:
        if SentenceTransformer is None:  # pragma: no cover
            raise RuntimeError("sentence-transformers is not installed or failed to import")
        self.model = SentenceTransformer(model)

    def embed(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()