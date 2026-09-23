from __future__ import annotations

from typing import Any

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentExplanation, AgentStage
from backend.llm.client import OllamaClient
from backend.llm.prompts import (
    build_explanation_prompt,
    build_investigation_context,
    get_system_prompt,
)

logger = get_logger("agent.nodes.explain")


class ExplainNode:
    """Generates grounded explanation of findings and actions using LLM or deterministic rule-based fallback."""

    def __init__(
        self,
        settings: Settings,
        llm_client: OllamaClient | None = None,
    ) -> None:
        self.settings = settings
        self.llm_client = llm_client or OllamaClient(settings=settings)

    def run(self, state: AgentRuntimeState) -> AgentRuntimeState:
        updated = advance_state(state, AgentStage.EXPLAIN)

        assessment = updated.get("assessment")
        risk_level = getattr(assessment, "risk_level", "unknown") if assessment else "unknown"
        risk_score = getattr(assessment, "risk_score", 0.0) if assessment else 0.0
        confidence = getattr(assessment, "confidence", 0.5) if assessment else 0.5

        evidence_list = updated.get("evidence", [])
        evidence_dicts = [
            e.model_dump() if hasattr(e, "model_dump") else dict(e)
            for e in evidence_list
        ]
        evidence_ids = [
            str(getattr(e, "evidence_id", ""))
            for e in evidence_list
            if getattr(e, "evidence_id", "")
        ]

        patterns = updated.get("detected_patterns", [])
        decisions = [
            d.model_dump() if hasattr(d, "model_dump") else dict(d)
            for d in updated.get("decisions", [])
        ]
        selected_action = updated.get("selected_action")
        action_dict = (
            selected_action.model_dump()
            if selected_action and hasattr(selected_action, "model_dump")
            else dict(selected_action) if selected_action else None
        )

        explanation: AgentExplanation | None = None

        if self.settings.llm_enabled and self.llm_client.is_available():
            try:
                inv_context = build_investigation_context(
                    investigation_id=updated.get("investigation_id", ""),
                    trigger=updated.get("trigger", {}),
                    evidence_count=len(evidence_list),
                )
                prompt = build_explanation_prompt(
                    investigation_context=inv_context,
                    evidence_items=evidence_dicts,
                    patterns=patterns,
                    risk_assessment={
                        "risk_level": risk_level,
                        "risk_score": risk_score,
                        "confidence": confidence,
                        "fraud_type": getattr(assessment, "fraud_type", None),
                    },
                    decisions=decisions,
                    selected_action=action_dict,
                )
                system_prompt = get_system_prompt()
                llm_response = self.llm_client.generate_json(
                    prompt=prompt,
                    system=system_prompt,
                )
                if isinstance(llm_response, dict) and "summary" in llm_response:
                    explanation = AgentExplanation(
                        summary=str(llm_response.get("summary", "")),
                        evidence_used=[str(x) for x in llm_response.get("evidence_used", evidence_ids)],
                        reasoning_points=[str(x) for x in llm_response.get("reasoning_points", [])],
                        uncertainty=[str(x) for x in llm_response.get("uncertainty", [])],
                        additional_evidence_reason=llm_response.get("additional_evidence_reason"),
                        action_reason=llm_response.get("action_reason"),
                    )
            except Exception as exc:
                logger.warning("llm_explanation_failed_falling_back", error=str(exc))

        if explanation is None:
            # Deterministic evidence-grounded fallback
            reasoning_points: list[str] = []
            for p in patterns:
                ptype = p.get("pattern_type", "anomaly")
                pdesc = p.get("description", "")
                p_ev = p.get("evidence_ids", [])
                ev_ref = f" (Evidence: {', '.join(p_ev)})" if p_ev else ""
                reasoning_points.append(f"Pattern {ptype}: {pdesc}{ev_ref}")

            if not reasoning_points:
                reasoning_points.append(f"Analyzed {len(evidence_list)} direct graph evidence items without confirmed patterns.")

            action_title = selected_action.title if selected_action else "No action"
            action_reason = selected_action.rationale if selected_action else None

            uncertainty_items: list[str] = []
            if assessment and assessment.uncertainty and assessment.uncertainty > 0.3:
                uncertainty_items.append(f"Moderate uncertainty ({assessment.uncertainty:.2f}) due to limited graph depth or unverified identity attributes.")

            summary_text = (
                f"Investigation completed with risk level assessed as {risk_level.upper() if isinstance(risk_level, str) else risk_level.value.upper()} "
                f"(score: {risk_score:.2f}). Identified {len(patterns)} patterns across {len(evidence_ids)} pieces of graph evidence."
            )

            explanation = AgentExplanation(
                summary=summary_text,
                evidence_used=evidence_ids[:20],
                reasoning_points=reasoning_points,
                uncertainty=uncertainty_items,
                additional_evidence_reason=None,
                action_reason=f"Recommended '{action_title}': {action_reason}" if action_reason else None,
            )

        updated["explanation"] = explanation
        return updated
