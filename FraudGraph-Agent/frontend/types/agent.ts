export type AgentStatus =
  | "idle"
  | "queued"
  | "starting"
  | "running"
  | "waiting"
  | "completed"
  | "failed"
  | "cancelled";

export type AgentEventType =
  | "connected"
  | "started"
  | "status"
  | "progress"
  | "finding"
  | "evidence"
  | "graph"
  | "pattern"
  | "risk"
  | "decision"
  | "action"
  | "completed"
  | "failed"
  | "error"
  | "message";

export type AgentType =
  | "orchestrator"
  | "fraud_detection"
  | "risk"
  | "graph"
  | "graphrag"
  | "evidence"
  | "pattern"
  | "decision"
  | "recommendation"
  | "report";

export interface AgentProgress {
  current: number;
  total: number;
  percentage: number;
  message: string | null;
  updated_at: string | null;
}

export interface Agent {
  agent_id: string;
  name: string;
  type: AgentType | string;
  status: AgentStatus;
  message: string | null;
  progress: AgentProgress | null;
  started_at: string | null;
  updated_at: string | null;
  completed_at: string | null;
  error: string | null;
}

export interface AgentEvent<T = unknown> {
  event_id: string | null;
  investigation_id: string | null;
  case_id: string | null;
  agent_id: string | null;
  type: AgentEventType | string;
  timestamp: string;
  message: string | null;
  data: T;
}

export interface AgentFinding {
  finding_id: string;
  agent_id: string | null;
  title: string;
  description: string;
  confidence: number | null;
  evidence_ids: string[];
  created_at: string;
}

export interface AgentDecision {
  decision_id: string;
  agent_id: string | null;
  decision_type: string;
  rationale: string;
  confidence: number | null;
  evidence_ids: string[];
  requires_approval: boolean;
  approved: boolean | null;
  created_at: string;
}

export interface AgentAction {
  action_id: string;
  agent_id: string | null;
  action_type: string;
  status: string;
  rationale: string | null;
  requires_approval: boolean;
  approval_id: string | null;
  result: Record<string, unknown>;
  created_at: string;
  completed_at: string | null;
}

export interface AgentRun {
  run_id: string;
  investigation_id: string | null;
  case_id: string | null;
  status: AgentStatus;
  agents: Agent[];
  events: AgentEvent[];
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
}