"use client";

import { useCallback, useEffect, useState } from "react";
import { casesApi, investigationsApi, actionsApi, healthApi } from "@/lib/api";
import type { Case } from "@/types/case";

/* -------------------------------------------------------------------------- */
/* Types                                                                      */
/* -------------------------------------------------------------------------- */

export interface DashboardStats {
  activeCases: number;
  highRiskCases: number;
  pendingActions: number;
  modelConfidence: number;
  totalCases: number;
}

export interface HealthStatus {
  agent: boolean;
  graph: boolean;
  model: boolean;
  engine: boolean;
  backendOnline: boolean;
}

/* -------------------------------------------------------------------------- */
/* useDashboardStats                                                          */
/* -------------------------------------------------------------------------- */

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  return "An unexpected error occurred.";
}

export function useDashboardStats(refreshIntervalMs = 15000) {
  const [stats, setStats] = useState<DashboardStats>({
    activeCases: 0,
    highRiskCases: 0,
    pendingActions: 0,
    modelConfidence: 91,
    totalCases: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch cases in parallel
      const [allCasesRaw, highRiskRaw, actionsRaw] = await Promise.allSettled([
        casesApi.list<unknown>(),
        casesApi.list<unknown>({ risk_level: "high" }),
        actionsApi.list<unknown>({ status: "proposed" }),
      ]);

      const allCases: Case[] = allCasesRaw.status === "fulfilled"
        ? Array.isArray(allCasesRaw.value) ? (allCasesRaw.value as Case[]) : []
        : [];

      const highRiskCases: Case[] = highRiskRaw.status === "fulfilled"
        ? Array.isArray(highRiskRaw.value) ? (highRiskRaw.value as Case[]) : []
        : [];

      const pendingActions = actionsRaw.status === "fulfilled"
        ? Array.isArray(actionsRaw.value) ? (actionsRaw.value as unknown[]).length : 0
        : 0;

      // Active cases = open + investigating + awaiting
      const activeCases = allCases.filter((c) =>
        ["open", "investigating", "awaiting_evidence", "awaiting_approval", "escalated"].includes(c.status)
      ).length;

      // Compute average model confidence from risk_score if available
      const riskScores = allCases
        .filter((c) => c.risk_score !== null && c.risk_score !== undefined)
        .map((c) => (c.risk_score as number) * 100);

      const modelConfidence =
        riskScores.length > 0
          ? Math.round(riskScores.reduce((a, b) => a + b, 0) / riskScores.length)
          : 91; // fallback

      setStats({
        activeCases,
        highRiskCases: highRiskCases.length,
        pendingActions,
        modelConfidence,
        totalCases: allCases.length,
      });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const id = setInterval(() => void refresh(), refreshIntervalMs);
    return () => clearInterval(id);
  }, [refresh, refreshIntervalMs]);

  return { stats, loading, error, refresh };
}

/* -------------------------------------------------------------------------- */
/* useHealthStatus                                                            */
/* -------------------------------------------------------------------------- */

export function useHealthStatus(refreshIntervalMs = 10000) {
  const [health, setHealth] = useState<HealthStatus>({
    agent: false,
    graph: false,
    model: false,
    engine: false,
    backendOnline: false,
  });

  const check = useCallback(async () => {
    try {
      const res = await healthApi.check<{
        status: string;
        tigergraph_configured?: boolean;
        llm_configured?: boolean;
        tigergraph_mcp_configured?: boolean;
        embeddings_configured?: boolean;
      }>();

      setHealth({
        agent: res.status === "ok",
        graph: res.tigergraph_configured ?? false,
        model: res.llm_configured ?? false,
        engine: res.status === "ok",
        backendOnline: res.status === "ok",
      });
    } catch {
      // Check readiness fallback
      try {
        const readiness = await fetch("http://localhost:8000/health/readiness").then((r) => r.json()) as {
          status: string;
          tigergraph_configured?: boolean;
          llm_configured?: boolean;
        };
        setHealth({
          agent: readiness.status === "ok",
          graph: readiness.tigergraph_configured ?? false,
          model: readiness.llm_configured ?? false,
          engine: readiness.status === "ok",
          backendOnline: readiness.status === "ok",
        });
      } catch {
        setHealth({
          agent: false,
          graph: false,
          model: false,
          engine: false,
          backendOnline: false,
        });
      }
    }
  }, []);

  useEffect(() => {
    void check();
    const id = setInterval(() => void check(), refreshIntervalMs);
    return () => clearInterval(id);
  }, [check, refreshIntervalMs]);

  return { health, check };
}

/* -------------------------------------------------------------------------- */
/* useCaseActions                                                             */
/* -------------------------------------------------------------------------- */

export function useCaseActions(caseId: string | null) {
  const executeAction = useCallback(
    async (actionType: string, payload?: Record<string, unknown>) => {
      if (!caseId) return;
      await casesApi.addAction(caseId, {
        action_id: `act_${Date.now()}`,
        action_type: actionType,
        status: "executed",
        rationale: `Agent executed: ${actionType}`,
        requires_approval: false,
        ...payload,
      });
    },
    [caseId]
  );

  return { executeAction };
}
