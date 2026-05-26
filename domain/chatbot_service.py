"""Lógica RAG del dominio. No importa nada externo (ni requests, ni chromadb)."""
from __future__ import annotations
from .entities import Answer, Chunk, Question
from .ports import LLMPort, RetrieverPort

REJECTION_PHRASE = "No tengo esa información en mis fuentes"

PROMPT_TEMPLATE = """Eres un asistente de la asociación DNI (Damos Nuestra Ilusión) Valencia.

REGLAS:
- Responde SOLO con la información del CONTEXTO. Si la respuesta no está, \
di literalmente: "{rejection}".
- Sé claro y cercano, sin tecnicismos innecesarios.
- Al final de cada dato o afirmación, cita entre paréntesis el archivo \
fuente exacto, por ejemplo: (07_desayunos_logistica.txt). Usa SOLO los \
archivos que aparecen en el CONTEXTO, nunca inventes nombres de archivo.
- Si el corpus contiene información contradictoria, preséntala indicando \
ambas fuentes sin inventar una respuesta única.
- No inventes datos (fechas, horarios, contactos) que no estén explícitos \
en el contexto.

EJEMPLO DE FORMATO CORRECTO:
Pregunta: ¿Cuándo son los desayunos?
Respuesta: Los desayunos son los sábados (07_desayunos_logistica.txt). \
El formulario se publica el miércoles por WhatsApp (01_faq_dni.txt).

CONTEXTO:
{context}

PREGUNTA: {question}

RESPUESTA:"""


class ChatbotService:
    def __init__(self, llm: LLMPort, retriever: RetrieverPort) -> None:
        self.llm = llm
        self.retriever = retriever

    def answer(self, question: Question, *, k: int = 8) -> Answer:
        chunks = self.retriever.retrieve(question.text, k=k)
        prompt = self._build_prompt(question.text, chunks)
        text, metricas = self.llm.generate(prompt)
        sources = _unique_preserving_order(c.source for c in chunks)
        return Answer(
            text=text.strip(),
            sources=sources,
            chunks=chunks,
            metricas=metricas,
            trazas=None,
        )

    def _build_prompt(self, question: str, chunks: list[Chunk]) -> str:
        context = "\n\n".join(f"[{c.source}]\n{c.text}" for c in chunks)
        return PROMPT_TEMPLATE.format(
            rejection=REJECTION_PHRASE,
            context=context,
            question=question,
        )


def _unique_preserving_order(items) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out