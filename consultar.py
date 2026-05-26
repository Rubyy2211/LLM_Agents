"""Punto de entrada del contrato (Opción A — módulo Python).
 
El corrector importa esta función con la signatura EXACTA del enunciado §9.
No cambies de sitio ni añadas argumentos posicionales.
 
Uso manual desde CLI:
    python consultar.py "¿Qué es DNI?"
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
 
# Aseguramos que domain/ y adapters/ son importables
sys.path.insert(0, str(Path(__file__).resolve().parent))
 
from config import build_service
from domain.entities import Question
 
# Servicio singleton (se inicializa una vez al importar el módulo)
_service, _retriever = build_service(llm_backend="ollama")
 
 
def consultar(pregunta: str, conversation_id: str | None = None) -> dict:
    """Función obligatoria del contrato (enunciado §9, opción A)."""
    q = Question(text=pregunta, conversation_id=conversation_id)
    answer = _service.answer(q)
    return {
        "respuesta": answer.text,
        "fuentes": answer.sources,
        "chunks": [
            {"source": c.source, "text": c.text, "score": c.score}
            for c in answer.chunks
        ],
        "metricas": answer.metricas,
        "trazas": answer.trazas,
        "conversation_id": conversation_id,
    }
 
 
def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print('Uso: python consultar.py "<pregunta>"', file=sys.stderr)
        return 2
    pregunta = " ".join(argv[1:])
    result = consultar(pregunta)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
 
 
if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))