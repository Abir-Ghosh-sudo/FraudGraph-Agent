from __future__ import annotations

from collections import defaultdict
from typing import Any

from backend.app.config import Settings
from backend.app.schemas.graph import (
    GraphEdge,
    GraphNode,
    GraphPath,
    GraphQueryResult,
    InvestigationSubgraph,
)
from backend.tigergraph.client import TigerGraphClient
from backend.tigergraph.query_runner import (
    QueryExecution,
    TigerGraphQueryRunner,
)


class GraphToolError(RuntimeError):
    """Raised when an agent graph operation cannot be completed."""


class GraphInvestigationTool:
    def __init__(
        self,
        settings: Settings,
        runner: TigerGraphQueryRunner | None = None,
    ) -> None:
        self.settings = settings

        if runner is None:
            client = TigerGraphClient(settings)
            runner = TigerGraphQueryRunner(
                settings=settings,
                client=client,
            )

        self.runner = runner

    def available_queries(self) -> list[dict[str, Any]]:
        return [
            {
                "name": query.name,
                "parameters": list(query.parameters),
                "description": query.description,
                "file": str(query.file_path),
            }
            for query in self.runner.list_queries()
        ]

    def run_query(
        self,
        query_name: str,
        parameters: dict[str, Any] | None = None,
        *,
        limit: int = 100,
    ) -> GraphQueryResult:
        if not 1 <= limit <= 1000:
            raise ValueError(
                "limit must be between 1 and 1000."
            )

        execution = self.runner.execute(
            query_name=query_name,
            parameters=parameters,
        )

        rows = execution.rows[:limit]

        return GraphQueryResult(
            query_name=query_name,
            rows=rows,
            count=len(rows),
            execution_time_ms=execution.execution_time_ms,
        )

    def investigate(
        self,
        query_name: str,
        parameters: dict[str, Any] | None = None,
        *,
        limit: int = 100,
    ) -> dict[str, Any]:
        result = self.run_query(
            query_name=query_name,
            parameters=parameters,
            limit=limit,
        )

        nodes, edges = self._extract_graph_entities(
            result.rows,
        )

        return {
            "query": result,
            "nodes": nodes,
            "edges": edges,
            "evidence": self._build_relationship_evidence(
                nodes,
                edges,
            ),
        }

    def build_subgraph(
        self,
        root_node_id: str,
        rows: list[dict[str, Any]],
        *,
        depth: int = 1,
    ) -> InvestigationSubgraph:
        if not root_node_id.strip():
            raise ValueError(
                "root_node_id cannot be empty."
            )

        if not 0 <= depth <= 10:
            raise ValueError(
                "depth must be between 0 and 10."
            )

        nodes, edges = self._extract_graph_entities(rows)

        reachable_nodes = self._limit_to_depth(
            root_node_id=root_node_id,
            nodes=nodes,
            edges=edges,
            depth=depth,
        )

        reachable_ids = {
            node.node_id
            for node in reachable_nodes
        }

        reachable_edges = [
            edge
            for edge in edges
            if edge.source_id in reachable_ids
            and edge.target_id in reachable_ids
        ]

        paths = self._build_paths(
            root_node_id=root_node_id,
            nodes=reachable_nodes,
            edges=reachable_edges,
        )

        return InvestigationSubgraph(
            root_node_id=root_node_id,
            nodes=reachable_nodes,
            edges=reachable_edges,
            paths=paths,
            depth=depth,
            node_count=len(reachable_nodes),
            edge_count=len(reachable_edges),
        )

    def _extract_graph_entities(
        self,
        rows: list[dict[str, Any]],
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: dict[str, GraphNode] = {}
        edges: dict[str, GraphEdge] = {}

        for row in rows:
            self._extract_nodes_from_row(
                row,
                nodes,
            )

            self._extract_edges_from_row(
                row,
                edges,
            )

        return (
            list(nodes.values()),
            list(edges.values()),
        )

    def _extract_nodes_from_row(
        self,
        row: dict[str, Any],
        nodes: dict[str, GraphNode],
    ) -> None:
        candidate_nodes = row.get("nodes")

        if isinstance(candidate_nodes, list):
            for item in candidate_nodes:
                node = self._node_from_value(item)

                if node is not None:
                    nodes[node.node_id] = node

        candidate_vertex = row.get("vertex")

        if candidate_vertex is not None:
            node = self._node_from_value(candidate_vertex)

            if node is not None:
                nodes[node.node_id] = node

        if self._looks_like_vertex(row):
            node = self._node_from_value(row)

            if node is not None:
                nodes[node.node_id] = node

    def _extract_edges_from_row(
        self,
        row: dict[str, Any],
        edges: dict[str, GraphEdge],
    ) -> None:
        candidate_edges = row.get("edges")

        if isinstance(candidate_edges, list):
            for item in candidate_edges:
                edge = self._edge_from_value(item)

                if edge is not None:
                    edges[self._edge_key(edge)] = edge

        candidate_edge = row.get("edge")

        if candidate_edge is not None:
            edge = self._edge_from_value(candidate_edge)

            if edge is not None:
                edges[self._edge_key(edge)] = edge

        if self._looks_like_edge(row):
            edge = self._edge_from_value(row)

            if edge is not None:
                edges[self._edge_key(edge)] = edge

    @staticmethod
    def _looks_like_vertex(
        value: dict[str, Any],
    ) -> bool:
        return bool(
            value.get("v_id")
            or value.get("vertex_id")
            or (
                value.get("id")
                and (
                    value.get("v_type")
                    or value.get("vertex_type")
                    or value.get("type")
                )
            )
        )

    @staticmethod
    def _looks_like_edge(
        value: dict[str, Any],
    ) -> bool:
        return bool(
            (
                value.get("from_id")
                and value.get("to_id")
            )
            or (
                value.get("source_id")
                and value.get("target_id")
            )
            or (
                value.get("from")
                and value.get("to")
            )
        )

    @staticmethod
    def _node_from_value(
        value: Any,
    ) -> GraphNode | None:
        if not isinstance(value, dict):
            return None

        node_id = (
            value.get("v_id")
            or value.get("vertex_id")
            or value.get("id")
        )

        if node_id is None:
            return None

        node_type = (
            value.get("v_type")
            or value.get("vertex_type")
            or value.get("type")
            or "unknown"
        )

        properties = value.get("attributes")

        if not isinstance(properties, dict):
            properties = value.get("properties")

        if not isinstance(properties, dict):
            properties = {
                key: item
                for key, item in value.items()
                if key not in {
                    "id",
                    "v_id",
                    "vertex_id",
                    "v_type",
                    "vertex_type",
                    "type",
                    "attributes",
                    "properties",
                }
            }

        label = (
            value.get("label")
            or value.get("name")
            or str(node_id)
        )

        return GraphNode(
            node_id=str(node_id),
            node_type=str(node_type),
            label=str(label),
            properties=properties,
        )

    @staticmethod
    def _edge_from_value(
        value: Any,
    ) -> GraphEdge | None:
        if not isinstance(value, dict):
            return None

        source_id = (
            value.get("from_id")
            or value.get("source_id")
            or value.get("from")
        )

        target_id = (
            value.get("to_id")
            or value.get("target_id")
            or value.get("to")
        )

        if source_id is None or target_id is None:
            return None

        edge_type = (
            value.get("e_type")
            or value.get("edge_type")
            or value.get("type")
            or value.get("relationship")
            or "unknown"
        )

        edge_id = value.get("edge_id") or value.get("id")

        properties = value.get("attributes")

        if not isinstance(properties, dict):
            properties = value.get("properties")

        if not isinstance(properties, dict):
            properties = {}

        return GraphEdge(
            edge_id=str(edge_id) if edge_id else None,
            source_id=str(source_id),
            target_id=str(target_id),
            edge_type=str(edge_type),
            properties=properties,
        )

    @staticmethod
    def _edge_key(
        edge: GraphEdge,
    ) -> str:
        return "|".join(
            [
                edge.source_id,
                edge.target_id,
                edge.edge_type,
            ]
        )

    @staticmethod
    def _limit_to_depth(
        root_node_id: str,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
        depth: int,
    ) -> list[GraphNode]:
        if depth == 0:
            return [
                node
                for node in nodes
                if node.node_id == root_node_id
            ]

        adjacency: dict[str, set[str]] = defaultdict(set)

        for edge in edges:
            adjacency[edge.source_id].add(
                edge.target_id,
            )
            adjacency[edge.target_id].add(
                edge.source_id,
            )

        visited = {root_node_id}
        frontier = {root_node_id}

        for _ in range(depth):
            next_frontier: set[str] = set()

            for node_id in frontier:
                for neighbour in adjacency.get(
                    node_id,
                    set(),
                ):
                    if neighbour not in visited:
                        visited.add(neighbour)
                        next_frontier.add(neighbour)

            frontier = next_frontier

            if not frontier:
                break

        return [
            node
            for node in nodes
            if node.node_id in visited
        ]

    @staticmethod
    def _build_paths(
        root_node_id: str,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
    ) -> list[GraphPath]:
        node_map = {
            node.node_id: node
            for node in nodes
        }

        paths: list[GraphPath] = []

        for edge in edges:
            if (
                edge.source_id != root_node_id
                and edge.target_id != root_node_id
            ):
                continue

            source = node_map.get(edge.source_id)
            target = node_map.get(edge.target_id)

            if source is None or target is None:
                continue

            paths.append(
                GraphPath(
                    nodes=[source, target],
                    edges=[edge],
                    length=1,
                    relationship=edge.edge_type,
                )
            )

        return paths

    @staticmethod
    def _build_relationship_evidence(
        nodes: list[GraphNode],
        edges: list[GraphEdge],
    ) -> list[dict[str, Any]]:
        node_map = {
            node.node_id: node
            for node in nodes
        }

        evidence: list[dict[str, Any]] = []

        for edge in edges:
            source = node_map.get(edge.source_id)
            target = node_map.get(edge.target_id)

            if source is None or target is None:
                continue

            evidence.append(
                {
                    "source_node_id": source.node_id,
                    "target_node_id": target.node_id,
                    "relationship": edge.edge_type,
                    "explanation": (
                        f"{source.node_type}:{source.node_id} "
                        f"is connected to "
                        f"{target.node_type}:{target.node_id} "
                        f"through {edge.edge_type}."
                    ),
                    "confidence": 1.0,
                }
            )

        return evidence

    @staticmethod
    def execution_metadata(
        execution: QueryExecution,
    ) -> dict[str, Any]:
        return {
            "query_name": execution.query_name,
            "execution_time_ms": execution.execution_time_ms,
            "parameter_names": list(
                execution.parameter_names,
            ),
            "row_count": len(execution.rows),
        }