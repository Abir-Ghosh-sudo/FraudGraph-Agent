from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.graphrag.documents import DocumentChunk, DocumentLoader

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: str
    source_file: str
    page: int
    offset: int
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class GraphRAGRetriever:
    """
    Retrieves relevant document chunks using vector similarity (FAISS + sentence-transformers)
    or keyword overlap fallback.

    Combines graph investigation evidence with document context for grounded LLM prompts.
    Provenance is tracked per retrieved chunk.
    """

    def __init__(
        self,
        settings: Settings,
        loader: DocumentLoader | None = None,
    ) -> None:
        self.settings = settings
        self.loader = loader or DocumentLoader(settings)
        self._index: Any = None  # faiss index
        self._chunks: list[DocumentChunk] = []
        self._embeddings_model: Any = None
        self._ready = False

    def initialize(self) -> None:
        """Load documents and build the retrieval index."""
        if self._ready:
            return

        chunks = self.loader.load_all()
        self._chunks = chunks

        if not chunks:
            logger.info("no document chunks available; retriever will return empty results")
            self._ready = True
            return

        if self.settings.embeddings_configured:
            self._build_faiss_index(chunks)
        else:
            logger.info("embeddings not configured; using keyword fallback")

        self._ready = True

    def _build_faiss_index(self, chunks: list[DocumentChunk]) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            import faiss

            model = SentenceTransformer(self.settings.embedding_model)
            self._embeddings_model = model

            texts = [c.text for c in chunks]
            embeddings = model.encode(texts, show_progress_bar=False)
            embeddings = np.array(embeddings, dtype=np.float32)

            # L2-normalize for cosine similarity
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1.0, norms)
            embeddings = embeddings / norms

            dim = embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)
            index.add(embeddings)  # type: ignore[arg-type]

            self._index = index

            logger.info(
                "FAISS index built",
                chunks=len(chunks),
                dimension=dim,
            )

        except ImportError as exc:
            logger.warning(
                "FAISS/sentence-transformers not available; falling back to keyword search",
                error=str(exc),
            )
            self._index = None
            self._embeddings_model = None

    def retrieve(
        self,
        query: str,
        *,
        graph_context: dict[str, Any] | None = None,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        """
        Retrieve relevant document chunks for the given query + graph context.

        Returns chunks with provenance metadata.
        """
        if not self._ready:
            self.initialize()

        if not self._chunks:
            return []

        k = top_k or self.settings.graphrag_top_k

        # Enrich query with graph context keywords
        enriched_query = query
        if graph_context:
            node_types = graph_context.get("node_types", [])
            edge_types = graph_context.get("edge_types", [])
            enriched_query += " " + " ".join(node_types) + " " + " ".join(edge_types)

        if self._index is not None and self._embeddings_model is not None:
            return self._faiss_retrieve(enriched_query.strip(), k)

        return self._keyword_retrieve(enriched_query.strip(), k)

    def _faiss_retrieve(self, query: str, k: int) -> list[RetrievedChunk]:
        try:
            import faiss  # noqa: F401

            query_embedding = self._embeddings_model.encode([query])
            query_embedding = np.array(query_embedding, dtype=np.float32)
            norm = np.linalg.norm(query_embedding)
            if norm > 0:
                query_embedding /= norm

            actual_k = min(k, len(self._chunks))
            scores, indices = self._index.search(query_embedding, actual_k)

            results: list[RetrievedChunk] = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self._chunks):
                    continue
                chunk = self._chunks[idx]
                results.append(
                    RetrievedChunk(
                        chunk_id=chunk.chunk_id,
                        source_file=chunk.source_file,
                        page=chunk.page,
                        offset=chunk.offset,
                        text=chunk.text,
                        score=float(score),
                        metadata={
                            **chunk.metadata,
                            "retrieval_method": "faiss",
                        },
                    )
                )
            return results

        except Exception as exc:
            logger.warning("FAISS retrieval failed; falling back to keyword", error=str(exc))
            return self._keyword_retrieve(query, k)

    def _keyword_retrieve(self, query: str, k: int) -> list[RetrievedChunk]:
        """Simple term-overlap keyword retrieval as fallback."""
        query_terms = set(query.lower().split())

        scored: list[tuple[float, DocumentChunk]] = []

        for chunk in self._chunks:
            chunk_terms = set(chunk.text.lower().split())
            overlap = len(query_terms & chunk_terms)
            if overlap == 0:
                continue
            score = overlap / max(len(query_terms), 1)
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            RetrievedChunk(
                chunk_id=c.chunk_id,
                source_file=c.source_file,
                page=c.page,
                offset=c.offset,
                text=c.text,
                score=s,
                metadata={
                    **c.metadata,
                    "retrieval_method": "keyword",
                },
            )
            for s, c in scored[:k]
        ]

    def build_context_string(
        self,
        chunks: list[RetrievedChunk],
        max_chars: int = 4000,
    ) -> str:
        """Format retrieved chunks into a context string for the LLM prompt."""
        if not chunks:
            return "(no relevant policy/regulatory documents found)"

        parts: list[str] = []
        total = 0

        for chunk in chunks:
            source = chunk.source_file.split("/")[-1].split("\\")[-1]
            snippet = f"[{source} p.{chunk.page + 1}] {chunk.text[:500]}"
            total += len(snippet)
            if total > max_chars:
                break
            parts.append(snippet)

        return "\n\n".join(parts)
