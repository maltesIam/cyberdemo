// Asset types
export interface Asset {
  id: string;
  hostname: string;
  ip: string;
  mac: string;
  os: string;
  os_version: string;
  type: "workstation" | "server" | "laptop" | "virtual_machine" | "container";
  owner: string;
  department: string;
  site: string;
  risk_score: number;
  tags: string[];
  last_seen: string;
  installed_software: string[];
  open_ports: number[];
  vulnerabilities: Vulnerability[];
}

export interface Vulnerability {
  cve_id: string;
  severity: "critical" | "high" | "medium" | "low";
  cvss_score: number;
  description: string;
}

// Incident types
export interface Incident {
  incident_id: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low";
  status: "open" | "investigating" | "contained" | "resolved" | "closed" | "new";
  created_at: string;
  updated_at: string;
  assigned_to?: string;
  asset_ids: string[];
  detection_ids: string[];
  entity_ids?: string[];
  tags: string[];
  priority?: string;
  category?: string;
  source?: string;
  ttd_minutes?: number;
  ttr_minutes?: number | null;
  resolved_at?: string | null;
  closed_at?: string | null;
}

// Detection types (matches API response from edr-detections-v1)
export interface Detection {
  detection_id: string;
  asset_id: string;
  hostname: string;
  detection_type: string;
  severity: "critical" | "high" | "medium" | "low";
  confidence: number;
  technique_id: string;
  technique_name: string;
  tactic: string;
  description: string;
  process_name: string;
  process_path: string;
  process_hash: string;
  parent_process: string;
  command_line: string;
  user: string;
  status: string;
  assigned_to?: string;
  detected_at: string;
  resolved_at?: string | null;
  created_at: string;
}

// Postmortem types
export interface Postmortem {
  id: string;
  incident_id: string;
  title: string;
  summary: string;
  root_cause: string;
  impact: string;
  timeline: PostmortemTimelineEntry[];
  lessons_learned: string[];
  action_items: ActionItem[];
  created_at: string;
  author: string;
}

export interface PostmortemTimelineEntry {
  timestamp: string;
  description: string;
}

export interface ActionItem {
  id: string;
  description: string;
  owner: string;
  due_date: string;
  status: "pending" | "in_progress" | "completed";
}

// Ticket types
export interface Ticket {
  id: string;
  external_id: string;
  incident_id: string;
  title: string;
  description: string;
  status: "open" | "in_progress" | "pending" | "resolved" | "closed";
  priority: "urgent" | "high" | "medium" | "low";
  assigned_to: string;
  created_at: string;
  updated_at: string;
  system: "jira" | "servicenow" | "pagerduty";
}

// Agent timeline types
export interface AgentAction {
  id: string;
  incident_id: string;
  action_type: "query" | "containment" | "enrichment" | "notification" | "analysis";
  description: string;
  status: "pending" | "running" | "completed" | "failed";
  started_at: string;
  completed_at: string | null;
  duration_ms: number | null;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  error: string | null;
}

// Generation types
export interface GenerationStatus {
  assets: number;
  incidents: number;
  detections: number;
  postmortems: number;
  tickets: number;
  agent_actions: number;
}

export interface GenerationResult {
  success: boolean;
  message: string;
  counts: GenerationStatus;
}

// Dashboard KPIs
export interface DashboardKPIs {
  total_incidents: number;
  critical_open: number;
  hosts_contained: number;
  mttr_hours: number;
  incidents_by_severity: { severity: string; count: number }[];
  incidents_by_hour: { hour: string; count: number }[];
  top_affected_hosts: { hostname: string; incident_count: number }[];
  detection_trend: { day: string; count: number }[];
}

// CTEM types
export interface CTEMFinding {
  finding_id: string;
  asset_id: string;
  cve_id: string;
  severity: "critical" | "high" | "medium" | "low";
  cvss_score: number;
  description: string;
  exposure: "internal" | "public" | "none";
  status: string;
  // Enrichment fields (populated after enrichment runs)
  epss_score?: number;
  risk_score?: number;
  threat_actors?: string[];
}

export interface CTEMFindingsResponse {
  findings: CTEMFinding[];
  total: number;
  page: number;
  page_size: number;
}

export interface CTEMSummary {
  severity_distribution: Record<string, number>;
  exposure_distribution: Record<string, number>;
  risk_distribution: Record<string, number>;
}

// Audit types
export type AuditActionType =
  | "containment"
  | "approval"
  | "investigation"
  | "config_change"
  | "alert_update"
  | "escalation"
  | "notification"
  | "playbook_execution"
  | "user_login"
  | "data_export";

export type AuditOutcome = "success" | "failure" | "pending" | "denied" | "approved";

export interface AuditLog {
  id: string;
  timestamp: string;
  user: string;
  action_type: AuditActionType;
  target: string;
  target_type: string;
  details: Record<string, unknown>;
  policy_decision: string | null;
  outcome: AuditOutcome;
  ip_address: string | null;
  session_id: string | null;
}

export interface AuditActionTypeOption {
  value: AuditActionType;
  label: string;
}

export interface AuditOutcomeOption {
  value: AuditOutcome;
  label: string;
}

// API Response types
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  error: string;
  message: string;
  status: number;
}

// Configuration types
export interface PolicyConfig {
  auto_contain_threshold: number;
  false_positive_threshold: number;
  auto_contain_enabled: boolean;
  vip_list: string[];
  critical_tags: string[];
  asset_criticality_overrides: Record<string, string>;
  last_updated?: string;
}

export interface NotificationConfig {
  slack_enabled: boolean;
  teams_enabled: boolean;
  email_enabled: boolean;
  webhook_enabled: boolean;
  slack_webhook_url?: string;
  teams_webhook_url?: string;
  email_recipients: string[];
  custom_webhook_url?: string;
  notify_on_critical: boolean;
  notify_on_high: boolean;
  notify_on_medium: boolean;
  notify_on_containment: boolean;
  notify_on_approval_needed: boolean;
  template_style: string;
  last_updated?: string;
}

export interface IntegrationConfig {
  api_keys: Record<string, string>;
  webhook_urls: Record<string, string>;
  enabled_integrations: string[];
  last_updated?: string;
}

export interface FullConfig {
  policy: PolicyConfig;
  notifications: NotificationConfig;
  integrations: IntegrationConfig;
  last_updated?: string;
}

// Re-export enrichment types
export type {
  EnrichmentJobResponse,
  EnrichmentStatusResponse,
  EnrichVulnerabilitiesOptions,
  EnrichThreatsOptions,
  SourceResult,
  EnrichmentError,
} from "./enrichment";
