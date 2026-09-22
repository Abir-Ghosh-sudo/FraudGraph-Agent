from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph

from backend.agent.state import AgentRuntimeState, is_step_limit_reached
from backend.app.schemas.agent import AgentStage


def _advance(
    state: AgentRuntimeState,
    stage: AgentStage,
) -> AgentRuntimeState:
    from backend.agent.state import advance_state

    return advance_state(state, stage)


def trigger_node(
    state: AgentRuntimeState,
) -> AgentRuntimeState:
    return _advance(
        state,
        AgentStage.INVESTIGATE,
    )


def investigate_node(
    state: AgentRuntimeState,
) -> AgentRuntimeState:
    return _advance(
        state,
        AgentStage.GATHER_EVIDENCE,
    )


def gather_evidence_node(
    state: AgentRuntimeState,
) -> AgentRuntimeState:
    return _advance(
        state,
        AgentStage.DETECT_PATTERNS,
    )


def detect_patterns_node(
    state: AgentRuntimeState,
) -> AgentRuntimeState:
    return _advance(
        state,
        AgentStage.ASSESS_RISK,
    )


def assess_risk_node(
    state: AgentRuntimeState,
) -> AgentRuntimeState:
    return _advance(
        state,
        AgentStage.ASSESS_UNCERTAINTY,
    )


def assess_uncertainty_node(
    state: AgentRuntimeState,
) -> AgentRuntimeState:
    if is_step_limit_reached(state):
        return _advance(
            state,
            AgentStage.EXPLAIN,
        )

    assessment = state.get("assessment")

    if assessment is not None and (
        assessment.uncertainty is not None
        and assessment.uncertainty
        > 0.40
    ):
        return _advance(
            state,
            AgentStage.REQUEST_EVIDENCE,
        )

    return _advance(
        state,
        AgentStage.RECOMMEND_ACTION,
    )


def request_evidence_node(
    state: AgentRuntimeState,
) -> AgentRuntimeState:
    return _advance(
        state,
        AgentStage.REASSESS,
    )


def reassess_node(
    state: AgentRuntimeState,
) -> AgentRuntimeState:
    return _advance(
        state,
        AgentStage.ASSESS_RISK,
    )


def recommend_action_node(
    state: AgentRuntimeState,
) -> AgentRuntimeState:
    return _advance(
        state,
        AgentStage.EXPLAIN,
    )


def explain_node(
    state: AgentRuntimeState,
) -> AgentRuntimeState:
    return _advance(
        state,
        AgentStage.UPDATE_MEMORY,
    )


def update_memory_node(
    state: AgentRuntimeState,
) -> AgentRuntimeState:
    updated = _advance(
        state,
        AgentStage.COMPLETE,
    )

    updated["completed_at"] = updated["updated_at"]

    return updated


def route_after_uncertainty(
    state: AgentRuntimeState,
) -> Literal[
    "request_evidence",
    "recommend_action",
    "explain",
]:
    stage = state.get("current_stage")

    if stage == AgentStage.REQUEST_EVIDENCE:
        return "request_evidence"

    if stage == AgentStage.EXPLAIN:
        return "explain"

    return "recommend_action"


def build_workflow() -> StateGraph:
    graph = StateGraph(AgentRuntimeState)

    graph.add_node(
        "trigger",
        trigger_node,
    )

    graph.add_node(
        "investigate",
        investigate_node,
    )

    graph.add_node(
        "gather_evidence",
        gather_evidence_node,
    )

    graph.add_node(
        "detect_patterns",
        detect_patterns_node,
    )

    graph.add_node(
        "assess_risk",
        assess_risk_node,
    )

    graph.add_node(
        "assess_uncertainty",
        assess_uncertainty_node,
    )

    graph.add_node(
        "request_evidence",
        request_evidence_node,
    )

    graph.add_node(
        "reassess",
        reassess_node,
    )

    graph.add_node(
        "recommend_action",
        recommend_action_node,
    )

    graph.add_node(
        "explain",
        explain_node,
    )

    graph.add_node(
        "update_memory",
        update_memory_node,
    )

    graph.add_edge(
        START,
        "trigger",
    )

    graph.add_edge(
        "trigger",
        "investigate",
    )

    graph.add_edge(
        "investigate",
        "gather_evidence",
    )

    graph.add_edge(
        "gather_evidence",
        "detect_patterns",
    )

    graph.add_edge(
        "detect_patterns",
        "assess_risk",
    )

    graph.add_edge(
        "assess_risk",
        "assess_uncertainty",
    )

    graph.add_conditional_edges(
        "assess_uncertainty",
        route_after_uncertainty,
        {
            "request_evidence": "request_evidence",
            "recommend_action": "recommend_action",
            "explain": "explain",
        },
    )

    graph.add_edge(
        "request_evidence",
        "reassess",
    )

    graph.add_edge(
        "reassess",
        "assess_risk",
    )

    graph.add_edge(
        "recommend_action",
        "explain",
    )

    graph.add_edge(
        "explain",
        "update_memory",
    )

    graph.add_edge(
        "update_memory",
        END,
    )

    return graph


def compile_workflow():
    return build_workflow().compile()