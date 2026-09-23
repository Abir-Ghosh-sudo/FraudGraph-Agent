"""
Registry for fraud-pattern detectors.

The registry keeps pattern discovery separate from the fraud detector
orchestration layer.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any


class PatternRegistry:
    """Register, retrieve, and manage fraud-pattern implementations."""

    def __init__(self, patterns: Iterable[Any] | None = None) -> None:
        self._patterns: dict[str, Any] = {}

        for pattern in patterns or []:
            self.register(pattern)

    def register(self, pattern: Any) -> str:
        """
        Register a pattern and return its identifier.

        A pattern must expose ``pattern_id`` or ``id``. If neither is
        available, its class name is used as a stable local identifier.
        """
        pattern_id = self._get_pattern_id(pattern)
        self._patterns[pattern_id] = pattern
        return pattern_id

    def unregister(self, pattern_id: str) -> Any | None:
        """Remove and return a registered pattern."""
        return self._patterns.pop(pattern_id, None)

    def get(self, pattern_id: str) -> Any | None:
        """Return a pattern by identifier."""
        return self._patterns.get(pattern_id)

    def require(self, pattern_id: str) -> Any:
        """Return a pattern or raise KeyError if it is not registered."""
        pattern = self.get(pattern_id)

        if pattern is None:
            raise KeyError(f"Fraud pattern not registered: {pattern_id}")

        return pattern

    def contains(self, pattern_id: str) -> bool:
        """Return whether a pattern is registered."""
        return pattern_id in self._patterns

    def clear(self) -> None:
        """Remove all registered patterns."""
        self._patterns.clear()

    def ids(self) -> list[str]:
        """Return registered pattern identifiers."""
        return list(self._patterns.keys())

    def values(self) -> list[Any]:
        """Return registered pattern implementations."""
        return list(self._patterns.values())

    def items(self) -> list[tuple[str, Any]]:
        """Return registered pattern identifier/implementation pairs."""
        return list(self._patterns.items())

    def __len__(self) -> int:
        return len(self._patterns)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._patterns.values())

    @staticmethod
    def _get_pattern_id(pattern: Any) -> str:
        """Resolve the identifier used by the registry."""
        pattern_id = getattr(pattern, "pattern_id", None)

        if pattern_id is None:
            pattern_id = getattr(pattern, "id", None)

        if pattern_id is None:
            pattern_id = pattern.__class__.__name__

        pattern_id = str(pattern_id).strip()

        if not pattern_id:
            raise ValueError("Fraud pattern identifier cannot be empty.")

        return pattern_id