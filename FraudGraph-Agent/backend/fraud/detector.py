"""
Fraud detection orchestration.

Combines registered fraud-pattern detectors with the available
transaction/investigation context and returns normalized findings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(slots=True)
class FraudFinding:
    """A normalized fraud-pattern finding."""

    pattern_id: str
    pattern_name: str
    detected: bool
    confidence: float = 0.0
    severity: str = "medium"
    rationale: str | None = None
    evidence_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.confidence = max(0.0, min(1.0, float(self.confidence)))
        self.evidence_ids = list(dict.fromkeys(self.evidence_ids))


class FraudDetector:
    """
    Orchestrates fraud-pattern detection.

    Pattern implementations are intentionally duck-typed so this class
    can work with both the current project skeleton and future pattern
    implementations without coupling the detector to one interface.
    """

    def __init__(
        self,
        patterns: Sequence[Any] | None = None,
        *,
        min_confidence: float = 0.0,
    ) -> None:
        self.patterns = list(patterns or [])
        self.min_confidence = max(0.0, min(1.0, float(min_confidence)))

    def register(self, pattern: Any) -> None:
        """Register a pattern detector if it is not already registered."""
        if pattern not in self.patterns:
            self.patterns.append(pattern)

    def detect(
        self,
        context: Mapping[str, Any] | None = None,
        *,
        transaction: Mapping[str, Any] | None = None,
        evidence: Sequence[Any] | None = None,
    ) -> list[FraudFinding]:
        """
        Run all registered patterns and normalize their results.

        Pattern implementations may expose one of:
        - detect(context)
        - detect(**context)
        - run(context)
        - evaluate(context)
        """
        payload: dict[str, Any] = dict(context or {})

        if transaction is not None:
            payload["transaction"] = transaction

        if evidence is not None:
            payload["evidence"] = list(evidence)

        findings: list[FraudFinding] = []

        for pattern in self.patterns:
            result = self._run_pattern(pattern, payload)

            for item in self._normalize_results(pattern, result):
                if item.detected and item.confidence >= self.min_confidence:
                    findings.append(item)

        return findings

    def detect_one(
        self,
        pattern: Any,
        context: Mapping[str, Any] | None = None,
    ) -> FraudFinding | None:
        """Run a single pattern detector."""
        payload = dict(context or {})
        result = self._run_pattern(pattern, payload)
        normalized = self._normalize_results(pattern, result)

        for finding in normalized:
            if finding.detected and finding.confidence >= self.min_confidence:
                return finding

        return None

    @staticmethod
    def _run_pattern(
        pattern: Any,
        context: Mapping[str, Any],
    ) -> Any:
        """Execute a pattern using the first supported interface."""
        detector = getattr(pattern, "detect", None)
        if callable(detector):
            return detector(context)

        runner = getattr(pattern, "run", None)
        if callable(runner):
            return runner(context)

        evaluator = getattr(pattern, "evaluate", None)
        if callable(evaluator):
            return evaluator(context)

        if callable(pattern):
            return pattern(context)

        raise TypeError(
            f"Unsupported fraud pattern type: {type(pattern).__name__}"
        )

    @staticmethod
    def _normalize_results(
        pattern: Any,
        result: Any,
    ) -> list[FraudFinding]:
        """Convert pattern output into FraudFinding objects."""
        if result is None:
            return []

        if isinstance(result, (list, tuple, set)):
            findings: list[FraudFinding] = []
            for item in result:
                finding = FraudDetector._normalize_result(pattern, item)
                if finding is not None:
                    findings.append(finding)
            return findings

        finding = FraudDetector._normalize_result(pattern, result)
        return [finding] if finding is not None else []

    @staticmethod
    def _normalize_result(
        pattern: Any,
        result: Any,
    ) -> FraudFinding | None:
        """Normalize one pattern result."""
        if isinstance(result, FraudFinding):
            return result

        pattern_id = str(
            getattr(pattern, "pattern_id", None)
            or getattr(pattern, "id", None)
            or pattern.__class__.__name__
        )

        pattern_name = str(
            getattr(pattern, "pattern_name", None)
            or getattr(pattern, "name", None)
            or pattern.__class__.__name__
        )

        if isinstance(result, Mapping):
            detected = bool(
                result.get(
                    "detected",
                    result.get("is_fraud", result.get("match", False)),
                )
            )

            confidence = float(result.get("confidence", 0.0) or 0.0)
            severity = str(result.get("severity", "medium"))
            rationale = result.get("rationale") or result.get("reason")

            evidence_ids = result.get("evidence_ids", [])
            if isinstance(evidence_ids, str):
                evidence_ids = [evidence_ids]

            return FraudFinding(
                pattern_id=str(result.get("pattern_id", pattern_id)),
                pattern_name=str(result.get("pattern_name", pattern_name)),
                detected=detected,
                confidence=confidence,
                severity=severity,
                rationale=str(rationale) if rationale is not None else None,
                evidence_ids=list(evidence_ids or []),
                metadata=dict(result.get("metadata", {}) or {}),
            )

        if isinstance(result, bool):
            return FraudFinding(
                pattern_id=pattern_id,
                pattern_name=pattern_name,
                detected=result,
                confidence=1.0 if result else 0.0,
            )

        return None

    @staticmethod
    def summarize(findings: Sequence[FraudFinding]) -> dict[str, Any]:
        """Create a compact summary suitable for agent state."""
        detected = [finding for finding in findings if finding.detected]

        max_confidence = max(
            (finding.confidence for finding in detected),
            default=0.0,
        )

        severity_order = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }

        highest_severity = "low"
        if detected:
            highest_severity = max(
                (finding.severity.lower() for finding in detected),
                key=lambda value: severity_order.get(value, 0),
            )

        return {
            "detected": bool(detected),
            "pattern_count": len(detected),
            "max_confidence": max_confidence,
            "highest_severity": highest_severity,
            "pattern_ids": [finding.pattern_id for finding in detected],
            "evidence_ids": list(
                dict.fromkeys(
                    evidence_id
                    for finding in detected
                    for evidence_id in finding.evidence_ids
                )
            ),
        }