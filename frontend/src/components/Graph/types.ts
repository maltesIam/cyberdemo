/**
 * Types for Graph components
 *
 * Defines the structure of nodes, edges, and graph data
 * compatible with Cytoscape.js format.
 */

export type NodeType = "incident" | "detection" | "asset" | "process" | "hash";
export type NodeColor = "green" | "yellow" | "red" | "blue";
export type RiskLevel = "none" | "low" | "medium" | "high" | "contained";

export interface NodeData {
  id: string;
  label: string;
  type: NodeType;
  color: NodeColor;
  riskLevel?: RiskLevel;
  metadata?: Record<string, unknown>;
}

export interface EdgeData {
  id: string;
  source: string;
  target: string;
  relation: string;
  label?: string;
}

export interface CytoscapeNode {
  data: NodeData;
  position?: { x: number; y: number };
  classes?: string;
}

export interface CytoscapeEdge {
  data: EdgeData;
  classes?: string;
}

export interface GraphData {
  nodes: CytoscapeNode[];
  edges: CytoscapeEdge[];
}

export interface SelectedNode extends NodeData {
  assetInfo?: AssetInfo;
  threatInfo?: ThreatInfo;
  recommendation?: RecommendationInfo;
  statusInfo?: StatusInfo;
}

export interface AssetInfo {
  hostname: string;
  ip: string;
  os: string;
  tags: string[];
  owner?: string;
  department?: string;
  lastSeen?: string;
}

export interface ThreatInfo {
  threatType: string;
  severity: string;
  confidence: number;
  indicators: string[];
  mitreTechniques?: string[];
}

export interface RecommendationInfo {
  action: string;
  reason: string;
  urgency: "immediate" | "high" | "medium" | "low";
  steps: string[];
}

export interface StatusInfo {
  containmentStatus: "none" | "pending" | "contained" | "lifted";
  ticketId?: string;
  ticketStatus?: string;
  approvalStatus?: "none" | "requested" | "approved" | "rejected";
}
