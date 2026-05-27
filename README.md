# Agente RAG — Asistente DNI Valencia
 
> Práctica de *Inteligencia Artificial* (3º GTI, UPV).
> Agente RAG con **arquitectura hexagonal** (banda 10) sobre el corpus de la
> asociación DNI (Damos Nuestra Ilusión) Valencia.
 
## Arranque rápido
 
```bash
# 1. Clonar y entrar
git clone https://github.com/Rubyy2211/LLM_Agents
cd LLM_Agents
 
# 2. Entorno virtual (Python 3.10+)
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows
 
# 3. Dependencias
pip install -r requirements.txt
 
# 4. Variables de entorno
cp .env.example .env
# Edita .env con tu POLIGPT_API_KEY y ajusta LLM_MODEL si hace falta
 
# 5. Tener Ollama corriendo con los modelos necesarios
ollama pull qwen2.5:3b
ollama pull llama3.2:3b
ollama pull nomic-embed-text
 
# 6. Construir el índice ChromaDB (solo una vez, ~2-7 min en CPU)
python scripts/build_index_hex.py
 
# 7. Lanzar una consulta
python consultar.py "¿Qué es la asociación DNI?"
```
 
Salida esperada:
 
```json
{
  "respuesta": "DNI (Damos Nuestra Ilusión) es una asociación de jóvenes voluntarios en Valencia... (08_preguntas_basicas.txt)",
  "fuentes": ["08_preguntas_basicas.txt", "04_filosofia_dni.txt"],
  "chunks": [...],
  "metricas": {"prompt_tokens": 767, "output_tokens": 112, "tokens_per_sec": 105.6, "latencia_s": 7.4, "modelo": "qwen2.5:3b"},
  "trazas": null,
  "conversation_id": null
}
```
 
## Estructura del repositorio
 
```
LLM_Agents/
├── consultar.py              # Contrato §9 opción A — punto de entrada
├── config.py                 # Composition root: monta adapters
├── features.json             # Declaración de bandas para el corrector
├── .env.example              # Plantilla de variables de entorno
│
├── domain/                   # Dominio puro (sin imports externos)
│   ├── entities.py           # Question, Answer, Chunk (dataclasses)
│   ├── ports.py              # LLMPort, EmbedderPort, RetrieverPort (Protocols)
│   └── chatbot_service.py    # Lógica RAG — orquesta retrieval + LLM
│
├── adapters/                 # Implementaciones intercambiables
│   ├── llm/
│   │   ├── ollama_llm.py     # LLMPort → Ollama local
│   │   ├── poligpt_llm.py    # LLMPort → PoliGPT UPV
│   │   └── fake_llm.py       # LLMPort → stub para tests
│   ├── embedder/
│   │   ├── ollama_embedder.py  # EmbedderPort → nomic-embed-text
│   │   └── st_embedder.py      # EmbedderPort → sentence-transformers
│   └── retriever/
│       ├── chroma_retriever.py # RetrieverPort → ChromaDB persistente
│       └── faiss_retriever.py  # RetrieverPort → FAISS (segunda impl.)
│
├── corpus/                   # 16 .txt del corpus DNI (no modificar)
├── scripts/
│   └── build_index_hex.py    # Construye índice ChromaDB
├── benchmark/
│   ├── preguntas.json        # 15 preguntas de evaluación
│   ├── benchmark.py          # Script benchmark 4 modelos
│   ├── benchmark.json        # Resultados crudos
│   └── benchmark.md          # Tabla + interpretación
├── evaluacion/
│   ├── ragas_eval.py         # Evaluación con métricas RAGAs
│   ├── ragas_results.json    # Resultados RAGAs + métricas propias
│   └── metricas_propias.md   # Definición y valores
├── tests/
│   └── test_chatbot_service.py  # 6 tests del dominio sin red
└── src/agente_rag/           # Pipeline original (chunker, config, etc.)
```
 
## Arquitectura hexagonal
 
El dominio no depende de ningún detalle de infraestructura. Los adapters
son intercambiables con **una línea** en `config.py`:
 
```
        adapters              ports            dominio puro
   ┌─────────────┐       ┌──────────┐       ┌─────────────────────┐
   │ OllamaLLM   │──────▶│ LLMPort  │──────▶│                     │
   │ PoliGPTLLM  │       └──────────┘       │   ChatbotService    │
   └─────────────┘                          │                     │
   ┌─────────────┐       ┌──────────────┐   │  Question → Answer  │
   │OllamaEmb    │──────▶│ EmbedderPort │──▶│                     │
   └─────────────┘       └──────────────┘   └─────────────────────┘
   ┌─────────────┐       ┌──────────────┐
   │ChromaRetr   │──────▶│RetrieverPort │
   │FAISSRetr    │       └──────────────┘
   └─────────────┘
```
 
### Cómo añadir un adapter nuevo
 
Por ejemplo, para añadir `GPT4oLLM`:
 
1. Crea `adapters/llm/gpt4o_llm.py` implementando el método `generate(prompt, *, temperature) -> tuple[str, dict]`
2. En `config.py`, añade un caso en `build_service`:
```python
elif llm_backend == "gpt4o":
    from adapters.llm.gpt4o_llm import GPT4oLLM
    llm = GPT4oLLM(api_key=os.getenv("OPENAI_API_KEY"))
```
3. Listo. El dominio no cambia.
## Bandas implementadas
 
| Banda | Descripción | Estado |
|-------|-------------|--------|
| 5 | Pipeline RAG completo + anti-alucinación + Ollama local | ✅ |
| 6 | Cita del archivo fuente en respuesta y campo `fuentes` | ✅ |
| 7 | Benchmark 4 modelos (2 Ollama + 2 PoliGPT) con métricas | ✅ |
| 8 | Métricas RAGAs (faithfulness, relevancy, precision, recall) + 2 propias | ✅ |
| 10 | Arquitectura hexagonal completa + tests sin red | ✅ |
 
## Benchmark — resumen
 
| Modelo | Servidor | Aciertos | Latencia media | Tokens/s |
|--------|----------|----------|----------------|----------|
| qwen2.5:3b | ollama_local | 14/15 | 4.18s | 108.9 |
| llama3.2:3b | ollama_local | 14/15 | 4.86s | 105.9 |
| gemma3:4b | poligpt | 14/15 | 1.27s | 66.2 |
| llama3.1:8b | poligpt | 14/15 | 4.72s | 72.2 |
 
**Modelo elegido**: `gemma3:4b` (PoliGPT) por mejor ratio calidad/latencia.
Fallback local: `qwen2.5:3b` (Ollama) cuando no hay VPN disponible.
 
## Métricas RAGAs
 
| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| faithfulness | 0.83 | Alta fidelidad al corpus |
| answer_relevancy | 0.88 | Respuestas bien orientadas |
| context_precision | 0.44 | Margen de mejora con k menor |
| context_recall | 0.88 | Retriever encuentra info necesaria |
| source_hit_rate | 1.00 | Fuente correcta siempre recuperada |
| rejection_precision | 1.00 | Anti-alucinación perfecto |
 
## Tests
 
```bash
pytest tests/ -v
# 6 passed in 0.04s — sin red, sin Ollama, sin ChromaDB
```
 
Los tests usan `FakeLLM` y `FakeRetriever` para verificar la lógica del
dominio de forma aislada.
 
## Requisitos
 
- Python 3.10+
- Ollama con `qwen2.5:3b`, `llama3.2:3b` y `nomic-embed-text`
- VPN UPV para usar PoliGPT (benchmark y RAGAs)
- Ver `requirements.txt` para dependencias Python
## Notas importantes
 
- El corpus (`corpus/`) no debe modificarse — forma parte del enunciado.
- Nunca subas `.env` al repositorio — usa `.env.example` como plantilla.
- El índice ChromaDB se genera en `data/chroma/` y no se versiona (`.gitignore`).
## Créditos
 
Práctica desarrollada para *Inteligencia Artificial*, Grado en Tecnologías
Interactivas, Universitat Politècnica de València, 2026.