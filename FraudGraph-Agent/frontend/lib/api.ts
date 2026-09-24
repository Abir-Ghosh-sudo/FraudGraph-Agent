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
  get<T = unknown>(params?: Record<string, QueryValue>): Promise<T> {
    return api.get<T>("/graph", params);
  },
};

/* -------------------------------------------------------------------------- */
/* Actions                                                                    */
/* -------------------------------------------------------------------------- */

export const actionsApi = {
  list<T = unknown>(params?: Record<string, QueryValue>): Promise<T> {
    return api.get<T>("/actions", params);
  },

  get<T = unknown>(actionId: string): Promise<T> {
    return api.get<T>(
      `/actions/${encodeURIComponent(actionId)}`,
    );
  },

  create<T = unknown>(payload: unknown): Promise<T> {
    return api.post<T>("/actions", payload);
  },

  approve<T = unknown>(actionId: string, payload?: unknown): Promise<T> {
    return api.post<T>(
      `/actions/${encodeURIComponent(actionId)}/approve`,
      payload,
    );
  },

  execute<T = unknown>(actionId: string, payload?: unknown): Promise<T> {
    return api.post<T>(
      `/actions/${encodeURIComponent(actionId)}/execute`,
      payload,
    );
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
  check<T = unknown>(): Promise<T> {
    return api.get<T>("/health");
  },
};

export default api;