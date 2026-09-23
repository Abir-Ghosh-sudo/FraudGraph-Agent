from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping


@dataclass(slots=True)
class GraphMatch:
    """A graph entity or relationship returned by graph retrieval."""

    node_id: str
    node_type: str | None = None
    label: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    paths: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "properties": dict(self.properties),
            "score": self.score,
            "paths": list(self.paths),
        }


class GraphRetriever:
    """
    Graph retrieval abstraction for GraphRAG.

    A TigerGraph query function can be injected through `query_fn`.
    A small in-memory graph representation is also supported for local
    development and deterministic tests.
    """

    def __init__(
        self,
        nodes: Iterable[Mapping[str, Any]] | None = None,
        edges: Iterable[Mapping[str, Any]] | None = None,
        query_fn: Callable[..., Any] | None = None,
    ) -> None:
        self._nodes = [dict(node) for node in (nodes or [])]
        self._edges = [dict(edge) for edge in (edges or [])]
        self._query_fn = query_fn

    def retrieve(
        self,
        query: str | None = None,
        *,
        node_id: str | None = None,
        node_type: str | None = None,
        top_k: int = 10,
        depth: int = 2,
        filters: Mapping[str, Any] | None = None,
    ) -> list[GraphMatch]:
        """
        Retrieve graph context around an investigation target.

        External TigerGraph retrieval is preferred when `query_fn` is
        configured. Otherwise the local graph representation is searched.
        """

        if top_k <= 0:
            return []

        if self._query_fn is not None:
            external = self._retrieve_external(
                query=query,
                node_id=node_id,
                node_type=node_type,
                top_k=top_k,
                depth=depth,
                filters=filters,
            )
            if external:
                return external[:top_k]

        return self._retrieve_local(
            query=query,
            node_id=node_id,
            node_type=node_type,
            top_k=top_k,
            depth=depth,
            filters=filters,
        )

    def retrieve_subgraph(
        self,
        node_id: str,
        *,
        depth: int = 2,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Return a compact node/edge subgraph around a root node."""

        if not node_id or depth < 0 or limit <= 0:
            return {
                "root_node_id": node_id,
                "nodes": [],
                "edges": [],
                "depth": 0,
            }

        if self._query_fn is not None:
            result = self._retrieve_external_subgraph(
                node_id=node_id,
                depth=depth,
                limit=limit,
            )
            if result:
                return result

        visited = {str(node_id)}
        frontier = {str(node_id)}
        selected_edges: list[dict[str, Any]] = []

        for _ in range(depth):
            next_frontier: set[str] = set()

            for edge in self._edges:
                source = self._edge_endpoint(
                    edge,
                    "source",
                    "source_id",
                )
                target = self._edge_endpoint(
                    edge,
                    "target",
                    "target_id",
                )

                if source in frontier or target in frontier:
                    if edge not in selected_edges:
                        selected_edges.append(edge)

                    if source:
                        next_frontier.add(source)
                    if target:
                        next_frontier.add(target)

                    if len(selected_edges) >= limit:
                        break

            next_frontier -= visited
            visited.update(next_frontier)
            frontier = next_frontier

            if not frontier or len(visited) >= limit:
                break

        selected_nodes = [
            dict(node)
            for node in self._nodes
            if self._node_id(node) in visited
        ]

        return {
            "root_node_id": str(node_id),
            "nodes": selected_nodes[:limit],
            "edges": selected_edges[:limit],
            "depth": depth,
        }

    def add_node(self, node: Mapping[str, Any]) -> None:
        """Add or replace a graph node."""

        normalized = dict(node)
        node_id = self._node_id(normalized)

        if not node_id:
            raise ValueError("Graph node must contain an id or node_id")

        self._nodes = [
            item
            for item in self._nodes
            if self._node_id(item) != node_id
        ]
        self._nodes.append(normalized)

    def add_edge(self, edge: Mapping[str, Any]) -> None:
        """Add a graph edge."""

        normalized = dict(edge)

        source = self._edge_endpoint(
            normalized,
            "source",
            "source_id",
        )
        target = self._edge_endpoint(
            normalized,
            "target",
            "target_id",
        )

        if not source or not target:
            raise ValueError(
                "Graph edge must contain source/source_id and "
                "target/target_id"
            )

        self._edges.append(normalized)

    def _retrieve_local(
        self,
        query: str | None,
        node_id: str | None,
        node_type: str | None,
        top_k: int,
        depth: int,
        filters: Mapping[str, Any] | None,
    ) -> list[GraphMatch]:
        candidates = self._filtered_nodes(
            node_type=node_type,
            filters=filters,
        )

        query_terms = self._tokenize(query or "")
        results: list[GraphMatch] = []

        for node in candidates:
            current_id = self._node_id(node)

            if node_id and current_id != str(node_id):
                continue

            match = self._normalize_node(node)

            if query_terms:
                match.score = self._score_node(
                    query_terms,
                    match,
                )
                if match.score <= 0:
                    continue
            else:
                match.score = 1.0

            if current_id:
                match.paths = self._related_paths(
                    current_id,
                    depth=depth,
                )

            results.append(match)

        results.sort(
            key=lambda item: (-item.score, item.node_id),
        )

        return results[:top_k]

    def _retrieve_external(
        self,
        *,
        query: str | None,
        node_id: str | None,
        node_type: str | None,
        top_k: int,
        depth: int,
        filters: Mapping[str, Any] | None,
    ) -> list[GraphMatch]:
        try:
            result = self._query_fn(
                query=query,
                node_id=node_id,
                node_type=node_type,
                top_k=top_k,
                depth=depth,
                filters=filters,
            )
        except TypeError:
            try:
                result = self._query_fn(
                    query,
                    node_id,
                    top_k,
                )
            except Exception:
                return []
        except Exception:
            return []

        if result is None:
            return []

        if isinstance(result, Mapping):
            result = result.get(
                "results",
                result.get(
                    "nodes",
                    result.get("vertices", []),
                ),
            )

        if isinstance(result, Mapping):
            result = [result]

        if not isinstance(result, Iterable) or isinstance(
            result,
            (str, bytes),
        ):
            return []

        matches: list[GraphMatch] = []

        for item in result:
            if isinstance(item, GraphMatch):
                matches.append(item)
            elif isinstance(item, Mapping):
                matches.append(self._normalize_node(item))

        matches.sort(
            key=lambda item: (-item.score, item.node_id),
        )

        return matches

    def _retrieve_external_subgraph(
        self,
        *,
        node_id: str,
        depth: int,
        limit: int,
    ) -> dict[str, Any] | None:
        try:
            result = self._query_fn(
                operation="subgraph",
                node_id=node_id,
                depth=depth,
                limit=limit,
            )
        except Exception:
            return None

        if not isinstance(result, Mapping):
            return None

        return {
            "root_node_id": str(
                result.get("root_node_id", node_id)
            ),
            "nodes": list(result.get("nodes", []))[:limit],
            "edges": list(result.get("edges", []))[:limit],
            "depth": int(result.get("depth", depth)),
        }

    def _filtered_nodes(
        self,
        *,
        node_type: str | None,
        filters: Mapping[str, Any] | None,
    ) -> list[Mapping[str, Any]]:
        result: list[Mapping[str, Any]] = []

        for node in self._nodes:
            if node_type:
                actual_type = (
                    node.get("node_type")
                    or node.get("type")
                    or node.get("vertex_type")
                )
                if str(actual_type).lower() != str(node_type).lower():
                    continue

            if filters and not self._matches_filters(
                node,
                filters,
            ):
                continue

            result.append(node)

        return result

    @staticmethod
    def _matches_filters(
        node: Mapping[str, Any],
        filters: Mapping[str, Any],
    ) -> bool:
        properties = node.get("properties", {})
        if not isinstance(properties, Mapping):
            properties = {}

        for key, expected in filters.items():
            actual = node.get(key, properties.get(key))

            if isinstance(expected, (list, tuple, set, frozenset)):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False

        return True

    def _related_paths(
        self,
        node_id: str,
        *,
        depth: int,
    ) -> list[dict[str, Any]]:
        if depth <= 0:
            return []

        paths: list[dict[str, Any]] = []

        for edge in self._edges:
            source = self._edge_endpoint(
                edge,
                "source",
                "source_id",
            )
            target = self._edge_endpoint(
                edge,
                "target",
                "target_id",
            )

            if source == node_id or target == node_id:
                paths.append(
                    {
                        "source_id": source,
                        "target_id": target,
                        "edge_type": (
                            edge.get("edge_type")
                            or edge.get("type")
                        ),
                        "properties": dict(
                            edge.get("properties", {})
                            if isinstance(
                                edge.get("properties", {}),
                                Mapping,
                            )
                            else {}
                        ),
                    }
                )

            if len(paths) >= 25:
                break

        return paths

    @staticmethod
    def _normalize_node(
        node: Mapping[str, Any],
    ) -> GraphMatch:
        node_id = GraphRetriever._node_id(node)

        if not node_id:
            raise ValueError(
                "Graph node must contain an id or node_id"
            )

        properties = node.get("properties", {})
        if not isinstance(properties, Mapping):
            properties = {}

        score = node.get(
            "score",
            node.get("similarity", 0.0),
        )

        try:
            score = float(score or 0.0)
        except (TypeError, ValueError):
            score = 0.0

        return GraphMatch(
            node_id=node_id,
            node_type=(
                str(
                    node.get("node_type")
                    or node.get("type")
                    or node.get("vertex_type")
                )
                if (
                    node.get("node_type")
                    or node.get("type")
                    or node.get("vertex_type")
                )
                else None
            ),
            label=(
                str(node.get("label"))
                if node.get("label") is not None
                else None
            ),
            properties=dict(properties),
            score=max(0.0, min(1.0, score)),
            paths=list(node.get("paths", [])),
        )

    @staticmethod
    def _node_id(node: Mapping[str, Any]) -> str:
        value = (
            node.get("node_id")
            or node.get("id")
            or node.get("vertex_id")
        )
        return str(value) if value is not None else ""

    @staticmethod
    def _edge_endpoint(
        edge: Mapping[str, Any],
        primary: str,
        fallback: str,
    ) -> str:
        value = edge.get(primary, edge.get(fallback))
        return str(value) if value is not None else ""

    @staticmethod
    def _tokenize(value: str) -> set[str]:
        return {
            token
            for token in "".join(
                character.lower()
                if character.isalnum()
                else " "
                for character in value
            ).split()
            if len(token) > 1
        }

    @classmethod
    def _score_node(
        cls,
        query_terms: set[str],
        node: GraphMatch,
    ) -> float:
        searchable = " ".join(
            part
            for part in (
                node.node_id,
                node.node_type or "",
                node.label or "",
                " ".join(
                    str(value)
                    for value in node.properties.values()
                ),
            )
            if part
        )

        node_terms = cls._tokenize(searchable)

        if not node_terms:
            return 0.0

        overlap = query_terms.intersection(node_terms)

        return len(overlap) / len(query_terms)