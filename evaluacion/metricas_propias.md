# Métricas propias — Agente RAG DNI

## source_hit_rate

**Valor**: 1.0

**Definición**: Proporción de preguntas donde el retriever recuperó al menos una fuente correcta. Calculado sobre el benchmark completo (15 preguntas, modelo gemma3:4b). Definición: aciertos + fuera_ambito_ok / total_preguntas.

**Modelo evaluado**: gemma3:4b

## rejection_precision

**Valor**: 1.0

**Definición**: Tasa de rechazo correcto en preguntas fuera del ámbito del corpus. Mide la robustez anti-alucinación del prompt. Definición: preguntas_fuera_ambito_rechazadas / total_fuera_ambito.

**Modelo evaluado**: gemma3:4b

