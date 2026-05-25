from domain.ports import LLMPort, RetrieverPort
from domain.entities import Question, Answer

class ChatbotService:
    def __init__(self, llm: LLMPort, retriever: RetrieverPort):
        self.llm = llm
        self.retriever = retriever

    def answer(self, question: Question)-> Answer:
        chunks = self.retriever.retrieve(question.text, k=5)
        context = "\n\n".join(c.text for c in chunks)
        prompt = self._build_prompt(question.text, context)
        text = self.llm.generate(prompt)
        return Answer(text=text, sources=[c.source for c in chunks],
                      chunks=chunks)

    def _build_prompt(self, q: str, ctx: str)-> str:
        return f"...PROMPT BIEN DISE~ NADO AQU´ I...\nCTX:\n{ctx}\nQ: {q}"
