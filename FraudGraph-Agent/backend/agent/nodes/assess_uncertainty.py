from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.agent.state import (
    AgentRuntimeState,
    advance_state,
    is_step_limit_reached,
)
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import (
    AgentEvent,
    AgentEventType,
    AgentStage,
)
from backend.app.schemas.evidence import EvidenceType
from backend.app.schemas.investigation import (
    InvestigationAssessment,
)

logger = get_logger("agent.nodes.assess_uncertainty")


def _utc_now() -> datetime:
    return datetime.now(UTC)


class AssessUncertaintyNode:
    """
    Evaluates whether the current investigation contains enough
    reliable evidence for a defensible action.

    Uncertainty is derived from:

    - missing evidence categories
    - evidence confidence
    - contradictory evidence
    - detected fraud patterns
    - available corroborating evidence
    - investigation step limits

    The node does not decide the final action. It only determines
    whether the investigation should request more evidence or proceed
    to action recommendation.
    """

    # These are evidence categories, not EvidenceSourceType enum values.
    # Matching is intentionally performed against normalized source
    # metadata because the actual Evidence schema contains several
    # different source categories.
    EXPECTED_SOURCE_KEYWORDS = {
        "transaction": (
            "transaction",
            "transactions",
        ),
        "device": (
            "device",
        ),
        "connection": (
            "connection",
            "ip",
            "network",
        ),
        "customer": (
            "customer",
            "identity",
        ),
        "account": (
            "account",
        ),
    }

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
            AgentStage.ASSESS_UNCERTAINTY,
        )

        evidence = list(
            updated.get(
                "evidence",
                [],
            )
        )

        patterns = list(
            updated.get(
                "detected_patterns",
                [],
            )
        )

        assessment = updated.get(
            "assessment"
        )

        if assessment is None:
            assessment = InvestigationAssessment()

        # ----------------------------------------------------------
        # 1. Identify missing evidence categories
        # ----------------------------------------------------------
        present_sources = self._detect_present_sources(
            evidence
        )

        missing_sources = sorted(
            set(self.EXPECTED_SOURCE_KEYWORDS)
            - present_sources
        )

        # ----------------------------------------------------------
        # 2. Evidence confidence
        # ----------------------------------------------------------
        evidence_uncertainty = self._calculate_evidence_uncertainty(
            evidence
        )

        # ----------------------------------------------------------
        # 3. Contradictory evidence
        # ----------------------------------------------------------
        conflicting_uncertainty = (
            self._calculate_conflict_uncertainty(
                evidence
            )
        )

        # ----------------------------------------------------------
        # 4. Pattern coverage
        # ----------------------------------------------------------
        pattern_uncertainty = (
            self._calculate_pattern_uncertainty(
                patterns
            )
        )

        # ----------------------------------------------------------
        # 5. Missing-source uncertainty
        # ----------------------------------------------------------
        missing_source_uncertainty = (
            self._calculate_missing_source_uncertainty(
                missing_sources,
                evidence,
            )
        )

        # ----------------------------------------------------------
        # 6. Combine uncertainty
        # ----------------------------------------------------------
        calculated_uncertainty = (
            missing_source_uncertainty * 0.30
            + evidence_uncertainty * 0.35
            + conflicting_uncertainty * 0.20
            + pattern_uncertainty * 0.15
        )

        calculated_uncertainty = self._clamp(
            calculated_uncertainty
        )

        # With no evidence at all, the investigation cannot reasonably
        # claim low uncertainty.
        if not evidence:
            calculated_uncertainty = max(
                calculated_uncertainty,
                0.80,
            )

        # ----------------------------------------------------------
        # 7. Confidence
        # ----------------------------------------------------------
        confidence = round(
            self._clamp(
                1.0 - calculated_uncertainty
            ),
            4,
        )

        calculated_uncertainty = round(
            calculated_uncertainty,
            4,
        )

        # ----------------------------------------------------------
        # 8. Preserve risk assessment and update uncertainty
        # ----------------------------------------------------------
        updated_assessment = InvestigationAssessment(
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level,
            uncertainty=calculated_uncertainty,
            fraud_type=assessment.fraud_type,
            confidence=confidence,
            rationale=assessment.rationale,
        )

        updated["assessment"] = updated_assessment

        # ----------------------------------------------------------
        # 9. Build event
        # ----------------------------------------------------------
        event = AgentEvent(
            event_id=f"evt_{uuid4().hex[:8]}",
            event_type=AgentEventType.UNCERTAINTY_ASSESSED,
            investigation_id=updated.get(
                "investigation_id",
                "",
            ),
            case_id=updated.get(
                "case_id"
            ),
            stage=AgentStage.ASSESS_UNCERTAINTY,
            message=(
                f"Uncertainty assessed at "
                f"{calculated_uncertainty:.2f}."
            ),
            payload={
                "uncertainty": calculated_uncertainty,
                "confidence": confidence,
                "missing_sources": missing_sources,
                "present_sources": sorted(
                    present_sources
                ),
                "evidence_count": len(evidence),
                "pattern_count": len(patterns),
                "evidence_uncertainty": round(
                    evidence_uncertainty,
                    4,
                ),
                "conflicting_uncertainty": round(
                    conflicting_uncertainty,
                    4,
                ),
                "pattern_uncertainty": round(
                    pattern_uncertainty,
                    4,
                ),
                "missing_source_uncertainty": round(
                    missing_source_uncertainty,
                    4,
                ),
            },
            created_at=_utc_now(),
        )

        updated["events"] = [
            *updated.get("events", []),
            event,
        ]

        # ----------------------------------------------------------
        # 10. Decide whether additional evidence is needed
        # ----------------------------------------------------------
        threshold = self._get_uncertainty_threshold()

        step_limit_reached = is_step_limit_reached(
            updated
        )

        if (
            calculated_uncertainty > threshold
            and not step_limit_reached
        ):
            updated["current_stage"] = (
                AgentStage.REQUEST_EVIDENCE
            )

            logger.info(
                "additional evidence required",
                investigation_id=updated.get(
                    "investigation_id",
                    "",
                ),
                uncertainty=calculated_uncertainty,
                threshold=threshold,
                missing_sources=missing_sources,
            )
        else:
            updated["current_stage"] = (
                AgentStage.RECOMMEND_ACTION
            )

            logger.info(
                "uncertainty assessment permits action recommendation",
                investigation_id=updated.get(
                    "investigation_id",
                    "",
                ),
                uncertainty=calculated_uncertainty,
                threshold=threshold,
                step_limit_reached=step_limit_reached,
            )

        return updated

    def _get_uncertainty_threshold(self) -> float:
        """
        Read the configured uncertainty threshold while remaining
        compatible with configurations where the field is absent.
        """
        threshold = getattr(
            self.settings,
            "agent_uncertainty_threshold",
            0.40,
        )

        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            threshold = 0.40

        return self._clamp(
            threshold
        )

    def _detect_present_sources(
        self,
        evidence: list[Any],
    ) -> set[str]:
        """
        Normalize actual Evidence source metadata into broad
        investigation evidence categories.
        """
        present: set[str] = set()

        for item in evidence:
            source_type = self._normalize_value(
                getattr(
                    item,
                    "source_type",
                    None,
                )
            )

            source_id = self._normalize_value(
                getattr(
                    item,
                    "source_id",
                    None,
                )
            )

            source_reference = self._normalize_value(
                getattr(
                    item,
                    "source_reference",
                    None,
                )
            )

            title = self._normalize_value(
                getattr(
                    item,
                    "title",
                    None,
                )
            )

            description = self._normalize_value(
                getattr(
                    item,
                    "description",
                    None,
                )
            )

            searchable = " ".join(
                (
                    source_type,
                    source_id,
                    source_reference,
                    title,
                    description,
                )
            )

            for category, keywords in (
                self.EXPECTED_SOURCE_KEYWORDS.items()
            ):
                if any(
                    keyword in searchable
                    for keyword in keywords
                ):
                    present.add(category)

        return present

    def _calculate_evidence_uncertainty(
        self,
        evidence: list[Any],
    ) -> float:
        if not evidence:
            return 0.80

        confidences: list[float] = []

        for item in evidence:
            confidence = getattr(
                item,
                "confidence",
                0.50,
            )

            try:
                confidence = float(
                    confidence
                )
            except (TypeError, ValueError):
                confidence = 0.50

            confidences.append(
                self._clamp(
                    confidence
                )
            )

        average_confidence = (
            sum(confidences)
            / len(confidences)
        )

        # A very small evidence set should retain some uncertainty.
        quantity_penalty = (
            0.20
            if len(evidence) == 1
            else 0.10
            if len(evidence) == 2
            else 0.0
        )

        return self._clamp(
            (1.0 - average_confidence)
            * 0.75
            + quantity_penalty
        )

    def _calculate_conflict_uncertainty(
        self,
        evidence: list[Any],
    ) -> float:
        if not evidence:
            return 0.0

        contradicting = 0
        direct = 0

        for item in evidence:
            evidence_type = getattr(
                item,
                "evidence_type",
                None,
            )

            if evidence_type == EvidenceType.CONTRADICTING:
                contradicting += 1

            if evidence_type == EvidenceType.DIRECT:
                direct += 1

        if contradicting == 0:
            return 0.0

        ratio = (
            contradicting
            / len(evidence)
        )

        # Direct corroboration partially offsets contradiction.
        corroboration_reduction = min(
            0.30,
            direct * 0.05,
        )

        return self._clamp(
            ratio * 0.90
            - corroboration_reduction
        )

    @staticmethod
    def _calculate_pattern_uncertainty(
        patterns: list[dict[str, Any]],
    ) -> float:
        if not patterns:
            return 0.35

        confidences: list[float] = []

        for pattern in patterns:
            value = pattern.get(
                "confidence",
                0.50,
            )

            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0.50

            confidences.append(
                max(
                    0.0,
                    min(1.0, value),
                )
            )

        average_confidence = (
            sum(confidences)
            / len(confidences)
        )

        return max(
            0.0,
            min(
                1.0,
                1.0 - average_confidence,
            ),
        )

    @staticmethod
    def _calculate_missing_source_uncertainty(
        missing_sources: list[str],
        evidence: list[Any],
    ) -> float:
        if not missing_sources:
            return 0.0

        # If there is no evidence, the separate no-evidence rule handles
        # the floor. Here we calculate the missing-source component.
        total_expected = len(
            AssessUncertaintyNode.EXPECTED_SOURCE_KEYWORDS
        )

        missing_ratio = (
            len(missing_sources)
            / total_expected
        )

        # More evidence can partially reduce concern caused by a missing
        # category because the existing evidence may already be strong.
        average_confidence = 0.0

        if evidence:
            values: list[float] = []

            for item in evidence:
                value = getattr(
                    item,
                    "confidence",
                    0.50,
                )

                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0.50

                values.append(
                    max(
                        0.0,
                        min(1.0, value),
                    )
                )

            if values:
                average_confidence = (
                    sum(values)
                    / len(values)
                )

        confidence_offset = min(
            0.25,
            average_confidence * 0.25,
        )

        return max(
            0.0,
            min(
                1.0,
                missing_ratio
                - confidence_offset,
            ),
        )

    @staticmethod
    def _normalize_value(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        if hasattr(value, "value"):
            value = value.value

        return str(
            value
        ).strip().lower()

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        return max(
            0.0,
            min(1.0, value),
        )