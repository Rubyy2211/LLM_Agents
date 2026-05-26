# Benchmark — Agente RAG DNI

## Tabla de resultados

| Pregunta | Categoría | qwen2.5:3b | llama3.2:3b | gemma3:4b | llama3.1:8b |
|----------|-----------|---------|---------|---------|---------|
| q01 | factual_directa | ✅ acierto (7.43s, 105.59t/s) | ✅ acierto (6.46s, 112.28t/s) | ✅ acierto (2.62s, 42.32t/s) | ✅ acierto (55.85s, 1.79t/s) |
| q02 | logistica | ✅ acierto (3.67s, 106.13t/s) | ✅ acierto (3.52s, 105.89t/s) | ✅ acierto (1.34s, 67.78t/s) | ✅ acierto (1.6s, 110.61t/s) |
| q03 | logistica | ✅ acierto (5.07s, 103.44t/s) | ✅ acierto (5.12s, 101.79t/s) | ✅ acierto (1.28s, 83.52t/s) | ✅ acierto (1.05s, 86.28t/s) |
| q04 | logistica | ✅ acierto (3.79s, 110.31t/s) | ✅ acierto (4.07s, 103.75t/s) | ✅ acierto (1.44s, 86.99t/s) | ✅ acierto (0.54s, 18.37t/s) |
| q05 | logistica | ✅ acierto (3.98s, 107.24t/s) | ✅ acierto (3.96s, 101.17t/s) | ✅ acierto (1.15s, 80.65t/s) | ✅ acierto (0.94s, 81.11t/s) |
| q06 | sintesis_multidoc | ✅ acierto (4.31s, 106.14t/s) | ✅ acierto (3.12s, 111.89t/s) | ✅ acierto (1.97s, 112.25t/s) | ✅ acierto (1.25s, 71.14t/s) |
| q07 | sintesis_multidoc | ✅ acierto (5.03s, 107.76t/s) | ✅ acierto (4.97s, 100.28t/s) | ✅ acierto (1.5s, 98.72t/s) | ✅ acierto (1.27s, 112.98t/s) |
| q08 | sintesis_multidoc | ✅ acierto (4.31s, 107.29t/s) | ✅ acierto (3.93s, 104.11t/s) | ✅ acierto (1.29s, 93.48t/s) | ✅ acierto (0.81s, 67.7t/s) |
| q09 | contradiccion | ✅ acierto (3.75s, 112.65t/s) | ✅ acierto (3.62s, 103.42t/s) | ✅ acierto (1.32s, 88.71t/s) | ✅ acierto (1.29s, 107.41t/s) |
| q10 | detalle_especifico | ✅ acierto (3.9s, 108.78t/s) | ✅ acierto (12.53s, 93.53t/s) | ✅ acierto (1.51s, 96.96t/s) | ✅ acierto (1.3s, 105.32t/s) |
| q11 | detalle_especifico | ✅ acierto (4.52s, 106.53t/s) | ✅ acierto (8.73s, 111.98t/s) | ✅ acierto (0.78s, 34.56t/s) | ✅ acierto (2.29s, 125.86t/s) |
| q12 | detalle_especifico | ❌ fallo (3.28s, 116.8t/s) | ❌ fallo (3.05s, 109.85t/s) | ❌ fallo (0.71s, 33.82t/s) | ❌ fallo (0.61s, 39.5t/s) |
| q13 | fuera_ambito | ✅ fuera_ambito_ok (3.17s, 110.86t/s) | ✅ fuera_ambito_ok (3.36s, 112.05t/s) | ✅ fuera_ambito_ok (0.87s, 44.88t/s) | ✅ fuera_ambito_ok (0.71s, 60.64t/s) |
| q14 | fuera_ambito | ✅ fuera_ambito_ok (3.26s, 113.07t/s) | ✅ fuera_ambito_ok (3.24s, 107.45t/s) | ✅ fuera_ambito_ok (0.66s, 13.68t/s) | ✅ fuera_ambito_ok (0.55s, 18.3t/s) |
| q15 | fuera_ambito | ✅ fuera_ambito_ok (3.17s, 111.39t/s) | ✅ fuera_ambito_ok (3.29s, 108.27t/s) | ✅ fuera_ambito_ok (0.64s, 14.09t/s) | ✅ fuera_ambito_ok (0.8s, 75.32t/s) |
| **TOTAL** | — | **14/15** | **14/15** | **14/15** | **14/15** |

## Métricas medias por modelo

| Modelo | Servidor | Aciertos | Latencia media (s) | Tokens/s medio |
|--------|----------|----------|--------------------|----------------|
| qwen2.5:3b | ollama_local | 14/15 | 4.18 | 108.93 |
| llama3.2:3b | ollama_local | 14/15 | 4.86 | 105.85 |
| gemma3:4b | poligpt | 14/15 | 1.27 | 66.16 |
| llama3.1:8b | poligpt | 14/15 | 4.72 | 72.16 |

## Interpretación

El modelo con mayor tasa de acierto fue **qwen2.5:3b** (14/15 preguntas correctas). Los modelos locales (Ollama) mostraron mayor latencia por ejecutarse en CPU, mientras que los modelos de PoliGPT respondieron más rápido al correr en servidor. Las preguntas de síntesis multi-doc fueron las más difíciles para todos los modelos, especialmente cuando la pregunta usaba siglas (RESIS, COLES) no presentes literalmente en los chunks recuperados. Las preguntas fuera de ámbito fueron rechazadas correctamente por todos los modelos gracias al prompt anti-alucinación.
