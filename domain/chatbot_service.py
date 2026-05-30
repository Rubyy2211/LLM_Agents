"""Lógica RAG del dominio. No importa nada externo (ni requests, ni chromadb)."""
from __future__ import annotations
from .entities import Answer, Chunk, Question
from .ports import LLMPort, RetrieverPort

REJECTION_PHRASE = "No tengo esa información en mis fuentes."

# PROMPT MAESTRO CON DOBLE ESCENARIO PARA MODELOS DE 3B
PROMPT_TEMPLATE = """Eres un asistente de la asociación DNI (Damos Nuestra Ilusión) Valencia. Tu tarea es responder a la pregunta de forma cercana y concisa usando exclusivamente los documentos provistos.

[EJEMPLO 1: INFORMACIÓN ENCONTRADA]
DOCUMENTO: archivo_ejemplo.txt
Contenido: Q: ¿Se necesita coche? A: No es obligatorio tener coche propio.
Pregunta: ¿Necesito coche para el voluntariado?
Respuesta: No es obligatorio tener coche propio para asistir a las actividades. (archivo_ejemplo.txt)

[EJEMPLO 2: INFORMACIÓN NO ENCONTRADA]
DOCUMENTO: horarios.txt
Contenido: Q: ¿A qué hora es? A: A las 17:00h en el centro.
Pregunta: ¿Cuál es el teléfono de contacto de la asociación?
Respuesta: No tengo esa información en mis fuentes.

[TAREA REAL]
{context}

Pregunta: {question}

REGLAS DE ORO (SÉ ESTRICTO):
1. SI LA INFORMACIÓN ESTÁ EN LOS DOCUMENTOS: Responde de forma clara, amigable y directa. Al final de tu respuesta, añade entre paréntesis el nombre del DOCUMENTO exacto de donde extrajiste el dato.
2. SI HAY RESPUESTAS QUE PARECEN CONTRADICTORIAS: No te asustes ni rechaces la pregunta. Unifícalas con sentido común (por ejemplo, explica que no hace falta un curso formal o experiencia, pero que el staff te dará una explicación o pautas antes de empezar la actividad).
3. SI LA INFORMACIÓN NO ESTÁ EN LOS DOCUMENTOS: Responde ÚNICAMENTE con la frase: "{rejection}" (sin añadir fuentes, ni comentarios, ni paréntesis).

Respuesta:"""


class ChatbotService:
    def __init__(self, llm: LLMPort, retriever: RetrieverPort) -> None:
        self.llm = llm
        self.retriever = retriever

    def answer(self, question: Question, *, k: int = 3) -> Answer:
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
        context_parts = []
        for c in chunks:
            context_parts.append(f"DOCUMENTO: {c.source}\nContenido: {c.text}\n---")
        context = "\n".join(context_parts)
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