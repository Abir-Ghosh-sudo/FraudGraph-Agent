from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import (
    AgentEvent,
    AgentEventType,
    AgentStage,
)
from backend.app.schemas.evidence import Evidence
from backend.app.schemas.investigation import InvestigationStatus

logger = get_logger("agent.nodes.reassess")


class ReassessNode:
    """
    Re-enters the investigation after an evidence request.

    Additional evidence can be supplied through:

        state["metadata"]["additional_evidence"]

    The evidence must already be normalized into the project's
    Evidence schema before reaching this node.

    This node does not fabricate evidence and does not itself call
    external systems.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(
        self,
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        """LangGraph-compatible entry point."""
        return self.__call__(state)

    def __call__(
        self,
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        updated = advance_state(
            state,
            AgentStage.REASSESS,
        )

        metadata = dict(
            updated.get(
                "metadata",
                {},
            )
        )

        # ----------------------------------------------------------
        # Reassessment counter
        # ----------------------------------------------------------
        reassess_count = self._safe_int(
            metadata.get(
                "reassess_count",
                0,
            )
        ) + 1

        metadata["reassess_count"] = reassess_count

        # ----------------------------------------------------------
        # Consume externally supplied evidence
        # ----------------------------------------------------------
        additional_evidence = metadata.pop(
            "additional_evidence",
            [],
        )

        normalized_additional_evidence = (
            self._normalize_evidence(
                additional_evidence
            )
        )

        existing_evidence = list(
            updated.get(
                "evidence",
                [],
            )
        )

        merged_evidence = self._merge_evidence(
            existing_evidence,
            normalized_additional_evidence,
        )

        updated["evidence"] = merged_evidence

        metadata["last_reassessment_evidence_count"] = (
            len(normalized_additional_evidence)
        )

        metadata["total_evidence_count"] = (
            len(merged_evidence)
        )

        # The previous request is no longer pending once this
        # reassessment cycle begins.
        metadata["awaiting_external_evidence"] = False

        updated["metadata"] = metadata

        # ----------------------------------------------------------
        # Resume investigation
        # ----------------------------------------------------------
        updated["status"] = (
            InvestigationStatus.INVESTIGATING
        )

        # ----------------------------------------------------------
        # Create audit event
        # ----------------------------------------------------------
        event = AgentEvent(
            event_id=f"evt_{uuid4().hex[:12]}",
            event_type=AgentEventType.STAGE_STARTED,
            investigation_id=updated.get(
                "investigation_id",
                "",
            ),
            case_id=updated.get(
                "case_id"
            ),
            stage=AgentStage.REASSESS,
            message=(
                f"Reassessment iteration "
                f"{reassess_count} started with "
                f"{len(normalized_additional_evidence)} "
                "new evidence item(s)."
            ),
            payload={
                "reassess_count": reassess_count,
                "new_evidence_count": len(
                    normalized_additional_evidence
                ),
                "total_evidence_count": len(
                    merged_evidence
                ),
                "previous_evidence_count": len(
                    existing_evidence
                ),
            },
            created_at=datetime.now(UTC),
        )

        updated["events"] = [
            *updated.get("events", []),
            event,
        ]

        logger.info(
            "investigation reassessment started",
            investigation_id=updated.get(
                "investigation_id",
                "",
            ),
            reassess_count=reassess_count,
            new_evidence_count=len(
                normalized_additional_evidence
            ),
            total_evidence_count=len(
                merged_evidence
            ),
        )

        return updated

    @staticmethod
    def _normalize_evidence(
        value: Any,
    ) -> list[Evidence]:
        """
        Accept already validated Evidence objects.

        Dictionary values are intentionally not silently converted here.
        External evidence ingestion should validate dictionaries at its
        boundary before inserting them into runtime state.
        """
        if not isinstance(
            value,
            list,
        ):
            return []

        return [
            item
            for item in value
            if isinstance(
                item,
                Evidence,
            )
        ]

    @staticmethod
    def _merge_evidence(
        existing: list[Evidence],
        additional: list[Evidence],
    ) -> list[Evidence]:
        """
        Merge evidence by evidence_id.

        Existing evidence wins when the same ID is supplied again.
        This keeps reassessment idempotent.
        """
        merged: list[Evidence] = []
        seen_ids: set[str] = set()

        for item in [
            *existing,
            *additional,
        ]:
            evidence_id = str(
                item.evidence_id
            )

            if evidence_id in seen_ids:
                continue

            seen_ids.add(
                evidence_id
            )

            merged.append(
                item
            )

        return merged

    @staticmethod
    def _safe_int(
        value: Any,
    ) -> int:
        try:
            return max(
                0,
                int(value),
            )
        except (
            TypeError,
            ValueError,
        ):
            return 0