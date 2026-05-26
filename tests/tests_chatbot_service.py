"""Tests del dominio sin red (FakeLLM + FakeRetriever).
 
Estos tests prueban la lógica pura del ChatbotService sin llamar
a Ollama ni a ChromaDB. CI corre sin red gracias a esto.
"""
from __future__ import annotations
import sys
from pathlib import Path
 
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
 
from domain.entities import Chunk, Question
from domain.chatbot_service import ChatbotService, REJECTION_PHRASE
 
 
class FakeLLM:
    def __init__(self, response: str = "Los desayunos son a las 8h") -> None:
        self.response = response
        self.last_prompt: str = ""
 
    def generate(self, prompt: str, *, temperature: float = 0.2) -> tuple[str, dict]:
        self.last_prompt = prompt
        return self.response, {
            "prompt_tokens": 10, "output_tokens": 5,
            "tokens_per_sec": 999.0, "latencia_s": 0.001, "modelo": "fake",
        }
 
 
class FakeRetriever:
    def __init__(self, chunks: list[Chunk] | None = None) -> None:
        self._chunks = chunks or [
            Chunk(source="01_faq_dni.txt", text="Q: ¿Hora desayunos? A: 8h",
                  score=0.95, chunk_id="01_faq_dni.txt__chunk_0000")
        ]
 
    def retrieve(self, query: str, *, k: int = 5) -> list[Chunk]:
        return self._chunks
 
    def build_index(self, chunks: list) -> int:
        return len(chunks)
 
 
def test_answer_returns_correct_structure():
    bot = ChatbotService(FakeLLM(), FakeRetriever())
    answer = bot.answer(Question(text="¿A qué hora son los desayunos?"))
    assert isinstance(answer.text, str)
    assert isinstance(answer.sources, list)
    assert isinstance(answer.chunks, list)
    assert isinstance(answer.metricas, dict)
 
def test_answer_includes_source():
    bot = ChatbotService(FakeLLM(), FakeRetriever())
    answer = bot.answer(Question(text="¿A qué hora son los desayunos?"))
    assert "01_faq_dni.txt" in answer.sources
 
def test_answer_text_from_llm():
    bot = ChatbotService(FakeLLM("Los desayunos son a las 8h"), FakeRetriever())
    answer = bot.answer(Question(text="¿A qué hora son los desayunos?"))
    assert "8h" in answer.text
 
def test_out_of_scope_rejection():
    bot = ChatbotService(FakeLLM(REJECTION_PHRASE), FakeRetriever())
    answer = bot.answer(Question(text="¿Cuánto cuesta el alquiler en Valencia?"))
    assert REJECTION_PHRASE in answer.text
 
def test_prompt_contains_question():
    llm = FakeLLM()
    bot = ChatbotService(llm, FakeRetriever())
    q = "¿Cómo me apunto a DNI?"
    bot.answer(Question(text=q))
    assert q in llm.last_prompt
 
def test_metricas_keys():
    bot = ChatbotService(FakeLLM(), FakeRetriever())
    answer = bot.answer(Question(text="test"))
    for key in ("prompt_tokens", "output_tokens", "tokens_per_sec", "latencia_s", "modelo"):
        assert key in answer.metricas
 