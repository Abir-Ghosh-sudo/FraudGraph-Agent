from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from backend.graphrag.document_retriever import (
    DocumentMatch,
    DocumentRetriever,
)
from backend.graphrag.graph_retriever import (
    GraphMatch,
    GraphRetriever,
)


@dataclass(slots=True)
class HybridMatch:
    """Unified GraphRAG retrieval result."""

    result_id: str
    result_type: str
    score: float
    title: str | None = None
    content: str = ""
    node_id: str | None = None
    node_type: str | None = None
    source: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    paths: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "result_type": self.result_type,
            "score": self.score,
            "title": self.title,
            "content": self.content,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "source": self.source,
            "properties": dict(self.properties),
            "metadata": dict(self.metadata),
            "paths": list(self.paths),
        }


class HybridRetriever:
    """
    Combines graph and document retrieval for GraphRAG.

    The retriever keeps the two retrieval mechanisms independent and merges
    their normalized results using configurable weights.
    """

    def __init__(
        self,
        graph_retriever: GraphRetriever | None = None,
        document_retriever: DocumentRetriever | None = None,
        *,
        graph_weight: float = 0.6,
        document_weight: float = 0.4,
    ) -> None:
        if graph_weight < 0 or document_weight < 0:
            raise ValueError("Retrieval weights cannot be negative")

        if graph_weight == 0 and document_weight == 0:
            raise ValueError(
                "At least one retrieval weight must be greater than zero"
            )

        self.graph_retriever = graph_retriever or GraphRetriever()
        self.document_retriever = document_retriever or DocumentRetriever()

        total = graph_weight + document_weight
        self.graph_weight = graph_weight / total
        self.document_weight = document_weight / total

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 10,
        node_id: str | None = None,
        node_type: str | None = None,
        depth: int = 2,
        filters: Mapping[str, Any] | None = None,
    ) -> list[HybridMatch]:
        """
        Retrieve graph and document context, then merge and rank it.
        """

        if not query or top_k <= 0:
            return []

        graph_results = self.graph_retriever.retrieve(
            query,
            node_id=node_id,
            node_type=node_type,
            top_k=top_k,
            depth=depth,
            filters=filters,
        )

        document_results = self.document_retriever.retrieve(
            query,
            top_k=top_k,
            filters=filters,
        )

        return self._merge(
            graph_results=graph_results,
            document_results=document_results,
            top_k=top_k,
        )

    def retrieve_many(
        self,
        queries: Sequence[str],
        *,
        top_k: int = 10,
        node_id: str | None = None,
        node_type: str | None = None,
        depth: int = 2,
        filters: Mapping[str, Any] | None = None,
    ) -> list[HybridMatch]:
        """Retrieve and merge context for multiple investigation queries."""

        if not queries or top_k <= 0:
            return []

        merged: dict[str, HybridMatch] = {}

        for query in queries:
            for match in self.retrieve(
                query,
                top_k=top_k,
                node_id=node_id,
                node_type=node_type,
                depth=depth,
                filters=filters,
            ):
                existing = merged.get(match.result_id)

                if existing is None or match.score > existing.score:
                    merged[match.result_id] = match

        return sorted(
            merged.values(),
            key=lambda item: (-item.score, item.result_id),
        )[:top_k]

    def retrieve_case_context(
        self,
        *,
        case_id: str,
        query: str | None = None,
        top_k: int = 10,
        depth: int = 2,
    ) -> list[HybridMatch]:
        """
        Retrieve context centered around a case.

        This is useful when the investigation starts from an existing
        fraud case rather than directly from a transaction.
        """

        effective_query = query or case_id

        return self.retrieve(
            effective_query,
            top_k=top_k,
            node_id=case_id,
            depth=depth,
        )

    def retrieve_entity_context(
        self,
        *,
        entity_id: str,
        query: str | None = None,
        node_type: str | None = None,
        top_k: int = 10,
        depth: int = 2,
    ) -> list[HybridMatch]:
        """Retrieve graph/document context around an entity."""

        effective_query = query or entity_id

        return self.retrieve(
            effective_query,
            top_k=top_k,
            node_id=entity_id,
            node_type=node_type,
            depth=depth,
        )

    def _merge(
        self,
        *,
        graph_results: Sequence[GraphMatch],
        document_results: Sequence[DocumentMatch],
        top_k: int,
    ) -> list[HybridMatch]:
        merged: dict[str, HybridMatch] = {}

        for graph in graph_results:
            normalized_score = self._normalize_score(graph.score)

            result = HybridMatch(
                result_id=f"graph:{graph.node_id}",
                result_type="graph",
                score=normalized_score * self.graph_weight,
                title=graph.label,
                content=self._graph_content(graph),
                node_id=graph.node_id,
                node_type=graph.node_type,
                properties=dict(graph.properties),
                paths=list(graph.paths),
            )

            self._merge_result(merged, result)

        for document in document_results:
            normalized_score = self._normalize_score(document.score)

            result = HybridMatch(
                result_id=f"document:{document.document_id}",
                result_type="document",
                score=normalized_score * self.document_weight,
                title=document.title,
                content=document.content,
                source=document.source,
                metadata=dict(document.metadata),
            )

            self._merge_result(merged, result)

        results = sorted(
            merged.values(),
            key=lambda item: (-item.score, item.result_id),
        )

        return results[:top_k]

    @staticmethod
    def _merge_result(
        merged: dict[str, HybridMatch],
        result: HybridMatch,
    ) -> None:
        existing = merged.get(result.result_id)

        if existing is None:
            merged[result.result_id] = result
            return

        if result.score > existing.score:
            merged[result.result_id] = result

    @staticmethod
    def _normalize_score(score: float) -> float:
        try:
            value = float(score)
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, min(1.0, value))

    @staticmethod
    def _graph_content(graph: GraphMatch) -> str:
        parts: list[str] = []

        if graph.label:
            parts.append(graph.label)

        if graph.node_type:
            parts.append(f"Type: {graph.node_type}")

        if graph.properties:
            properties = ", ".join(
                f"{key}={value}"
                for key, value in graph.properties.items()
            )
            parts.append(properties)

        if graph.paths:
            parts.append(
                f"Related relationships: {len(graph.paths)}"
            )

        return " | ".join(parts)