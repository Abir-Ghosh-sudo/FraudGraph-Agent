from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph

from backend.agent.nodes.approval import ApprovalNode
from backend.agent.nodes.assess_risk import AssessRiskNode
from backend.agent.nodes.assess_uncertainty import AssessUncertaintyNode
from backend.agent.nodes.detect_patterns import DetectPatternsNode
from backend.agent.nodes.execute_action import ExecuteActionNode
from backend.agent.nodes.explain import ExplainNode
from backend.agent.nodes.gather_evidence import GatherEvidenceNode
from backend.agent.nodes.investigate import InvestigationNode
from backend.agent.nodes.reassess import ReassessNode
from backend.agent.nodes.recommend_action import RecommendActionNode
from backend.agent.nodes.request_evidence import RequestEvidenceNode
from backend.agent.nodes.trigger import TriggerNode
from backend.agent.nodes.update_memory import UpdateMemoryNode
from backend.agent.state import AgentRuntimeState
from backend.app.config import Settings
from backend.app.schemas.agent import AgentStage


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


def build_workflow(settings: Settings | None = None) -> StateGraph:
    if settings is None:
        settings = Settings()

    trigger_node = TriggerNode(settings=settings)
    investigation_node = InvestigationNode(settings=settings)
    gather_evidence_node = GatherEvidenceNode(settings=settings)
    detect_patterns_node = DetectPatternsNode(settings=settings)
    assess_risk_node = AssessRiskNode(settings=settings)
    assess_uncertainty_node = AssessUncertaintyNode(settings=settings)
    request_evidence_node = RequestEvidenceNode(settings=settings)
    reassess_node = ReassessNode(settings=settings)
    recommend_action_node = RecommendActionNode(settings=settings)
    approval_node = ApprovalNode(settings=settings)
    explain_node = ExplainNode(settings=settings)
    update_memory_node = UpdateMemoryNode(settings=settings)

    graph = StateGraph(AgentRuntimeState)

    graph.add_node("trigger", trigger_node.run)
    graph.add_node("investigate", investigation_node.run)
    graph.add_node("gather_evidence", gather_evidence_node.run)
    graph.add_node("detect_patterns", detect_patterns_node.run)
    graph.add_node("assess_risk", assess_risk_node.run)
    graph.add_node("assess_uncertainty", assess_uncertainty_node.run)
    graph.add_node("request_evidence", request_evidence_node.run)
    graph.add_node("reassess", reassess_node.run)
    graph.add_node("recommend_action", recommend_action_node.run)
    graph.add_node("approval", approval_node.run)
    graph.add_node("explain", explain_node.run)
    graph.add_node("update_memory", update_memory_node.run)

    graph.add_edge(START, "trigger")
    graph.add_edge("trigger", "investigate")
    graph.add_edge("investigate", "gather_evidence")
    graph.add_edge("gather_evidence", "detect_patterns")
    graph.add_edge("detect_patterns", "assess_risk")
    graph.add_edge("assess_risk", "assess_uncertainty")

    graph.add_conditional_edges(
        "assess_uncertainty",
        route_after_uncertainty,
        {
            "request_evidence": "request_evidence",
            "recommend_action": "recommend_action",
            "explain": "explain",
        },
    )

    graph.add_edge("request_evidence", "reassess")
    graph.add_edge("reassess", "assess_risk")

    graph.add_edge("recommend_action", "approval")
    graph.add_edge("approval", "explain")
    graph.add_edge("explain", "update_memory")
    graph.add_edge("update_memory", END)

    return graph


def compile_workflow(settings: Settings | None = None):
    return build_workflow(settings).compile()