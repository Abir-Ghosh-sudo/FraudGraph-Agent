export type ActionStatus =
  | "proposed"
  | "pending"
  | "awaiting_approval"
  | "approved"
  | "rejected"
  | "executing"
  | "completed"
  | "failed"
  | "cancelled";

export type ActionType =
  | "allow"
  | "block"
  | "monitor"
  | "warn"
  | "request_evidence"
  | "escalate"
  | "create_report"
  | "freeze_account"
  | "flag_transaction"
  | "notify_customer"
  | "notify_investigator"
  | "close_case"
  | string;

export type ApprovalStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "expired"
  | "cancelled";

export interface ActionApproval {
  approval_id: string;

  action_id: string;

  status: ApprovalStatus;

  requested_by: string | null;

  approved_by: string | null;

  requested_at: string;

  decided_at: string | null;

  comment: string | null;
}

export interface ActionResult {
  success: boolean;

  status: string;

  message: string | null;

  data: Record<string, unknown>;

  error: string | null;

  executed_at: string | null;
}

export interface Action {
  action_id: string;

  case_id: string | null;

  investigation_id: string | null;

  transaction_id: string | null;

  customer_id: string | null;

  account_id: string | null;

  action_type: ActionType;

  status: ActionStatus;

  title: string | null;

  description: string | null;

  rationale: string | null;

  confidence: number | null;

  evidence_ids: string[];

  requires_approval: boolean;

  approval: ActionApproval | null;

  result: ActionResult | null;

  metadata: Record<string, unknown>;

  created_at: string;

  updated_at: string | null;

  completed_at: string | null;
}

export interface ActionCreate {
  case_id?: string | null;

  investigation_id?: string | null;

  transaction_id?: string | null;

  customer_id?: string | null;

  account_id?: string | null;

  action_type: ActionType;

  title?: string | null;

  description?: string | null;

  rationale?: string | null;

  evidence_ids?: string[];

  requires_approval?: boolean;

  metadata?: Record<string, unknown>;
}

export interface ActionUpdate {
  status?: ActionStatus;

  rationale?: string | null;

  metadata?: Record<string, unknown>;
}

export interface ActionApprovalRequest {
  comment?: string | null;
}

export interface ActionExecutionRequest {
  parameters?: Record<string, unknown>;
}

export interface ActionListResponse {
  items: Action[];

  total?: number;

  page?: number;

  page_size?: number;

  has_next?: boolean;
}