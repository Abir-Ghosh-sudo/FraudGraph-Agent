export type InvestigationStatus =
  | "pending"
  | "running"
  | "investigating"
  | "awaiting_evidence"
  | "awaiting_approval"
  | "completed"
  | "failed"
  | "cancelled";

export type InvestigationPriority =
  | "low"
  | "medium"
  | "high"
  | "critical";

export type InvestigationStage =
  | "initialization"
  | "data_collection"
  | "graph_analysis"
  | "risk_analysis"
  | "evidence_analysis"
  | "pattern_detection"
  | "decision"
  | "action"
  | "completed";

export interface InvestigationProgress {
  stage: InvestigationStage;
  progress: number;
  message: string | null;
  started_at: string | null;
  updated_at: string | null;
}

export interface InvestigationAgent {
  agent_id: string;
  name: string;
  type: string;
  status: string;
  message: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface Investigation {
  investigation_id: string;

  case_id: string | null;

  transaction_id: string | null;

  customer_id: string | null;

  account_id: string | null;

  title: string;

  description: string | null;

  status: InvestigationStatus;

  priority: InvestigationPriority;

  risk_score: number | null;

  risk_level: string | null;

  progress: InvestigationProgress | null;

  agents: InvestigationAgent[];

  evidence_ids: string[];

  finding_ids: string[];

  decision_ids: string[];

  action_ids: string[];

  created_at: string;

  started_at: string | null;

  updated_at: string;

  completed_at: string | null;

  error: string | null;
}

export interface InvestigationCreate {
  case_id?: string | null;

  transaction_id?: string | null;

  customer_id?: string | null;

  account_id?: string | null;

  title: string;

  description?: string | null;

  priority?: InvestigationPriority;
}

export interface InvestigationUpdate {
  status?: InvestigationStatus;

  priority?: InvestigationPriority;

  title?: string;

  description?: string | null;

  risk_score?: number | null;

  risk_level?: string | null;
}

export interface InvestigationListResponse {
  items: Investigation[];

  total?: number;

  page?: number;

  page_size?: number;

  has_next?: boolean;
}

export interface InvestigationEvent {
  event_id?: string;

  investigation_id: string;

  type: string;

  timestamp: string;

  message?: string | null;

  data?: Record<string, unknown>;
}