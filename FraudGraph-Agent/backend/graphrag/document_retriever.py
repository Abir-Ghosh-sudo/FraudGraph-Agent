from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence


@dataclass(slots=True)
class DocumentMatch:
    """A document retrieved as supporting investigation context."""

    document_id: str
    title: str | None = None
    content: str = ""
    score: float = 0.0
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "content": self.content,
            "score": self.score,
            "source": self.source,
            "metadata": dict(self.metadata),
        }


class DocumentRetriever:
    """
    Lightweight document retriever for GraphRAG.

    The retriever intentionally keeps storage/vector-search concerns outside
    this layer. A repository, vector store, or search backend can be supplied
    through `documents` or through the optional search callable.
    """

    def __init__(
        self,
        documents: Iterable[Mapping[str, Any]] | None = None,
        search_fn: Any | None = None,
    ) -> None:
        self._documents: list[dict[str, Any]] = [
            dict(document) for document in (documents or [])
        ]
        self._search_fn = search_fn

    def add(self, document: Mapping[str, Any]) -> DocumentMatch:
        """Add or replace a document by its identifier."""

        normalized = self._normalize(document)
        document_id = normalized.document_id

        self._documents = [
            item
            for item in self._documents
            if str(item.get("document_id", item.get("id", ""))) != document_id
        ]
        self._documents.append(normalized.to_dict())
        return normalized

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: Mapping[str, Any] | None = None,
    ) -> list[DocumentMatch]:
        """
        Retrieve documents relevant to a query.

        If an external search function is configured, its results are
        normalized into DocumentMatch objects. Otherwise a deterministic
        lexical fallback is used, which keeps local development and tests
        functional without requiring a vector database.
        """

        query = str(query or "").strip()
        if not query or top_k <= 0:
            return []

        if self._search_fn is not None:
            results = self._search_external(query, top_k, filters)
            if results:
                return results[:top_k]

        candidates = self._apply_filters(self._documents, filters)
        query_terms = self._tokenize(query)

        scored: list[DocumentMatch] = []
        for document in candidates:
            match = self._normalize(document)
            score = self._lexical_score(query_terms, match)

            if score > 0:
                match.score = score
                scored.append(match)

        scored.sort(
            key=lambda item: (-item.score, item.document_id),
        )

        return scored[:top_k]

    def retrieve_many(
        self,
        queries: Sequence[str],
        *,
        top_k: int = 5,
        filters: Mapping[str, Any] | None = None,
    ) -> list[DocumentMatch]:
        """Retrieve and deduplicate results across multiple queries."""

        merged: dict[str, DocumentMatch] = {}

        for query in queries:
            for match in self.retrieve(
                query,
                top_k=top_k,
                filters=filters,
            ):
                existing = merged.get(match.document_id)
                if existing is None or match.score > existing.score:
                    merged[match.document_id] = match

        return sorted(
            merged.values(),
            key=lambda item: (-item.score, item.document_id),
        )[:top_k]

    def _search_external(
        self,
        query: str,
        top_k: int,
        filters: Mapping[str, Any] | None,
    ) -> list[DocumentMatch]:
        try:
            result = self._search_fn(
                query=query,
                top_k=top_k,
                filters=filters,
            )
        except TypeError:
            try:
                result = self._search_fn(query, top_k)
            except Exception:
                return []
        except Exception:
            return []

        if result is None:
            return []

        if isinstance(result, Mapping):
            result = result.get("results", result.get("documents", []))

        if isinstance(result, DocumentMatch):
            result = [result]

        if not isinstance(result, Iterable) or isinstance(
            result,
            (str, bytes),
        ):
            return []

        matches: list[DocumentMatch] = []
        for item in result:
            if isinstance(item, DocumentMatch):
                matches.append(item)
            elif isinstance(item, Mapping):
                matches.append(self._normalize(item))

        matches.sort(
            key=lambda item: (-item.score, item.document_id),
        )
        return matches

    @staticmethod
    def _normalize(document: Mapping[str, Any]) -> DocumentMatch:
        document_id = (
            document.get("document_id")
            or document.get("id")
            or document.get("chunk_id")
        )

        if document_id is None:
            raise ValueError("Document must contain document_id or id")

        content = (
            document.get("content")
            or document.get("text")
            or document.get("page_content")
            or ""
        )

        metadata = document.get("metadata")
        if not isinstance(metadata, Mapping):
            metadata = {}

        title = document.get("title") or document.get("name")
        source = document.get("source") or document.get("url")

        score = document.get("score", document.get("similarity", 0.0))
        try:
            score = float(score or 0.0)
        except (TypeError, ValueError):
            score = 0.0

        return DocumentMatch(
            document_id=str(document_id),
            title=str(title) if title is not None else None,
            content=str(content),
            score=max(0.0, min(1.0, score)),
            source=str(source) if source is not None else None,
            metadata=dict(metadata),
        )

    @staticmethod
    def _apply_filters(
        documents: Iterable[Mapping[str, Any]],
        filters: Mapping[str, Any] | None,
    ) -> list[Mapping[str, Any]]:
        if not filters:
            return list(documents)

        result: list[Mapping[str, Any]] = []

        for document in documents:
            metadata = document.get("metadata", {})
            if not isinstance(metadata, Mapping):
                metadata = {}

            matches = True
            for key, expected in filters.items():
                actual = document.get(key, metadata.get(key))

                if isinstance(expected, (list, tuple, set, frozenset)):
                    if actual not in expected:
                        matches = False
                        break
                elif actual != expected:
                    matches = False
                    break

            if matches:
                result.append(document)

        return result

    @staticmethod
    def _tokenize(value: str) -> set[str]:
        return {
            token
            for token in "".join(
                character.lower()
                if character.isalnum()
                else " "
                for character in value
            ).split()
            if len(token) > 1
        }

    @classmethod
    def _lexical_score(
        cls,
        query_terms: set[str],
        document: DocumentMatch,
    ) -> float:
        if not query_terms:
            return 0.0

        searchable = " ".join(
            part
            for part in (
                document.title or "",
                document.content,
                document.source or "",
                " ".join(
                    str(value) for value in document.metadata.values()
                ),
            )
            if part
        )

        document_terms = cls._tokenize(searchable)
        if not document_terms:
            return 0.0

        overlap = query_terms.intersection(document_terms)
        return len(overlap) / len(query_terms)