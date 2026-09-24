"use client";

import { useCallback, useEffect, useState } from "react";

import { investigationsApi } from "@/lib/api";

export interface Investigation {
  investigation_id: string;
  case_id?: string | null;
  transaction_id?: string | null;
  customer_id?: string | null;
  status?: string;
  risk_score?: number | null;
  risk_level?: string | null;
  title?: string | null;
  description?: string | null;
  created_at?: string;
  updated_at?: string;
  [key: string]: unknown;
}

interface UseInvestigationsOptions {
  status?: string;
  risk_level?: string;
  enabled?: boolean;
}

interface UseInvestigationsResult {
  investigations: Investigation[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

interface UseInvestigationResult {
  investigation: Investigation | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  createInvestigation: (
    payload: Record<string, unknown>,
  ) => Promise<Investigation>;
  updateInvestigation: (
    payload: Record<string, unknown>,
  ) => Promise<Investigation>;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred.";
}

function normalizeInvestigationList(
  payload: unknown,
): Investigation[] {
  if (Array.isArray(payload)) {
    return payload as Investigation[];
  }

  if (
    payload &&
    typeof payload === "object" &&
    "items" in payload &&
    Array.isArray(payload.items)
  ) {
    return payload.items as Investigation[];
  }

  if (
    payload &&
    typeof payload === "object" &&
    "investigations" in payload &&
    Array.isArray(payload.investigations)
  ) {
    return payload.investigations as Investigation[];
  }

  return [];
}

/* -------------------------------------------------------------------------- */
/* Investigation collection                                                   */
/* -------------------------------------------------------------------------- */

export function useInvestigations(
  options: UseInvestigationsOptions = {},
): UseInvestigationsResult {
  const {
    status,
    risk_level,
    enabled = true,
  } = options;

  const [investigations, setInvestigations] = useState<
    Investigation[]
  >([]);

  const [loading, setLoading] = useState<boolean>(enabled);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!enabled) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await investigationsApi.list<unknown>({
        status,
        risk_level,
      });

      setInvestigations(
        normalizeInvestigationList(response),
      );
    } catch (err) {
      setError(getErrorMessage(err));
      setInvestigations([]);
    } finally {
      setLoading(false);
    }
  }, [enabled, risk_level, status]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    investigations,
    loading,
    error,
    refresh,
  };
}

/* -------------------------------------------------------------------------- */
/* Single investigation                                                       */
/* -------------------------------------------------------------------------- */

export function useInvestigation(
  investigationId: string | null | undefined,
): UseInvestigationResult {
  const [investigation, setInvestigation] =
    useState<Investigation | null>(null);

  const [loading, setLoading] = useState<boolean>(
    Boolean(investigationId),
  );

  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!investigationId) {
      setInvestigation(null);
      setLoading(false);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response =
        await investigationsApi.get<Investigation>(
          investigationId,
        );

      setInvestigation(response);
    } catch (err) {
      setError(getErrorMessage(err));
      setInvestigation(null);
    } finally {
      setLoading(false);
    }
  }, [investigationId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const createInvestigation = useCallback(
    async (
      payload: Record<string, unknown>,
    ): Promise<Investigation> => {
      setError(null);

      try {
        const created =
          await investigationsApi.create<Investigation>(
            payload,
          );

        setInvestigation(created);

        return created;
      } catch (err) {
        setError(getErrorMessage(err));
        throw err;
      }
    },
    [],
  );

  const updateInvestigation = useCallback(
    async (
      payload: Record<string, unknown>,
    ): Promise<Investigation> => {
      if (!investigationId) {
        const error = new Error(
          "An investigation ID is required.",
        );

        setError(error.message);
        throw error;
      }

      setError(null);

      try {
        const updated =
          await investigationsApi.update<Investigation>(
            investigationId,
            payload,
          );

        setInvestigation(updated);

        return updated;
      } catch (err) {
        setError(getErrorMessage(err));
        throw err;
      }
    },
    [investigationId],
  );

  return {
    investigation,
    loading,
    error,
    refresh,
    createInvestigation,
    updateInvestigation,
  };
}

export default useInvestigation;