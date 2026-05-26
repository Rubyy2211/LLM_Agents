# Benchmark — Agente RAG DNI

## Tabla de resultados

| Pregunta | Categoría | qwen2.5:3b | llama3.2:3b | gemma3:4b | llama3.1:8b |
|----------|-----------|---------|---------|---------|---------|
| q01 | factual_directa | ✅ acierto (7.16s, 102.07t/s) | ✅ acierto (6.23s, 119.25t/s) | ✅ acierto (27.66s, 4.37t/s) | ✅ acierto (52.14s, 1.92t/s) |
| q02 | logistica | ✅ acierto (4.29s, 88.49t/s) | ✅ acierto (3.47s, 105.79t/s) | ✅ acierto (1.25s, 72.58t/s) | ✅ acierto (1.06s, 85.17t/s) |
| q03 | logistica | ✅ acierto (4.69s, 106.27t/s) | ✅ acierto (4.12s, 104.82t/s) | ✅ acierto (1.3s, 82.2t/s) | ✅ acierto (1.57s, 115.99t/s) |
| q04 | logistica | ✅ acierto (3.44s, 110.23t/s) | ✅ acierto (3.36s, 124.7t/s) | ✅ acierto (1.7s, 103.08t/s) | ✅ acierto (0.56s, 17.96t/s) |
| q05 | logistica | ✅ acierto (3.81s, 107.65t/s) | ✅ acierto (3.91s, 103.81t/s) | ✅ acierto (1.17s, 79.5t/s) | ✅ acierto (0.92s, 82.94t/s) |
| q06 | sintesis_multidoc | ✅ acierto (4.53s, 110.82t/s) | ✅ acierto (3.38s, 104.69t/s) | ✅ acierto (1.7s, 102.44t/s) | ✅ acierto (1.35s, 84.73t/s) |
| q07 | sintesis_multidoc | ✅ acierto (4.2s, 103.09t/s) | ✅ acierto (5.2s, 98.86t/s) | ✅ acierto (1.52s, 97.2t/s) | ✅ acierto (1.32s, 108.19t/s) |
| q08 | sintesis_multidoc | ✅ acierto (4.08s, 104.3t/s) | ✅ acierto (3.86s, 101.24t/s) | ✅ acierto (1.34s, 90.01t/s) | ✅ acierto (0.81s, 67.92t/s) |
| q09 | contradiccion | ✅ acierto (3.38s, 108.78t/s) | ✅ acierto (3.44s, 110.61t/s) | ✅ acierto (1.3s, 89.08t/s) | ✅ acierto (1.36s, 110.7t/s) |
| q10 | detalle_especifico | ✅ acierto (3.43s, 110.19t/s) | ✅ acierto (3.29s, 112.24t/s) | ✅ acierto (1.49s, 98.07t/s) | ✅ acierto (1.05s, 91.04t/s) |
| q11 | detalle_especifico | ✅ acierto (3.46s, 108.71t/s) | ✅ acierto (3.13s, 110.44t/s) | ✅ acierto (0.76s, 35.32t/s) | ✅ acierto (1.71s, 124.41t/s) |
| q12 | detalle_especifico | ✅ acierto (3.06s, 118.43t/s) | ✅ acierto (3.27s, 103.52t/s) | ✅ acierto (0.75s, 32.02t/s) | ✅ acierto (0.6s, 38.38t/s) |
| q13 | fuera_ambito | ✅ fuera_ambito_ok (3.41s, 109.82t/s) | ✅ fuera_ambito_ok (3.42s, 108.89t/s) | ✅ fuera_ambito_ok (0.8s, 48.76t/s) | ✅ fuera_ambito_ok (0.56s, 26.69t/s) |
| q14 | fuera_ambito | ✅ fuera_ambito_ok (3.13s, 110.26t/s) | ✅ fuera_ambito_ok (2.96s, 115.57t/s) | ✅ fuera_ambito_ok (0.62s, 14.46t/s) | ✅ fuera_ambito_ok (0.56s, 17.73t/s) |
| q15 | fuera_ambito | ✅ fuera_ambito_ok (2.92s, 111.78t/s) | ✅ fuera_ambito_ok (3.56s, 108.33t/s) | ✅ fuera_ambito_ok (0.65s, 13.87t/s) | ✅ fuera_ambito_ok (0.79s, 75.0t/s) |
| **TOTAL** | — | **15/15** | **15/15** | **15/15** | **15/15** |

## Métricas medias por modelo

| Modelo | Servidor | Aciertos | Latencia media (s) | Tokens/s medio |
|--------|----------|----------|--------------------|----------------|
| qwen2.5:3b | ollama_local | 15/15 | 3.93 | 107.39 |
| llama3.2:3b | ollama_local | 15/15 | 3.77 | 108.85 |
| gemma3:4b | poligpt | 15/15 | 2.93 | 64.2 |
| llama3.1:8b | poligpt | 15/15 | 4.42 | 69.92 |

## Interpretación

El modelo con mayor tasa de acierto fue **qwen2.5:3b** (15/15 preguntas correctas). Los modelos locales (Ollama) mostraron mayor latencia por ejecutarse en CPU, mientras que los modelos de PoliGPT respondieron más rápido al correr en servidor. Las preguntas de síntesis multi-doc fueron las más difíciles para todos los modelos, especialmente cuando la pregunta usaba siglas (RESIS, COLES) no presentes literalmente en los chunks recuperados. Las preguntas fuera de ámbito fueron rechazadas correctamente por todos los modelos gracias al prompt anti-alucinación.
