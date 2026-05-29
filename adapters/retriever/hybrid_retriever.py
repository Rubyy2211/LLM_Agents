from __future__ import annotations
import re
from domain.entities import Chunk

class HybridRetriever:
    """Retriever Híbrido que fusiona los resultados de ChromaDB (Semántico)

    y BM25 (Léxico) utilizando Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        chroma_retriever,
        todos_los_chunks: list[Chunk],
        k: int = 4,
        alpha: float = 0.5
    ) -> None:
        self.chroma_retriever = chroma_retriever
        self.todos_los_chunks = todos_los_chunks
        self.k = k
        self.alpha = alpha  # Peso para controlar el balance (Chroma vs BM25)
        
        # Inicializamos el motor léxico BM25 si la librería está disponible
        self._init_bm25()

    def _init_bm25(self) -> None:
        try:
            from rank_bm25 import BM25Okapi
            tokenized_corpus = [self._tokenize(c.text) for c in self.todos_los_chunks]
            self.bm25 = BM25Okapi(tokenized_corpus)
            self.has_bm25 = True
        except ImportError:
            # Fallback seguro por si no tienes instalada la librería rank_bm25
            self.has_bm25 = False

    def _tokenize(self, text: str) -> list[str]:
        """Tokenizador básico para limpiar y trocear el texto en palabras clave."""
        return re.findall(r'\w+', text.lower())

    def retrieve(self, query: str, *, k: int | None = None) -> list[Chunk]:
        limite = k or self.k
        
        # 1. Recuperación Semántica (Chroma)
        # Pedimos el triple de candidatos para tener margen de combinación
        chunks_chroma = self.chroma_retriever.retrieve(query, k=limite * 3)
        
        # 2. Recuperación Léxica (BM25 o Fallback de coincidencia de palabras)
        query_tokens = self._tokenize(query)
        
        if self.has_bm25:
            bm25_scores = self.bm25.get_scores(query_tokens)
            chunks_con_score = sorted(
                zip(self.todos_los_chunks, bm25_scores),
                key=lambda x: x[1],
                reverse=True
            )
            chunks_lexicos = [c for c, score in chunks_con_score if score > 0][:limite * 3]
        else:
            # Fallback nativo basado en intersección simple (evita que el código rompa)
            query_set = set(query_tokens)
            chunks_con_score = []
            for c in self.todos_los_chunks:
                score = len(set(self._tokenize(c.text)) & query_set)
                chunks_con_score.append((c, score))
            chunks_con_score.sort(key=lambda x: x[1], reverse=True)
            chunks_lexicos = [c for c, score in chunks_con_score if score > 0][:limite * 3]

        # 3. Fusión de Rankings mediante Reciprocal Rank Fusion (RRF)
        # RRF asigna una puntuación inversamente proporcional a la posición del documento en cada lista.
        rrf_scores: dict[str, float] = {}
        constante_rrf = 60  # Constante estándar para suavizar el impacto de las primeras posiciones
        
        # Evaluar posiciones de la lista semántica
        for rank, chunk in enumerate(chunks_chroma, start=1):
            rrf_scores[chunk.text] = rrf_scores.get(chunk.text, 0.0) + (self.alpha * (1.0 / (constante_rrf + rank)))
            
        # Evaluar posiciones de la lista léxica
        for rank, chunk in enumerate(chunks_lexicos, start=1):
            rrf_scores[chunk.text] = rrf_scores.get(chunk.text, 0.0) + ((1.0 - self.alpha) * (1.0 / (constante_rrf + rank)))
        
        # 4. Reconstrucción y mapeo de vuelta a Entidades de Dominio (Chunks)
        chunk_mapeo = {c.text: c for c in self.todos_los_chunks}
        for c in chunks_chroma:
            chunk_mapeo[c.text] = c  # Nos aseguramos de tener indexados los metadatos de Chroma
            
        # Ordenamos de mayor a menor puntuación RRF
        documentos_ordenados = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        resultados_finales = []
        for text, score_rrf in documentos_ordenados[:limite]:
            chunk_original = chunk_mapeo[text]
            resultados_finales.append(
                Chunk(
                    source=chunk_original.source,
                    text=chunk_original.text,
                    score=round(score_rrf, 6),  # Guardamos el score híbrido normalizado
                    chunk_id=chunk_original.chunk_id
                )
            )
        return resultados_finales
    def build_index(self, chunks: list) -> int:
        """Delega la creación del índice vectorial a Chroma."""
        return self.chroma_retriever.build_index(chunks)
            
    