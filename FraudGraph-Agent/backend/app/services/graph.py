from __future__ import annotations

from typing import Any

from backend.agent.tools.graph import GraphInvestigationTool
from backend.app.config import Settings
from backend.app.logging import get_logger
from backend.app.schemas.graph import (
    GraphQueryRequest,
    GraphQueryResult,
    InvestigationSubgraph,
)
from backend.app.services.relational_graph import RelationalFraudGraph
from backend.tigergraph.client import TigerGraphClient
from backend.tigergraph.mcp import (
    TigerGraphMCPClient,
    TigerGraphMCPError,
)

logger = get_logger(__name__)


class GraphService:
    def __init__(
        self,
        settings: Settings,
        client: TigerGraphClient | None = None,
        tool: GraphInvestigationTool | None = None,
        relational: RelationalFraudGraph | None = None,
    ) -> None:
        self.settings = settings

        if client is None and tool is None:
            client = TigerGraphClient(settings)

        self.client = client

        if tool is not None:
            self.tool = tool
        else:
            self.tool = GraphInvestigationTool(
                settings=settings,
            )

        # Derived from the raw ledger. Used only when TigerGraph cannot answer.
        self.relational = relational

    def is_configured(self) -> bool:
        return self.settings.tigergraph_configured

    def _relational_or_none(self) -> RelationalFraudGraph | None:
        graph = self.relational
        if graph is not None and not graph.is_empty:
            return graph
        return None

    def health(self) -> dict[str, Any]:
        if not self.is_configured():
            fallback = self._relational_or_none()
            if fallback is not None:
                return {
                    "configured": False,
                    "healthy": True,
                    "transport": "relational",
                    "message": (
                        "TigerGraph is not configured; serving the graph "
                        "derived from the raw transaction ledger."
                    ),
                    **fallback.stats(),
                }
            return {
                "configured": False,
                "healthy": False,
                "message": (
                    "TigerGraph is not configured. Set TIGERGRAPH_HOST and "
                    "TIGERGRAPH_GRAPH_NAME, plus TIGERGRAPH_API_TOKEN or "
                    "TIGERGRAPH_USERNAME/TIGERGRAPH_PASSWORD."
                ),
            }

        # When the MCP server is enabled, ask it to report connectivity: it
        # knows how to authenticate against Cloud instances, including the
        # token/allowlist rules the raw REST++ client does not cover.
        if self.settings.tigergraph_mcp_enabled:
            mcp_health = self._mcp_health()
            if mcp_health is not None:
                return {"configured": True, **mcp_health}

        if self.client is None:
            self.client = TigerGraphClient(
                self.settings,
            )

        result = self.client.health_check()

        return {
            "configured": True,
            **result,
        }

    def _mcp_health(self) -> dict[str, Any] | None:
        """Probe TigerGraph through the MCP server.

        Returns None when the MCP route is not usable, so the caller can fall
        back to the direct client. Any real failure is reported rather than
        hidden behind a healthy-looking result.
        """
        client: TigerGraphMCPClient | None = None
        try:
            client = TigerGraphMCPClient(self.settings)
            if not client.is_enabled():
                return None
            result = client.health()
        except TigerGraphMCPError as exc:
            logger.warning("tigergraph mcp health probe failed", error=str(exc))
            return {
                "healthy": False,
                "transport": "mcp",
                "message": f"MCP server unreachable: {exc}",
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("tigergraph mcp health probe errored", error=str(exc))
            return {
                "healthy": False,
                "transport": "mcp",
                "message": f"MCP health probe failed: {exc}",
            }
        finally:
            if client is not None:
                client.close()

        if not result.success:
            return {
                "healthy": False,
                "transport": "mcp",
                "message": result.error or result.summary or "MCP reported unhealthy",
            }

        # `list_connections` succeeding only means the server answered. The
        # profile itself carries `connected`, and that is what determines
        # whether TigerGraph is actually usable.
        profiles = []
        data = result.data
        if isinstance(data, dict):
            raw = data.get("profiles")
            if isinstance(raw, list):
                profiles = [p for p in raw if isinstance(p, dict)]

        if profiles:
            connected = [p for p in profiles if p.get("connected")]
            if not connected:
                names = ", ".join(
                    str(p.get("profile", "unnamed")) for p in profiles
                )
                return {
                    "healthy": False,
                    "transport": "mcp",
                    "profiles": [p.get("profile") for p in profiles],
                    "message": (
                        "MCP server is running, but no configured profile is "
                        f"connected to TigerGraph ({names}). Check the "
                        "credentials and the instance IP allowlist."
                    ),
                }

        return {
            "healthy": True,
            "transport": "mcp",
            "message": result.summary or "MCP connected.",
        }

    def list_queries(self) -> list[dict[str, Any]]:
        if not self.is_configured():
            return []

        return self.tool.available_queries()

    def query(
        self,
        request: GraphQueryRequest,
    ) -> GraphQueryResult:
        if not self.is_configured():
            raise RuntimeError(
                "TigerGraph is not configured."
            )

        return self.tool.run_query(
            query_name=request.query_name,
            parameters=request.parameters,
            limit=request.limit,
        )

    def query_by_name(
        self,
        query_name: str,
        parameters: dict[str, Any] | None = None,
        *,
        limit: int = 100,
    ) -> GraphQueryResult:
        if not query_name.strip():
            raise ValueError(
                "query_name cannot be empty."
            )

        if not self.is_configured():
            raise RuntimeError(
                "TigerGraph is not configured."
            )

        return self.tool.run_query(
            query_name=query_name,
            parameters=parameters,
            limit=limit,
        )

    def investigation(
        self,
        root_node_id: str,
        query_name: str,
        parameters: dict[str, Any] | None = None,
        *,
        depth: int = 2,
        limit: int = 100,
    ) -> InvestigationSubgraph:
        if not self.is_configured():
            fallback = self._relational_or_none()
            if fallback is not None:
                return fallback.traverse(
                    root_node_id,
                    depth=depth,
                    limit=limit,
                )
            raise RuntimeError(
                "TigerGraph is not configured."
            )

        if not root_node_id.strip():
            raise ValueError(
                "root_node_id cannot be empty."
            )

        if not 0 <= depth <= 10:
            raise ValueError(
                "depth must be between 0 and 10."
            )

        result = self.tool.run_query(
            query_name=query_name,
            parameters=parameters,
            limit=limit,
        )

        return self.tool.build_subgraph(
            root_node_id=root_node_id,
            rows=result.rows,
            depth=depth,
        )

    def investigate_rows(
        self,
        root_node_id: str,
        rows: list[dict[str, Any]],
        *,
        depth: int = 2,
    ) -> InvestigationSubgraph:
        if not root_node_id.strip():
            raise ValueError(
                "root_node_id cannot be empty."
            )

        return self.tool.build_subgraph(
            root_node_id=root_node_id,
            rows=rows,
            depth=depth,
        )

    def collect_graph_evidence(
        self,
        query_name: str,
        parameters: dict[str, Any] | None = None,
        *,
        limit: int = 100,
    ) -> dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError(
                "TigerGraph is not configured."
            )

        result = self.tool.investigate(
            query_name=query_name,
            parameters=parameters,
            limit=limit,
        )

        return {
            "query": result["query"].model_dump(),
            "nodes": [
                node.model_dump()
                for node in result["nodes"]
            ],
            "edges": [
                edge.model_dump()
                for edge in result["edges"]
            ],
            "evidence": result["evidence"],
            "provenance": {
                "source": "tigergraph",
                "query_name": query_name,
                "parameter_names": sorted(
                    (parameters or {}).keys(),
                ),
                "row_count": result["query"].count,
                "execution_time_ms": (
                    result["query"].execution_time_ms
                ),
            },
        }

    def describe_query(
        self,
        query_name: str,
    ) -> dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError(
                "TigerGraph is not configured."
            )

        definition = self.tool.runner.get(
            query_name,
        )

        return {
            "name": definition.name,
            "file": str(definition.file_path),
            "parameters": list(
                definition.parameters,
            ),
            "description": definition.description,
        }

    def close(self) -> None:
        client = self.client

        if client is not None:
            client.close()