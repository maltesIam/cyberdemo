/**
 * MCP WebSocket State Types (DATA-005)
 *
 * Defines the JSON schema for WebSocket UI commands
 * sent from the MCP WS Server (port 3001) to React clients.
 */

/** Highlight mode for asset nodes */
export type HighlightMode = 'pulse' | 'glow' | 'zoom';

/** Chart type for floating overlays */
export type ChartType = 'bar' | 'line' | 'pie' | 'area' | 'donut';

/** A single data point for chart overlays */
export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

/** Chart overlay definition from MCP state */
export interface McpChart {
  id: string;
  title: string;
  type: ChartType;
  data: ChartDataPoint[];
  position?: { x: number; y: number };
  autoDismissMs?: number;
}

/** Timeline entry from MCP state */
export interface McpTimelineEntry {
  id: string;
  timestamp: string;
  title: string;
  description: string;
  severity?: 'critical' | 'high' | 'medium' | 'low' | 'info';
  icon?: string;
}

/** Timeline definition from MCP state */
export interface McpTimeline {
  title: string;
  entries: McpTimelineEntry[];
}

/** Highlighted asset definition */
export interface McpHighlightedAsset {
  assetId: string;
  mode: HighlightMode;
  color?: string;
  durationMs?: number;
}

/** KPI override from MCP state */
export interface McpKpiOverride {
  key: string;
  value: number;
  label?: string;
  animateFromZero?: boolean;
}

/**
 * Full MCP state update message.
 * All fields are optional - only changed fields are sent.
 */
export interface McpStateUpdate {
  /** Navigate to a specific page */
  currentPage?: string;
  /** Assets to highlight on the graph page */
  highlightedAssets?: McpHighlightedAsset[];
  /** Charts to display as floating overlays */
  charts?: McpChart[];
  /** Timeline to display as a sliding panel */
  timeline?: McpTimeline | null;
  /** KPI overrides for the dashboard */
  kpiOverrides?: McpKpiOverride[];
  /** Generic metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Return type for useMcpStateSync hook.
 */
export interface McpStateSyncReturn {
  /** Current MCP state (merged from all received updates) */
  state: McpStateUpdate;
  /** WebSocket connection status */
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  /** Whether the WS server is available */
  isConnected: boolean;
  /** Manually trigger a reconnect */
  reconnect: () => void;
  /** Disconnect from the WS server */
  disconnect: () => void;
}
