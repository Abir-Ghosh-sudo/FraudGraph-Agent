from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class GraphRAGContext:
    """Structured context assembled from retrieved investigation evidence."""

    query: str
    graph_context: tuple[Mapping[str, Any], ...] = ()
    document_context: tuple[Mapping[str, Any], ...] = ()
    case_context: tuple[Mapping[str, Any], ...] = ()
    evidence_context: tuple[Mapping[str, Any], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def item_count(self) -> int:
        return (
            len(self.graph_context)
            + len(self.document_context)
            + len(self.case_context)
            + len(self.evidence_context)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "graph_context": [
                dict(item) for item in self.graph_context
            ],
            "document_context": [
                dict(item) for item in self.document_context
            ],
            "case_context": [
                dict(item) for item in self.case_context
            ],
            "evidence_context": [
                dict(item) for item in self.evidence_context
            ],
            "metadata": dict(self.metadata),
            "item_count": self.item_count,
        }

    def as_text(self) -> str:
        sections: list[str] = []

        self._append_section(
            sections,
            "GRAPH CONTEXT",
            self.graph_context,
        )
        self._append_section(
            sections,
            "DOCUMENT CONTEXT",
            self.document_context,
        )
        self._append_section(
            sections,
            "CASE MEMORY",
            self.case_context,
        )
        self._append_section(
            sections,
            "EVIDENCE",
            self.evidence_context,
        )

        return "\n\n".join(sections)

    @staticmethod
    def _append_section(
        sections: list[str],
        title: str,
        items: Iterable[Mapping[str, Any]],
    ) -> None:
        values = list(items)

        if not values:
            return

        lines = [f"## {title}"]

        for index, item in enumerate(values, start=1):
            lines.append(
                f"{index}. {GraphRAGContext._format_item(item)}"
            )

        sections.append("\n".join(lines))

    @staticmethod
    def _format_item(
        item: Mapping[str, Any],
    ) -> str:
        parts: list[str] = []

        for key, value in item.items():
            if value is None:
                continue

            if isinstance(value, (dict, list, tuple, set)):
                value = str(value)

            parts.append(f"{key}: {value}")

        return "; ".join(parts)


class ContextBuilder:
    """Build investigation context from GraphRAG retrieval results."""

    def build(
        self,
        *,
        query: str,
        graph_results: Iterable[Any] | None = None,
        document_results: Iterable[Any] | None = None,
        case_results: Iterable[Any] | None = None,
        evidence_results: Iterable[Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> GraphRAGContext:
        return GraphRAGContext(
            query=query.strip(),
            graph_context=self._normalise_results(
                graph_results
            ),
            document_context=self._normalise_results(
                document_results
            ),
            case_context=self._normalise_results(
                case_results
            ),
            evidence_context=self._normalise_results(
                evidence_results
            ),
            metadata=dict(metadata or {}),
        )

    def add_graph_results(
        self,
        context: GraphRAGContext,
        results: Iterable[Any],
    ) -> GraphRAGContext:
        return self._replace(
            context,
            graph_context=(
                *context.graph_context,
                *self._normalise_results(results),
            ),
        )

    def add_document_results(
        self,
        context: GraphRAGContext,
        results: Iterable[Any],
    ) -> GraphRAGContext:
        return self._replace(
            context,
            document_context=(
                *context.document_context,
                *self._normalise_results(results),
            ),
        )

    def add_case_results(
        self,
        context: GraphRAGContext,
        results: Iterable[Any],
    ) -> GraphRAGContext:
        return self._replace(
            context,
            case_context=(
                *context.case_context,
                *self._normalise_results(results),
            ),
        )

    def add_evidence_results(
        self,
        context: GraphRAGContext,
        results: Iterable[Any],
    ) -> GraphRAGContext:
        return self._replace(
            context,
            evidence_context=(
                *context.evidence_context,
                *self._normalise_results(results),
            ),
        )

    def deduplicate(
        self,
        context: GraphRAGContext,
    ) -> GraphRAGContext:
        return self._replace(
            context,
            graph_context=self._deduplicate(
                context.graph_context
            ),
            document_context=self._deduplicate(
                context.document_context
            ),
            case_context=self._deduplicate(
                context.case_context
            ),
            evidence_context=self._deduplicate(
                context.evidence_context
            ),
        )

    def _replace(
        self,
        context: GraphRAGContext,
        *,
        graph_context: tuple[Mapping[str, Any], ...]
        | None = None,
        document_context: tuple[Mapping[str, Any], ...]
        | None = None,
        case_context: tuple[Mapping[str, Any], ...]
        | None = None,
        evidence_context: tuple[Mapping[str, Any], ...]
        | None = None,
    ) -> GraphRAGContext:
        return GraphRAGContext(
            query=context.query,
            graph_context=(
                graph_context
                if graph_context is not None
                else context.graph_context
            ),
            document_context=(
                document_context
                if document_context is not None
                else context.document_context
            ),
            case_context=(
                case_context
                if case_context is not None
                else context.case_context
            ),
            evidence_context=(
                evidence_context
                if evidence_context is not None
                else context.evidence_context
            ),
            metadata=dict(context.metadata),
        )

    def _normalise_results(
        self,
        results: Iterable[Any] | None,
    ) -> tuple[Mapping[str, Any], ...]:
        if results is None:
            return ()

        normalised: list[Mapping[str, Any]] = []

        for result in results:
            value = self._normalise_item(result)

            if value:
                normalised.append(value)

        return tuple(normalised)

    def _normalise_item(
        self,
        value: Any,
    ) -> Mapping[str, Any] | None:
        if value is None:
            return None

        if isinstance(value, Mapping):
            return dict(value)

        if hasattr(value, "model_dump"):
            dumped = value.model_dump()
            if isinstance(dumped, Mapping):
                return dict(dumped)

        if hasattr(value, "to_dict"):
            dumped = value.to_dict()
            if isinstance(dumped, Mapping):
                return dict(dumped)

        if hasattr(value, "__dict__"):
            return {
                str(key): item
                for key, item in vars(value).items()
                if not key.startswith("_")
            }

        return {"value": value}

    def _deduplicate(
        self,
        items: Iterable[Mapping[str, Any]],
    ) -> tuple[Mapping[str, Any], ...]:
        seen: set[str] = set()
        result: list[Mapping[str, Any]] = []

        for item in items:
            key = self._identity(item)

            if key in seen:
                continue

            seen.add(key)
            result.append(item)

        return tuple(result)

    def _identity(
        self,
        item: Mapping[str, Any],
    ) -> str:
        for key in (
            "id",
            "node_id",
            "document_id",
            "case_id",
            "evidence_id",
            "chunk_id",
            "edge_id",
        ):
            value = item.get(key)

            if value is not None:
                return f"{key}:{value}"

        return repr(sorted(item.items(), key=lambda pair: pair[0]))