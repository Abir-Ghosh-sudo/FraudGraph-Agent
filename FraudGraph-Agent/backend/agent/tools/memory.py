"""
Agent-facing tools for case memory.

These wrappers expose existing memory components to the agent for retrieving
similar historical investigations and recording investigation outcomes.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from backend.memory.outcomes import OutcomeStore
from backend.memory.retrieval import MemoryRetriever
from backend.memory.similarity import CaseSimilarity
from backend.memory.writer import MemoryWriter


class MemoryTools:
    """Interface for historical case-memory operations."""

    def __init__(
        self,
        *,
        retriever: MemoryRetriever | None = None,
        similarity: CaseSimilarity | None = None,
        outcomes: OutcomeStore | None = None,
        writer: MemoryWriter | None = None,
    ) -> None:
        self.retriever = retriever or MemoryRetriever()
        self.similarity = similarity or CaseSimilarity()
        self.outcomes = outcomes or OutcomeStore()
        self.writer = writer or MemoryWriter()

    def retrieve(
        self,
        query: Any,
        *,
        limit: int = 5,
    ) -> list[Any]:
        """Retrieve relevant historical case memories."""
        for method_name in ("retrieve", "search", "find"):
            method = getattr(self.retriever, method_name, None)
            if method is not None:
                result = method(query, limit=limit)
                return list(result or [])

        raise AttributeError(
            "MemoryRetriever does not expose a supported retrieval method."
        )

    def similar_cases(
        self,
        case: Any,
        candidates: Sequence[Any],
        *,
        limit: int = 5,
    ) -> list[Any]:
        """Find cases structurally similar to the current investigation."""
        for method_name in ("find_similar", "similar", "compare"):
            method = getattr(self.similarity, method_name, None)
            if method is not None:
                result = method(
                    case,
                    candidates,
                    limit=limit,
                )
                return list(result or [])

        raise AttributeError(
            "CaseSimilarity does not expose a supported comparison method."
        )

    def record_outcome(self, outcome: Any) -> Any:
        """Store an investigation outcome."""
        for method_name in ("record", "add", "store"):
            method = getattr(self.outcomes, method_name, None)
            if method is not None:
                return method(outcome)

        raise AttributeError(
            "OutcomeStore does not expose a supported write method."
        )

    def write_memory(
        self,
        case_id: str,
        memory: Mapping[str, Any],
    ) -> Any:
        """Persist a case-memory record through the existing writer."""
        for method_name in ("write", "record", "store"):
            method = getattr(self.writer, method_name, None)
            if method is not None:
                try:
                    return method(case_id, memory)
                except TypeError:
                    return method(memory)

        raise AttributeError(
            "MemoryWriter does not expose a supported write method."
        )

    def summary(
        self,
        query: Any,
        *,
        limit: int = 5,
    ) -> dict[str, Any]:
        """Return a compact memory-retrieval result for agent reasoning."""
        matches = self.retrieve(query, limit=limit)

        return {
            "match_count": len(matches),
            "matches": [
                (
                    item.model_dump()
                    if hasattr(item, "model_dump")
                    else item.to_dict()
                    if hasattr(item, "to_dict")
                    else item
                )
                for item in matches
            ],
        }


def create_memory_tools(
    *,
    retriever: MemoryRetriever | None = None,
    similarity: CaseSimilarity | None = None,
    outcomes: OutcomeStore | None = None,
    writer: MemoryWriter | None = None,
) -> MemoryTools:
    """Create the default memory-tool collection."""
    return MemoryTools(
        retriever=retriever,
        similarity=similarity,
        outcomes=outcomes,
        writer=writer,
    )