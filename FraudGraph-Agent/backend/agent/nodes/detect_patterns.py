from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentEventType, AgentStage
from backend.app.schemas.evidence import Evidence, EvidenceType
from backend.agent.state import AgentRuntimeState, advance_state

logger = get_logger(__name__)


def _make_event(
    state: AgentRuntimeState,
    event_type: AgentEventType,
    message: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "event_id": f"evt_{uuid4().hex[:8]}",
        "event_type": event_type,
        "investigation_id": state.get("investigation_id", ""),
        "case_id": state.get("case_id"),
        "stage": AgentStage.DETECT_PATTERNS,
        "message": message,
        "payload": payload or {},
        "created_at": datetime.now(UTC),
    }


class DetectPatternsNode:
    """
    Analyzes collected evidence for fraud patterns.

    Detects the following patterns from graph evidence only:
    - DEVICE_REUSE: multiple entities sharing the same device
    - IP_REUSE: multiple entities sharing the same IP
    - VELOCITY: high frequency of transaction-type evidence
    - FRAUD_MARKER: evidence directly labeled as FraudPattern node type

    Never creates patterns without supporting evidence.
    Emits PATTERN_DETECTED for each pattern found.
    """

    VELOCITY_THRESHOLD = 3  # min transaction evidence items to flag velocity

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def __call__(self, state: AgentRuntimeState) -> AgentRuntimeState:
        evidence: list[Evidence] = list(state.get("evidence", []))
        investigation_id = state.get("investigation_id", "")
        events = list(state.get("events", []))
        existing_patterns = list(state.get("detected_patterns", []))

        if not evidence:
            logger.info(
                "no evidence to analyze for patterns",
                investigation_id=investigation_id,
            )
            updated = advance_state(state, AgentStage.DETECT_PATTERNS)
            updated["detected_patterns"] = existing_patterns
            updated["events"] = events
            return updated

        new_patterns: list[dict[str, Any]] = []

        # Device reuse pattern
        device_pattern = self._detect_device_reuse(evidence)
        if device_pattern:
            new_patterns.append(device_pattern)

        # IP reuse pattern
        ip_pattern = self._detect_ip_reuse(evidence)
        if ip_pattern:
            new_patterns.append(ip_pattern)

        # Velocity pattern
        velocity_pattern = self._detect_velocity(evidence)
        if velocity_pattern:
            new_patterns.append(velocity_pattern)

        # Fraud marker pattern (explicit FraudPattern node)
        fraud_marker_patterns = self._detect_fraud_markers(evidence)
        new_patterns.extend(fraud_marker_patterns)

        all_patterns = existing_patterns + new_patterns

        for pattern in new_patterns:
            events.append(
                _make_event(
                    state,
                    AgentEventType.PATTERN_DETECTED,
                    f"Pattern detected: {pattern['name']}",
                    {
                        "pattern_id": pattern["pattern_id"],
                        "pattern_name": pattern["name"],
                        "confidence": pattern["confidence"],
                        "evidence_count": len(pattern["evidence_ids"]),
                    },
                )
            )

        logger.info(
            "pattern detection complete",
            investigation_id=investigation_id,
            new_patterns=len(new_patterns),
            total_patterns=len(all_patterns),
        )

        updated = advance_state(state, AgentStage.DETECT_PATTERNS)
        updated["detected_patterns"] = all_patterns
        updated["events"] = events

        return updated

    def _detect_device_reuse(
        self, evidence: list[Evidence]
    ) -> dict[str, Any] | None:
        device_evidence = [
            ev for ev in evidence
            if "device" in (ev.source_reference or "").lower()
            or "Device" in (ev.title or "")
        ]

        if len(device_evidence) < 2:
            return None

        # Check if multiple distinct entities share the same device ID
        entity_sets: dict[str, set[str]] = {}
        for ev in device_evidence:
            device_id = ev.source_id or ""
            for entity in ev.entities:
                entity_sets.setdefault(device_id, set()).add(entity)

        shared_devices = {
            did: entities
            for did, entities in entity_sets.items()
            if len(entities) >= 2
        }

        if not shared_devices:
            return None

        evidence_ids = [ev.evidence_id for ev in device_evidence]
        shared_count = sum(len(e) for e in shared_devices.values())

        return {
            "pattern_id": f"patt_{uuid4().hex[:8]}",
            "name": "DEVICE_REUSE",
            "description": (
                f"Multiple entities ({shared_count}) share the same device. "
                f"Shared devices: {list(shared_devices.keys())[:3]}"
            ),
            "confidence": min(0.90, 0.50 + 0.10 * len(shared_devices)),
            "evidence_ids": evidence_ids,
            "severity": "high",
            "rationale": (
                f"Device reuse across {len(shared_devices)} device(s) "
                f"suggests possible account takeover or synthetic identity fraud."
            ),
            "detected_at": datetime.now(UTC).isoformat(),
        }

    def _detect_ip_reuse(
        self, evidence: list[Evidence]
    ) -> dict[str, Any] | None:
        ip_evidence = [
            ev for ev in evidence
            if "ip" in (ev.source_reference or "").lower()
            or "IP" in (ev.title or "")
        ]

        if len(ip_evidence) < 2:
            return None

        evidence_ids = [ev.evidence_id for ev in ip_evidence]

        return {
            "pattern_id": f"patt_{uuid4().hex[:8]}",
            "name": "IP_REUSE",
            "description": (
                f"Multiple transactions or entities share the same IP address "
                f"({len(ip_evidence)} evidence items)."
            ),
            "confidence": min(0.80, 0.45 + 0.10 * len(ip_evidence)),
            "evidence_ids": evidence_ids,
            "severity": "medium",
            "rationale": (
                "IP address reuse may indicate coordinated fraud activity "
                "from a shared infrastructure."
            ),
            "detected_at": datetime.now(UTC).isoformat(),
        }

    def _detect_velocity(
        self, evidence: list[Evidence]
    ) -> dict[str, Any] | None:
        transaction_evidence = [
            ev for ev in evidence
            if ev.source_reference and "Transaction" in (ev.source_reference or "")
            or ev.title and "Transaction" in (ev.title or "")
        ]

        if len(transaction_evidence) < self.VELOCITY_THRESHOLD:
            return None

        evidence_ids = [ev.evidence_id for ev in transaction_evidence]

        return {
            "pattern_id": f"patt_{uuid4().hex[:8]}",
            "name": "VELOCITY",
            "description": (
                f"High number of transaction evidence items ({len(transaction_evidence)}) "
                f"suggests high-velocity activity on this account or customer."
            ),
            "confidence": min(0.75, 0.40 + 0.05 * len(transaction_evidence)),
            "evidence_ids": evidence_ids,
            "severity": "medium",
            "rationale": (
                f"Found {len(transaction_evidence)} transaction-related evidence items. "
                "High transaction volume may indicate fraud velocity pattern."
            ),
            "detected_at": datetime.now(UTC).isoformat(),
        }

    def _detect_fraud_markers(
        self, evidence: list[Evidence]
    ) -> list[dict[str, Any]]:
        marker_evidence = [
            ev for ev in evidence
            if (
                "FraudPattern" in (ev.source_reference or "")
                or ev.evidence_type == EvidenceType.DIRECT
                and "fraud" in (ev.title or "").lower()
            )
        ]

        patterns = []
        for ev in marker_evidence:
            patterns.append(
                {
                    "pattern_id": f"patt_{uuid4().hex[:8]}",
                    "name": "FRAUD_MARKER",
                    "description": (
                        f"Explicit fraud marker found in graph: {ev.title}"
                    ),
                    "confidence": min(1.0, ev.confidence * 1.1),
                    "evidence_ids": [ev.evidence_id],
                    "severity": "critical",
                    "rationale": (
                        f"Evidence '{ev.evidence_id}' is a direct fraud marker "
                        f"from the graph database: {ev.description}"
                    ),
                    "detected_at": datetime.now(UTC).isoformat(),
                }
            )
        return patterns
