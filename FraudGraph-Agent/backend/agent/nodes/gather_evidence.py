from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentEventType, AgentStage
from backend.app.schemas.evidence import (
    Evidence,
    EvidenceCreate,
    EvidenceSourceType,
    EvidenceStrength,
    EvidenceType,
)
from backend.app.schemas.graph import GraphEdge, GraphNode, InvestigationSubgraph
from backend.agent.state import AgentRuntimeState, advance_state

logger = get_logger(__name__)

_NODE_TYPE_TO_EVIDENCE_TYPE: dict[str, EvidenceType] = {
    "Transaction": EvidenceType.DIRECT,
    "Customer": EvidenceType.CORROBORATING,
    "Device": EvidenceType.CORROBORATING,
    "IP": EvidenceType.CORROBORATING,
    "Card": EvidenceType.CORROBORATING,
    "Merchant": EvidenceType.CONTEXTUAL,
    "Address": EvidenceType.CONTEXTUAL,
    "Email": EvidenceType.CONTEXTUAL,
    "Case": EvidenceType.HISTORICAL,
    "FraudPattern": EvidenceType.DIRECT,
}

_NODE_TYPE_TO_SOURCE_TYPE: dict[str, EvidenceSourceType] = {
    "Transaction": EvidenceSourceType.GRAPH,
    "Customer": EvidenceSourceType.GRAPH,
    "Device": EvidenceSourceType.GRAPH,
    "IP": EvidenceSourceType.GRAPH,
    "Card": EvidenceSourceType.GRAPH,
    "Merchant": EvidenceSourceType.GRAPH,
    "Address": EvidenceSourceType.GRAPH,
    "Email": EvidenceSourceType.GRAPH,
    "Case": EvidenceSourceType.CASE_HISTORY,
    "FraudPattern": EvidenceSourceType.RULE_ENGINE,
}

_NODE_TYPE_TO_STRENGTH: dict[str, EvidenceStrength] = {
    "Transaction": EvidenceStrength.STRONG,
    "FraudPattern": EvidenceStrength.VERY_STRONG,
    "Case": EvidenceStrength.STRONG,
    "Device": EvidenceStrength.MODERATE,
    "IP": EvidenceStrength.MODERATE,
    "Card": EvidenceStrength.MODERATE,
    "Customer": EvidenceStrength.WEAK,
    "Merchant": EvidenceStrength.WEAK,
    "Address": EvidenceStrength.WEAK,
    "Email": EvidenceStrength.WEAK,
}


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
        "stage": AgentStage.GATHER_EVIDENCE,
        "message": message,
        "payload": payload or {},
        "created_at": datetime.now(UTC),
    }


class GatherEvidenceNode:
    """
    Translates graph nodes and edges from the InvestigationSubgraph into
    structured Evidence objects.

    Evidence is typed based on node/edge type and deduplicated by
    (source_type, source_id, evidence_type).
    Emits EVIDENCE_FOUND events for each distinct node type found.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def __call__(self, state: AgentRuntimeState) -> AgentRuntimeState:
        graph: InvestigationSubgraph | None = state.get("graph")
        investigation_id = state.get("investigation_id", "")
        trigger = state.get("trigger", {})

        existing_evidence = list(state.get("evidence", []))
        events = list(state.get("events", []))
        errors = list(state.get("errors", []))

        if graph is None:
            logger.info(
                "no graph data available for evidence gathering",
                investigation_id=investigation_id,
            )
            events.append(
                _make_event(
                    state,
                    AgentEventType.EVIDENCE_FOUND,
                    "No graph data available; evidence gathering skipped.",
                    {"evidence_count": 0},
                )
            )
            updated = advance_state(state, AgentStage.GATHER_EVIDENCE)
            updated["evidence"] = existing_evidence
            updated["events"] = events
            return updated

        new_evidence = self._collect_from_graph(
            graph=graph,
            investigation_id=investigation_id,
            trigger=trigger,
            existing_evidence=existing_evidence,
        )

        all_evidence = existing_evidence + new_evidence

        # Summarize by type
        type_counts: dict[str, int] = {}
        for ev in new_evidence:
            type_counts[ev.evidence_type] = type_counts.get(ev.evidence_type, 0) + 1

        logger.info(
            "evidence gathered from graph",
            investigation_id=investigation_id,
            new_count=len(new_evidence),
            total_count=len(all_evidence),
            by_type=type_counts,
        )

        events.append(
            _make_event(
                state,
                AgentEventType.EVIDENCE_FOUND,
                f"Gathered {len(new_evidence)} evidence items from graph.",
                {
                    "new_evidence_count": len(new_evidence),
                    "total_evidence_count": len(all_evidence),
                    "graph_node_count": graph.node_count,
                    "graph_edge_count": graph.edge_count,
                    "evidence_by_type": type_counts,
                },
            )
        )

        updated = advance_state(state, AgentStage.GATHER_EVIDENCE)
        updated["evidence"] = all_evidence
        updated["events"] = events
        updated["errors"] = errors

        return updated

    def _collect_from_graph(
        self,
        graph: InvestigationSubgraph,
        investigation_id: str,
        trigger: dict[str, Any],
        existing_evidence: list[Evidence],
    ) -> list[Evidence]:
        new_evidence: list[Evidence] = []
        existing_keys: set[tuple[str, str | None, str]] = {
            (ev.source_type, ev.source_id, ev.evidence_type)
            for ev in existing_evidence
        }

        for node in graph.nodes:
            ev = self._node_to_evidence(
                node=node,
                investigation_id=investigation_id,
                trigger=trigger,
                existing_keys=existing_keys,
            )
            if ev is not None:
                new_evidence.append(ev)
                existing_keys.add((ev.source_type, ev.source_id, ev.evidence_type))

        for edge in graph.edges:
            ev = self._edge_to_evidence(
                edge=edge,
                investigation_id=investigation_id,
                existing_keys=existing_keys,
            )
            if ev is not None:
                new_evidence.append(ev)
                existing_keys.add((ev.source_type, ev.source_id, ev.evidence_type))

        return new_evidence

    def _node_to_evidence(
        self,
        node: GraphNode,
        investigation_id: str,
        trigger: dict[str, Any],
        existing_keys: set[tuple[str, str | None, str]],
    ) -> Evidence | None:
        node_type = node.node_type
        evidence_type = _NODE_TYPE_TO_EVIDENCE_TYPE.get(node_type, EvidenceType.CONTEXTUAL)
        source_type = _NODE_TYPE_TO_SOURCE_TYPE.get(node_type, EvidenceSourceType.GRAPH)
        strength = _NODE_TYPE_TO_STRENGTH.get(node_type, EvidenceStrength.WEAK)

        dedup_key = (str(source_type), node.node_id, str(evidence_type))
        if dedup_key in existing_keys:
            return None

        # Build title from node properties
        name = node.properties.get("name") or node.label or node.node_id
        amount = node.properties.get("amount") or node.properties.get("TransactionAmt", "")

        if node_type == "Transaction" and amount:
            title = f"Transaction {node.node_id}: amount={amount}"
        elif node_type == "FraudPattern":
            pattern_name = node.properties.get("pattern_name", node.node_id)
            title = f"Fraud Pattern: {pattern_name}"
        else:
            title = f"{node_type}: {name}"

        description = self._build_node_description(node, trigger)
        confidence = self._estimate_node_confidence(node, trigger)

        now = datetime.now(UTC)
        evidence_id = f"ev_{uuid4().hex[:12]}"

        return Evidence(
            evidence_id=evidence_id,
            source_type=source_type,
            evidence_type=evidence_type,
            title=title,
            description=description,
            source_id=node.node_id,
            source_reference=f"graph:node:{node_type}:{node.node_id}",
            strength=strength,
            reliability=0.85,
            relevance=self._estimate_relevance(node, trigger),
            confidence=confidence,
            entities=[node.node_id],
            transaction_ids=(
                [node.node_id]
                if node_type == "Transaction"
                else []
            ),
            case_ids=[],
            provenance={
                "node_type": node_type,
                "node_id": node.node_id,
                "graph_query": "investigation_subgraph",
                "investigation_id": investigation_id,
            },
            metadata={
                "properties": {
                    k: str(v)
                    for k, v in (node.properties or {}).items()
                    if v is not None
                }
            },
            collected_at=now,
            created_at=now,
        )

    def _edge_to_evidence(
        self,
        edge: GraphEdge,
        investigation_id: str,
        existing_keys: set[tuple[str, str | None, str]],
    ) -> Evidence | None:
        evidence_type = EvidenceType.CORROBORATING
        source_type = EvidenceSourceType.GRAPH

        edge_key = f"{edge.source_id}-{edge.edge_type}-{edge.target_id}"
        dedup_key = (str(source_type), edge_key, str(evidence_type))
        if dedup_key in existing_keys:
            return None

        title = f"Connection: {edge.source_id} → [{edge.edge_type}] → {edge.target_id}"
        description = (
            f"Graph relationship '{edge.edge_type}' connects "
            f"entity {edge.source_id} to entity {edge.target_id}."
        )

        now = datetime.now(UTC)
        evidence_id = f"ev_{uuid4().hex[:12]}"

        return Evidence(
            evidence_id=evidence_id,
            source_type=source_type,
            evidence_type=evidence_type,
            title=title,
            description=description,
            source_id=edge_key,
            source_reference=f"graph:edge:{edge.edge_type}:{edge.source_id}:{edge.target_id}",
            strength=EvidenceStrength.MODERATE,
            reliability=0.80,
            relevance=0.50,
            confidence=0.60,
            entities=[edge.source_id, edge.target_id],
            transaction_ids=[],
            case_ids=[],
            provenance={
                "edge_type": edge.edge_type,
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "investigation_id": investigation_id,
            },
            metadata={"properties": edge.properties or {}},
            collected_at=now,
            created_at=now,
        )

    @staticmethod
    def _build_node_description(
        node: GraphNode,
        trigger: dict[str, Any],
    ) -> str:
        props = node.properties or {}
        parts = [f"{node.node_type} entity: {node.node_id}"]

        significant_props = {
            "amount", "TransactionAmt", "isFraud", "is_flagged",
            "risk_score", "status", "device_type", "country",
        }

        for key in significant_props:
            val = props.get(key)
            if val is not None:
                parts.append(f"{key}={val}")

        if trigger.get("transaction_id") == node.node_id:
            parts.append("[PRIMARY INVESTIGATION TARGET]")
        elif trigger.get("customer_id") == node.node_id:
            parts.append("[PRIMARY INVESTIGATION TARGET]")

        return "; ".join(parts)

    @staticmethod
    def _estimate_node_confidence(
        node: GraphNode,
        trigger: dict[str, Any],
    ) -> float:
        base = 0.60
        props = node.properties or {}

        if (
            trigger.get("transaction_id") == node.node_id
            or trigger.get("customer_id") == node.node_id
        ):
            base = 0.90

        if props.get("isFraud") == 1 or props.get("is_flagged"):
            base = min(1.0, base + 0.20)

        if props.get("risk_score") is not None:
            try:
                rs = float(props["risk_score"])
                base = min(1.0, base + rs * 0.15)
            except (ValueError, TypeError):
                pass

        return round(base, 3)

    @staticmethod
    def _estimate_relevance(
        node: GraphNode,
        trigger: dict[str, Any],
    ) -> float:
        if (
            trigger.get("transaction_id") == node.node_id
            or trigger.get("customer_id") == node.node_id
            or trigger.get("account_id") == node.node_id
        ):
            return 1.0

        type_relevance: dict[str, float] = {
            "Transaction": 0.90,
            "FraudPattern": 0.90,
            "Case": 0.80,
            "Device": 0.70,
            "IP": 0.70,
            "Card": 0.65,
            "Customer": 0.60,
            "Merchant": 0.50,
            "Address": 0.40,
            "Email": 0.40,
        }

        return type_relevance.get(node.node_type, 0.30)
