export type EvidenceType =
  | "transaction"
  | "customer"
  | "account"
  | "device"
  | "location"
  | "document"
  | "image"
  | "network"
  | "graph"
  | "model"
  | "rule"
  | "external"
  | "behavioral"
  | "communication"
  | "other";

export type EvidenceStrength =
  | "weak"
  | "moderate"
  | "strong"
  | "conclusive";

export type EvidenceStatus =
  | "available"
  | "pending"
  | "processing"
  | "verified"
  | "rejected"
  | "unavailable";

export interface EvidenceSource {
  source_id: string;
  source_type: string;
  name: string;
  description: string | null;
  uri: string | null;
  provider: string | null;
  retrieved_at: string | null;
  metadata: Record<string, unknown>;
}

export interface EvidenceProvenance {
  provenance_id: string;
  source_id: string | null;
  source_type: string | null;
  collection_method: string | null;
  collected_at: string | null;
  processed_at: string | null;
  processor: string | null;
  chain_of_custody: string[];
  metadata: Record<string, unknown>;
}

export interface Evidence {
  evidence_id: string;

  case_id: string | null;

  investigation_id: string | null;

  transaction_id: string | null;

  customer_id: string | null;

  account_id: string | null;

  type: EvidenceType | string;

  title: string;

  description: string | null;

  content: string | null;

  status: EvidenceStatus;

  strength: EvidenceStrength | null;

  confidence: number | null;

  relevance: number | null;

  source: EvidenceSource | null;

  provenance: EvidenceProvenance | null;

  tags: string[];

  related_evidence_ids: string[];

  metadata: Record<string, unknown>;

  created_at: string;

  updated_at: string | null;
}

export interface EvidenceCreate {
  case_id?: string | null;

  investigation_id?: string | null;

  transaction_id?: string | null;

  customer_id?: string | null;

  account_id?: string | null;

  type: EvidenceType | string;

  title: string;

  description?: string | null;

  content?: string | null;

  source_id?: string | null;

  tags?: string[];

  metadata?: Record<string, unknown>;
}

export interface EvidenceListResponse {
  items: Evidence[];

  total?: number;

  page?: number;

  page_size?: number;

  has_next?: boolean;
}