import axios, { AxiosError, AxiosInstance } from "axios";
import type {
  Asset,
  Incident,
  Detection,
  Postmortem,
  Ticket,
  AgentAction,
  GenerationResult,
  GenerationStatus,
  DashboardKPIs,
  PaginatedResponse,
  ApiError,
  CTEMFindingsResponse,
  CTEMSummary,
} from "../types";

// API base URL from environment or default
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Error handler
function handleApiError(error: unknown): never {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;
    const message = axiosError.response?.data?.message || axiosError.message || "Unknown error";
    const status = axiosError.response?.status || 500;
    throw new Error(`API Error (${status}): ${message}`);
  }
  throw error;
}

// ============================================================================
// Generation API
// ============================================================================

export async function generateAll(seed?: number): Promise<GenerationResult> {
  try {
    const params = seed !== undefined ? { seed } : {};
    const response = await apiClient.post<GenerationResult>("/gen/all", null, { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function generateAssets(count?: number, seed?: number): Promise<GenerationResult> {
  try {
    const params: Record<string, number> = {};
    if (count !== undefined) params.count = count;
    if (seed !== undefined) params.seed = seed;
    const response = await apiClient.post<GenerationResult>("/gen/assets", null, { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function generateEDR(count?: number, seed?: number): Promise<GenerationResult> {
  try {
    const params: Record<string, number> = {};
    if (count !== undefined) params.count = count;
    if (seed !== undefined) params.seed = seed;
    const response = await apiClient.post<GenerationResult>("/gen/edr", null, { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function generateIncidents(count?: number, seed?: number): Promise<GenerationResult> {
  try {
    const params: Record<string, number> = {};
    if (count !== undefined) params.count = count;
    if (seed !== undefined) params.seed = seed;
    const response = await apiClient.post<GenerationResult>("/gen/incidents", null, { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function generatePostmortems(
  count?: number,
  seed?: number,
): Promise<GenerationResult> {
  try {
    const params: Record<string, number> = {};
    if (count !== undefined) params.count = count;
    if (seed !== undefined) params.seed = seed;
    const response = await apiClient.post<GenerationResult>("/gen/postmortems", null, { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function generateTickets(count?: number, seed?: number): Promise<GenerationResult> {
  try {
    const params: Record<string, number> = {};
    if (count !== undefined) params.count = count;
    if (seed !== undefined) params.seed = seed;
    const response = await apiClient.post<GenerationResult>("/gen/tickets", null, { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function generateAgentActions(
  count?: number,
  seed?: number,
): Promise<GenerationResult> {
  try {
    const params: Record<string, number> = {};
    if (count !== undefined) params.count = count;
    if (seed !== undefined) params.seed = seed;
    const response = await apiClient.post<GenerationResult>("/gen/agent-actions", null, { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function resetData(): Promise<GenerationResult> {
  try {
    const response = await apiClient.post<GenerationResult>("/gen/reset");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getGenerationStatus(): Promise<GenerationStatus> {
  try {
    const response = await apiClient.get<GenerationStatus>("/gen/status");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Assets API
// ============================================================================

export interface AssetsQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  type?: string;
  os?: string;
  risk_min?: number;
  risk_max?: number;
  tags?: string[];
  site?: string;
}

export async function getAssets(params: AssetsQueryParams = {}): Promise<PaginatedResponse<Asset>> {
  try {
    const queryParams: Record<string, string | number | string[]> = {};
    if (params.page !== undefined) queryParams.page = params.page;
    if (params.page_size !== undefined) queryParams.page_size = params.page_size;
    if (params.search) queryParams.search = params.search;
    if (params.type) queryParams.type = params.type;
    if (params.os) queryParams.os = params.os;
    if (params.risk_min !== undefined) queryParams.risk_min = params.risk_min;
    if (params.risk_max !== undefined) queryParams.risk_max = params.risk_max;
    if (params.tags && params.tags.length > 0) queryParams.tags = params.tags.join(",");
    if (params.site) queryParams.site = params.site;

    const response = await apiClient.get<PaginatedResponse<Asset>>("/assets", {
      params: queryParams,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getAsset(id: string): Promise<Asset> {
  try {
    const response = await apiClient.get<Asset>(`/assets/${id}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Incidents API
// ============================================================================

export interface IncidentsQueryParams {
  page?: number;
  page_size?: number;
  status?: string;
  severity?: string;
  assigned_to?: string;
  search?: string;
}

export async function getIncidents(
  params: IncidentsQueryParams = {},
): Promise<PaginatedResponse<Incident>> {
  try {
    const queryParams: Record<string, string | number> = {};
    if (params.page !== undefined) queryParams.page = params.page;
    if (params.page_size !== undefined) queryParams.page_size = params.page_size;
    if (params.status) queryParams.status = params.status;
    if (params.severity) queryParams.severity = params.severity;
    if (params.assigned_to) queryParams.assigned_to = params.assigned_to;
    if (params.search) queryParams.search = params.search;

    const response = await apiClient.get<PaginatedResponse<Incident>>("/siem/incidents", {
      params: queryParams,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getIncident(id: string): Promise<Incident> {
  try {
    const response = await apiClient.get<Incident>(`/siem/incidents/${id}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Detections API
// ============================================================================

export interface DetectionsQueryParams {
  page?: number;
  page_size?: number;
  severity?: string;
  hostname?: string;
  rule_name?: string;
  from_date?: string;
  to_date?: string;
}

export async function getDetections(
  params: DetectionsQueryParams = {},
): Promise<PaginatedResponse<Detection>> {
  try {
    const queryParams: Record<string, string | number> = {};
    if (params.page !== undefined) queryParams.page = params.page;
    if (params.page_size !== undefined) queryParams.page_size = params.page_size;
    if (params.severity) queryParams.severity = params.severity;
    if (params.hostname) queryParams.hostname = params.hostname;
    if (params.rule_name) queryParams.rule_name = params.rule_name;
    if (params.from_date) queryParams.from_date = params.from_date;
    if (params.to_date) queryParams.to_date = params.to_date;

    const response = await apiClient.get<PaginatedResponse<Detection>>("/edr/detections", {
      params: queryParams,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getDetection(id: string): Promise<Detection> {
  try {
    const response = await apiClient.get<Detection>(`/edr/detections/${id}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Postmortems API
// ============================================================================

export interface PostmortemsQueryParams {
  page?: number;
  page_size?: number;
  incident_id?: string;
}

export async function getPostmortems(
  params: PostmortemsQueryParams = {},
): Promise<PaginatedResponse<Postmortem>> {
  try {
    const queryParams: Record<string, string | number> = {};
    if (params.page !== undefined) queryParams.page = params.page;
    if (params.page_size !== undefined) queryParams.page_size = params.page_size;
    if (params.incident_id) queryParams.incident_id = params.incident_id;

    const response = await apiClient.get<PaginatedResponse<Postmortem>>("/postmortems", {
      params: queryParams,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getPostmortem(id: string): Promise<Postmortem> {
  try {
    const response = await apiClient.get<Postmortem>(`/postmortems/${id}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Tickets API
// ============================================================================

export interface TicketsQueryParams {
  page?: number;
  page_size?: number;
  status?: string;
  priority?: string;
  incident_id?: string;
  system?: string;
}

export async function getTickets(
  params: TicketsQueryParams = {},
): Promise<PaginatedResponse<Ticket>> {
  try {
    const queryParams: Record<string, string | number> = {};
    if (params.page !== undefined) queryParams.page = params.page;
    if (params.page_size !== undefined) queryParams.page_size = params.page_size;
    if (params.status) queryParams.status = params.status;
    if (params.priority) queryParams.priority = params.priority;
    if (params.incident_id) queryParams.incident_id = params.incident_id;
    if (params.system) queryParams.system = params.system;

    const response = await apiClient.get<PaginatedResponse<Ticket>>("/tickets", {
      params: queryParams,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getTicket(id: string): Promise<Ticket> {
  try {
    const response = await apiClient.get<Ticket>(`/tickets/${id}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Agent Timeline API
// ============================================================================

export interface AgentActionsQueryParams {
  page?: number;
  page_size?: number;
  incident_id?: string;
  action_type?: string;
  status?: string;
}

export async function getAgentActions(
  params: AgentActionsQueryParams = {},
): Promise<PaginatedResponse<AgentAction>> {
  try {
    const queryParams: Record<string, string | number> = {};
    if (params.page !== undefined) queryParams.page = params.page;
    if (params.page_size !== undefined) queryParams.page_size = params.page_size;
    if (params.incident_id) queryParams.incident_id = params.incident_id;
    if (params.action_type) queryParams.action_type = params.action_type;
    if (params.status) queryParams.status = params.status;

    const response = await apiClient.get<PaginatedResponse<AgentAction>>("/agent-actions", {
      params: queryParams,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getAgentAction(id: string): Promise<AgentAction> {
  try {
    const response = await apiClient.get<AgentAction>(`/agent-actions/${id}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Dashboard API
// ============================================================================

export async function getDashboardKPIs(): Promise<DashboardKPIs> {
  try {
    const response = await apiClient.get<DashboardKPIs>("/dashboard/kpis");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// CTEM API
// ============================================================================

export interface CTEMFindingsQueryParams {
  page?: number;
  page_size?: number;
  severity?: string;
  exposure?: string;
}

export async function getCTEMFindings(
  params: CTEMFindingsQueryParams = {},
): Promise<CTEMFindingsResponse> {
  try {
    const queryParams: Record<string, string | number> = {};
    if (params.page !== undefined) queryParams.page = params.page;
    if (params.page_size !== undefined) queryParams.page_size = params.page_size;
    if (params.severity) queryParams.severity = params.severity;
    if (params.exposure) queryParams.exposure = params.exposure;

    const response = await apiClient.get<CTEMFindingsResponse>("/ctem/findings", {
      params: queryParams,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getCTEMSummary(): Promise<CTEMSummary> {
  try {
    const response = await apiClient.get<CTEMSummary>("/ctem/summary");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Configuration API
// ============================================================================

import type {
  PolicyConfig,
  NotificationConfig,
  IntegrationConfig,
  FullConfig,
  AuditLog,
  AuditActionType,
  AuditOutcome,
  AuditActionTypeOption,
  AuditOutcomeOption,
} from "../types";

export async function getPolicyConfig(): Promise<PolicyConfig> {
  try {
    const response = await apiClient.get<PolicyConfig>("/config/policy");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function updatePolicyConfig(config: Partial<PolicyConfig>): Promise<PolicyConfig> {
  try {
    const response = await apiClient.put<PolicyConfig>("/config/policy", config);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getNotificationConfig(): Promise<NotificationConfig> {
  try {
    const response = await apiClient.get<NotificationConfig>("/config/notifications");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function updateNotificationConfig(
  config: Partial<NotificationConfig>,
): Promise<NotificationConfig> {
  try {
    const response = await apiClient.put<NotificationConfig>("/config/notifications", config);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getIntegrationConfig(): Promise<IntegrationConfig> {
  try {
    const response = await apiClient.get<IntegrationConfig>("/config/integrations");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function updateIntegrationConfig(
  config: Partial<IntegrationConfig>,
): Promise<IntegrationConfig> {
  try {
    const response = await apiClient.put<IntegrationConfig>("/config/integrations", config);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getFullConfig(): Promise<FullConfig> {
  try {
    const response = await apiClient.get<FullConfig>("/config/all");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function resetConfig(): Promise<{ message: string; timestamp: string }> {
  try {
    const response = await apiClient.post<{ message: string; timestamp: string }>("/config/reset");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Audit API
// ============================================================================

export interface AuditLogsQueryParams {
  page?: number;
  page_size?: number;
  date_from?: string;
  date_to?: string;
  user?: string;
  action_type?: AuditActionType;
  target?: string;
  outcome?: AuditOutcome;
}

export async function getAuditLogs(
  params: AuditLogsQueryParams = {},
): Promise<PaginatedResponse<AuditLog>> {
  try {
    const queryParams: Record<string, string | number> = {};
    if (params.page !== undefined) queryParams.page = params.page;
    if (params.page_size !== undefined) queryParams.page_size = params.page_size;
    if (params.date_from) queryParams.date_from = params.date_from;
    if (params.date_to) queryParams.date_to = params.date_to;
    if (params.user) queryParams.user = params.user;
    if (params.action_type) queryParams.action_type = params.action_type;
    if (params.target) queryParams.target = params.target;
    if (params.outcome) queryParams.outcome = params.outcome;

    const response = await apiClient.get<PaginatedResponse<AuditLog>>("/audit/logs", {
      params: queryParams,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function exportAuditLogs(
  format: "csv" | "json",
  params: Omit<AuditLogsQueryParams, "page" | "page_size"> = {},
): Promise<Blob> {
  try {
    const queryParams: Record<string, string> = { format };
    if (params.date_from) queryParams.date_from = params.date_from;
    if (params.date_to) queryParams.date_to = params.date_to;
    if (params.user) queryParams.user = params.user;
    if (params.action_type) queryParams.action_type = params.action_type;
    if (params.target) queryParams.target = params.target;
    if (params.outcome) queryParams.outcome = params.outcome;

    const response = await apiClient.get("/audit/logs/export", {
      params: queryParams,
      responseType: "blob",
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getAuditUsers(): Promise<{ users: string[] }> {
  try {
    const response = await apiClient.get<{ users: string[] }>("/audit/users");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getAuditActionTypes(): Promise<{ action_types: AuditActionTypeOption[] }> {
  try {
    const response = await apiClient.get<{ action_types: AuditActionTypeOption[] }>(
      "/audit/action-types",
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getAuditOutcomes(): Promise<{ outcomes: AuditOutcomeOption[] }> {
  try {
    const response = await apiClient.get<{ outcomes: AuditOutcomeOption[] }>("/audit/outcomes");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Surface API
// ============================================================================

export async function getSurfaceOverview() {
  try {
    const response = await apiClient.get("/surface/overview");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getSurfaceNodes(params: Record<string, any> = {}) {
  try {
    const response = await apiClient.get("/surface/nodes", { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getSurfaceConnections(params: Record<string, any> = {}) {
  try {
    const response = await apiClient.get("/surface/connections", { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Vulnerabilities API
// ============================================================================

export async function getVulnerabilities(params: Record<string, any> = {}) {
  try {
    const response = await apiClient.get("/vulnerabilities", { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getVulnerabilityDetail(cveId: string) {
  try {
    const response = await apiClient.get(`/vulnerabilities/cves/${cveId}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getVulnerabilitySummary() {
  try {
    const response = await apiClient.get("/vulnerabilities/summary");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// Vulnerability Visualization Endpoints
export async function getVulnerabilityTerrain() {
  try {
    const response = await apiClient.get("/api/vulnerabilities/terrain");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getVulnerabilityHeatmap() {
  try {
    const response = await apiClient.get("/api/vulnerabilities/heatmap");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getVulnerabilitySunburst() {
  try {
    const response = await apiClient.get("/api/vulnerabilities/sunburst");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getVulnerabilityBubbles() {
  try {
    const response = await apiClient.get("/api/vulnerabilities/bubbles");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getRemediationFlow() {
  try {
    const response = await apiClient.get("/vulnerabilities/remediation/flow");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// CVE Nested Page Endpoints
export async function getCVEAffectedAssets(cveId: string, params: { page?: number; page_size?: number } = {}) {
  try {
    const response = await apiClient.get(`/vulnerabilities/cves/${cveId}/assets`, { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getCVEExploits(cveId: string) {
  try {
    const response = await apiClient.get(`/vulnerabilities/cves/${cveId}/exploits`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getSSVCDashboard() {
  try {
    const response = await apiClient.get("/vulnerabilities/ssvc/dashboard");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// ============================================================================
// Threats API
// ============================================================================

export async function getThreats(params: Record<string, any> = {}) {
  try {
    const response = await apiClient.get("/threats", { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getThreatDetail(iocId: string) {
  try {
    const response = await apiClient.get(`/threats/iocs/${iocId}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getThreatMap() {
  try {
    const response = await apiClient.get("/threats/map");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

export async function getThreatMitre() {
  try {
    const response = await apiClient.get("/threats/mitre");
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

// Export the axios instance for custom requests
export { apiClient };

// Export api alias for components that need it (e.g., Graph/useGraphData.ts)
export const api = apiClient;
