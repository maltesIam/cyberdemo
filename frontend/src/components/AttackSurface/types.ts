/**
 * Attack Surface Visualization Types
 *
 * Defines types for the multi-layer attack surface visualization system.
 */

/**
 * Available visualization layers
 */
export type LayerType =
  | "base" // Gray - All assets
  | "edr" // Red - Assets with detections
  | "siem" // Orange - Assets in incidents
  | "ctem" // Yellow/Green gradient - Vulnerability risk
  | "vulnerabilities" // Red/Orange - Individual CVE vulnerabilities
  | "threats" // Purple - Related IOCs
  | "containment" // Blue - Contained hosts
  | "relations"; // Cyan - Cause-effect connections

/**
 * Layer configuration with visual properties
 */
export interface LayerConfig {
  id: LayerType;
  label: string;
  colorBase: string;
  colorLight: string;
  colorDark: string;
  description: string;
  icon: "shield" | "alert" | "incident" | "vulnerability" | "threat" | "lock" | "network";
}

/**
 * Asset representation for visualization
 */
export interface VisualAsset {
  id: string;
  hostname: string;
  ip: string;
  type: string;
  riskScore: number;
  // Layer-specific data
  layers: {
    base: boolean;
    edr: {
      active: boolean;
      detectionCount: number;
      severity: "critical" | "high" | "medium" | "low" | null;
      lastAlert: string | null;
    };
    siem: {
      active: boolean;
      incidentCount: number;
      status: "open" | "investigating" | "contained" | "resolved" | null;
    };
    ctem: {
      active: boolean;
      riskLevel: "critical" | "high" | "medium" | "low";
      cveCount: number;
      exposureScore: number;
    };
    vulnerabilities: {
      active: boolean;
      cveCount: number;
      criticalCount: number;
      kevCount: number;
    };
    threats: {
      active: boolean;
      iocCount: number;
      threatActors: string[];
      connections: string[]; // IDs of connected assets
    };
    containment: {
      active: boolean;
      isContained: boolean;
      containedAt: string | null;
      containmentReason: string | null;
    };
    relations: {
      active: boolean;
      connectionCount: number;
    };
  };
  // Position for visualization (optional, can be calculated)
  position?: {
    x: number;
    y: number;
  };
  // Cluster assignment for semantic zoom
  clusterId?: string;
}

/**
 * Cluster for grouped assets at low zoom levels
 */
export interface AssetCluster {
  id: string;
  label: string;
  assetIds: string[];
  center: { x: number; y: number };
  aggregatedMetrics: {
    totalAssets: number;
    criticalCount: number;
    highCount: number;
    containedCount: number;
    activeIncidents: number;
  };
}

/**
 * Time range for temporal filtering
 */
export interface TimeRange {
  start: Date;
  end: Date;
}

/**
 * Zoom level definitions for semantic zoom
 */
export type ZoomLevel = "clustered" | "grouped" | "detailed";

/**
 * Layer state for toggle controls
 */
export interface LayerState {
  id: LayerType;
  enabled: boolean;
  opacity: number;
}

/**
 * Visualization state
 */
export interface VisualizationState {
  layers: LayerState[];
  zoomLevel: ZoomLevel;
  timeRange: TimeRange;
  selectedAssetId: string | null;
  hoveredAssetId: string | null;
}

/**
 * Connection between assets (for threats layer)
 */
export interface AssetConnection {
  sourceId: string;
  targetId: string;
  type: "lateral_movement" | "c2_communication" | "data_exfil" | "shared_ioc";
  strength: number; // 0-1
  timestamp: string;
}

/**
 * Export event for current view
 */
export interface ExportData {
  timestamp: string;
  layers: LayerType[];
  timeRange: TimeRange;
  assets: VisualAsset[];
  connections: AssetConnection[];
}

/**
 * Layer color definitions
 */
export const LAYER_COLORS: Record<LayerType, LayerConfig> = {
  base: {
    id: "base",
    label: "Base",
    colorBase: "#6b7280", // gray-500
    colorLight: "#9ca3af", // gray-400
    colorDark: "#4b5563", // gray-600
    description: "All assets in the infrastructure",
    icon: "shield",
  },
  edr: {
    id: "edr",
    label: "EDR",
    colorBase: "#ef4444", // red-500
    colorLight: "#f87171", // red-400
    colorDark: "#dc2626", // red-600
    description: "Assets with active detections",
    icon: "alert",
  },
  siem: {
    id: "siem",
    label: "SIEM",
    colorBase: "#f97316", // orange-500
    colorLight: "#fb923c", // orange-400
    colorDark: "#ea580c", // orange-600
    description: "Assets involved in incidents",
    icon: "incident",
  },
  ctem: {
    id: "ctem",
    label: "CTEM",
    colorBase: "#eab308", // yellow-500
    colorLight: "#22c55e", // green-500 (for low risk)
    colorDark: "#dc2626", // red-600 (for high risk)
    description: "Vulnerability and exposure risk",
    icon: "vulnerability",
  },
  vulnerabilities: {
    id: "vulnerabilities",
    label: "Vulnerabilities",
    colorBase: "#dc2626", // red-600
    colorLight: "#f97316", // orange-500
    colorDark: "#991b1b", // red-800
    description: "Individual CVE vulnerabilities by severity",
    icon: "vulnerability",
  },
  threats: {
    id: "threats",
    label: "Threats",
    colorBase: "#a855f7", // purple-500
    colorLight: "#c084fc", // purple-400
    colorDark: "#9333ea", // purple-600
    description: "IOC connections and threat actors",
    icon: "threat",
  },
  containment: {
    id: "containment",
    label: "Containment",
    colorBase: "#3b82f6", // blue-500
    colorLight: "#60a5fa", // blue-400
    colorDark: "#2563eb", // blue-600
    description: "Contained and isolated hosts",
    icon: "lock",
  },
  relations: {
    id: "relations",
    label: "Relations",
    colorBase: "#06b6d4", // cyan-500
    colorLight: "#22d3ee", // cyan-400
    colorDark: "#0891b2", // cyan-600
    description: "Cause-effect connections between assets",
    icon: "network",
  },
};

/**
 * Layer order for rendering (bottom to top)
 */
export const LAYER_RENDER_ORDER: LayerType[] = [
  "base",
  "ctem",
  "vulnerabilities",
  "siem",
  "edr",
  "threats",
  "containment",
  "relations",
];

/**
 * Visual mode for the Surface Command Center
 */
export type VisualMode = "surface" | "graph" | "vulns" | "threats" | "timeline";
