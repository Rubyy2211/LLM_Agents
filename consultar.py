"""Punto de entrada del contrato (Opción A — módulo Python).

El corrector importa esta función con la signatura EXACTA que define el
enunciado §9. No la cambies de sitio ni le añadas argumentos posicionales:
si rompe el contrato, la nota es 0 automáticamente.

Uso manual desde CLI:
    python consultar.py "¿Hay una asignatura sobre videojuegos en GTI?"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from agente_rag.pipeline import answer  # noqa: E402


def consultar(pregunta: str, conversation_id: str | None = None) -> dict:
    """Función obligatoria del contrato (enunciado §9, opción A).

    Args:
        pregunta: pregunta en lenguaje natural.
        conversation_id: opcional; útil si en el futuro se añade memoria.

    Returns:
        Dict con las claves: ``respuesta``, ``fuentes``, ``chunks``,
        ``metricas``, ``trazas``. Ver ``docs/CONTRACT.md``.
    """
    return answer(pregunta, conversation_id=conversation_id)


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
