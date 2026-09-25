"use client";

import { useCallback, useEffect, useState } from "react";
import { casesApi, investigationsApi, healthApi } from "@/lib/api";
import type { Case } from "@/types/case";

/* -------------------------------------------------------------------------- */
/* Types                                                                      */
/* -------------------------------------------------------------------------- */

export interface DashboardStats {
  /** Cases in an active pipeline state, counted from the cases API. */
  activeCases: number;
  /** Cases the backend classified as high risk. */
  highRiskCases: number;
  /** Total cases returned by the backend. */
  totalCases: number;
  /** Investigations currently tracked by the backend. */
  activeInvestigations: number;
  /** Mean of case risk_score (0-100). This is RISK, not accuracy. */
  meanRiskScore: number | null;
  /**
   * False when the benchmark endpoint reports that the ground-truth answer key
   * is unavailable. The UI must not present an accuracy figure in that case.
   */
  accuracyAvailable: boolean;
}

export interface HealthStatus {
  agent: boolean;
  graph: boolean;
  model: boolean;
  engine: boolean;
  backendOnline: boolean;
}

interface ReadinessPayload {
  status?: string;
  tigergraph_configured?: boolean;
  tigergraph_mcp_configured?: boolean;
  llm_configured?: boolean;
  embeddings_configured?: boolean;
  vector_store_configured?: boolean;
}

/* -------------------------------------------------------------------------- */
/* Helpers                                                                    */
/* -------------------------------------------------------------------------- */

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  return "An unexpected error occurred.";
}

function asArray<T>(settled: PromiseSettledResult<unknown>): T[] {
  if (settled.status !== "fulfilled") return [];
  return Array.isArray(settled.value) ? (settled.value as T[]) : [];
}

/* -------------------------------------------------------------------------- */
/* useDashboardStats                                                          */
/* -------------------------------------------------------------------------- */

export function useDashboardStats(refreshIntervalMs = 15000) {
  const [stats, setStats] = useState<DashboardStats>({
    activeCases: 0,
    highRiskCases: 0,
    totalCases: 0,
    activeInvestigations: 0,
    meanRiskScore: null,
    accuracyAvailable: false,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [allCasesRaw, highRiskRaw, investigationsRaw, benchmarkRaw] =
        await Promise.allSettled([
          casesApi.list<unknown>(),
          casesApi.list<unknown>({ risk_level: "high" }),
          investigationsApi.list<unknown>(),
          import("@/lib/api").then((m) =>
            m.benchmarkApi.run<{ ground_truth_available?: boolean }>(),
          ),
        ]);

      const allCases = asArray<Case>(allCasesRaw);
      const highRiskCases = asArray<Case>(highRiskRaw);
      const investigations = asArray<unknown>(investigationsRaw);

      const activeCases = allCases.filter((c) =>
        [
          "open",
          "investigating",
          "awaiting_evidence",
          "awaiting_approval",
          "escalated",
        ].includes(c.status),
      ).length;

      const riskScores = allCases
        .map((c) => c.risk_score)
        .filter((v): v is number => typeof v === "number" && !Number.isNaN(v));

      const meanRiskScore =
        riskScores.length > 0
          ? Math.round(
              (riskScores.reduce((a, b) => a + b, 0) / riskScores.length) *
                100,
            )
          : null;

      const groundTruthAvailable =
        benchmarkRaw.status === "fulfilled" &&
        benchmarkRaw.value?.ground_truth_available === true;

      setStats({
        activeCases,
        highRiskCases: highRiskCases.length,
        totalCases: allCases.length,
        activeInvestigations: investigations.length,
        meanRiskScore,
        accuracyAvailable: groundTruthAvailable,
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
/*                                                                             */
/* Configuration flags (tigergraph_configured, llm_configured, ...) are only   */
/* exposed by /health/readiness. The liveness endpoint /health does not       */
/* include them, so the readiness probe is the authoritative source.           */
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
      const res = await healthApi.readiness<ReadinessPayload>();

      setHealth({
        agent: res.status === "ok",
        graph: res.tigergraph_configured ?? false,
        model: res.llm_configured ?? false,
        engine: res.status === "ok",
        backendOnline: true,
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
    [caseId],
  );

  return { executeAction };
}
