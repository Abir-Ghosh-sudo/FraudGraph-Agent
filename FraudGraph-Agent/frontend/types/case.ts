export type CaseStatus =
  | "open"
  | "investigating"
  | "awaiting_evidence"
  | "awaiting_approval"
  | "actioned"
  | "escalated"
  | "resolved"
  | "closed";

export type CaseOutcome =
  | "confirmed_fraud"
  | "cleared"
  | "inconclusive"
  | "escalated";

export type DecisionType =
  | "allow"
  | "block"
  | "monitor"
  | "warn"
  | "request_evidence"
  | "escalate"
  | "create_report"
  | "close";

export interface CaseFinding {
  finding_id: string;
  title: string;
  description: string;
  evidence_ids: string[];
  confidence: number | null;
  created_at: string;
}

export interface CaseDecision {
  decision_id: string;
  decision_type: DecisionType;
  rationale: string;
  evidence_ids: string[];
  requires_approval: boolean;
  approved: boolean | null;
  approved_by: string | null;
  created_at: string;
}

export interface CaseAction {
  action_id: string;
  action_type: string;
  status: string;
  rationale: string | null;
  requires_approval: boolean;
  approval_id: string | null;
  result: Record<string, unknown>;
  created_at: string;
  completed_at: string | null;
}

export interface CaseMemoryReference {
  memory_id: string;
  case_id: string;
  similarity: number | null;
  relevance_reason: string | null;
}

export interface Case {
  case_id: string;
  investigation_id: string;
  transaction_id: string | null;
  customer_id: string | null;
  account_id: string | null;
  title: string;
  description: string | null;
  status: CaseStatus;
  outcome: CaseOutcome | null;
  risk_score: number | null;
  risk_level: string;
  fraud_type: string | null;
  evidence_ids: string[];
  findings: CaseFinding[];
  decisions: CaseDecision[];
  actions: CaseAction[];
  related_cases: CaseMemoryReference[];
  memory_ids: string[];
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  closed_at: string | null;
}

export interface CaseCreate {
  investigation_id: string;
  transaction_id?: string | null;
  customer_id?: string | null;
  account_id?: string | null;
  title: string;
  description?: string | null;
}

export interface CaseUpdate {
  status?: CaseStatus;
  risk_score?: number | null;
  risk_level?: string;
  outcome?: CaseOutcome | null;
  title?: string;
  description?: string | null;
}
