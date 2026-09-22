from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GraphNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str

    node_type: str = Field(
        min_length=1,
    )

    label: str | None = None

    properties: dict[str, Any] = Field(
        default_factory=dict,
    )


class GraphEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    edge_id: str | None = None

    source_id: str

    target_id: str

    edge_type: str = Field(
        min_length=1,
    )

    properties: dict[str, Any] = Field(
        default_factory=dict,
    )


class GraphPath(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: list[GraphNode] = Field(
        default_factory=list,
    )

    edges: list[GraphEdge] = Field(
        default_factory=list,
    )

    length: int = Field(
        default=0,
        ge=0,
    )

    relationship: str | None = None

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class InvestigationSubgraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    root_node_id: str

    nodes: list[GraphNode] = Field(
        default_factory=list,
    )

    edges: list[GraphEdge] = Field(
        default_factory=list,
    )

    paths: list[GraphPath] = Field(
        default_factory=list,
    )

    depth: int = Field(
        default=1,
        ge=0,
    )

    node_count: int = Field(
        default=0,
        ge=0,
    )

    edge_count: int = Field(
        default=0,
        ge=0,
    )


class GraphQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query_name: str = Field(
        min_length=1,
    )

    parameters: dict[str, Any] = Field(
        default_factory=dict,
    )

    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
    )


class GraphQueryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query_name: str

    rows: list[dict[str, Any]] = Field(
        default_factory=list,
    )

    count: int = Field(
        default=0,
        ge=0,
    )

    execution_time_ms: float | None = Field(
        default=None,
        ge=0.0,
    )


class GraphEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_node_id: str

    target_node_id: str

    relationship: str

    path: GraphPath

    explanation: str

    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )