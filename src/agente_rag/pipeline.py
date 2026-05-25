"""Orquestador del flujo RAG: percibir → decidir → actuar.

Este es el "loop del agente" del Colab, encapsulado para que ``consultar.py``
y ``api.py`` lo compartan sin duplicar código.

La salida cumple el contrato del enunciado §9 con todos los campos opcionales
poblados (banda 7). El campo ``trazas`` queda en ``None`` porque no es
obligatorio y este repo-ejemplo no lo necesita.
"""

from __future__ import annotations

from .generator import generate
from .prompts import build_prompt
from .retriever import retrieve


def answer(question: str, *, k: int = 5, conversation_id: str | None = None) -> dict:
    """Responde a ``question`` siguiendo el contrato del enunciado §9."""
    retrieved = retrieve(question, k=k)
    prompt = build_prompt(question, retrieved)
    gen = generate(prompt)

    return {
        "respuesta": gen.text.strip(),
        "fuentes": _unique_preserving_order(c.source for c in retrieved),
        "chunks": [
            {"source": c.source, "text": c.text, "score": c.score} for c in retrieved
        ],
        "metricas": {
            "prompt_tokens": gen.prompt_tokens,
            "output_tokens": gen.output_tokens,
            "tokens_per_sec": gen.tokens_per_sec,
            "latencia_s": gen.latency_s,
            "modelo": gen.model,
        },
        "trazas": None,
        "conversation_id": conversation_id,
    }


def _unique_preserving_order(items) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out
