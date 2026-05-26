"""Adapter retriever → FAISS (segunda implementación para banda 10)."""
from __future__ import annotations
import json
import pickle
from pathlib import Path
from domain.entities import Chunk
 
 
class FAISSRetriever:
    """Implementa RetrieverPort estructuralmente usando FAISS."""
 
    def __init__(self, embedder, index_path: Path) -> None:
        import faiss
        self.embedder = embedder
        self.index_path = Path(index_path)
        self._index = None
        self._chunks: list[Chunk] = []
 
    def build_index(self, chunks: list) -> int:
        import faiss
        import numpy as np
        embeddings = [self.embedder.embed(c.text) for c in chunks]
        dim = len(embeddings[0])
        index = faiss.IndexFlatIP(dim)  # Inner product ~ coseno si vectores normalizados
        matrix = np.array(embeddings, dtype="float32")
        faiss.normalize_L2(matrix)
        index.add(matrix)
        self._index = index
        self._chunks = list(chunks)
        # Persistir
        self.index_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(self.index_path / "index.faiss"))
        with open(self.index_path / "chunks.pkl", "wb") as f:
            pickle.dump(self._chunks, f)
        return index.ntotal
 
    def retrieve(self, query: str, *, k: int = 5) -> list[Chunk]:
        import faiss
        import numpy as np
        if self._index is None:
            self._load()
        q = np.array([self.embedder.embed(query)], dtype="float32")
        faiss.normalize_L2(q)
        scores, indices = self._index.search(q, k)
        out: list[Chunk] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            c = self._chunks[idx]
            out.append(Chunk(source=c.source, text=c.text, score=round(float(score), 4), chunk_id=c.chunk_id))
        return out
 
    def _load(self) -> None:
        import faiss
        self._index = faiss.read_index(str(self.index_path / "index.faiss"))
        with open(self.index_path / "chunks.pkl", "rb") as f:
            self._chunks = pickle.load(f)