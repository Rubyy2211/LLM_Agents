# Benchmark — set de preguntas tipo

Set reducido de **8 preguntas** para validar el agente sobre el corpus
GTI Orienta. Cubre cuatro categorías:

| Categoría | Cuántas | Para qué |
|---|---|---|
| `asignaturas` | 3 | Pregunta directa por temario. Retrieval semántico debería acertar. |
| `primer_curso` | 1 | Pregunta acotada a un único documento. Útil para detectar si el chunking pierde contexto. |
| `consejo` | 1 | Pregunta abierta que requiere combinar varios cursos. |
| `trampa_retrieval` | 1 | El retrieval semántico se distrae (ver Colab §10). Aquí brillaría un retrieval híbrido (BM25 + semántico). |
| `fuera_de_ambito` | 2 | Deben rechazarse con la frase literal `No tengo esa información en mis fuentes`. |

> **Nota pedagógica.** Este set es un *ejemplo* deliberadamente pequeño.
> Para banda 7 hace falta un benchmark contra **4 modelos distintos**
> (2 PoliGPT + 2 locales). Este repo no lo trae porque es trabajo del alumno.

## Ejecutar

```bash
python scripts/run_eval.py
```

Salida en `benchmark/runs/run_<timestamp>.json`. Cada entrada incluye
respuesta, chunks recuperados, fuentes y métricas (`prompt_tokens`,
`output_tokens`, `tokens_per_sec`, `latencia_s`).

## Cómo evaluar los resultados

1. **Acierto factual**: ¿la respuesta es correcta según el corpus?
2. **Cita correcta**: ¿la fuente declarada en `fuentes` contiene
   realmente la información (banda 6)? Cruzad con `chunks[].text`.
3. **No-alucinación**: las preguntas `fuera_de_ambito` deben devolver
   la frase literal de rechazo.
4. **Latencia**: cualquier `latencia_s > 30` baja a banda 5.
5. **Tokens/segundo**: para comparar modelos.

Para banda 8 podéis automatizar (1) y (3) con
[RAGAs](https://docs.ragas.io/) — `faithfulness` y `answer_relevancy` son
los dos más útiles para un set tan pequeño.
