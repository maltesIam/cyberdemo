import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "../services/api";
import type {
  Asset,
  Incident,
  Detection,
  Postmortem,
  Ticket,
  AgentAction,
  GenerationStatus,
  DashboardKPIs,
  CTEMFindingsResponse,
  CTEMSummary,
  PolicyConfig,
  NotificationConfig,
  IntegrationConfig,
  FullConfig,
  AuditLog,
  AuditActionTypeOption,
  AuditOutcomeOption,
  PaginatedResponse,
} from "../types";

// ============================================================================
// Generation Hooks
// ============================================================================

export function useGenerationStatus() {
  return useQuery<GenerationStatus>({
    queryKey: ["generation", "status"],
    queryFn: api.getGenerationStatus,
    refetchInterval: 5000, // Poll every 5 seconds
  });
}

export function useGenerateAll() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (seed?: number) => api.generateAll(seed),
    onSuccess: () => {
      // Invalidate all queries to refresh data
      queryClient.invalidateQueries({ queryKey: ["generation"] });
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["detections"] });
      queryClient.invalidateQueries({ queryKey: ["postmortems"] });
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
      queryClient.invalidateQueries({ queryKey: ["agent-actions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useGenerateAssets() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ count, seed }: { count?: number; seed?: number }) =>
      api.generateAssets(count, seed),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["generation"] });
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useGenerateEDR() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ count, seed }: { count?: number; seed?: number }) =>
      api.generateEDR(count, seed),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["generation"] });
      queryClient.invalidateQueries({ queryKey: ["detections"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useGenerateIncidents() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ count, seed }: { count?: number; seed?: number }) =>
      api.generateIncidents(count, seed),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["generation"] });
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useGeneratePostmortems() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ count, seed }: { count?: number; seed?: number }) =>
      api.generatePostmortems(count, seed),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["generation"] });
      queryClient.invalidateQueries({ queryKey: ["postmortems"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useGenerateTickets() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ count, seed }: { count?: number; seed?: number }) =>
      api.generateTickets(count, seed),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["generation"] });
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useGenerateAgentActions() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ count, seed }: { count?: number; seed?: number }) =>
      api.generateAgentActions(count, seed),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["generation"] });
      queryClient.invalidateQueries({ queryKey: ["agent-actions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useResetData() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.resetData,
    onSuccess: () => {
      // Invalidate all queries
      queryClient.invalidateQueries();
    },
  });
}

// ============================================================================
// Assets Hooks
// ============================================================================

export function useAssets(params: api.AssetsQueryParams = {}) {
  return useQuery({
    queryKey: ["assets", params],
    queryFn: () => api.getAssets(params),
  });
}

export function useAsset(id: string | null) {
  return useQuery<Asset>({
    queryKey: ["assets", id],
    queryFn: () => api.getAsset(id!),
    enabled: !!id,
  });
}

// ============================================================================
// Incidents Hooks
// ============================================================================

export function useIncidents(params: api.IncidentsQueryParams = {}) {
  return useQuery({
    queryKey: ["incidents", params],
    queryFn: () => api.getIncidents(params),
  });
}

export function useIncident(id: string | null) {
  return useQuery<Incident>({
    queryKey: ["incidents", id],
    queryFn: () => api.getIncident(id!),
    enabled: !!id,
  });
}

// ============================================================================
// Detections Hooks
// ============================================================================

export function useDetections(params: api.DetectionsQueryParams = {}) {
  return useQuery({
    queryKey: ["detections", params],
    queryFn: () => api.getDetections(params),
  });
}

export function useDetection(id: string | null) {
  return useQuery<Detection>({
    queryKey: ["detections", id],
    queryFn: () => api.getDetection(id!),
    enabled: !!id,
  });
}

// ============================================================================
// Postmortems Hooks
// ============================================================================

export function usePostmortems(params: api.PostmortemsQueryParams = {}) {
  return useQuery({
    queryKey: ["postmortems", params],
    queryFn: () => api.getPostmortems(params),
  });
}

export function usePostmortem(id: string | null) {
  return useQuery<Postmortem>({
    queryKey: ["postmortems", id],
    queryFn: () => api.getPostmortem(id!),
    enabled: !!id,
  });
}

// ============================================================================
// Tickets Hooks
// ============================================================================

export function useTickets(params: api.TicketsQueryParams = {}) {
  return useQuery({
    queryKey: ["tickets", params],
    queryFn: () => api.getTickets(params),
  });
}

export function useTicket(id: string | null) {
  return useQuery<Ticket>({
    queryKey: ["tickets", id],
    queryFn: () => api.getTicket(id!),
    enabled: !!id,
  });
}

// ============================================================================
// Agent Actions Hooks
// ============================================================================

export function useAgentActions(params: api.AgentActionsQueryParams = {}) {
  return useQuery({
    queryKey: ["agent-actions", params],
    queryFn: () => api.getAgentActions(params),
  });
}

export function useAgentAction(id: string | null) {
  return useQuery<AgentAction>({
    queryKey: ["agent-actions", id],
    queryFn: () => api.getAgentAction(id!),
    enabled: !!id,
  });
}

// ============================================================================
// Dashboard Hooks
// ============================================================================

export function useDashboardKPIs() {
  return useQuery<DashboardKPIs>({
    queryKey: ["dashboard", "kpis"],
    queryFn: api.getDashboardKPIs,
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

// ============================================================================
// CTEM Hooks
// ============================================================================

export function useCTEMFindings(params: api.CTEMFindingsQueryParams = {}) {
  return useQuery<CTEMFindingsResponse>({
    queryKey: ["ctem", "findings", params],
    queryFn: () => api.getCTEMFindings(params),
  });
}

export function useCTEMSummary() {
  return useQuery<CTEMSummary>({
    queryKey: ["ctem", "summary"],
    queryFn: api.getCTEMSummary,
  });
}

// ============================================================================
// Configuration Hooks
// ============================================================================

export function usePolicyConfig() {
  return useQuery<PolicyConfig>({
    queryKey: ["config", "policy"],
    queryFn: api.getPolicyConfig,
  });
}

export function useUpdatePolicyConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: Partial<PolicyConfig>) => api.updatePolicyConfig(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["config", "policy"] });
      queryClient.invalidateQueries({ queryKey: ["config", "all"] });
    },
  });
}

export function useNotificationConfig() {
  return useQuery<NotificationConfig>({
    queryKey: ["config", "notifications"],
    queryFn: api.getNotificationConfig,
  });
}

export function useUpdateNotificationConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: Partial<NotificationConfig>) => api.updateNotificationConfig(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["config", "notifications"] });
      queryClient.invalidateQueries({ queryKey: ["config", "all"] });
    },
  });
}

export function useIntegrationConfig() {
  return useQuery<IntegrationConfig>({
    queryKey: ["config", "integrations"],
    queryFn: api.getIntegrationConfig,
  });
}

export function useUpdateIntegrationConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: Partial<IntegrationConfig>) => api.updateIntegrationConfig(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["config", "integrations"] });
      queryClient.invalidateQueries({ queryKey: ["config", "all"] });
    },
  });
}

export function useFullConfig() {
  return useQuery<FullConfig>({
    queryKey: ["config", "all"],
    queryFn: api.getFullConfig,
  });
}

export function useResetConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.resetConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["config"] });
    },
  });
}

// ============================================================================
// Audit Hooks
// ============================================================================

export function useAuditLogs(params: api.AuditLogsQueryParams = {}) {
  return useQuery<PaginatedResponse<AuditLog>>({
    queryKey: ["audit", "logs", params],
    queryFn: () => api.getAuditLogs(params),
  });
}

export function useAuditUsers() {
  return useQuery<{ users: string[] }>({
    queryKey: ["audit", "users"],
    queryFn: api.getAuditUsers,
  });
}

export function useAuditActionTypes() {
  return useQuery<{ action_types: AuditActionTypeOption[] }>({
    queryKey: ["audit", "action-types"],
    queryFn: api.getAuditActionTypes,
  });
}

export function useAuditOutcomes() {
  return useQuery<{ outcomes: AuditOutcomeOption[] }>({
    queryKey: ["audit", "outcomes"],
    queryFn: api.getAuditOutcomes,
  });
}

export function useExportAuditLogs() {
  return useMutation({
    mutationFn: ({
      format,
      params,
    }: {
      format: "csv" | "json";
      params?: Omit<api.AuditLogsQueryParams, "page" | "page_size">;
    }) => api.exportAuditLogs(format, params),
  });
}

// ============================================================================
// Surface Hooks
// ============================================================================

export function useSurfaceOverview() {
  return useQuery({
    queryKey: ["surface-overview"],
    queryFn: () => api.getSurfaceOverview(),
    refetchInterval: 15000,
  });
}

export function useSurfaceNodes(params: Record<string, any> = {}) {
  return useQuery({
    queryKey: ["surface-nodes", params],
    queryFn: () => api.getSurfaceNodes(params),
  });
}

export function useSurfaceConnections(params: Record<string, any> = {}) {
  return useQuery({
    queryKey: ["surface-connections", params],
    queryFn: () => api.getSurfaceConnections(params),
  });
}

// ============================================================================
// Vulnerability Visualization Hooks
// ============================================================================

export function useVulnerabilityTerrain() {
  return useQuery({
    queryKey: ["vulnerabilities", "terrain"],
    queryFn: () => api.getVulnerabilityTerrain(),
    refetchInterval: 60000, // Refresh every minute
  });
}

export function useVulnerabilityHeatmap() {
  return useQuery({
    queryKey: ["vulnerabilities", "heatmap"],
    queryFn: () => api.getVulnerabilityHeatmap(),
    refetchInterval: 60000,
  });
}

export function useVulnerabilitySunburst() {
  return useQuery({
    queryKey: ["vulnerabilities", "sunburst"],
    queryFn: () => api.getVulnerabilitySunburst(),
    refetchInterval: 60000,
  });
}

export function useVulnerabilityBubbles() {
  return useQuery({
    queryKey: ["vulnerabilities", "bubbles"],
    queryFn: () => api.getVulnerabilityBubbles(),
    refetchInterval: 60000,
  });
}

export function useRemediationFlow() {
  return useQuery({
    queryKey: ["vulnerabilities", "remediation-flow"],
    queryFn: () => api.getRemediationFlow(),
    refetchInterval: 60000,
  });
}
