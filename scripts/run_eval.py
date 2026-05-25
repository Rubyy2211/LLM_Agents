"""Ejecuta el benchmark contra ``benchmark/preguntas.json``.

Por cada pregunta llama al pipeline real (Ollama + ChromaDB) y guarda un
JSON con respuesta, fuentes recuperadas y métricas. La evaluación cualitativa
(¿la respuesta es correcta? ¿cita la fuente esperada?) la hace el alumno
leyendo el resultado o automatizando con RAGAs (banda 8).

Salida en ``benchmark/runs/run_<timestamp>.json``.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agente_rag.pipeline import answer  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_FILE = REPO_ROOT / "benchmark" / "preguntas.json"
RUNS_DIR = REPO_ROOT / "benchmark" / "runs"


def main() -> int:
    if not QUESTIONS_FILE.exists():
        print(f"No existe {QUESTIONS_FILE}", file=sys.stderr)
        return 1

    questions = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    print(f"[eval] {len(questions)} preguntas")
    for i, q in enumerate(questions, 1):
        t0 = time.time()
        try:
            res = answer(q["pregunta"])
        except Exception as exc:
            res = {"error": str(exc)}
        elapsed = time.time() - t0
        print(
            f"  [{i}/{len(questions)}] ({elapsed:.1f}s) {q['pregunta'][:60]}..."
        )
        results.append(
            {
                "id": q.get("id", f"q{i}"),
                "pregunta": q["pregunta"],
                "fuentes_esperadas": q.get("fuentes_esperadas", []),
                "categoria": q.get("categoria"),
                "salida": res,
            }
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = RUNS_DIR / f"run_{timestamp}.json"
    out_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[eval] resultados → {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
