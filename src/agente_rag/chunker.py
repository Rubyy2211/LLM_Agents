"""Troceo del corpus.

Usamos ``RecursiveCharacterTextSplitter`` con (500, 100) como en el Colab
y como recomienda el manual del desarrollador. Conservamos siempre el
nombre del archivo origen en los metadatos: es lo que nos permite citar
fuentes (banda 6) sin romper la trazabilidad.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class Chunk:
    id: str
    text: str
    source: str
    chunk_index: int


def load_corpus(corpus_dir: Path) -> list[dict]:
    """Carga todos los .txt de ``corpus_dir`` en memoria."""
    if not corpus_dir.exists():
        raise FileNotFoundError(f"Corpus no encontrado en {corpus_dir}")
    docs = []
    for path in sorted(corpus_dir.glob("*.txt")):
        docs.append({"name": path.name, "text": path.read_text(encoding="utf-8")})
    if not docs:
        raise RuntimeError(f"No hay .txt en {corpus_dir}")
    return docs


def split_documents(
    docs: list[dict],
    *,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[Chunk]:
    """Trocea cada documento conservando trazabilidad al archivo origen."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks: list[Chunk] = []
    for doc in docs:
        for i, piece in enumerate(splitter.split_text(doc["text"])):
            chunks.append(
                Chunk(
                    id=f"{doc['name']}__chunk_{i:04d}",
                    text=piece,
                    source=doc["name"],
                    chunk_index=i,
                )
            )
    return chunks
