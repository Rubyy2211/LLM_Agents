"""Tests del prompt template. No requieren Ollama."""

from dataclasses import dataclass

from agente_rag.prompts import REJECTION_PHRASE, build_prompt


@dataclass
class _FakeChunk:
    source: str
    text: str
    score: float = 0.9
    chunk_id: str = "fake"


def test_prompt_includes_rejection_phrase_literal():
    prompt = build_prompt("¿Algo?", [])
    assert REJECTION_PHRASE in prompt, "el prompt debe contener la frase de rechazo literal"


def test_prompt_includes_context_with_source_tags():
    chunks = [
        _FakeChunk(source="3_tercero.txt", text="Inteligencia Artificial — 3º curso"),
        _FakeChunk(source="2_segundo.txt", text="Programación de aplicaciones móviles"),
    ]
    prompt = build_prompt("¿Se da IA?", chunks)
    assert "[3_tercero.txt]" in prompt
    assert "[2_segundo.txt]" in prompt
    assert "Inteligencia Artificial" in prompt


def test_prompt_includes_question_at_end():
    prompt = build_prompt("¿Pregunta concreta?", [])
    assert prompt.rstrip().endswith("RESPUESTA:") or "PREGUNTA: ¿Pregunta concreta?" in prompt
