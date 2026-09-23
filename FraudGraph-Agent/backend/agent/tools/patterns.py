"""
Agent-facing fraud-pattern tools.

These wrappers expose the existing fraud pattern registry and detector to
agent nodes without duplicating pattern detection logic.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from backend.fraud.detector import FraudDetector
from backend.fraud.pattern_registry import PatternRegistry


class PatternTools:
    """Interface for fraud-pattern discovery available to the agent."""

    def __init__(
        self,
        *,
        detector: FraudDetector | None = None,
        registry: PatternRegistry | None = None,
    ) -> None:
        self.registry = registry or PatternRegistry()
        self.detector = detector or FraudDetector()

    def pattern_ids(self) -> list[str]:
        """Return registered fraud-pattern identifiers."""
        return list(self.registry.ids())

    def get_pattern(self, pattern_id: str) -> Any:
        """Retrieve a registered pattern."""
        return self.registry.require(pattern_id)

    def detect(
        self,
        data: Mapping[str, Any] | Sequence[Any],
    ) -> list[Any]:
        """Run the configured fraud detector."""
        result = self.detector.detect(data)
        return list(result or [])

    def detect_pattern(
        self,
        pattern_id: str,
        data: Mapping[str, Any] | Sequence[Any],
    ) -> Any:
        """Run one specific registered pattern."""
        pattern = self.get_pattern(pattern_id)

        for method_name in ("detect", "run", "evaluate"):
            method = getattr(pattern, method_name, None)
            if method is not None:
                return method(data)

        if callable(pattern):
            return pattern(data)

        raise TypeError(
            f"Pattern '{pattern_id}' does not expose a supported "
            "detection interface."
        )

    def summarize(
        self,
        data: Mapping[str, Any] | Sequence[Any],
    ) -> dict[str, Any]:
        """Return a compact pattern-detection summary."""
        findings = self.detect(data)

        normalized: list[Any] = []
        for finding in findings:
            if hasattr(finding, "to_dict"):
                normalized.append(finding.to_dict())
            elif hasattr(finding, "model_dump"):
                normalized.append(finding.model_dump())
            elif isinstance(finding, Mapping):
                normalized.append(dict(finding))
            else:
                normalized.append(finding)

        return {
            "pattern_count": len(normalized),
            "findings": normalized,
        }


def create_pattern_tools(
    *,
    detector: FraudDetector | None = None,
    registry: PatternRegistry | None = None,
) -> PatternTools:
    """Create the default pattern-tool collection."""
    return PatternTools(
        detector=detector,
        registry=registry,
    )