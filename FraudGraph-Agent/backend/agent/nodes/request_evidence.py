from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.action import ApprovalRoute
from backend.app.schemas.agent import (
    AgentEvent,
    AgentEventType,
    AgentStage,
    EvidenceRequest,
)
from backend.app.schemas.evidence import EvidenceSourceType
from backend.app.schemas.investigation import InvestigationStatus

logger = get_logger("agent.nodes.request_evidence")


class RequestEvidenceNode:
    """
    Creates a structured request for additional evidence when the
    investigation remains too uncertain for a defensible action.

    The node only requests evidence that is not already represented
    in the collected evidence. It does not execute any external
    evidence-gathering action itself.
    """

    # Evidence categories that are particularly useful for fraud
    # investigations. These map to the actual EvidenceSourceType enum
    # in the project.
    PRIORITY_SOURCES: tuple[EvidenceSourceType, ...] = (
        EvidenceSourceType.DEVICE,
        EvidenceSourceType.CONNECTION,
        EvidenceSourceType.CUSTOMER,
        EvidenceSourceType.ACCOUNT,
        EvidenceSourceType.TRANSACTION,
        EvidenceSourceType.HISTORICAL_CASE,
    )

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
            AgentStage.REQUEST_EVIDENCE,
        )

        evidence = list(
            updated.get(
                "evidence",
                [],
            )
        )

        existing_requests = list(
            updated.get(
                "evidence_requests",
                [],
            )
        )

        existing_sources = self._collect_existing_sources(
            evidence
        )

        requested_sources = self._select_sources(
            existing_sources=existing_sources,
            state=updated,
        )

        # If all high-value categories are already present, ask for
        # additional context rather than requesting a source that is
        # already represented.
        if not requested_sources:
            requested_sources = [
                "additional_transaction_context"
            ]

        evidence_ids = [
            getattr(
                item,
                "evidence_id",
                "",
            )
            for item in evidence
        ]

        evidence_ids = [
            evidence_id
            for evidence_id in evidence_ids
            if evidence_id
        ]

        uncertainty = self._get_uncertainty(
            updated
        )

        risk_level = self._get_risk_level(
            updated
        )

        reason = self._build_reason(
            uncertainty=uncertainty,
            risk_level=risk_level,
            requested_sources=requested_sources,
        )

        request = EvidenceRequest(
            request_id=f"req_{uuid4().hex[:12]}",
            reason=reason,
            requested_evidence=requested_sources,
            evidence_ids=evidence_ids[:10],
            approval_required=False,
            approval_route=ApprovalRoute.ANALYST.value,
            created_at=datetime.now(UTC),
        )

        updated["evidence_requests"] = [
            *existing_requests,
            request,
        ]

        updated["status"] = (
            InvestigationStatus.AWAITING_EVIDENCE
        )

        event = AgentEvent(
            event_id=f"evt_{uuid4().hex[:12]}",
            event_type=AgentEventType.EVIDENCE_REQUESTED,
            investigation_id=updated.get(
                "investigation_id",
                "",
            ),
            case_id=updated.get(
                "case_id"
            ),
            stage=AgentStage.REQUEST_EVIDENCE,
            message=(
                "Additional evidence requested: "
                + ", ".join(requested_sources)
            ),
            payload={
                "request_id": request.request_id,
                "requested_sources": requested_sources,
                "uncertainty": uncertainty,
                "risk_level": risk_level,
                "existing_evidence_count": len(
                    evidence
                ),
                "existing_sources": sorted(
                    existing_sources
                ),
            },
            created_at=datetime.now(UTC),
        )

        updated["events"] = [
            *updated.get("events", []),
            event,
        ]

        logger.info(
            "additional evidence requested",
            investigation_id=updated.get(
                "investigation_id",
                "",
            ),
            request_id=request.request_id,
            requested_sources=requested_sources,
            uncertainty=uncertainty,
            risk_level=risk_level,
        )

        return updated

    @staticmethod
    def _collect_existing_sources(
        evidence: list[object],
    ) -> set[str]:
        """
        Normalize EvidenceSourceType enum values to their string values.
        """
        sources: set[str] = set()

        for item in evidence:
            source_type = getattr(
                item,
                "source_type",
                None,
            )

            if source_type is None:
                continue

            value = getattr(
                source_type,
                "value",
                source_type,
            )

            sources.add(
                str(value).strip().lower()
            )

        return sources

    def _select_sources(
        self,
        *,
        existing_sources: set[str],
        state: AgentRuntimeState,
    ) -> list[str]:
        """
        Select evidence sources that are currently absent.

        Risk level is used to prioritize the breadth of requested
        evidence without turning this node into an action decision.
        """
        risk_level = self._get_risk_level(
            state
        )

        selected: list[str] = []

        for source in self.PRIORITY_SOURCES:
            source_value = source.value

            if source_value in existing_sources:
                continue

            selected.append(
                self._source_to_request_name(
                    source
                )
            )

            # Higher-risk cases can request more corroborating sources.
            if risk_level in {
                "high",
                "critical",
            }:
                if len(selected) >= 3:
                    break
            elif risk_level == "medium":
                if len(selected) >= 2:
                    break
            else:
                if len(selected) >= 1:
                    break

        return selected

    @staticmethod
    def _source_to_request_name(
        source: EvidenceSourceType,
    ) -> str:
        """
        Convert internal evidence source types into human-readable
        request identifiers used by the agent/API layer.
        """
        mapping = {
            EvidenceSourceType.TRANSACTION: (
                "transaction_context"
            ),
            EvidenceSourceType.GRAPH: (
                "graph_relationship_context"
            ),
            EvidenceSourceType.CUSTOMER: (
                "customer_validation"
            ),
            EvidenceSourceType.ACCOUNT: (
                "account_history"
            ),
            EvidenceSourceType.DEVICE: (
                "device_fingerprint"
            ),
            EvidenceSourceType.CONNECTION: (
                "connection_or_ip_context"
            ),
            EvidenceSourceType.HISTORICAL_CASE: (
                "similar_historical_cases"
            ),
            EvidenceSourceType.DOCUMENT: (
                "supporting_document"
            ),
            EvidenceSourceType.POLICY: (
                "applicable_policy"
            ),
            EvidenceSourceType.REGULATION: (
                "applicable_regulation"
            ),
            EvidenceSourceType.EXTERNAL: (
                "approved_external_data"
            ),
            EvidenceSourceType.ANALYST: (
                "analyst_context"
            ),
        }

        return mapping[source]

    @staticmethod
    def _get_uncertainty(
        state: AgentRuntimeState,
    ) -> float:
        assessment = state.get(
            "assessment"
        )

        if assessment is None:
            return 1.0

        value = getattr(
            assessment,
            "uncertainty",
            None,
        )

        if value is None:
            return 1.0

        try:
            return max(
                0.0,
                min(
                    1.0,
                    float(value),
                ),
            )
        except (TypeError, ValueError):
            return 1.0

    @staticmethod
    def _get_risk_level(
        state: AgentRuntimeState,
    ) -> str:
        assessment = state.get(
            "assessment"
        )

        if assessment is None:
            return "unknown"

        risk_level = getattr(
            assessment,
            "risk_level",
            "unknown",
        )

        value = getattr(
            risk_level,
            "value",
            risk_level,
        )

        return str(
            value
        ).strip().lower()

    @staticmethod
    def _build_reason(
        *,
        uncertainty: float,
        risk_level: str,
        requested_sources: list[str],
    ) -> str:
        source_text = ", ".join(
            requested_sources
        )

        return (
            "Additional evidence is required because the current "
            f"investigation uncertainty is {uncertainty:.2f} and the "
            f"current risk level is {risk_level}. "
            f"Requested evidence: {source_text}. "
            "The requested information is intended to reduce "
            "uncertainty and provide corroboration before a "
            "defensible next-best action is selected."
        )