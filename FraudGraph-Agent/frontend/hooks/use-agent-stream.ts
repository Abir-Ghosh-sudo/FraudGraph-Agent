"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export type AgentEventType =
  | "connected"
  | "started"
  | "status"
  | "progress"
  | "finding"
  | "evidence"
  | "graph"
  | "decision"
  | "action"
  | "completed"
  | "failed"
  | "error"
  | "message"
  | string;

export interface AgentStreamEvent<T = unknown> {
  id?: string;
  type: AgentEventType;
  data: T;
  timestamp?: string;
}

interface UseAgentStreamOptions {
  investigationId?: string | null;
  caseId?: string | null;
  enabled?: boolean;
  autoConnect?: boolean;
  onEvent?: (event: AgentStreamEvent) => void;
}

interface UseAgentStreamResult {
  events: AgentStreamEvent[];
  latestEvent: AgentStreamEvent | null;
  connected: boolean;
  connecting: boolean;
  error: string | null;
  connect: () => void;
  disconnect: () => void;
  clearEvents: () => void;
}

const STREAM_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") ||
  "http://localhost:8000/api/v1";

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected stream error occurred.";
}

function parseEventData(raw: string): unknown {
  if (!raw.trim()) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return raw;
  }
}

function buildStreamUrl(
  investigationId?: string | null,
  caseId?: string | null,
): string {
  const url = new URL(
    `${STREAM_BASE_URL}/investigations/stream`,
  );

  if (investigationId) {
    url.searchParams.set(
      "investigation_id",
      investigationId,
    );
  }

  if (caseId) {
    url.searchParams.set("case_id", caseId);
  }

  return url.toString();
}

export function useAgentStream(
  options: UseAgentStreamOptions = {},
): UseAgentStreamResult {
  const {
    investigationId,
    caseId,
    enabled = true,
    autoConnect = true,
    onEvent,
  } = options;

  const eventSourceRef =
    useRef<EventSource | null>(null);

  const onEventRef =
    useRef<((event: AgentStreamEvent) => void) | undefined>(
      onEvent,
    );

  const [events, setEvents] = useState<
    AgentStreamEvent[]
  >([]);

  const [latestEvent, setLatestEvent] =
    useState<AgentStreamEvent | null>(null);

  const [connected, setConnected] =
    useState(false);

  const [connecting, setConnecting] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  const disconnect = useCallback(() => {
    const source = eventSourceRef.current;

    if (source) {
      source.close();
      eventSourceRef.current = null;
    }

    setConnected(false);
    setConnecting(false);
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
    setLatestEvent(null);
    setError(null);
  }, []);

  const connect = useCallback(() => {
    if (!enabled) {
      return;
    }

    if (!investigationId && !caseId) {
      setError(
        "An investigation ID or case ID is required.",
      );
      return;
    }

    if (
      eventSourceRef.current &&
      eventSourceRef.current.readyState !== EventSource.CLOSED
    ) {
      return;
    }

    disconnect();

    setConnecting(true);
    setError(null);

    const source = new EventSource(
      buildStreamUrl(
        investigationId,
        caseId,
      ),
    );

    eventSourceRef.current = source;

    source.onopen = () => {
      setConnected(true);
      setConnecting(false);
      setError(null);
    };

    source.onmessage = (message) => {
      const event: AgentStreamEvent = {
        id: message.lastEventId || undefined,
        type: "message",
        data: parseEventData(message.data),
      };

      setEvents((previous) => [
        ...previous,
        event,
      ]);

      setLatestEvent(event);

      onEventRef.current?.(event);
    };

    const eventTypes: AgentEventType[] = [
      "connected",
      "started",
      "status",
      "progress",
      "finding",
      "evidence",
      "graph",
      "decision",
      "action",
      "completed",
      "failed",
      "error",
      "message",
    ];

    const handleNamedEvent = (
      type: AgentEventType,
      event: Event,
    ) => {
      const messageEvent =
        event as MessageEvent<string>;

      const parsed: AgentStreamEvent = {
        id: messageEvent.lastEventId || undefined,
        type,
        data: parseEventData(
          messageEvent.data ?? "",
        ),
      };

      setEvents((previous) => [
        ...previous,
        parsed,
      ]);

      setLatestEvent(parsed);

      onEventRef.current?.(parsed);
    };

    for (const eventType of eventTypes) {
      source.addEventListener(
        eventType,
        (event) =>
          handleNamedEvent(
            eventType,
            event,
          ),
      );
    }

    source.onerror = () => {
      setConnected(false);
      setConnecting(false);

      if (
        source.readyState === EventSource.CLOSED
      ) {
        setError(
          "The agent investigation stream was closed.",
        );
      } else {
        setError(
          "Unable to receive the agent investigation stream.",
        );
      }
    };
  }, [
    caseId,
    disconnect,
    enabled,
    investigationId,
  ]);

  useEffect(() => {
    if (
      enabled &&
      autoConnect &&
      (investigationId || caseId)
    ) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [
    autoConnect,
    caseId,
    connect,
    disconnect,
    enabled,
    investigationId,
  ]);

  return {
    events,
    latestEvent,
    connected,
    connecting,
    error,
    connect,
    disconnect,
    clearEvents,
  };
}

export default useAgentStream;