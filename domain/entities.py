"""Entidades del dominio. Sin imports externos."""
from __future__ import annotations
from dataclasses import dataclass, field
 
 
@dataclass
class Chunk:
    source: str
    text: str
    score: float = 0.0
    chunk_id: str = ""
 
 
@dataclass
class Question:
    text: str
    conversation_id: str | None = None
 
 
@dataclass
class Answer:
    text: str
    sources: list[str] = field(default_factory=list)
    chunks: list[Chunk] = field(default_factory=list)
    metricas: dict = field(default_factory=dict)
    trazas: list[dict] | None = None