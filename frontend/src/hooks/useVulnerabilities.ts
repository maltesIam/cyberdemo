/**
 * useVulnerabilities - React Query hooks for Vulnerability Intelligence
 *
 * Provides hooks for:
 * - useVulnerabilityOverview: Dashboard overview/summary
 * - useVulnerabilityList: Paginated list with filters
 * - useVulnerabilitySummary: KPI data
 */

import { useQuery } from "@tanstack/react-query";
import * as api from "../services/api";

// ============================================================================
// Types
// ============================================================================

export interface VulnerabilitySummary {
  total_cves: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  kev_count: number;
  exploitable_count: number;
  overdue_count: number;
  remediated_count: number;
  in_progress_count: number;
  open_count: number;
  ssvc_act: number;
  ssvc_attend: number;
  ssvc_track_star: number;
  ssvc_track: number;
  mttr_days: number;
  sla_compliance_percent: number;
}

export interface VulnerabilityListParams {
  page?: number;
  page_size?: number;
  severity?: string;
  cvss_min?: number;
  cvss_max?: number;
  is_kev?: boolean;
  ssvc_decision?: string;
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export interface EnrichedCVE {
  cve_id: string;
  title: string;
  description?: string;
  cvss_v3_score: number;
  cvss_v3_vector?: string;
  epss_score: number;
  epss_percentile?: number;
  risk_score?: number;
  severity: "Critical" | "High" | "Medium" | "Low";
  is_kev: boolean;
  kev_date_added?: string;
  kev_due_date?: string;
  kev_ransomware_use?: boolean;
  ssvc_decision: "Act" | "Attend" | "Track*" | "Track";
  ssvc_exploitation?: string;
  ssvc_automatable?: boolean;
  exploit_count: number;
  exploit_maturity?: string;
  has_nuclei_template?: boolean;
  affected_asset_count?: number;
  affected_critical_assets?: number;
  remediation_status: "open" | "in_progress" | "remediated" | "accepted_risk" | "false_positive";
  assigned_to?: string;
  sla_due_date?: string;
  sla_status?: "on_track" | "at_risk" | "overdue";
  cwe_ids?: string[];
  ecosystems?: string[];
  patch_available?: boolean;
  published_date?: string;
  last_enriched_at?: string;
  enrichment_level?: string;
}

export interface VulnerabilityListResponse {
  data: EnrichedCVE[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ============================================================================
// Hooks
// ============================================================================

/**
 * Hook to fetch vulnerability overview/summary for the dashboard
 * Includes KPIs and aggregate metrics
 */
export function useVulnerabilityOverview() {
  return useQuery<VulnerabilitySummary>({
    queryKey: ["vulnerabilities", "overview"],
    queryFn: async () => {
      const data = await api.getVulnerabilitySummary();
      return data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

/**
 * Hook to fetch paginated list of vulnerabilities with filters
 */
export function useVulnerabilityList(params: VulnerabilityListParams = {}) {
  return useQuery<VulnerabilityListResponse>({
    queryKey: ["vulnerabilities", "list", params],
    queryFn: async () => {
      const data = await api.getVulnerabilities(params);
      return data;
    },
  });
}

/**
 * Hook to fetch vulnerability summary (KPIs)
 * Alias for useVulnerabilityOverview for specific KPI use cases
 */
export function useVulnerabilitySummary() {
  return useQuery<VulnerabilitySummary>({
    queryKey: ["vulnerabilities", "summary"],
    queryFn: async () => {
      const data = await api.getVulnerabilitySummary();
      return data;
    },
    refetchInterval: 30000,
  });
}

/**
 * Hook to fetch a single CVE detail
 */
export function useVulnerabilityDetail(cveId: string | null) {
  return useQuery<EnrichedCVE>({
    queryKey: ["vulnerabilities", "detail", cveId],
    queryFn: async () => {
      if (!cveId) throw new Error("CVE ID required");
      const data = await api.getVulnerabilityDetail(cveId);
      return data;
    },
    enabled: !!cveId,
  });
}

// ============================================================================
// Visualization Hooks
// ============================================================================

import type {
  TerrainViewData,
  CalendarHeatmapData,
  SunburstChartData,
  BubblesViewData,
  DNAViewData,
  SankeyFlowData,
} from "../types/vulnerabilityViews";

/**
 * Hook to fetch terrain visualization data
 * 3D terrain where height = CVSS, color = severity
 */
export function useTerrainData() {
  return useQuery<TerrainViewData>({
    queryKey: ["vulnerabilities", "terrain"],
    queryFn: async () => {
      const data = await api.getVulnerabilityTerrain();
      return data;
    },
    refetchInterval: 60000, // Refresh every minute
  });
}

/**
 * Hook to fetch calendar heatmap data
 * GitHub-style calendar showing CVE discoveries per day
 */
export function useCalendarHeatmapData() {
  return useQuery<CalendarHeatmapData>({
    queryKey: ["vulnerabilities", "heatmap"],
    queryFn: async () => {
      const data = await api.getVulnerabilityHeatmap();
      return data;
    },
    refetchInterval: 60000,
  });
}

/**
 * Hook to fetch sunburst chart data
 * Hierarchical CWE visualization
 */
export function useSunburstData() {
  return useQuery<SunburstChartData>({
    queryKey: ["vulnerabilities", "sunburst"],
    queryFn: async () => {
      const data = await api.getVulnerabilitySunburst();
      return data;
    },
    refetchInterval: 60000,
  });
}

/**
 * Hook to fetch bubbles view data
 * Animated bubbles where size = risk score
 */
export function useBubblesData() {
  return useQuery<BubblesViewData>({
    queryKey: ["vulnerabilities", "bubbles"],
    queryFn: async () => {
      const data = await api.getVulnerabilityBubbles();
      return data;
    },
    refetchInterval: 60000,
  });
}

/**
 * Hook to fetch DNA view data
 * Double helix showing CVE-Asset pairs
 */
export function useDNAData() {
  return useQuery<DNAViewData>({
    queryKey: ["vulnerabilities", "dna"],
    queryFn: async () => {
      // DNA view uses the bubbles endpoint with transformation
      // For now, create mock data structure from bubbles
      const bubbles = await api.getVulnerabilityBubbles();
      const strands = bubbles.bubbles?.slice(0, 20).map((b: any, idx: number) => ({
        cve_id: b.cve_id,
        asset_id: `asset-${idx}`,
        asset_hostname: `host-${idx}.corp.local`,
        cvss_score: b.cvss_score,
        severity: b.severity,
        is_kev: b.is_kev,
        exploit_available: b.is_kev || Math.random() > 0.5,
        position: idx,
      })) || [];
      return {
        strands,
        total_pairs: strands.length,
        kev_pairs: strands.filter((s: any) => s.is_kev).length,
        exploitable_pairs: strands.filter((s: any) => s.exploit_available).length,
      };
    },
    refetchInterval: 60000,
  });
}

/**
 * Hook to fetch Sankey flow data
 * Remediation workflow visualization
 */
export function useSankeyFlowData() {
  return useQuery<SankeyFlowData>({
    queryKey: ["vulnerabilities", "remediation-flow"],
    queryFn: async () => {
      const data = await api.getRemediationFlow();
      return data;
    },
    refetchInterval: 60000,
  });
}
