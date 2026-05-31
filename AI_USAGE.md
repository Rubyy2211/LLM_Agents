# AI_USAGE.md — uso honesto de asistentes de IA

> Plantilla obligatoria. Rellenadla con la verdad. **No penaliza usar IA**;
> penaliza mentir sobre el uso (ver enunciado §6 y rúbrica).

## ¿Qué herramientas habéis usado?

- [ ] ChatGPT (GPT-4 / GPT-5 / o3 / ...)
- [X] Claude (Sonnet / Opus / ...)
- [ ] GitHub Copilot
- [ ] Cursor / Windsurf / IDE con asistente integrado
- [ ] Gemini
- [ ] Ollama local con modelos abiertos
- [ ] Otras: ...

## ¿En qué partes os ha ayudado?

- **Arquitectura hexagonal completa**: Claude generó la estructura de carpetas
  `domain/`, `adapters/` y `config.py` a partir de los requisitos del enunciado
  y el manual técnico. Ficheros generados: `domain/entities.py`, `domain/ports.py`,
  `domain/chatbot_service.py`, todos los adapters en `adapters/llm/`,
  `adapters/embedder/` y `adapters/retriever/`.
- **Prompt anti-alucinación**: Claude diseñó el `PROMPT_TEMPLATE` en
  `domain/chatbot_service.py`, incluyendo el ejemplo few-shot para forzar
  la cita de fuentes. Lo probamos y ajustamos iterativamente hasta conseguir
  citas consistentes en las respuestas.
- **Scripts de infraestructura**: `scripts/build_index_hex.py`,
  `config.py` y `consultar.py` fueron generados por Claude y revisados
  por nosotros para asegurar que el contrato del enunciado se cumplía.
- **Benchmark**: `benchmark/benchmark.py` y `benchmark/preguntas.json`
  generados por Claude. Las 15 preguntas las revisamos y ajustamos
  (cambio de fuentes esperadas en q12 tras detectar falso negativo del evaluador).
- **Evaluación RAGAs**: `evaluacion/ragas_eval.py` generado por Claude.
  La incompatibilidad de RAGAs 0.2.x con Python 3.14 en Windows la
  diagnosticamos juntos y Claude implementó la solución alternativa con
  PoliGPT como juez directo.
- **Frontend Streamlit**: `adapters/web/streamlit_ui.py` generado por Claude
  y ajustado por nosotros para corregir el bug de fuentes vacías en el historial.
- **Tests**: `tests/test_chatbot_service.py` generado por Claude.
  Los ejecutamos, pasaron los 6, y entendemos qué prueba cada uno.

### Documentación
 
- **README.md**: generado por Claude con los datos reales del benchmark
  y la arquitectura. Revisado y aprobado por el equipo.
- **features.json**: generado por Claude, revisado y validado por nosotros.

### Lo que NO usamos IA
 
- **Informe de la práctica**: redactado íntegramente por el equipo.
- **Decisiones de diseño**: qué banda aspirar, qué modelos elegir para el
  benchmark, qué chunk_size usar — decisiones propias.
- **Depuración de entorno**: instalación de Build Tools para compilar
  dependencias, configuración de VPN UPV, resolución de conflictos de
  versiones Python 3.14 — resueltos por nosotros con orientación de Claude.
  
## Compromiso

Hemos leído y entendido todo el código que hemos entregado. En la presentación
oral en directo seremos capaces de defender cualquier línea que el profesor
nos señale. Si no podemos defender una decisión, asumimos que la nota baja.

Firma (digital, escribiendo el nombre): **Alexandru**, **Fedor**, **Rubén**
