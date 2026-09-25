// frontend/lib/api.ts

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") ||
  "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(status: number, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

type QueryValue = string | number | boolean | null | undefined;

interface RequestOptions extends Omit<RequestInit, "body"> {
  query?: Record<string, QueryValue>;
  body?: unknown;
}

function buildUrl(
  path: string,
  query?: Record<string, QueryValue>,
): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  const url = new URL(`${API_BASE_URL}${normalizedPath}`);

  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  return url.toString();
}

async function parseResponse(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();

  return text || null;
}

async function request<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { query, body, headers, ...fetchOptions } = options;

  const response = await fetch(buildUrl(path, query), {
    ...fetchOptions,
    headers: {
      Accept: "application/json",
      ...(body !== undefined
        ? {
            "Content-Type": "application/json",
          }
        : {}),
      ...headers,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  });

  const payload = await parseResponse(response);

  if (!response.ok) {
    let message = `API request failed with status ${response.status}`;

    if (
      payload &&
      typeof payload === "object" &&
      "detail" in payload &&
      typeof payload.detail === "string"
    ) {
      message = payload.detail;
    } else if (typeof payload === "string" && payload.trim()) {
      message = payload;
    }

    throw new ApiError(response.status, message, payload);
  }

  return payload as T;
}

/* -------------------------------------------------------------------------- */
/* Root-scoped API methods                                                     */
/*                                                                             */
/* A small number of backend routes are mounted at the application root       */
/* rather than under the /api/v1 router (currently /health and                 */
/* /health/readiness). Those must not be prefixed with API_BASE_URL or they    */
/* resolve to /api/v1/health and return 404.                                   */
/* -------------------------------------------------------------------------- */

const API_ROOT_URL = (
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") || "http://localhost:8000"
).replace(/\/api\/v1$/, "");

function buildRootUrl(
  path: string,
  query?: Record<string, QueryValue>,
): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${API_ROOT_URL}${normalizedPath}`);

  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  return url.toString();
}

export const rootApi = {
  get<T>(
    path: string,
    query?: Record<string, QueryValue>,
  ): Promise<T> {
    return fetch(buildRootUrl(path, query), {
      method: "GET",
      headers: { Accept: "application/json" },
    }).then(async (response) => {
      if (!response.ok) {
        const details = await parseResponse(response).catch(() => null);
        throw new ApiError(
          response.status,
          `Request to ${path} failed with status ${response.status}`,
          details,
        );
      }

      return (await parseResponse(response)) as T;
    });
  },
};

/* -------------------------------------------------------------------------- */
/* Generic API methods                                                        */
/* -------------------------------------------------------------------------- */

export const api = {
  get<T>(
    path: string,
    query?: Record<string, QueryValue>,
  ): Promise<T> {
    return request<T>(path, {
      method: "GET",
      query,
    });
  },

  post<T>(
    path: string,
    body?: unknown,
  ): Promise<T> {
    return request<T>(path, {
      method: "POST",
      body,
    });
  },

  patch<T>(
    path: string,
    body?: unknown,
  ): Promise<T> {
    return request<T>(path, {
      method: "PATCH",
      body,
    });
  },

  put<T>(
    path: string,
    body?: unknown,
  ): Promise<T> {
    return request<T>(path, {
      method: "PUT",
      body,
    });
  },

  delete<T>(
    path: string,
  ): Promise<T> {
    return request<T>(path, {
      method: "DELETE",
    });
  },
};

/* -------------------------------------------------------------------------- */
/* Cases                                                                     */
/* -------------------------------------------------------------------------- */

export const casesApi = {
  list<T = unknown>(params?: {
    status?: string;
    risk_level?: string;
  }): Promise<T> {
    return api.get<T>("/cases", params);
  },

  get<T = unknown>(caseId: string): Promise<T> {
    return api.get<T>(`/cases/${encodeURIComponent(caseId)}`);
  },

  create<T = unknown>(payload: unknown): Promise<T> {
    return api.post<T>("/cases", payload);
  },

  update<T = unknown>(
    caseId: string,
    payload: unknown,
  ): Promise<T> {
    return api.patch<T>(
      `/cases/${encodeURIComponent(caseId)}`,
      payload,
    );
  },

  addFinding<T = unknown>(
    caseId: string,
    payload: unknown,
  ): Promise<T> {
    return api.post<T>(
      `/cases/${encodeURIComponent(caseId)}/findings`,
      payload,
    );
  },

  addDecision<T = unknown>(
    caseId: string,
    payload: unknown,
  ): Promise<T> {
    return api.post<T>(
      `/cases/${encodeURIComponent(caseId)}/decisions`,
      payload,
    );
  },

  addAction<T = unknown>(
    caseId: string,
    payload: unknown,
  ): Promise<T> {
    return api.post<T>(
      `/cases/${encodeURIComponent(caseId)}/actions`,
      payload,
    );
  },

  setOutcome<T = unknown>(
    caseId: string,
    payload: unknown,
  ): Promise<T> {
    return api.post<T>(
      `/cases/${encodeURIComponent(caseId)}/outcome`,
      payload,
    );
  },
};

/* -------------------------------------------------------------------------- */
/* Investigations                                                             */
/* -------------------------------------------------------------------------- */

export const investigationsApi = {
  list<T = unknown>(params?: Record<string, QueryValue>): Promise<T> {
    return api.get<T>("/investigations", params);
  },

  get<T = unknown>(investigationId: string): Promise<T> {
    return api.get<T>(
      `/investigations/${encodeURIComponent(investigationId)}`,
    );
  },

  create<T = unknown>(payload: unknown): Promise<T> {
    return api.post<T>("/investigations", payload);
  },

  update<T = unknown>(
    investigationId: string,
    payload: unknown,
  ): Promise<T> {
    return api.patch<T>(
      `/investigations/${encodeURIComponent(investigationId)}`,
      payload,
    );
  },
};

/* -------------------------------------------------------------------------- */
/* Customers                                                                  */
/* -------------------------------------------------------------------------- */

export const customersApi = {
  list<T = unknown>(params?: Record<string, QueryValue>): Promise<T> {
    return api.get<T>("/customers", params);
  },

  get<T = unknown>(customerId: string): Promise<T> {
    return api.get<T>(
      `/customers/${encodeURIComponent(customerId)}`,
    );
  },
};

/* -------------------------------------------------------------------------- */
/* Transactions                                                               */
/* -------------------------------------------------------------------------- */

export const transactionsApi = {
  list<T = unknown>(params?: Record<string, QueryValue>): Promise<T> {
    return api.get<T>("/transactions", params);
  },

  get<T = unknown>(transactionId: string): Promise<T> {
    return api.get<T>(
      `/transactions/${encodeURIComponent(transactionId)}`,
    );
  },
};

/* -------------------------------------------------------------------------- */
/* Evidence                                                                   */
/* -------------------------------------------------------------------------- */

export const evidenceApi = {
  list<T = unknown>(params?: Record<string, QueryValue>): Promise<T> {
    return api.get<T>("/evidence", params);
  },

  get<T = unknown>(evidenceId: string): Promise<T> {
    return api.get<T>(
      `/evidence/${encodeURIComponent(evidenceId)}`,
    );
  },
};

/* -------------------------------------------------------------------------- */
/* Fraud graph                                                                */
/* -------------------------------------------------------------------------- */

export const graphApi = {
  health<T = unknown>(): Promise<T> {
    return api.get<T>("/graph/health");
  },

  queries<T = unknown>(): Promise<T> {
    return api.get<T>("/graph/queries");
  },

  describeQuery<T = unknown>(queryName: string): Promise<T> {
    return api.get<T>(`/graph/queries/${encodeURIComponent(queryName)}`);
  },

  query<T = unknown>(payload: {
    query_name: string;
    parameters?: Record<string, unknown>;
    limit?: number;
  }): Promise<T> {
    return api.post<T>("/graph/query", payload);
  },

  investigation<T = unknown>(
    nodeId: string,
    params?: { query_name?: string; depth?: number; limit?: number },
  ): Promise<T> {
    return api.get<T>(`/graph/investigation/${encodeURIComponent(nodeId)}`, {
      query_name: params?.query_name || "investigate_entity",
      depth: params?.depth ?? 2,
      limit: params?.limit ?? 100,
    });
  },

  evidence<T = unknown>(payload: {
    query_name: string;
    parameters?: Record<string, unknown>;
    limit?: number;
  }): Promise<T> {
    return api.post<T>("/graph/evidence", payload);
  },

  get<T = unknown>(params?: Record<string, QueryValue>): Promise<T> {
    const target =
      params?.node_id ||
      params?.customer_id ||
      params?.transaction_id ||
      params?.account_id ||
      params?.target;

    if (typeof target === "string" && target.trim()) {
      return graphApi.investigation<T>(target.trim(), {
        depth: typeof params?.depth === "number" ? params.depth : 2,
      });
    }

    return api.get<T>("/graph/health", params);
  },
};


/* -------------------------------------------------------------------------- */
/* Actions                                                                    */
/*                                                                             */
/* The backend exposes only these action routes:                                */
/*   GET  /actions/investigation/{investigation_id}  -> ActionPlan             */
/*   GET  /actions/{action_id}                       -> NextBestAction         */
/*   GET  /actions/approvals/{approval_id}           -> ApprovalRequest        */
/*   POST /actions/execute                            -> ActionExecutionResult  */
/* There is deliberately no GET /actions collection endpoint.                  */
/* -------------------------------------------------------------------------- */

export const actionsApi = {
  /** Action plan (including the next-best action) for one investigation. */
  planForInvestigation<T = unknown>(investigationId: string): Promise<T> {
    return api.get<T>(
      `/actions/investigation/${encodeURIComponent(investigationId)}`,
    );
  },

  get<T = unknown>(actionId: string): Promise<T> {
    return api.get<T>(`/actions/${encodeURIComponent(actionId)}`);
  },

  getApproval<T = unknown>(approvalId: string): Promise<T> {
    return api.get<T>(`/actions/approvals/${encodeURIComponent(approvalId)}`);
  },

  /**
   * Request server-side execution. The backend fails closed: without a
   * registered provider handler and, where required, a server-side approval
   * bound to this action, it returns success=false. Never treat a 200 as a
   * completed action.
   */
  execute<T = unknown>(payload: {
    action_id: string;
    approval_id?: string;
  }): Promise<T> {
    return api.post<T>("/actions/execute", payload);
  },
};

/* -------------------------------------------------------------------------- */
/* Benchmark                                                                  */
/* -------------------------------------------------------------------------- */

export const benchmarkApi = {
  get<T = unknown>(params?: Record<string, QueryValue>): Promise<T> {
    return api.get<T>("/benchmark", params);
  },

  run<T = unknown>(payload?: unknown): Promise<T> {
    return api.post<T>("/benchmark", payload);
  },
};

/* -------------------------------------------------------------------------- */
/* Health                                                                     */
/* -------------------------------------------------------------------------- */

export const healthApi = {
  /** Liveness probe. Mounted at the server root, NOT under /api/v1. */
  check<T = unknown>(): Promise<T> {
    return rootApi.get<T>("/health");
  },

  /**
   * Readiness probe reporting which subsystems are actually configured
   * (tigergraph_configured, llm_configured, vector_store_configured).
   * Also mounted at the server root.
   */
  readiness<T = unknown>(): Promise<T> {
    return rootApi.get<T>("/health/readiness");
  },
};

export default api;