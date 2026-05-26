"""Adapter retriever → ChromaDB persistente."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import chromadb
from domain.entities import Chunk
 
 
class ChromaRetriever:
    """Implementa RetrieverPort estructuralmente."""
 
    def __init__(
        self,
        embedder,
        collection_name: str,
        chroma_path: Path,
    ) -> None:
        self.embedder = embedder
        self.collection_name = collection_name
        self.chroma_path = Path(chroma_path)
 
    def _client(self) -> chromadb.api.ClientAPI:
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=str(self.chroma_path))
 
    def build_index(self, chunks: list) -> int:
        """Reconstruye la colección desde cero con los chunks dados."""
        client = self._client()
        existing = [c.name for c in client.list_collections()]
        if self.collection_name in existing:
            client.delete_collection(self.collection_name)
        col = client.create_collection(
            self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        col.add(
            ids=[c.id for c in chunks],
            embeddings=[self.embedder.embed(c.text) for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[{"source": c.source, "chunk_index": c.chunk_index} for c in chunks],
        )
        return col.count()
 
    def retrieve(self, query: str, *, k: int = 5) -> list[Chunk]:
        client = self._client()
        col = client.get_collection(self.collection_name)
        q_emb = self.embedder.embed(query)
        res = col.query(query_embeddings=[q_emb], n_results=k)
        out: list[Chunk] = []
        for i in range(len(res["ids"][0])):
            distance = float(res["distances"][0][i])
            out.append(Chunk(
                source=res["metadatas"][0][i]["source"],
                text=res["documents"][0][i],
                score=round(1.0 - distance, 4),
                chunk_id=res["ids"][0][i],
            ))
        return out