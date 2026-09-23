from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentEventType, AgentStage
from backend.app.schemas.evidence import Evidence, EvidenceType

logger = get_logger(__name__)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _make_event(
    state: AgentRuntimeState,
    message: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "event_id": f"evt_{uuid4().hex[:8]}",
        "event_type": AgentEventType.PATTERN_DETECTED,
        "investigation_id": state.get("investigation_id", ""),
        "case_id": state.get("case_id"),
        "stage": AgentStage.DETECT_PATTERNS,
        "message": message,
        "payload": payload or {},
        "created_at": _utc_now(),
    }


class DetectPatternsNode:
    """
    Detects fraud-related patterns from already-collected evidence.

    Current evidence-driven patterns:

    - DEVICE_REUSE
        Multiple distinct entities are associated with the same device.

    - IP_REUSE
        Multiple evidence items reference the same IP/infrastructure.

    - VELOCITY
        A high number of transaction-related evidence items is observed.

    - FRAUD_MARKER
        Evidence explicitly identifies a FraudPattern graph node or
        directly describes a fraud marker.

    This node does not invent patterns without supporting evidence.
    """

    VELOCITY_THRESHOLD = 3

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, state: AgentRuntimeState) -> AgentRuntimeState:
        """LangGraph-compatible entry point."""
        return self.__call__(state)

    def __call__(self, state: AgentRuntimeState) -> AgentRuntimeState:
        evidence = list(state.get("evidence", []))
        existing_patterns = list(state.get("detected_patterns", []))
        events = list(state.get("events", []))
        investigation_id = state.get("investigation_id", "")

        if not evidence:
            logger.info(
                "no evidence available for pattern detection",
                investigation_id=investigation_id,
            )

            updated = advance_state(
                state,
                AgentStage.DETECT_PATTERNS,
            )
            updated["detected_patterns"] = existing_patterns
            updated["events"] = events
            return updated

        new_patterns: list[dict[str, Any]] = []

        device_pattern = self._detect_device_reuse(evidence)
        if device_pattern is not None:
            new_patterns.append(device_pattern)

        ip_pattern = self._detect_ip_reuse(evidence)
        if ip_pattern is not None:
            new_patterns.append(ip_pattern)

        velocity_pattern = self._detect_velocity(evidence)
        if velocity_pattern is not None:
            new_patterns.append(velocity_pattern)

        fraud_marker_patterns = self._detect_fraud_markers(evidence)
        new_patterns.extend(fraud_marker_patterns)

        all_patterns = existing_patterns + new_patterns

        for pattern in new_patterns:
            events.append(
                _make_event(
                    state,
                    message=f"Pattern detected: {pattern['name']}",
                    payload={
                        "pattern_id": pattern["pattern_id"],
                        "pattern_name": pattern["name"],
                        "confidence": pattern["confidence"],
                        "severity": pattern["severity"],
                        "evidence_ids": pattern["evidence_ids"],
                        "evidence_count": len(pattern["evidence_ids"]),
                    },
                )
            )

        logger.info(
            "pattern detection completed",
            investigation_id=investigation_id,
            new_patterns=len(new_patterns),
            total_patterns=len(all_patterns),
        )

        updated = advance_state(
            state,
            AgentStage.DETECT_PATTERNS,
        )
        updated["detected_patterns"] = all_patterns
        updated["events"] = events

        return updated

    def _detect_device_reuse(
        self,
        evidence: list[Evidence],
    ) -> dict[str, Any] | None:
        device_evidence = [
            ev
            for ev in evidence
            if self._is_device_evidence(ev)
        ]

        if len(device_evidence) < 2:
            return None

        device_entities: dict[str, set[str]] = {}

        for ev in device_evidence:
            device_id = (
                ev.source_id
                or ev.source_reference
                or ""
            ).strip()

            if not device_id:
                continue

            entities = {
                entity.strip()
                for entity in ev.entities
                if entity and entity.strip()
            }

            if entities:
                device_entities.setdefault(
                    device_id,
                    set(),
                ).update(entities)

        shared_devices = {
            device_id: entities
            for device_id, entities in device_entities.items()
            if len(entities) >= 2
        }

        if not shared_devices:
            return None

        evidence_ids = [
            ev.evidence_id
            for ev in device_evidence
        ]

        shared_entity_count = sum(
            len(entities)
            for entities in shared_devices.values()
        )

        confidence = min(
            0.90,
            0.50 + 0.10 * len(shared_devices),
        )

        return {
            "pattern_id": f"patt_{uuid4().hex[:8]}",
            "name": "DEVICE_REUSE",
            "description": (
                f"{shared_entity_count} distinct entities share "
                f"{len(shared_devices)} device(s)."
            ),
            "confidence": confidence,
            "evidence_ids": evidence_ids,
            "severity": "high",
            "rationale": (
                "Shared device identifiers across distinct entities "
                "may indicate coordinated activity, account takeover, "
                "or synthetic identity relationships."
            ),
            "detected_at": _utc_now().isoformat(),
            "attributes": {
                "shared_devices": {
                    device_id: sorted(entities)
                    for device_id, entities in shared_devices.items()
                },
            },
        }

    def _detect_ip_reuse(
        self,
        evidence: list[Evidence],
    ) -> dict[str, Any] | None:
        ip_evidence = [
            ev
            for ev in evidence
            if self._is_ip_evidence(ev)
        ]

        if len(ip_evidence) < 2:
            return None

        ip_groups: dict[str, set[str]] = {}

        for ev in ip_evidence:
            reference = (
                ev.source_id
                or ev.source_reference
                or ""
            ).strip()

            if not reference:
                continue

            entities = {
                entity.strip()
                for entity in ev.entities
                if entity and entity.strip()
            }

            ip_groups.setdefault(reference, set()).update(
                entities
            )

        shared_ips = {
            ip: entities
            for ip, entities in ip_groups.items()
            if len(entities) >= 2
        }

        evidence_ids = [
            ev.evidence_id
            for ev in ip_evidence
        ]

        if not evidence_ids:
            return None

        confidence = min(
            0.80,
            0.45 + 0.05 * len(ip_evidence),
        )

        return {
            "pattern_id": f"patt_{uuid4().hex[:8]}",
            "name": "IP_REUSE",
            "description": (
                f"{len(ip_evidence)} evidence items reference "
                "shared IP/infrastructure information."
            ),
            "confidence": confidence,
            "evidence_ids": evidence_ids,
            "severity": "medium",
            "rationale": (
                "Repeated IP or infrastructure relationships can "
                "provide corroborating evidence of coordinated activity."
            ),
            "detected_at": _utc_now().isoformat(),
            "attributes": {
                "shared_ip_groups": {
                    reference: sorted(entities)
                    for reference, entities in shared_ips.items()
                },
            },
        }

    def _detect_velocity(
        self,
        evidence: list[Evidence],
    ) -> dict[str, Any] | None:
        transaction_evidence = [
            ev
            for ev in evidence
            if self._is_transaction_evidence(ev)
        ]

        if len(transaction_evidence) < self.VELOCITY_THRESHOLD:
            return None

        evidence_ids = [
            ev.evidence_id
            for ev in transaction_evidence
        ]

        confidence = min(
            0.75,
            0.40 + 0.05 * len(transaction_evidence),
        )

        return {
            "pattern_id": f"patt_{uuid4().hex[:8]}",
            "name": "VELOCITY",
            "description": (
                f"{len(transaction_evidence)} transaction-related "
                "evidence items were collected."
            ),
            "confidence": confidence,
            "evidence_ids": evidence_ids,
            "severity": "medium",
            "rationale": (
                f"Observed {len(transaction_evidence)} transaction-related "
                "evidence items. This is a velocity signal and should be "
                "considered together with transaction timing, amount, "
                "customer history, and other evidence."
            ),
            "detected_at": _utc_now().isoformat(),
            "attributes": {
                "transaction_evidence_count": len(
                    transaction_evidence
                ),
                "threshold": self.VELOCITY_THRESHOLD,
            },
        }

    def _detect_fraud_markers(
        self,
        evidence: list[Evidence],
    ) -> list[dict[str, Any]]:
        marker_evidence = [
            ev
            for ev in evidence
            if self._is_fraud_marker(ev)
        ]

        patterns: list[dict[str, Any]] = []

        for ev in marker_evidence:
            confidence = min(
                1.0,
                max(0.0, ev.confidence) * 1.10,
            )

            patterns.append(
                {
                    "pattern_id": f"patt_{uuid4().hex[:8]}",
                    "name": "FRAUD_MARKER",
                    "description": (
                        f"Explicit fraud marker found: {ev.title}"
                    ),
                    "confidence": confidence,
                    "evidence_ids": [ev.evidence_id],
                    "severity": "critical",
                    "rationale": (
                        f"Evidence '{ev.evidence_id}' contains a direct "
                        f"fraud-related marker: {ev.description}"
                    ),
                    "detected_at": _utc_now().isoformat(),
                    "attributes": {
                        "source_type": str(ev.source_type),
                        "source_id": ev.source_id,
                    },
                }
            )

        return patterns

    @staticmethod
    def _is_device_evidence(ev: Evidence) -> bool:
        source_reference = (
            ev.source_reference or ""
        ).lower()
        title = ev.title.lower()

        return (
            "device" in source_reference
            or "device" in title
            or str(ev.source_type).lower().endswith("device")
        )

    @staticmethod
    def _is_ip_evidence(ev: Evidence) -> bool:
        source_reference = (
            ev.source_reference or ""
        ).lower()
        title = ev.title.lower()
        description = ev.description.lower()

        return (
            "ip" in source_reference
            or "ip" in title
            or "ip address" in description
        )

    @staticmethod
    def _is_transaction_evidence(ev: Evidence) -> bool:
        source_reference = (
            ev.source_reference or ""
        ).lower()
        title = ev.title.lower()

        return (
            str(ev.source_type).lower().endswith("transaction")
            or "transaction" in source_reference
            or "transaction" in title
            or bool(ev.transaction_ids)
        )

    @staticmethod
    def _is_fraud_marker(ev: Evidence) -> bool:
        source_reference = (
            ev.source_reference or ""
        ).lower()
        title = ev.title.lower()

        return (
            "fraudpattern" in source_reference
            or (
                ev.evidence_type == EvidenceType.DIRECT
                and "fraud" in title
            )
        )