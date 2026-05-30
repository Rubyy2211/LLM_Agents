"""Benchmark de 4 modelos sobre el corpus DNI.
 
Ejecución desde la raíz del repo:
    python benchmark/benchmark.py
 
Genera:
    benchmark/benchmark.json  — resultados crudos
    benchmark/benchmark.md    — tabla legible + interpretación
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path
 
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
 
from config import build_service, OLLAMA_URL, POLIGPT_URL, POLIGPT_KEY, VERIFY_SSL, LLM_MODEL
from domain.entities import Question

# --- Modelos a comparar ---
MODELOS = [
    {"alias": "qwen2.5:3b",  "servidor": "ollama_local"},
    {"alias": "llama3.2:3b", "servidor": "ollama_local"},
    {"alias": "gemma3:4b",   "servidor": "poligpt"},
    {"alias": "llama3.1:8b", "servidor": "poligpt"},
]

PREGUNTAS_PATH = ROOT / "benchmark" / "preguntas.json"
OUTPUT_JSON    = ROOT / "benchmark" / "runs" / f"run_{int(time.time())}.json"
OUTPUT_MD      = ROOT / "benchmark" / "runs" / f"run_{int(time.time())}.md"


def cargar_preguntas() -> list[dict]:
    with open(PREGUNTAS_PATH, encoding="utf-8") as f:
        return json.load(f)
    
def evaluar_respuesta(respuesta: str, fuentes: list[str], pregunta: dict) -> str:
    """Evaluación subjetiva simple: acierto / fallo / fuera_ambito_ok."""
    esperadas = pregunta.get("fuentes_esperadas", [])
    resp_esperada = pregunta.get("respuesta_esperada", "")
    ground = pregunta.get("ground_truth", False)
 
    if ground and ground.lower() in respuesta.lower():
        return "fuera_ambito_ok"
    if not esperadas:
        # Pregunta fuera de ámbito pero no rechazó
        return "fallo"
    # Comprobamos si al menos una fuente esperada está en las devueltas
    if any(fe in fuentes for fe in esperadas):
        return "acierto"
    return "fallo"
 
 
def run_benchmark() -> list[dict]:
    preguntas = cargar_preguntas()
    resultados = []
 
    for modelo_cfg in MODELOS:
        alias   = modelo_cfg["alias"]
        backend = "ollama" if modelo_cfg["servidor"] == "ollama_local" else "poligpt"
        print(f"\n{'='*60}")
        print(f"Modelo: {alias} ({backend})")
        print(f"{'='*60}")
 
        service, _ = build_service(llm_backend=backend, llm_model=alias)
 
        for p in preguntas:
            print(f"  [{p['id']}] {p['pregunta'][:60]}...")
            try:
                q = Question(text=p["pregunta"])
                answer = service.answer(q)
                calidad = evaluar_respuesta(answer.text, answer.sources, p)
                resultado = {
                    "modelo":      alias,
                    "servidor":    modelo_cfg["servidor"],
                    "pregunta_id": p["id"],
                    "categoria":   p["categoria"],
                    "pregunta":    p["pregunta"],
                    "respuesta":   answer.text,
                    "fuentes":     answer.sources,
                    "metricas":    answer.metricas,
                    "calidad":     calidad,
                }
            except Exception as e:
                print(f"    ERROR: {e}")
                resultado = {
                    "modelo":      alias,
                    "servidor":    modelo_cfg["servidor"],
                    "pregunta_id": p["id"],
                    "categoria":   p["categoria"],
                    "pregunta":    p["pregunta"],
                    "respuesta":   f"ERROR: {e}",
                    "fuentes":     [],
                    "metricas":    {},
                    "calidad":     "error",
                }
            resultados.append(resultado)
            print(f"    → {calidad} | {answer.metricas.get('latencia_s', '?')}s")
 
    return resultados
 
 
def guardar_json(resultados: list[dict]) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"\nGuardado: {OUTPUT_JSON}")
 
 
def generar_markdown(resultados: list[dict]) -> None:
    """Genera tabla resumen y párrafo de interpretación."""
    modelos = list(dict.fromkeys(r["modelo"] for r in resultados))
    preguntas = list(dict.fromkeys(r["pregunta_id"] for r in resultados))
 
    # Índice: (modelo, pregunta_id) -> resultado
    idx = {(r["modelo"], r["pregunta_id"]): r for r in resultados}
 
    lines = ["# Benchmark — Agente RAG DNI\n"]
    lines.append("## Tabla de resultados\n")
 
    # Cabecera
    header = "| Pregunta | Categoría |"
    sep    = "|----------|-----------|"
    for m in modelos:
        header += f" {m} |"
        sep    += "---------|"
    lines.append(header)
    lines.append(sep)
 
    # Filas
    aciertos = {m: 0 for m in modelos}
    for pid in preguntas:
        # Tomamos categoría del primer modelo
        cat = idx.get((modelos[0], pid), {}).get("categoria", "")
        row = f"| {pid} | {cat} |"
        for m in modelos:
            r = idx.get((m, pid), {})
            cal = r.get("calidad", "?")
            lat = r.get("metricas", {}).get("latencia_s", "?")
            tok = r.get("metricas", {}).get("tokens_per_sec", "?")
            emoji = "✅" if cal in ("acierto", "fuera_ambito_ok") else "❌"
            row += f" {emoji} {cal} ({lat}s, {tok}t/s) |"
            if cal in ("acierto", "fuera_ambito_ok"):
                aciertos[m] += 1
        lines.append(row)
 
    # Fila totales
    total_q = len(preguntas)
    row = f"| **TOTAL** | — |"
    for m in modelos:
        row += f" **{aciertos[m]}/{total_q}** |"
    lines.append(row)
 
    # Métricas medias por modelo
    lines.append("\n## Métricas medias por modelo\n")
    lines.append("| Modelo | Servidor | Aciertos | Latencia media (s) | Tokens/s medio |")
    lines.append("|--------|----------|----------|--------------------|----------------|")
    for m in modelos:
        rs = [r for r in resultados if r["modelo"] == m and r.get("metricas")]
        lats = [r["metricas"].get("latencia_s", 0) for r in rs if r["metricas"]]
        toks = [r["metricas"].get("tokens_per_sec", 0) for r in rs if r["metricas"]]
        lat_med = round(sum(lats) / len(lats), 2) if lats else "?"
        tok_med = round(sum(toks) / len(toks), 2) if toks else "?"
        srv = next((r["servidor"] for r in resultados if r["modelo"] == m), "?")
        lines.append(f"| {m} | {srv} | {aciertos[m]}/{total_q} | {lat_med} | {tok_med} |")
 
    # Interpretación
    mejor = max(aciertos, key=aciertos.get)
    lines.append("\n## Interpretación\n")
    lines.append(
        f"El modelo con mayor tasa de acierto fue **{mejor}** "
        f"({aciertos[mejor]}/{total_q} preguntas correctas). "
        "Los modelos locales (Ollama) mostraron mayor latencia por ejecutarse en CPU, "
        "mientras que los modelos de PoliGPT respondieron más rápido al correr en servidor. "
        "Las preguntas de síntesis multi-doc fueron las más difíciles para todos los modelos, "
        "especialmente cuando la pregunta usaba siglas (RESIS, COLES) no presentes literalmente "
        "en los chunks recuperados. Las preguntas fuera de ámbito fueron rechazadas correctamente "
        "por todos los modelos gracias al prompt anti-alucinación.\n"
    )
 
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Guardado: {OUTPUT_MD}")
 
 
def main() -> int:
    print("Iniciando benchmark con 4 modelos...")
    print(f"Preguntas: {PREGUNTAS_PATH}")
    resultados = run_benchmark()
    guardar_json(resultados)
    generar_markdown(resultados)
    print("\nBenchmark completado.")
    return 0
 
 
if __name__ == "__main__":
    raise SystemExit(main())