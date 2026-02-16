/**
 * MCP Server Type Definitions
 *
 * Types for the Model Context Protocol server that enables
 * Claude to control the CyberDemo frontend UI.
 */

// ============================================================================
// Core MCP Message Types
// ============================================================================

export interface MCPMessage {
  id: string;
  type: "tool_call" | "ping" | "list_tools";
  tool?: string;
  params?: Record<string, unknown>;
}

export interface MCPResponse {
  id: string;
  success: boolean;
  result?: Record<string, unknown>;
  error?: string;
}

export type MCPToolHandler<TInput = unknown, TOutput = unknown> = (
  input: TInput,
  context: MCPContext,
) => Promise<TOutput>;

export interface MCPToolRegistry {
  has(toolName: string): boolean;
  get(toolName: string): MCPToolHandler | undefined;
  listTools(): string[];
  register(toolName: string, handler: MCPToolHandler): void;
}

// ============================================================================
// Demo State Types
// ============================================================================

export interface DemoState {
  activeScenario: 1 | 2 | 3 | null;
  simulationRunning: boolean;
  highlightedAssets: string[];
  currentView: "dashboard" | "graph" | "timeline" | "postmortem" | "assets";
  charts: ChartState[];
  timeline: AlertTimelineState | null;
}

export interface ChartState {
  chart_id: string;
  chart_type: "bar" | "line" | "pie";
  title: string;
  data: ChartData;
}

export interface AlertTimelineState {
  incident_id: string;
  alerts: AlertTimelineEntry[];
}

// ============================================================================
// Tool Input Types
// ============================================================================

export interface ShowSimulationInput {
  simulation_id: string;
  type: string;
  data: Record<string, unknown>;
}

export interface ShowSimulationOutput {
  success: boolean;
  message?: string;
  error?: string;
}

export interface GenerateChartInput {
  chart_type: "bar" | "line" | "pie";
  title: string;
  data: ChartData;
}

export interface GenerateChartOutput {
  success: boolean;
  chart_id?: string;
  error?: string;
}

export interface ChartData {
  labels: string[];
  values: number[];
}

export interface RunDemoScenarioInput {
  scenario: 1 | 2 | 3;
}

export interface RunDemoScenarioOutput {
  success: boolean;
  scenario_name?: string;
  error?: string;
}

export interface GetDemoStateInput {
  // No input required
}

export interface GetDemoStateOutput {
  success: boolean;
  state?: DemoState;
  error?: string;
}

export interface UpdateDashboardInput {
  kpis?: {
    total_incidents: number;
    critical_open: number;
    hosts_contained: number;
    mttr_hours: number;
  };
  charts?: ChartUpdate[];
}

export interface ChartUpdate {
  chart_id: string;
  data: ChartData;
}

export interface UpdateDashboardOutput {
  success: boolean;
  error?: string;
}

export interface ShowAlertTimelineInput {
  incident_id: string;
  alerts: AlertTimelineEntry[];
}

export interface AlertTimelineEntry {
  timestamp: string;
  type: "detection" | "containment" | "enrichment" | "analysis" | "notification";
  severity: "critical" | "high" | "medium" | "low" | "info";
  description: string;
}

export interface ShowAlertTimelineOutput {
  success: boolean;
  error?: string;
}

export interface HighlightAssetInput {
  asset_id: string;
  highlight_type: "pulse" | "glow" | "zoom";
}

export interface HighlightAssetOutput {
  success: boolean;
  error?: string;
}

export interface ShowPostmortemInput {
  postmortem_id: string;
}

export interface ShowPostmortemOutput {
  success: boolean;
  error?: string;
}

// ============================================================================
// Context Types
// ============================================================================

export interface MCPContext {
  setState: (updater: (prevState: DemoState) => DemoState) => void;
  getState: () => DemoState;
}

// ============================================================================
// Scenario Definitions
// ============================================================================

export const SCENARIOS = {
  1: {
    name: "Ransomware Attack",
    description: "Simulates a ransomware attack with encryption and lateral movement",
  },
  2: {
    name: "Data Exfiltration",
    description: "Simulates data theft via compromised credentials",
  },
  3: {
    name: "Lateral Movement",
    description: "Simulates an attacker moving through the network",
  },
} as const;
