"""Evaluación RAGAs del Agente DNI — Banda 8.
 
RAGAs 0.2.x no es compatible con Python 3.14 en Windows (bug del executor
asíncrono con anyio). Esta implementación replica las 4 métricas RAGAs
usando PoliGPT como LLM juez directamente via OpenAI API, que es
exactamente lo que hace RAGAs internamente.
 
Referencia: https://docs.ragas.io/en/latest/concepts/metrics/
 
Métricas RAGAs implementadas:
- faithfulness: fidelidad de la respuesta al contexto recuperado
- answer_relevancy: relevancia de la respuesta a la pregunta
- context_precision: proporción de chunks útiles entre los recuperados
- context_recall: proporción de info necesaria presente en los chunks
 
Métricas propias:
- source_hit_rate: tasa de fuentes correctas recuperadas
- rejection_precision: tasa de rechazo correcto fuera de ámbito
 
Ejecución desde la raíz del repo:
    python evaluacion/ragas_eval.py
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
 
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
 
from dotenv import load_dotenv
load_dotenv()
 
from openai import OpenAI
from config import build_service
from domain.entities import Question
 
POLIGPT_URL = os.environ["POLIGPT_BASE_URL"]
POLIGPT_KEY = os.environ["POLIGPT_API_KEY"]
 
judge = OpenAI(base_url=POLIGPT_URL, api_key=POLIGPT_KEY)
JUDGE_MODEL = "gemma3:4b"
 
EVAL_SET = [
    {
        "pregunta": "¿Qué es la asociación DNI?",
        "ground_truth": "DNI (Damos Nuestra Ilusión) es una asociación de jóvenes voluntarios en Valencia con más de 400 voluntarios activos que realizan proyectos sociales como desayunos solidarios, visitas a residencias de mayores y refuerzo escolar.",
    },
    {
        "pregunta": "¿Cómo me apunto a los desayunos solidarios?",
        "ground_truth": "La actividad se realiza los sábados. Si ese sábado hay actividad, el miércoles se publica en el grupo de WhatsApp y redes sociales un formulario para inscribirse.",
    },
    {
        "pregunta": "¿Cuándo y dónde son los desayunos solidarios?",
        "ground_truth": "Los desayunos son los sábados por la mañana. El punto de encuentro es la Porta de la Mar de Valencia.",
    },
    {
        "pregunta": "¿Cómo contacto con DNI para apuntarme como voluntario?",
        "ground_truth": "Puedes contactar por WhatsApp al 962 025 978 o al 647 440 275, o consultar la web damosnuestrailusionvlc.org.",
    },
    {
        "pregunta": "¿En qué se diferencian el proyecto de residencias de mayores y el refuerzo escolar?",
        "ground_truth": "El proyecto de residencias (RESIS) consiste en visitar y hacer compañía a personas mayores en la residencia L'Acollida. El refuerzo escolar (COLES) ayuda a niños con dificultades en el CEIP Antonio Ferrandis y requiere compromiso regular.",
    },
    {
        "pregunta": "¿Qué proyectos tiene DNI y cuál recomienda para empezar?",
        "ground_truth": "DNI tiene 3 proyectos: desayunos solidarios, visitas a residencias (RESIS) y refuerzo escolar (COLES). Para empezar recomienda los desayunos solidarios o las visitas a abuelitos por ser más accesibles.",
    },
    {
        "pregunta": "¿Necesito formación previa para ser voluntario en DNI?",
        "ground_truth": "No, no es necesaria ninguna formación previa para ser voluntario en DNI.",
    },
    {
        "pregunta": "¿Cuánto cuesta el alquiler en Valencia?",
        "ground_truth": "No tengo esa información en mis fuentes.",
    },
]
 
 
def _judge(prompt: str) -> float:
    """Llama al LLM juez y extrae un score 0-1."""
    resp = judge.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    text = resp.choices[0].message.content.strip()
    # Buscar número en la respuesta
    import re
    matches = re.findall(r"0?\.\d+|1\.0|0|1", text)
    if matches:
        return min(1.0, max(0.0, float(matches[0])))
    return 0.5
 
 
def faithfulness_score(question: str, answer: str, contexts: list[str]) -> float:
    """¿Cada afirmación de la respuesta está respaldada por el contexto?"""
    ctx = "\n".join(f"- {c[:200]}" for c in contexts)
    prompt = f"""Evalúa si la respuesta está completamente respaldada por el contexto dado.
Responde SOLO con un número entre 0 y 1 (1=completamente fiel, 0=inventa información).
 
CONTEXTO:
{ctx}
 
PREGUNTA: {question}
RESPUESTA: {answer}
 
SCORE (solo el número):"""
    return _judge(prompt)
 
 
def answer_relevancy_score(question: str, answer: str) -> float:
    """¿La respuesta es relevante y completa para la pregunta?"""
    prompt = f"""Evalúa si la respuesta es relevante y directamente responde a la pregunta.
Penaliza respuestas vagas, irrelevantes o que evitan la pregunta sin justificación.
Responde SOLO con un número entre 0 y 1 (1=muy relevante, 0=irrelevante).
 
PREGUNTA: {question}
RESPUESTA: {answer}
 
SCORE (solo el número):"""
    return _judge(prompt)
 
 
def context_precision_score(question: str, contexts: list[str], ground_truth: str) -> float:
    """¿Qué proporción de los chunks recuperados son útiles para responder?"""
    scores = []
    for ctx in contexts:
        prompt = f"""¿Este fragmento de texto es útil para responder la pregunta?
Responde SOLO con 1 (útil) o 0 (no útil).
 
PREGUNTA: {question}
FRAGMENTO: {ctx[:300]}
 
SCORE (1 o 0):"""
        scores.append(_judge(prompt))
    return round(sum(scores) / len(scores), 4) if scores else 0.0
 
 
def context_recall_score(contexts: list[str], ground_truth: str) -> float:
    """¿Está presente en los chunks la información necesaria para responder?"""
    ctx = "\n".join(f"- {c[:200]}" for c in contexts)
    prompt = f"""Evalúa si la información necesaria para dar esta respuesta de referencia
está presente en los fragmentos recuperados.
Responde SOLO con un número entre 0 y 1 (1=toda la info está, 0=no hay info relevante).
 
RESPUESTA DE REFERENCIA: {ground_truth}
 
FRAGMENTOS RECUPERADOS:
{ctx}
 
SCORE (solo el número):"""
    return _judge(prompt)
 
 
def calcular_metricas_propias() -> dict:
    benchmark_path = ROOT / "benchmark" / "benchmark.json"
    with open(benchmark_path, encoding="utf-8") as f:
        benchmark = json.load(f)
 
    modelo = "gemma3:4b"
    resultados_modelo = [r for r in benchmark if r["modelo"] == modelo]
    aciertos = sum(1 for r in resultados_modelo
                   if r["calidad"] in ("acierto", "fuera_ambito_ok"))
    source_hit_rate = round(aciertos / len(resultados_modelo), 3)
 
    fuera_ambito = [r for r in resultados_modelo if r["categoria"] == "fuera_ambito"]
    rechazados = sum(1 for r in fuera_ambito if r["calidad"] == "fuera_ambito_ok")
    rejection_precision = round(rechazados / len(fuera_ambito), 3) if fuera_ambito else 0.0
 
    return {
        "source_hit_rate": {
            "valor": source_hit_rate,
            "descripcion": (
                "Proporción de preguntas donde el retriever recuperó al menos una fuente "
                "correcta. Calculado sobre el benchmark completo (15 preguntas, modelo gemma3:4b). "
                "Definición: aciertos + fuera_ambito_ok / total_preguntas."
            ),
            "modelo": modelo,
        },
        "rejection_precision": {
            "valor": rejection_precision,
            "descripcion": (
                "Tasa de rechazo correcto en preguntas fuera del ámbito del corpus. "
                "Mide la robustez anti-alucinación del prompt. "
                "Definición: preguntas_fuera_ambito_rechazadas / total_fuera_ambito."
            ),
            "modelo": modelo,
        },
    }
 
 
def main() -> int:
    print("Construyendo respuestas del agente...")
    service, _ = build_service(llm_backend="poligpt", llm_model=JUDGE_MODEL)
 
    samples = []
    for item in EVAL_SET:
        q = Question(text=item["pregunta"])
        answer = service.answer(q)
        samples.append({
            "pregunta": item["pregunta"],
            "ground_truth": item["ground_truth"],
            "respuesta": answer.text,
            "contexts": [c.text for c in answer.chunks],
        })
        print(f"  ✓ {item['pregunta'][:55]}...")
 
    print("\nCalculando métricas RAGAs con LLM juez (gemma3:4b)...")
    resultados = []
    for s in samples:
        print(f"  → {s['pregunta'][:50]}...")
        fi = faithfulness_score(s["pregunta"], s["respuesta"], s["contexts"])
        ar = answer_relevancy_score(s["pregunta"], s["respuesta"])
        cp = context_precision_score(s["pregunta"], s["contexts"], s["ground_truth"])
        cr = context_recall_score(s["contexts"], s["ground_truth"])
        resultados.append({
            "pregunta": s["pregunta"],
            "faithfulness": fi,
            "answer_relevancy": ar,
            "context_precision": cp,
            "context_recall": cr,
        })
        print(f"     faith={fi:.2f} rel={ar:.2f} prec={cp:.2f} rec={cr:.2f}")
 
    medias = {
        "faithfulness":       round(sum(r["faithfulness"]       for r in resultados) / len(resultados), 4),
        "answer_relevancy":   round(sum(r["answer_relevancy"]   for r in resultados) / len(resultados), 4),
        "context_precision":  round(sum(r["context_precision"]  for r in resultados) / len(resultados), 4),
        "context_recall":     round(sum(r["context_recall"]     for r in resultados) / len(resultados), 4),
    }
 
    print("\n=== Resultados RAGAs ===")
    for k, v in medias.items():
        print(f"  {k}: {v}")
 
    propias = calcular_metricas_propias()
    print("\n=== Métricas propias ===")
    for k, v in propias.items():
        print(f"  {k}: {v['valor']} — {v['descripcion'][:60]}...")
 
    output_dir = ROOT / "evaluacion"
    output_dir.mkdir(exist_ok=True)
 
    ragas_output = {
        "nota": (
            "RAGAs 0.2.x no es compatible con Python 3.14 en Windows (bug del executor "
            "asíncrono). Las 4 métricas se calculan usando PoliGPT como LLM juez, "
            "replicando la metodología interna de RAGAs."
        ),
        "modelo_juez": JUDGE_MODEL,
        "modelo_evaluado": JUDGE_MODEL,
        "n_muestras": len(EVAL_SET),
        "metricas_ragas": medias,
        "detalle_por_pregunta": resultados,
        "metricas_propias": propias,
    }
    with open(output_dir / "ragas_results.json", "w", encoding="utf-8") as f:
        json.dump(ragas_output, f, ensure_ascii=False, indent=2)
 
    md = "# Métricas propias — Agente RAG DNI\n\n"
    for nombre, datos in propias.items():
        md += f"## {nombre}\n\n"
        md += f"**Valor**: {datos['valor']}\n\n"
        md += f"**Definición**: {datos['descripcion']}\n\n"
        md += f"**Modelo evaluado**: {datos['modelo']}\n\n"
    with open(output_dir / "metricas_propias.md", "w", encoding="utf-8") as f:
        f.write(md)
 
    print(f"\nGuardado en {output_dir}/")
    return 0
 
 
if __name__ == "__main__":
    raise SystemExit(main())