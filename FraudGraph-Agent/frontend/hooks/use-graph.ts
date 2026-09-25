"use client";

import { useCallback, useEffect, useState } from "react";

import { graphApi } from "@/lib/api";

export interface GraphNode {
  id: string;
  type?: string;
  label?: string;
  properties?: Record<string, unknown>;
  risk_score?: number | null;
  risk_level?: string | null;
  [key: string]: unknown;
}

export interface GraphEdge {
  id?: string;
  source: string;
  target: string;
  type?: string;
  label?: string;
  properties?: Record<string, unknown>;
  weight?: number | null;
  [key: string]: unknown;
}

export interface FraudGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: Record<string, unknown>;
}

interface UseGraphOptions {
  caseId?: string | null;
  customerId?: string | null;
  transactionId?: string | null;
  investigationId?: string | null;
  depth?: number;
  enabled?: boolean;
}

interface UseGraphResult {
  graph: FraudGraphData | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred.";
}

function normalizeGraph(payload: unknown): FraudGraphData {
  if (!payload || typeof payload !== "object") {
    return {
      nodes: [],
      edges: [],
    };
  }

  const data = payload as Record<string, unknown>;

  const rawNodes = Array.isArray(data.nodes)
    ? data.nodes
    : [];

  const rawEdges = Array.isArray(data.edges)
    ? data.edges
    : [];

  const normalizedNodes: GraphNode[] = rawNodes.map((n: Record<string, unknown>) => ({
    id: String(n.node_id || n.id || ""),
    type: String(n.node_type || n.type || "unknown"),
    label: String(n.label || n.node_id || n.id || ""),
    properties: (n.properties as Record<string, unknown>) || {},
    risk_score: typeof n.risk_score === "number" ? n.risk_score : null,
    risk_level: typeof n.risk_level === "string" ? n.risk_level : null,
    ...n,
  }));

  const normalizedEdges: GraphEdge[] = rawEdges.map((e: Record<string, unknown>) => ({
    id: e.edge_id ? String(e.edge_id) : e.id ? String(e.id) : undefined,
    source: String(e.source_id || e.source || ""),
    target: String(e.target_id || e.target || ""),
    type: String(e.edge_type || e.type || "connected"),
    label: e.label ? String(e.label) : undefined,
    properties: (e.properties as Record<string, unknown>) || {},
    weight: typeof e.weight === "number" ? e.weight : null,
    ...e,
  }));

  return {
    nodes: normalizedNodes,
    edges: normalizedEdges,
    metadata:
      data.metadata && typeof data.metadata === "object"
        ? (data.metadata as Record<string, unknown>)
        : {
            node_count: data.node_count ?? normalizedNodes.length,
            edge_count: data.edge_count ?? normalizedEdges.length,
            depth: data.depth,
          },
  };
}


export function useGraph(
  options: UseGraphOptions = {},
): UseGraphResult {
  const {
    caseId,
    customerId,
    transactionId,
    investigationId,
    depth,
    enabled = true,
  } = options;

  const [graph, setGraph] =
    useState<FraudGraphData | null>(null);

  const [loading, setLoading] = useState<boolean>(enabled);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!enabled) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await graphApi.get<unknown>({
        case_id: caseId ?? undefined,
        customer_id: customerId ?? undefined,
        transaction_id:
          transactionId ?? undefined,
        investigation_id:
          investigationId ?? undefined,
        depth,
      });

      setGraph(normalizeGraph(response));
    } catch (err) {
      setError(getErrorMessage(err));
      setGraph(null);
    } finally {
      setLoading(false);
    }
  }, [
    caseId,
    customerId,
    depth,
    enabled,
    investigationId,
    transactionId,
  ]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    graph,
    loading,
    error,
    refresh,
  };
}

export default useGraph;