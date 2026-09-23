from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.agent.state import AgentRuntimeState, add_error, advance_state
from backend.app.config import Settings
from backend.app.schemas.agent import AgentStage
from backend.app.schemas.graph import InvestigationSubgraph
from backend.app.services.graph import GraphService
from backend.tigergraph.client import TigerGraphError
from backend.tigergraph.query_runner import QueryRegistryError


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


class InvestigationNodeError(RuntimeError):
    """Raised when graph-backed investigation cannot proceed."""


class InvestigationNode:
    """Run the graph-backed investigation stage."""

    def __init__(
        self,
        settings: Settings,
        graph_service: GraphService | None = None,
    ) -> None:
        self.settings = settings
        self.graph_service = graph_service or GraphService(
            settings=settings,
        )

    def run(
        self,
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        """Execute graph-backed investigation."""
        updated = advance_state(
            state,
            AgentStage.INVESTIGATE,
        )

        metadata = dict(
            updated.get("metadata", {}),
        )

        metadata["graph_status"] = "starting"
        updated["metadata"] = metadata

        if not self.graph_service.is_configured():
            return self._handle_unavailable_graph(
                updated,
            )

        target = self._resolve_target(updated)

        if target is None:
            return self._handle_missing_target(
                updated,
            )

        query_name = self._resolve_query(updated)

        if query_name is None:
            return self._handle_missing_query(
                updated,
            )

        parameters = self._build_parameters(
            updated,
            target,
        )

        try:
            subgraph = self.graph_service.investigation(
                root_node_id=target["node_id"],
                query_name=query_name,
                parameters=parameters,
                depth=self._resolve_depth(updated),
                limit=self._resolve_limit(updated),
            )

        except (
            QueryRegistryError,
            TigerGraphError,
            ValueError,
            RuntimeError,
        ) as exc:
            return self._handle_graph_error(
                updated,
                exc,
            )

        if subgraph is None:
            return self._handle_graph_error(
                updated,
                InvestigationNodeError(
                    "TigerGraph returned no investigation subgraph.",
                ),
            )

        return self._apply_subgraph(
            updated,
            subgraph=subgraph,
            query_name=query_name,
            target=target,
        )

    def _resolve_target(
        self,
        state: AgentRuntimeState,
    ) -> dict[str, str] | None:
        """Resolve the graph root entity from the investigation trigger."""
        trigger = state.get("trigger", {})

        if not isinstance(trigger, dict):
            return None

        trigger_metadata = trigger.get("metadata")

        if not isinstance(trigger_metadata, dict):
            trigger_metadata = {}

        explicit_type = (
            trigger_metadata.get("target_type")
            or trigger_metadata.get("node_type")
        )

        candidates = (
            ("transaction_id", "transaction"),
            ("customer_id", "customer"),
            ("account_id", "account"),
        )

        for field_name, inferred_type in candidates:
            value = trigger.get(field_name)

            if value:
                return {
                    "node_id": str(value),
                    "node_type": str(
                        explicit_type or inferred_type,
                    ),
                }

        metadata_node_id = trigger_metadata.get(
            "node_id",
        )

        if metadata_node_id:
            return {
                "node_id": str(metadata_node_id),
                "node_type": str(
                    explicit_type or "unknown",
                ),
            }

        return None

    def _resolve_query(
        self,
        state: AgentRuntimeState,
    ) -> str | None:
        """Resolve the configured TigerGraph investigation query."""
        trigger = state.get("trigger", {})

        if not isinstance(trigger, dict):
            trigger = {}

        trigger_metadata = trigger.get("metadata")

        if not isinstance(trigger_metadata, dict):
            trigger_metadata = {}

        query_name = trigger_metadata.get(
            "investigation_query",
        )

        if query_name:
            return str(query_name)

        configured_query = getattr(
            self.settings,
            "tigergraph_investigation_query",
            "",
        )

        if configured_query:
            return str(configured_query)

        return None

    @staticmethod
    def _build_parameters(
        state: AgentRuntimeState,
        target: dict[str, str],
    ) -> dict[str, Any]:
        """Build safe query parameters for TigerGraph."""
        trigger = state.get("trigger", {})

        if not isinstance(trigger, dict):
            trigger = {}

        trigger_metadata = trigger.get("metadata")

        parameters: dict[str, Any] = {}

        if isinstance(trigger_metadata, dict):
            configured = trigger_metadata.get(
                "query_parameters",
            )

            if isinstance(configured, dict):
                parameters.update(configured)

        parameters.setdefault(
            "node_id",
            target["node_id"],
        )

        parameters.setdefault(
            "root_node_id",
            target["node_id"],
        )

        return parameters

    @staticmethod
    def _resolve_depth(
        state: AgentRuntimeState,
    ) -> int:
        """Resolve and bound graph traversal depth."""
        metadata = state.get("metadata", {})

        if not isinstance(metadata, dict):
            metadata = {}

        value = metadata.get(
            "graph_depth",
            2,
        )

        try:
            depth = int(value)
        except (TypeError, ValueError):
            depth = 2

        return max(0, min(depth, 10))

    @staticmethod
    def _resolve_limit(
        state: AgentRuntimeState,
    ) -> int:
        """Resolve and bound graph result size."""
        metadata = state.get("metadata", {})

        if not isinstance(metadata, dict):
            metadata = {}

        value = metadata.get(
            "graph_limit",
            100,
        )

        try:
            limit = int(value)
        except (TypeError, ValueError):
            limit = 100

        return max(1, min(limit, 1000))

    @staticmethod
    def _apply_subgraph(
        state: AgentRuntimeState,
        *,
        subgraph: InvestigationSubgraph,
        query_name: str,
        target: dict[str, str],
    ) -> AgentRuntimeState:
        """Store the investigation subgraph in runtime state."""
        now = utc_now()

        updated = dict(state)

        updated["graph"] = subgraph
        updated["updated_at"] = now

        metadata = dict(
            state.get("metadata", {}),
        )

        metadata["graph_status"] = "completed"

        metadata["graph_investigation"] = {
            "query_name": query_name,
            "root_node_id": target["node_id"],
            "root_node_type": target["node_type"],
            "node_count": subgraph.node_count,
            "edge_count": subgraph.edge_count,
            "depth": subgraph.depth,
            "collected_at": now.isoformat(),
        }

        updated["metadata"] = metadata

        return updated

    @staticmethod
    def _handle_unavailable_graph(
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        """Handle an unavailable TigerGraph connection."""
        updated = dict(state)

        updated = add_error(
            updated,
            (
                "TigerGraph is not configured; "
                "graph investigation could not run."
            ),
        )

        metadata = dict(
            updated.get("metadata", {}),
        )

        metadata["graph_status"] = "unavailable"
        metadata["graph_investigation_completed"] = False

        updated["metadata"] = metadata
        updated["updated_at"] = utc_now()

        return updated

    @staticmethod
    def _handle_missing_target(
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        """Handle a trigger without a graph investigation target."""
        updated = add_error(
            state,
            (
                "Investigation trigger does not contain "
                "a graph investigation target."
            ),
        )

        metadata = dict(
            updated.get("metadata", {}),
        )

        metadata["graph_status"] = "target_missing"
        metadata["graph_investigation_completed"] = False

        updated["metadata"] = metadata

        return updated

    @staticmethod
    def _handle_missing_query(
        state: AgentRuntimeState,
    ) -> AgentRuntimeState:
        """Handle a missing TigerGraph investigation query."""
        updated = add_error(
            state,
            (
                "No TigerGraph investigation query was configured "
                "for this investigation."
            ),
        )

        metadata = dict(
            updated.get("metadata", {}),
        )

        metadata["graph_status"] = "query_not_configured"
        metadata["graph_investigation_completed"] = False

        updated["metadata"] = metadata

        return updated

    @staticmethod
    def _handle_graph_error(
        state: AgentRuntimeState,
        error: Exception,
    ) -> AgentRuntimeState:
        """Handle graph investigation failures consistently."""
        updated = add_error(
            state,
            f"Graph investigation failed: {error}",
        )

        metadata = dict(
            updated.get("metadata", {}),
        )

        metadata["graph_status"] = "error"
        metadata["graph_investigation_completed"] = False
        metadata["graph_error_type"] = type(error).__name__

        updated["metadata"] = metadata

        return updated


def investigate_node(
    state: AgentRuntimeState,
    settings: Settings,
) -> AgentRuntimeState:
    """Functional wrapper for the investigation node."""
    return InvestigationNode(
        settings=settings,
    ).run(state)