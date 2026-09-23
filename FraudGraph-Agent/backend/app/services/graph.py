from __future__ import annotations

from typing import Any

from backend.agent.tools.graph import GraphInvestigationTool
from backend.app.config import Settings
from backend.app.schemas.graph import (
    GraphQueryRequest,
    GraphQueryResult,
    InvestigationSubgraph,
)
from backend.tigergraph.client import TigerGraphClient


class GraphService:
    def __init__(
        self,
        settings: Settings,
        client: TigerGraphClient | None = None,
        tool: GraphInvestigationTool | None = None,
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

    def is_configured(self) -> bool:
        return self.settings.tigergraph_configured

    def health(self) -> dict[str, Any]:
        if not self.is_configured():
            return {
                "configured": False,
                "healthy": False,
                "message": "TigerGraph is not configured.",
            }

        if self.client is None:
            self.client = TigerGraphClient(
                self.settings,
            )

        result = self.client.health_check()

        return {
            "configured": True,
            **result,
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