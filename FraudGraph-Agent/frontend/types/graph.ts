export type GraphNodeType =
  | "customer"
  | "account"
  | "transaction"
  | "device"
  | "merchant"
  | "location"
  | "beneficiary"
  | "phone"
  | "email"
  | "ip"
  | "document"
  | "case"
  | "investigation"
  | "unknown"
  | string;

export type GraphEdgeType =
  | "owns"
  | "uses"
  | "transacted_with"
  | "sent_to"
  | "received_from"
  | "located_at"
  | "linked_to"
  | "shared_device"
  | "shared_ip"
  | "shared_phone"
  | "shared_email"
  | "associated_with"
  | "related_to"
  | string;

export interface GraphNode {
  id: string;

  type: GraphNodeType;

  label: string;

  properties: Record<string, unknown>;

  risk_score: number | null;

  risk_level: string | null;

  fraud_score: number | null;

  degree: number | null;

  metadata: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;

  source: string;

  target: string;

  type: GraphEdgeType;

  label: string | null;

  weight: number | null;

  confidence: number | null;

  properties: Record<string, unknown>;

  metadata: Record<string, unknown>;
}

export interface GraphPath {
  path_id: string;

  node_ids: string[];

  edge_ids: string[];

  length: number;

  score: number | null;

  risk_score: number | null;

  description: string | null;
}

export interface GraphCluster {
  cluster_id: string;

  node_ids: string[];

  edge_ids: string[];

  label: string | null;

  risk_score: number | null;

  fraud_probability: number | null;

  metadata: Record<string, unknown>;
}

export interface GraphMetadata {
  source: string | null;

  generated_at: string | null;

  query: string | null;

  depth: number | null;

  node_count: number;

  edge_count: number;

  execution_time_ms: number | null;

  metadata: Record<string, unknown>;
}

export interface FraudGraph {
  nodes: GraphNode[];

  edges: GraphEdge[];

  paths: GraphPath[];

  clusters: GraphCluster[];

  metadata: GraphMetadata | null;
}

export interface GraphQuery {
  case_id?: string;

  investigation_id?: string;

  customer_id?: string;

  transaction_id?: string;

  account_id?: string;

  depth?: number;

  limit?: number;

  node_types?: GraphNodeType[];

  edge_types?: GraphEdgeType[];
}

export interface GraphResponse {
  graph: FraudGraph;

  query: GraphQuery;

  generated_at: string;
}