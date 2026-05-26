"""Ports (interfaces) del dominio. Sin imports externos."""
from __future__ import annotations
from typing import Protocol
from .entities import Chunk


class LLMPort(Protocol):
    def generate(self, prompt: str, *, temperature: float = 0.2) -> tuple[str, dict]:
        """Devuelve (texto, metricas)."""
        ...


class EmbedderPort(Protocol):
    def embed(self, text: str) -> list[float]:
        ...


class RetrieverPort(Protocol):
    def retrieve(self, query: str, *, k: int = 5) -> list[Chunk]:
        ...

    def build_index(self, chunks: list) -> int:
        """Indexa chunks en el vector store. Devuelve nº de chunks indexados."""
        ...