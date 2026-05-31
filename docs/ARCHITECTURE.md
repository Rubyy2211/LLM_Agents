# Decisiones de arquitectura

> Documento corto que explica el **por qué** detrás de cada elección.
> No describe **qué** hace cada fichero (eso lo cuenta el código y el
> README). Aquí va lo que un alumno no puede deducir leyendo el árbol.

## 1. Por qué arquitectura hexagonal (Banda 10)

Este repo implementa una **arquitectura hexagonal completa**, aspirando a la banda 10. A diferencia de una plantilla básica:
- `domain/` contiene el core puro (entidades, puertos y lógica RAG).
- `adapters/` contiene las implementaciones reales y aisladas (Ollama, Chroma, Web).
- `config.py` es el **composition root** que inyecta las dependencias.

## 2. Por qué ChromaDB persistente y no in-memory

En nuestro repo el examinador clona, indexa **una vez**, y luego hace múltiples preguntas. Reembedar los chunks cada vez son ~30 s extra que **se pagan en la oral**. Con `PersistentClient` el segundo arranque cae a < 2 s.
Coste: el directorio `data/chroma/` no se sube a Git. **Hay que regenerar el índice** localmente con `python scripts/build_index_hex.py`.

## 3. Por qué `nomic-embed-text` y no sentence-transformers

`nomic-embed-text` viene en el catálogo de Ollama UPV → un único endpoint para LLM y embeddings. Una sola dependencia (`requests`), un solo timeout, un solo error.
Aun así, **hemos implementado** `sentence-transformers` en `adapters/embedder/st_embedder.py` como fallback local por si la red de la UPV falla.

## 4. Por qué chunk_size=500 / overlap=100

Es el "sweet spot" para texto en español:
- 100: pierde contexto, recupera trozos inconexos.
- 2000: el embedding se diluye y el prompt se infla.
- 500/100: un chunk típico es un párrafo o medio, suficiente para que el retrieval semántico distinga contextos.

## 5. Por qué `score = 1 - distance` en el retriever

ChromaDB devuelve **distancias** (más bajo = más cercano), pero el contrato y el informe esperan **scores** (más alto = mejor match). Hacemos la conversión una sola vez en el adapter (`chroma_retriever.py`) para que el dominio razone siempre en "score".

## 6. Por qué `verify_ssl=False` SOLO contra UPV

El endpoint Ollama UPV usa cert autofirmado. Con `verify=False` el handshake pasa pero **se desactivan las comprobaciones de identidad** (asumible dentro de la red UPV, pero peligroso fuera). Por eso el default en `.env.example` es `VERIFY_SSL=true` y solo se baja cuando es necesario.

## 7. Por qué los tests no llaman a Ollama

Tres razones:
1. **Reproducibilidad**: el CI no tiene acceso a Ollama.
2. **Velocidad**: con stubs (`FakeLLM`), los tests tardan milisegundos en vez de minutos.
3. **Cobertura**: verificamos la **forma** del JSON de salida, no el contenido.
La validación E2E real la hemos automatizado en `scripts/benchmark.py`.

## 8. Extras y decisiones adicionales implementadas

A diferencia de la plantilla base, en este proyecto **sí hemos desarrollado** los extras:
- **Retrieval híbrido (BM25 + semántico)**: Implementado en `adapters/retriever/hybrid_retriever.py`.
- **Frontend (+1.5)**: Interfaz web funcional con Streamlit (`adapters/web/streamlit_ui.py`) que incluye historial y fuentes.
- **AWS Rekognition (+1.5)**: Extracción de texto de fotos subidas por el usuario para verificarlas contra el corpus oficial, implementado en `adapters/web/rekognition_adapter.py`.