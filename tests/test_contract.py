"""Tests del contrato (enunciado §9).

No llamamos a Ollama: parchamos ``retrieve`` y ``generate`` con stubs para
verificar que la forma del JSON de salida cumple el contrato exacto.
"""

from __future__ import annotations

from unittest.mock import patch

from agente_rag.generator import Generation
from agente_rag.retriever import RetrievedChunk

CONTRACT_KEYS = {"respuesta", "fuentes", "chunks", "metricas", "trazas"}


def _fake_retrieved():
    return [
        RetrievedChunk(
            source="3_tercero.txt",
            text="Inteligencia Artificial — 6 ECTS — 3º curso",
            score=0.91,
            chunk_id="3_tercero.txt__chunk_0001",
        ),
        RetrievedChunk(
            source="3_tercero.txt",
            text="Visión Artificial — 6 ECTS — 3º curso",
            score=0.84,
            chunk_id="3_tercero.txt__chunk_0007",
        ),
    ]


def _fake_generation():
    return Generation(
        text="En 3º se imparte Inteligencia Artificial (3_tercero.txt).",
        prompt_tokens=420,
        output_tokens=37,
        tokens_per_sec=42.1,
        latency_s=1.8,
        model="gemma2:27b",
    )


def test_consultar_signature_and_keys():
    import consultar

    with patch("agente_rag.pipeline.retrieve", return_value=_fake_retrieved()), patch(
        "agente_rag.pipeline.generate", return_value=_fake_generation()
    ):
        out = consultar.consultar("¿Se da IA en 3º?")

    assert set(out.keys()) >= CONTRACT_KEYS, f"faltan claves: {CONTRACT_KEYS - set(out.keys())}"
    assert isinstance(out["respuesta"], str) and out["respuesta"]
    assert isinstance(out["fuentes"], list)
    assert all(isinstance(s, str) for s in out["fuentes"])
    assert isinstance(out["chunks"], list)
    assert isinstance(out["metricas"], dict)


def test_consultar_accepts_conversation_id():
    import consultar

    with patch("agente_rag.pipeline.retrieve", return_value=_fake_retrieved()), patch(
        "agente_rag.pipeline.generate", return_value=_fake_generation()
    ):
        out = consultar.consultar("¿Se da IA?", conversation_id="conv-42")
    assert out["conversation_id"] == "conv-42"


def test_fuentes_are_unique_and_preserve_order():
    import consultar

    chunks = [
        RetrievedChunk(source="3_tercero.txt", text="x", score=0.9, chunk_id="a"),
        RetrievedChunk(source="2_segundo.txt", text="y", score=0.8, chunk_id="b"),
        RetrievedChunk(source="3_tercero.txt", text="z", score=0.7, chunk_id="c"),
    ]
    with patch("agente_rag.pipeline.retrieve", return_value=chunks), patch(
        "agente_rag.pipeline.generate", return_value=_fake_generation()
    ):
        out = consultar.consultar("¿x?")

    assert out["fuentes"] == ["3_tercero.txt", "2_segundo.txt"]


def test_metricas_have_banda7_fields():
    import consultar

    with patch("agente_rag.pipeline.retrieve", return_value=_fake_retrieved()), patch(
        "agente_rag.pipeline.generate", return_value=_fake_generation()
    ):
        out = consultar.consultar("¿algo?")

    metricas = out["metricas"]
    for k in ("prompt_tokens", "output_tokens", "tokens_per_sec", "latencia_s"):
        assert k in metricas, f"falta métrica {k!r}"
    assert metricas["output_tokens"] == 37
    assert metricas["tokens_per_sec"] == 42.1
