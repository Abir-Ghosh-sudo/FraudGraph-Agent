from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.fraud.detector import FraudDetector


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    if hasattr(value, "__dict__"):
        return dict(value.__dict__)

    result: dict[str, Any] = {}

    for name in (
        "pattern",
        "pattern_name",
        "name",
        "fraud_type",
        "score",
        "confidence",
        "probability",
        "description",
        "evidence_ids",
        "evidence",
        "metadata",
    ):
        if hasattr(value, name):
            result[name] = getattr(value, name)

    return result


def _normalise_finding(
    finding: Any,
    index: int,
) -> dict[str, Any]:
    data = _as_dict(finding)

    pattern = (
        data.get("pattern")
        or data.get("pattern_name")
        or data.get("name")
        or data.get("fraud_type")
        or "unknown_pattern"
    )

    score = data.get("score")

    if score is None:
        score = data.get("confidence")

    if score is None:
        score = data.get("probability")

    try:
        score = float(score) if score is not None else 0.0
    except (TypeError, ValueError):
        score = 0.0

    score = max(0.0, min(1.0, score))

    evidence_ids = data.get("evidence_ids") or []

    if not isinstance(evidence_ids, list):
        evidence_ids = [str(evidence_ids)]

    evidence_ids = [
        str(item)
        for item in evidence_ids
        if item is not None
    ]

    description = (
        data.get("description")
        or data.get("rationale")
        or data.get("message")
        or f"Pattern {pattern} was detected."
    )

    return {
        "finding_id": str(
            data.get("finding_id")
            or f"pattern-{index + 1}-{pattern}"
        ),
        "pattern": str(pattern),
        "score": score,
        "confidence": score,
        "description": str(description),
        "evidence_ids": evidence_ids,
        "metadata": (
            data.get("metadata")
            if isinstance(data.get("metadata"), dict)
            else {}
        ),
        "raw": data,
    }


def _run_detector(
    detector: Any,
    *,
    transaction: dict[str, Any],
    evidence: list[dict[str, Any]],
    state: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Support the detector APIs already used by the project.

    Existing detectors may expose:
        .detect(...)
        .run(...)
        .evaluate(...)
        __call__(...)
    """

    payload = {
        "transaction": transaction,
        "evidence": evidence,
        "state": state,
    }

    result: Any = None

    methods = (
        "detect",
        "run",
        "evaluate",
    )

    for method_name in methods:
        method = getattr(detector, method_name, None)

        if not callable(method):
            continue

        try:
            result = method(**payload)
            break
        except TypeError:
            try:
                result = method(transaction)
                break
            except TypeError:
                try:
                    result = method(payload)
                    break
                except TypeError:
                    continue

    if result is None and callable(detector):
        try:
            result = detector(**payload)
        except TypeError:
            try:
                result = detector(transaction)
            except TypeError:
                result = detector(payload)

    if result is None:
        return []

    if isinstance(result, dict):
        if isinstance(result.get("findings"), list):
            result = result["findings"]
        elif isinstance(result.get("patterns"), list):
            result = result["patterns"]
        else:
            result = [result]

    if not isinstance(result, (list, tuple, set)):
        result = [result]

    return list(result)


def _extract_detectors(
    detector: Any,
) -> list[Any]:
    """
    Extract registered detectors without assuming one particular
    PatternRegistry implementation.
    """

    if detector is None:
        return []

    # PatternRegistry-style containers.
    for attribute in (
        "detectors",
        "patterns",
        "registry",
        "registered_patterns",
    ):
        value = getattr(detector, attribute, None)

        if isinstance(value, dict):
            return list(value.values())

        if isinstance(value, (list, tuple, set)):
            return list(value)

    # A detector itself is usable.
    return [detector]


def _load_detector() -> FraudDetector | None:
    try:
        return FraudDetector()
    except Exception:
        return None


def _merge_findings(
    existing: list[dict[str, Any]],
    new_findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result = list(existing)

    seen: set[tuple[str, str]] = set()

    for finding in result:
        if not isinstance(finding, dict):
            continue

        seen.add(
            (
                str(finding.get("pattern", "")),
                str(finding.get("description", "")),
            )
        )

    for finding in new_findings:
        if not isinstance(finding, dict):
            continue

        key = (
            str(finding.get("pattern", "")),
            str(finding.get("description", "")),
        )

        if key in seen:
            continue

        result.append(finding)
        seen.add(key)

    return result


def detect_patterns(
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Detect known fraud patterns using the actual investigation context.

    Important:
    - A detected pattern is evidence, not a final fraud verdict.
    - Multiple patterns may coexist.
    - Existing graph/historical evidence is passed to detectors.
    - Detector failures do not terminate the investigation.
    """

    result = dict(state)

    result["current_stage"] = "DETECT_PATTERNS"
    result["status"] = "INVESTIGATING"

    transaction = result.get("transaction")

    if not isinstance(transaction, dict):
        result["warnings"] = [
            *list(result.get("warnings") or []),
            "Pattern detection skipped because transaction context "
            "is unavailable.",
        ]
        return result

    evidence = [
        item
        for item in (result.get("evidence") or [])
        if isinstance(item, dict)
    ]

    # Add graph and historical evidence explicitly so detectors can
    # reason over relationships and prior cases.
    graph_evidence = result.get("graph_evidence") or []
    historical_evidence = result.get("historical_evidence") or []

    if isinstance(graph_evidence, list):
        evidence.extend(
            item
            for item in graph_evidence
            if isinstance(item, dict)
        )

    if isinstance(historical_evidence, list):
        evidence.extend(
            item
            for item in historical_evidence
            if isinstance(item, dict)
        )

    detector_registry = _load_detector()

    all_findings: list[dict[str, Any]] = []
    detector_errors: list[str] = []

    if detector_registry is not None:
        detectors = _extract_detectors(detector_registry)

        for detector in detectors:
            try:
                raw_findings = _run_detector(
                    detector,
                    transaction=transaction,
                    evidence=evidence,
                    state=result,
                )

                for index, finding in enumerate(raw_findings):
                    normalised = _normalise_finding(
                        finding,
                        len(all_findings) + index,
                    )

                    all_findings.append(normalised)

            except Exception as exc:
                detector_name = type(detector).__name__

                detector_errors.append(
                    f"{detector_name}: {exc}"
                )

    # ------------------------------------------------------------------
    # Existing findings may have been produced by another stage.
    # Preserve them.
    # ------------------------------------------------------------------
    existing_findings = [
        item
        for item in (
            result.get("pattern_findings")
            or result.get("patterns")
            or result.get("fraud_findings")
            or []
        )
        if isinstance(item, dict)
    ]

    merged_findings = _merge_findings(
        existing_findings,
        all_findings,
    )

    result["pattern_findings"] = merged_findings
    result["patterns"] = merged_findings
    result["fraud_findings"] = merged_findings

    # ------------------------------------------------------------------
    # Primary pattern = strongest detected pattern.
    # ------------------------------------------------------------------
    strongest = max(
        merged_findings,
        key=lambda item: float(
            item.get("score")
            or item.get("confidence")
            or 0.0
        ),
        default=None,
    )

    if strongest:
        result["fraud_type"] = strongest.get(
            "pattern"
        )

    # ------------------------------------------------------------------
    # Pattern score is the strongest pattern signal, not a sum.
    # Summing would artificially inflate risk when several detectors
    # describe the same underlying event.
    # ------------------------------------------------------------------
    pattern_score = max(
        (
            float(
                item.get("score")
                or item.get("confidence")
                or 0.0
            )
            for item in merged_findings
            if isinstance(item, dict)
        ),
        default=0.0,
    )

    pattern_score = max(
        0.0,
        min(1.0, pattern_score),
    )

    result["pattern_score"] = pattern_score

    if detector_errors:
        result["pattern_detector_errors"] = detector_errors

        warnings = list(
            result.get("warnings") or []
        )

        warnings.append(
            f"{len(detector_errors)} fraud pattern detector(s) "
            "failed during this stage."
        )

        result["warnings"] = warnings

    # ------------------------------------------------------------------
    # Event
    # ------------------------------------------------------------------
    now = _utc_now()

    events = list(result.get("events") or [])

    events.append(
        {
            "event_id": (
                f"patterns-"
                f"{result.get('transaction_id') or 'unknown'}-"
                f"{now}"
            ),
            "event_type": "PATTERN_DETECTED",
            "investigation_id": result.get(
                "investigation_id"
            ),
            "case_id": result.get("case_id"),
            "stage": "DETECT_PATTERNS",
            "message": (
                f"Detected {len(merged_findings)} fraud pattern "
                f"finding(s)."
            ),
            "payload": {
                "transaction_id": result.get(
                    "transaction_id"
                ),
                "pattern_count": len(
                    merged_findings
                ),
                "pattern_score": pattern_score,
                "primary_pattern": (
                    result.get("fraud_type")
                ),
                "detector_errors": len(
                    detector_errors
                ),
            },
            "created_at": now,
        }
    )

    result["events"] = events

    result["progress"] = max(
        float(result.get("progress") or 0.0),
        0.45,
    )

    return result


def run(
    state: dict[str, Any],
) -> dict[str, Any]:
    return detect_patterns(state)


class DetectPatternsNode:
    """LangGraph adapter for the existing pattern-detection function."""

    def __init__(self, settings: Any) -> None:
        self.settings = settings

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        return detect_patterns(state)
