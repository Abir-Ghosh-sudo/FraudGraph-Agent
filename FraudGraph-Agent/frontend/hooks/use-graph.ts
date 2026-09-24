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

  return {
    nodes: rawNodes as GraphNode[],
    edges: rawEdges as GraphEdge[],
    metadata:
      data.metadata &&
      typeof data.metadata === "object"
        ? (data.metadata as Record<string, unknown>)
        : undefined,
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