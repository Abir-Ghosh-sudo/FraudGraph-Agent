"use client";

import { useCallback, useEffect, useState } from "react";

import { casesApi } from "@/lib/api";
import type {
  Case,
  CaseCreate,
  CaseUpdate,
} from "@/types/case";

interface UseCasesOptions {
  status?: string;
  risk_level?: string;
  enabled?: boolean;
}

interface UseCasesResult {
  cases: Case[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

interface UseCaseResult {
  caseData: Case | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  createCase: (payload: CaseCreate) => Promise<Case>;
  updateCase: (payload: CaseUpdate) => Promise<Case>;
  addFinding: (payload: unknown) => Promise<Case>;
  addDecision: (payload: unknown) => Promise<Case>;
  addAction: (payload: unknown) => Promise<Case>;
  setOutcome: (payload: unknown) => Promise<Case>;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred.";
}

function normalizeCaseList(payload: unknown): Case[] {
  if (Array.isArray(payload)) {
    return payload as Case[];
  }

  if (
    payload &&
    typeof payload === "object" &&
    "items" in payload &&
    Array.isArray(payload.items)
  ) {
    return payload.items as Case[];
  }

  if (
    payload &&
    typeof payload === "object" &&
    "cases" in payload &&
    Array.isArray(payload.cases)
  ) {
    return payload.cases as Case[];
  }

  return [];
}

/* -------------------------------------------------------------------------- */
/* Case collection                                                            */
/* -------------------------------------------------------------------------- */

export function useCases(
  options: UseCasesOptions = {},
): UseCasesResult {
  const {
    status,
    risk_level,
    enabled = true,
  } = options;

  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState<boolean>(enabled);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!enabled) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await casesApi.list<unknown>({
        status,
        risk_level,
      });

      setCases(normalizeCaseList(response));
    } catch (err) {
      setError(getErrorMessage(err));
      setCases([]);
    } finally {
      setLoading(false);
    }
  }, [enabled, risk_level, status]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    cases,
    loading,
    error,
    refresh,
  };
}

/* -------------------------------------------------------------------------- */
/* Single case                                                                */
/* -------------------------------------------------------------------------- */

export function useCase(
  caseId: string | null | undefined,
): UseCaseResult {
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [loading, setLoading] = useState<boolean>(Boolean(caseId));
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!caseId) {
      setCaseData(null);
      setLoading(false);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await casesApi.get<Case>(caseId);
      setCaseData(response);
    } catch (err) {
      setError(getErrorMessage(err));
      setCaseData(null);
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const createCase = useCallback(
    async (payload: CaseCreate): Promise<Case> => {
      setError(null);

      try {
        const created = await casesApi.create<Case>(payload);
        setCaseData(created);
        return created;
      } catch (err) {
        const message = getErrorMessage(err);
        setError(message);
        throw err;
      }
    },
    [],
  );

  const updateCase = useCallback(
    async (payload: CaseUpdate): Promise<Case> => {
      if (!caseId) {
        const error = new Error("A case ID is required.");
        setError(error.message);
        throw error;
      }

      setError(null);

      try {
        const updated = await casesApi.update<Case>(
          caseId,
          payload,
        );

        setCaseData(updated);

        return updated;
      } catch (err) {
        const message = getErrorMessage(err);
        setError(message);
        throw err;
      }
    },
    [caseId],
  );

  const addFinding = useCallback(
    async (payload: unknown): Promise<Case> => {
      if (!caseId) {
        const error = new Error("A case ID is required.");
        setError(error.message);
        throw error;
      }

      setError(null);

      try {
        const updated = await casesApi.addFinding<Case>(
          caseId,
          payload,
        );

        setCaseData(updated);

        return updated;
      } catch (err) {
        const message = getErrorMessage(err);
        setError(message);
        throw err;
      }
    },
    [caseId],
  );

  const addDecision = useCallback(
    async (payload: unknown): Promise<Case> => {
      if (!caseId) {
        const error = new Error("A case ID is required.");
        setError(error.message);
        throw error;
      }

      setError(null);

      try {
        const updated = await casesApi.addDecision<Case>(
          caseId,
          payload,
        );

        setCaseData(updated);

        return updated;
      } catch (err) {
        const message = getErrorMessage(err);
        setError(message);
        throw err;
      }
    },
    [caseId],
  );

  const addAction = useCallback(
    async (payload: unknown): Promise<Case> => {
      if (!caseId) {
        const error = new Error("A case ID is required.");
        setError(error.message);
        throw error;
      }

      setError(null);

      try {
        const updated = await casesApi.addAction<Case>(
          caseId,
          payload,
        );

        setCaseData(updated);

        return updated;
      } catch (err) {
        const message = getErrorMessage(err);
        setError(message);
        throw err;
      }
    },
    [caseId],
  );

  const setOutcome = useCallback(
    async (payload: unknown): Promise<Case> => {
      if (!caseId) {
        const error = new Error("A case ID is required.");
        setError(error.message);
        throw error;
      }

      setError(null);

      try {
        const updated = await casesApi.setOutcome<Case>(
          caseId,
          payload,
        );

        setCaseData(updated);

        return updated;
      } catch (err) {
        const message = getErrorMessage(err);
        setError(message);
        throw err;
      }
    },
    [caseId],
  );

  return {
    caseData,
    loading,
    error,
    refresh,
    createCase,
    updateCase,
    addFinding,
    addDecision,
    addAction,
    setOutcome,
  };
}

export default useCase;