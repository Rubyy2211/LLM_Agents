from agente_rag.chunker import Chunk
from domain.chatbot_service import ChatbotService, Question


class FakeLLM:
    def generate(self, prompt, *, temperature=0.2):
        return "Los desayunos son a las 8h (fuente: 01_faq_dni.txt)"
class FakeRetriever:
    def retrieve(self, query, *, k=5):
        return [Chunk(source="01_faq_dni.txt",
                    text="Q: ¿Hora desayunos? A: 8h",
                    score=0.95)]
def test_chatbot_returns_answer_with_source():
    bot = ChatbotService(FakeLLM(), FakeRetriever())
    answer = bot.answer(Question(text="¿A qu´e hora son los desayunos?"))
    assert "8" in answer.text
    assert "01_faq_dni.txt" in answer.sources