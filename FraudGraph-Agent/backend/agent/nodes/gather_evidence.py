from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.agent.state import AgentRuntimeState, advance_state
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.agent import AgentEventType, AgentStage
from backend.app.schemas.evidence import (
    Evidence,
    EvidenceSourceType,
    EvidenceStrength,
    EvidenceType,
)
from backend.app.schemas.graph import (
    GraphEdge,
    GraphNode,
    InvestigationSubgraph,
)

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
    "Case": EvidenceType.CORROBORATING,
    "FraudPattern": EvidenceType.DERIVED,
}


_NODE_TYPE_TO_SOURCE_TYPE: dict[str, EvidenceSourceType] = {
    "Transaction": EvidenceSourceType.TRANSACTION,
    "Customer": EvidenceSourceType.CUSTOMER,
    "Device": EvidenceSourceType.DEVICE,
    "IP": EvidenceSourceType.CONNECTION,
    "Card": EvidenceSourceType.CONNECTION,
    "Merchant": EvidenceSourceType.GRAPH,
    "Address": EvidenceSourceType.GRAPH,
    "Email": EvidenceSourceType.GRAPH,
    "Case": EvidenceSourceType.HISTORICAL_CASE,
    "FraudPattern": EvidenceSourceType.GRAPH,
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


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def _make_event(
    state: AgentRuntimeState,
    event_type: AgentEventType,
    message: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a normalized evidence-gathering event."""
    return {
        "event_id": f"evt_{uuid4().hex[:12]}",
        "event_type": event_type,
        "investigation_id": state.get("investigation_id", ""),
        "case_id": state.get("case_id"),
        "stage": AgentStage.GATHER_EVIDENCE,
        "message": message,
        "payload": payload or {},
        "created_at": utc_now(),
    }


class GatherEvidenceNode:
    """
    Convert investigation graph data into structured evidence.

    Graph nodes become entity-level evidence and graph edges become
    relationship evidence. Existing evidence is preserved and duplicate
    evidence is not added again.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def __call__(
        self,
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        """Execute the evidence-gathering node."""
        return self.run(state)

    def run(
        self,
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        """Collect evidence from the investigation subgraph."""
        graph = state.get("graph")
        investigation_id = state.get(
            "investigation_id",
            "",
        )
        trigger = state.get("trigger", {})

        existing_evidence = list(
            state.get("evidence", []),
        )
        events = list(
            state.get("events", []),
        )

        if not isinstance(trigger, dict):
            trigger = {}

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
                    {
                        "evidence_count": 0,
                    },
                )
            )

            updated = advance_state(
                state,
                AgentStage.GATHER_EVIDENCE,
            )

            updated["evidence"] = existing_evidence
            updated["events"] = events

            metadata = dict(
                state.get("metadata", {}),
            )
            metadata["evidence_collection_status"] = "no_graph_data"
            updated["metadata"] = metadata

            return updated

        new_evidence = self._collect_from_graph(
            graph=graph,
            investigation_id=investigation_id,
            trigger=trigger,
            existing_evidence=existing_evidence,
        )

        all_evidence = (
            existing_evidence + new_evidence
        )

        type_counts: dict[str, int] = {}

        for evidence in new_evidence:
            evidence_type = str(
                evidence.evidence_type,
            )
            type_counts[evidence_type] = (
                type_counts.get(
                    evidence_type,
                    0,
                )
                + 1
            )

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
                (
                    f"Gathered {len(new_evidence)} "
                    "new evidence items from graph."
                ),
                {
                    "new_evidence_count": len(
                        new_evidence,
                    ),
                    "total_evidence_count": len(
                        all_evidence,
                    ),
                    "graph_node_count": graph.node_count,
                    "graph_edge_count": graph.edge_count,
                    "evidence_by_type": type_counts,
                },
            )
        )

        updated = advance_state(
            state,
            AgentStage.GATHER_EVIDENCE,
        )

        updated["evidence"] = all_evidence
        updated["events"] = events

        metadata = dict(
            state.get("metadata", {}),
        )

        metadata["evidence_collection_status"] = "completed"
        metadata["evidence_count"] = len(
            all_evidence,
        )
        metadata["new_evidence_count"] = len(
            new_evidence,
        )
        metadata["evidence_by_type"] = type_counts

        updated["metadata"] = metadata

        return updated

    def _collect_from_graph(
        self,
        graph: InvestigationSubgraph,
        investigation_id: str,
        trigger: dict[str, Any],
        existing_evidence: list[Evidence],
    ) -> list[Evidence]:
        """Collect unique evidence from graph nodes and edges."""
        new_evidence: list[Evidence] = []

        existing_keys: set[
            tuple[str, str | None, str]
        ] = {
            (
                str(evidence.source_type),
                evidence.source_id,
                str(evidence.evidence_type),
            )
            for evidence in existing_evidence
        }

        for node in graph.nodes:
            evidence = self._node_to_evidence(
                node=node,
                investigation_id=investigation_id,
                trigger=trigger,
                existing_keys=existing_keys,
            )

            if evidence is None:
                continue

            new_evidence.append(evidence)

            existing_keys.add(
                (
                    str(evidence.source_type),
                    evidence.source_id,
                    str(evidence.evidence_type),
                )
            )

        for edge in graph.edges:
            evidence = self._edge_to_evidence(
                edge=edge,
                investigation_id=investigation_id,
                existing_keys=existing_keys,
            )

            if evidence is None:
                continue

            new_evidence.append(evidence)

            existing_keys.add(
                (
                    str(evidence.source_type),
                    evidence.source_id,
                    str(evidence.evidence_type),
                )
            )

        return new_evidence

    def _node_to_evidence(
        self,
        node: GraphNode,
        investigation_id: str,
        trigger: dict[str, Any],
        existing_keys: set[
            tuple[str, str | None, str]
        ],
    ) -> Evidence | None:
        """Convert a graph node into evidence."""
        node_type = node.node_type

        evidence_type = (
            _NODE_TYPE_TO_EVIDENCE_TYPE.get(
                node_type,
                EvidenceType.CONTEXTUAL,
            )
        )

        source_type = (
            _NODE_TYPE_TO_SOURCE_TYPE.get(
                node_type,
                EvidenceSourceType.GRAPH,
            )
        )

        strength = (
            _NODE_TYPE_TO_STRENGTH.get(
                node_type,
                EvidenceStrength.WEAK,
            )
        )

        dedup_key = (
            str(source_type),
            node.node_id,
            str(evidence_type),
        )

        if dedup_key in existing_keys:
            return None

        properties = node.properties or {}

        name = (
            properties.get("name")
            or node.label
            or node.node_id
        )

        amount = (
            properties.get("amount")
            or properties.get("TransactionAmt")
        )

        if node_type == "Transaction" and amount is not None:
            title = (
                f"Transaction {node.node_id}: "
                f"amount={amount}"
            )
        elif node_type == "FraudPattern":
            pattern_name = properties.get(
                "pattern_name",
                node.node_id,
            )
            title = (
                f"Fraud Pattern: {pattern_name}"
            )
        else:
            title = (
                f"{node_type}: {name}"
            )

        description = self._build_node_description(
            node,
            trigger,
        )

        confidence = self._estimate_node_confidence(
            node,
            trigger,
        )

        relevance = self._estimate_relevance(
            node,
            trigger,
        )

        now = utc_now()

        return Evidence(
            evidence_id=f"ev_{uuid4().hex[:12]}",
            source_type=source_type,
            evidence_type=evidence_type,
            title=title,
            description=description,
            source_id=node.node_id,
            source_reference=(
                f"graph:node:"
                f"{node_type}:"
                f"{node.node_id}"
            ),
            strength=strength,
            reliability=0.85,
            relevance=relevance,
            confidence=confidence,
            entities=[node.node_id],
            transaction_ids=(
                [node.node_id]
                if node_type == "Transaction"
                else []
            ),
            case_ids=(
                [node.node_id]
                if node_type == "Case"
                else []
            ),
            provenance={
                "node_type": node_type,
                "node_id": node.node_id,
                "graph_query": (
                    "investigation_subgraph"
                ),
                "investigation_id": investigation_id,
            },
            metadata={
                "properties": {
                    str(key): str(value)
                    for key, value in properties.items()
                    if value is not None
                }
            },
            collected_at=now,
            created_at=now,
        )

    def _edge_to_evidence(
        self,
        edge: GraphEdge,
        investigation_id: str,
        existing_keys: set[
            tuple[str, str | None, str]
        ],
    ) -> Evidence | None:
        """Convert a graph relationship into evidence."""
        source_type = EvidenceSourceType.CONNECTION
        evidence_type = EvidenceType.CORROBORATING

        edge_key = (
            f"{edge.source_id}:"
            f"{edge.edge_type}:"
            f"{edge.target_id}"
        )

        dedup_key = (
            str(source_type),
            edge_key,
            str(evidence_type),
        )

        if dedup_key in existing_keys:
            return None

        now = utc_now()

        return Evidence(
            evidence_id=f"ev_{uuid4().hex[:12]}",
            source_type=source_type,
            evidence_type=evidence_type,
            title=(
                f"Connection: "
                f"{edge.source_id} "
                f"→ [{edge.edge_type}] → "
                f"{edge.target_id}"
            ),
            description=(
                f"Graph relationship "
                f"'{edge.edge_type}' connects "
                f"entity {edge.source_id} "
                f"to entity {edge.target_id}."
            ),
            source_id=edge_key,
            source_reference=(
                f"graph:edge:"
                f"{edge.edge_type}:"
                f"{edge.source_id}:"
                f"{edge.target_id}"
            ),
            strength=EvidenceStrength.MODERATE,
            reliability=0.80,
            relevance=0.50,
            confidence=0.60,
            entities=[
                edge.source_id,
                edge.target_id,
            ],
            transaction_ids=[],
            case_ids=[],
            provenance={
                "edge_type": edge.edge_type,
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "investigation_id": investigation_id,
            },
            metadata={
                "properties": edge.properties or {},
            },
            collected_at=now,
            created_at=now,
        )

    @staticmethod
    def _build_node_description(
        node: GraphNode,
        trigger: dict[str, Any],
    ) -> str:
        """Build a concise evidence description."""
        properties = node.properties or {}

        parts = [
            f"{node.node_type} entity: "
            f"{node.node_id}"
        ]

        significant_properties = {
            "amount",
            "TransactionAmt",
            "risk_score",
            "isFraud",
            "is_flagged",
            "status",
            "device_type",
            "country",
        }

        for key in significant_properties:
            value = properties.get(key)

            if value is not None:
                parts.append(
                    f"{key}={value}"
                )

        if (
            trigger.get("transaction_id")
            == node.node_id
            or trigger.get("customer_id")
            == node.node_id
            or trigger.get("account_id")
            == node.node_id
        ):
            parts.append(
                "[PRIMARY INVESTIGATION TARGET]"
            )

        return "; ".join(parts)

    @staticmethod
    def _estimate_node_confidence(
        node: GraphNode,
        trigger: dict[str, Any],
    ) -> float:
        """Estimate confidence in node-derived evidence."""
        properties = node.properties or {}

        confidence = 0.60

        if (
            trigger.get("transaction_id")
            == node.node_id
            or trigger.get("customer_id")
            == node.node_id
            or trigger.get("account_id")
            == node.node_id
        ):
            confidence = 0.90

        if (
            properties.get("isFraud") == 1
            or properties.get("is_flagged") is True
        ):
            confidence = min(
                1.0,
                confidence + 0.20,
            )

        risk_score = properties.get(
            "risk_score",
        )

        if risk_score is not None:
            try:
                confidence = min(
                    1.0,
                    confidence
                    + float(risk_score) * 0.15,
                )
            except (
                TypeError,
                ValueError,
            ):
                pass

        return round(
            confidence,
            3,
        )

    @staticmethod
    def _estimate_relevance(
        node: GraphNode,
        trigger: dict[str, Any],
    ) -> float:
        """Estimate relevance of graph evidence."""
        if (
            trigger.get("transaction_id")
            == node.node_id
            or trigger.get("customer_id")
            == node.node_id
            or trigger.get("account_id")
            == node.node_id
        ):
            return 1.0

        type_relevance = {
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

        return type_relevance.get(
            node.node_type,
            0.30,
        )


def gather_evidence_node(
    state: AgentRuntimeState,
    settings: Settings,
) -> AgentRuntimeState:
    """Functional wrapper for the evidence node."""
    return GatherEvidenceNode(
        settings=settings,
    ).run(state)