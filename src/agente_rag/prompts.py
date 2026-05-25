"""Plantilla del prompt anti-alucinación.

Cinco bloques: rol + instrucciones + contexto + restricciones + formato.
El bloque crítico es la regla del rechazo: ante una pregunta cuya respuesta
no esté en el contexto, el LLM responde literalmente la frase de rechazo
en vez de inventar.

Esta cadena exacta se usa en los tests de no-alucinación para asegurar que
el sistema rechaza correctamente preguntas fuera de ámbito.
"""

REJECTION_PHRASE = "No tengo esa información en mis fuentes"


PROMPT_TEMPLATE = """Eres un asistente que orienta a estudiantes y familias \
sobre el Grado en Tecnologías Interactivas (GTI) de la UPV.

REGLAS:
- Responde SÓLO con la información del CONTEXTO. Si la respuesta no está, \
di literalmente: "{rejection}".
- Sé claro y cercano, sin tecnicismos innecesarios.
- Cita siempre el archivo del que sale la información, entre paréntesis.
- No inventes datos numéricos (créditos, horas, fechas) que no estén \
explícitos en el contexto.

CONTEXTO:
{context}

PREGUNTA: {question}

RESPUESTA:"""


def build_prompt(question: str, retrieved: list) -> str:
    """Une los chunks recuperados y rellena la plantilla."""
    context = "\n\n".join(f"[{c.source}]\n{c.text}" for c in retrieved)
    return PROMPT_TEMPLATE.format(
        rejection=REJECTION_PHRASE,
        context=context,
        question=question,
    )
