/**
 * SurfacePage - Cyber Exposure Command Center
 *
 * The main Surface WOW page with 5 zones:
 * - Header Bar (top): mode tabs, search, export
 * - Layer Panel (left): presets, 8 layer toggles
 * - Canvas Central (center): asset nodes with layer rings
 * - Detail Panel (right): slide-in asset details
 * - Bottom Bar: KPI chips
 */

import { useState, useCallback, useEffect, useMemo, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import clsx from "clsx";
import { useSurfaceOverview, useSurfaceNodes, useSurfaceConnections } from "../hooks/useApi";
import type { LayerType, VisualMode, ZoomLevel } from "../components/AttackSurface/types";
import { LAYER_COLORS, LAYER_RENDER_ORDER } from "../components/AttackSurface/types";
import * as api from "../services/api";
import {
  GlobalFilters,
  DEFAULT_GLOBAL_FILTERS,
  LayerFilters,
  DEFAULT_LAYER_FILTERS,
  SearchBar,
  BottomBar,
  DEFAULT_TIME_RANGE,
  QueryBuilder,
} from "../components/surface";
import type { GlobalFilterState } from "../components/surface";
import type { LayerFilterState } from "../components/surface";
import type { TimeRangeState } from "../components/surface";
import type { SearchResult } from "../components/surface";

// ============================================================================
// Constants
// ============================================================================

const STORAGE_KEY = "surface-layers";

const ALL_LAYERS: LayerType[] = LAYER_RENDER_ORDER;

/** Layer preset definitions */
const PRESETS: Record<string, { label: string; layers: LayerType[] }> = {
  soc: {
    label: "SOC",
    layers: ["base", "edr", "siem", "ctem"],
  },
  hunt: {
    label: "Hunt",
    layers: ["base", "threats", "relations", "edr"],
  },
  vuln: {
    label: "Vuln",
    layers: ["base", "vulnerabilities", "ctem"],
  },
  contain: {
    label: "Contain",
    layers: ["base", "siem", "edr", "containment"],
  },
  full: {
    label: "Full",
    layers: [...ALL_LAYERS],
  },
};

/** Mode tab definitions */
const MODE_TABS: { id: VisualMode; label: string; icon: string }[] = [
  { id: "surface", label: "Surface 2D", icon: "grid" },
  { id: "graph", label: "Graph", icon: "graph" },
  { id: "vulns", label: "Vuln Landscape", icon: "vuln" },
  { id: "threats", label: "Threat Map", icon: "threat" },
  { id: "timeline", label: "Timeline", icon: "timeline" },
];

/** Connection type colors for graph mode */
const CONNECTION_COLORS: Record<string, string> = {
  lateral_movement: "#ef4444",
  c2_communication: "#f97316",
  c2: "#f97316",
  data_exfil: "#a855f7",
  shared_ioc: "#06b6d4",
};

/** Asset type icons (simple SVG paths) */
const ASSET_ICONS: Record<string, string> = {
  server: "M5 12H3l9-9 9 9h-2M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7",
  workstation:
    "M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z",
  laptop: "M12 18h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z",
  virtual_machine:
    "M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z",
  container: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",
};

// ============================================================================
// Helpers
// ============================================================================

/** Load layer selection from localStorage */
function loadLayersFromStorage(): Set<LayerType> {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as LayerType[];
      if (Array.isArray(parsed) && parsed.length > 0) {
        // Always include base
        const set = new Set<LayerType>(parsed);
        set.add("base");
        return set;
      }
    }
  } catch {
    // Ignore parse errors
  }
  // Default: SOC preset
  return new Set<LayerType>(PRESETS.soc.layers);
}

/** Save layer selection to localStorage */
function saveLayersToStorage(layers: Set<LayerType>) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...layers]));
  } catch {
    // Ignore storage errors
  }
}

/** Generate deterministic pseudo-random number from seed */
function seededRandom(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 16807 + 0) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

// ============================================================================
// Sub-components
// ============================================================================

/** Mode tab icon renderer */
function ModeIcon({ mode, className }: { mode: string; className?: string }) {
  const base = clsx("w-5 h-5", className);
  switch (mode) {
    case "grid":
      return (
        <svg className={base} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
          />
        </svg>
      );
    case "graph":
      return (
        <svg className={base} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
          />
        </svg>
      );
    case "vuln":
      return (
        <svg className={base} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      );
    case "threat":
      return (
        <svg className={base} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      );
    case "timeline":
      return (
        <svg className={base} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      );
    default:
      return null;
  }
}

/** Asset type icon SVG */
function AssetTypeIcon({ type, className }: { type: string; className?: string }) {
  const path = ASSET_ICONS[type] ?? ASSET_ICONS.server ?? "";
  return (
    <svg
      className={clsx("w-4 h-4", className)}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={path} />
    </svg>
  );
}

/** Enhanced asset node in the surface canvas with WOW effects */
function SurfaceAssetNode({
  node,
  activeLayers,
  isSelected,
  onClick,
  zoomLevel,
}: {
  node: any;
  activeLayers: Set<LayerType>;
  isSelected: boolean;
  onClick: () => void;
  zoomLevel?: ZoomLevel;
}) {
  const [isHovered, setIsHovered] = useState(false);
  const tooltipTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);

  const hostname = node?.hostname ?? "unknown";
  const ip = node?.ip ?? "N/A";
  const type = node?.type ?? "server";
  const owner = node?.owner ?? "N/A";
  const riskScore = node?.risk_score ?? node?.riskScore ?? 50;
  const isCritical = riskScore >= 80;
  const hasKEV = (node?.layers?.vulnerabilities?.kevCount ?? 0) > 0;
  const ctemRisk = node?.layers?.ctem?.riskLevel ?? "medium";
  const isCTEMHighRisk = ctemRisk === "critical" || ctemRisk === "high";
  const detectionCount = node?.layers?.edr?.detectionCount ?? 0;
  const incidentCount = node?.layers?.siem?.incidentCount ?? 0;

  // Calculate size based on risk score
  const baseSize = zoomLevel === "detailed" ? 48 : zoomLevel === "clustered" ? 28 : 40;
  const size = baseSize + (riskScore / 100) * 20;

  // Determine rings from active layers that match this node
  const rings = useMemo(() => {
    const result: { color: string; layer: LayerType }[] = [];
    for (const layerId of LAYER_RENDER_ORDER) {
      if (!activeLayers.has(layerId)) continue;
      if (layerId === "base") continue;
      const layerData = node?.layers?.[layerId];
      if (layerData?.active) {
        result.push({ color: LAYER_COLORS[layerId].colorBase, layer: layerId });
      }
    }
    return result;
  }, [node, activeLayers]);

  const primaryColor =
    rings.length > 0
      ? (rings[rings.length - 1]?.color ?? LAYER_COLORS.base.colorBase)
      : LAYER_COLORS.base.colorBase;

  // Hover handlers with tooltip delay
  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
    tooltipTimerRef.current = setTimeout(() => {
      setShowTooltip(true);
    }, 250);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
    setShowTooltip(false);
    if (tooltipTimerRef.current) {
      clearTimeout(tooltipTimerRef.current);
      tooltipTimerRef.current = null;
    }
  }, []);

  // Double-click handler for zoom-to-node
  const handleDoubleClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      const event = new CustomEvent("surface-zoom-to-node", { detail: { nodeId: node?.id } });
      window.dispatchEvent(event);
      console.log("[Surface] Zoom to node:", node?.id, hostname);
    },
    [node?.id, hostname],
  );

  useEffect(() => {
    return () => {
      if (tooltipTimerRef.current) clearTimeout(tooltipTimerRef.current);
    };
  }, []);

  // Determine CSS animation class
  const animationClass = useMemo(() => {
    if (hasKEV && activeLayers.has("vulnerabilities")) return "surface-shake-subtle";
    if (isCTEMHighRisk && activeLayers.has("ctem")) return "surface-gradient-pulse";
    if (isCritical) return "surface-glow-pulse";
    return "";
  }, [hasKEV, isCTEMHighRisk, isCritical, activeLayers]);

  return (
    <div
      onClick={onClick}
      onDoubleClick={handleDoubleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={clsx(
        "relative flex flex-col items-center cursor-pointer transition-transform duration-200",
        isSelected && "scale-110 z-10",
        isHovered && !isSelected && "scale-110 z-10",
        !isSelected && !isHovered && "hover:scale-105",
      )}
    >
      {/* Outer rings for each active layer */}
      <div
        className="relative"
        style={{ width: size + rings.length * 6, height: size + rings.length * 6 }}
      >
        {rings.map((ring, i) => (
          <div
            key={ring.layer}
            className={clsx(
              "absolute rounded-full transition-opacity duration-200",
              activeLayers.has(ring.layer) ? "surface-fade-in" : "surface-fade-out",
            )}
            style={{
              inset: i * 3,
              border: `2px solid ${ring.color}80`,
              backgroundColor: `${ring.color}10`,
            }}
          />
        ))}

        {/* Detection count badge (top-left) */}
        {detectionCount > 0 && zoomLevel !== "clustered" && (
          <div
            className="absolute -top-1 -left-1 w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold text-white z-20"
            style={{ backgroundColor: LAYER_COLORS.edr.colorBase }}
            title={`${detectionCount} detections`}
          >
            {detectionCount > 9 ? "9+" : detectionCount}
          </div>
        )}

        {/* Incident count badge (top-right) */}
        {incidentCount > 0 && zoomLevel !== "clustered" && (
          <div
            className="absolute -top-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold text-white z-20"
            style={{ backgroundColor: LAYER_COLORS.siem.colorBase }}
            title={`${incidentCount} incidents`}
          >
            {incidentCount > 9 ? "9+" : incidentCount}
          </div>
        )}

        {/* Main circle */}
        <div
          className={clsx(
            "absolute rounded-full flex items-center justify-center text-white font-bold text-xs",
            animationClass,
            isSelected && "ring-2 ring-cyan-400 ring-offset-2 ring-offset-gray-900",
          )}
          style={{
            inset: rings.length * 3,
            backgroundColor: primaryColor,
            boxShadow: isCritical
              ? `0 0 16px ${primaryColor}80, 0 0 32px ${primaryColor}40`
              : `0 0 8px ${primaryColor}60`,
            ...(animationClass === "surface-glow-pulse"
              ? ({ "--glow-color": primaryColor } as React.CSSProperties)
              : {}),
          }}
        >
          {zoomLevel === "detailed" ? (
            <AssetTypeIcon type={type} className="text-white/90" />
          ) : (
            <span>{riskScore}</span>
          )}
        </div>
      </div>

      {/* Hostname label - hidden at clustered zoom */}
      {zoomLevel !== "clustered" && (
        <span className="mt-1.5 text-[10px] font-mono text-gray-400 max-w-[80px] truncate text-center">
          {hostname}
        </span>
      )}

      {/* Tooltip on hover */}
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 pointer-events-none surface-fade-in">
          <div className="bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 shadow-xl min-w-[180px]">
            <div className="text-white text-xs font-bold mb-1">{hostname}</div>
            <div className="space-y-0.5 text-[10px]">
              <div className="flex justify-between text-gray-400">
                <span>IP</span>
                <span className="text-gray-300 font-mono">{ip}</span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Type</span>
                <span className="text-gray-300 capitalize">
                  {type?.replace?.(/_/g, " ") ?? type}
                </span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Owner</span>
                <span className="text-gray-300">{owner}</span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Risk</span>
                <span
                  className={clsx(
                    "font-bold",
                    riskScore >= 80 && "text-red-400",
                    riskScore >= 60 && riskScore < 80 && "text-orange-400",
                    riskScore >= 40 && riskScore < 60 && "text-yellow-400",
                    riskScore < 40 && "text-green-400",
                  )}
                >
                  {riskScore}/100
                </span>
              </div>
            </div>
            {/* Tooltip arrow */}
            <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-600" />
          </div>
        </div>
      )}
    </div>
  );
}

/** Detail panel that slides in from the right */
function DetailPanel({
  node,
  activeLayers,
  onClose,
  isPinned,
  onTogglePin,
}: {
  node: any;
  activeLayers: Set<LayerType>;
  onClose: () => void;
  isPinned: boolean;
  onTogglePin: () => void;
}) {
  if (!node) return null;

  const hostname = node?.hostname ?? "unknown";
  const ip = node?.ip ?? "N/A";
  const type = node?.type ?? "unknown";
  const os = node?.os ?? "N/A";
  const owner = node?.owner ?? "N/A";
  const riskScore = node?.risk_score ?? node?.riskScore ?? 0;

  return (
    <div className="w-[360px] bg-gray-800 border-l border-gray-700 flex flex-col h-full overflow-hidden animate-slide-in-right">
      {/* Panel header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <h3 className="text-white font-semibold truncate">{hostname}</h3>
        <div className="flex items-center gap-1">
          <button
            onClick={onTogglePin}
            className={clsx(
              "p-1.5 rounded transition-colors",
              isPinned ? "text-cyan-400 bg-cyan-900/30" : "text-gray-500 hover:text-gray-300",
            )}
            title={isPinned ? "Unpin panel" : "Pin panel"}
          >
            <svg
              className="w-4 h-4"
              fill={isPinned ? "currentColor" : "none"}
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
              />
            </svg>
          </button>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-500 hover:text-white transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Basic info */}
        <div className="space-y-2">
          <InfoRow label="IP Address" value={ip} mono />
          <InfoRow label="Type" value={type?.replace?.(/_/g, " ") ?? type} />
          <InfoRow label="OS" value={os} />
          <InfoRow label="Owner" value={owner} />
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Risk Score</span>
            <span
              className={clsx(
                "px-2 py-0.5 rounded text-xs font-bold",
                riskScore >= 80 && "bg-red-900/60 text-red-300",
                riskScore >= 60 && riskScore < 80 && "bg-orange-900/60 text-orange-300",
                riskScore >= 40 && riskScore < 60 && "bg-yellow-900/60 text-yellow-300",
                riskScore < 40 && "bg-green-900/60 text-green-300",
              )}
            >
              {riskScore}/100
            </span>
          </div>
        </div>

        {/* Layer sections */}
        {LAYER_RENDER_ORDER.filter((l) => activeLayers.has(l) && l !== "base").map((layerId) => {
          const config = LAYER_COLORS[layerId];
          const layerData = node?.layers?.[layerId];
          if (!layerData?.active) return null;

          return (
            <div
              key={layerId}
              className="p-3 rounded-lg border"
              style={{
                backgroundColor: `${config.colorBase}10`,
                borderColor: `${config.colorBase}30`,
              }}
            >
              <div className="flex items-center gap-2 mb-2">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: config.colorBase }}
                />
                <span className="text-sm font-medium" style={{ color: config.colorLight }}>
                  {config.label}
                </span>
              </div>
              <div className="space-y-1 text-xs">
                {layerId === "edr" && (
                  <>
                    <DetailRow label="Detections" value={layerData?.detectionCount ?? 0} />
                    {layerData?.severity && (
                      <DetailRow label="Severity" value={layerData.severity} />
                    )}
                  </>
                )}
                {layerId === "siem" && (
                  <>
                    <DetailRow label="Incidents" value={layerData?.incidentCount ?? 0} />
                    {layerData?.status && <DetailRow label="Status" value={layerData.status} />}
                  </>
                )}
                {layerId === "ctem" && (
                  <>
                    <DetailRow label="CVEs" value={layerData?.cveCount ?? 0} />
                    <DetailRow label="Risk Level" value={layerData?.riskLevel ?? "N/A"} />
                    <DetailRow label="Exposure" value={layerData?.exposureScore ?? 0} />
                  </>
                )}
                {layerId === "vulnerabilities" && (
                  <>
                    <DetailRow label="Total CVEs" value={layerData?.cveCount ?? 0} />
                    <DetailRow label="Critical" value={layerData?.criticalCount ?? 0} />
                    <DetailRow label="KEV Count" value={layerData?.kevCount ?? 0} />
                  </>
                )}
                {layerId === "threats" && (
                  <>
                    <DetailRow label="IOCs" value={layerData?.iocCount ?? 0} />
                    {(layerData?.threatActors?.length ?? 0) > 0 && (
                      <div className="mt-1">
                        <span className="text-gray-500">Threat Actors:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {(layerData?.threatActors ?? []).map((actor: string) => (
                            <span
                              key={actor}
                              className="px-1.5 py-0.5 bg-purple-900/50 text-purple-300 rounded text-[10px]"
                            >
                              {actor}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
                {layerId === "containment" && (
                  <>
                    <DetailRow
                      label="Status"
                      value={layerData?.isContained ? "Contained" : "Not Contained"}
                    />
                    {layerData?.containmentReason && (
                      <DetailRow label="Reason" value={layerData.containmentReason} />
                    )}
                  </>
                )}
                {layerId === "relations" && (
                  <DetailRow label="Connections" value={layerData?.connectionCount ?? 0} />
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Action buttons */}
      <div className="p-4 border-t border-gray-700 space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <ActionButton label="Investigate" color="cyan" />
          <ActionButton label="Contain" color="orange" />
          <ActionButton label="Create Ticket" color="blue" />
          <ActionButton label="Export" color="gray" />
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-gray-500">{label}</span>
      <span className={clsx("text-gray-300", mono && "font-mono")}>{value}</span>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex justify-between text-gray-400">
      <span>{label}</span>
      <span className="text-white capitalize">{String(value)}</span>
    </div>
  );
}

function ActionButton({ label, color }: { label: string; color: string }) {
  const colorMap: Record<string, string> = {
    cyan: "bg-cyan-600 hover:bg-cyan-500 text-white",
    orange: "bg-orange-600 hover:bg-orange-500 text-white",
    blue: "bg-blue-600 hover:bg-blue-500 text-white",
    gray: "bg-gray-600 hover:bg-gray-500 text-gray-200",
  };
  return (
    <button
      className={clsx(
        "px-3 py-2 rounded-lg text-xs font-medium transition-colors",
        colorMap[color] ?? colorMap.gray,
      )}
    >
      {label}
    </button>
  );
}

/** Context menu that appears on right-click */
function ContextMenu({
  x,
  y,
  nodeId,
  onClose,
}: {
  x: number;
  y: number;
  nodeId: string | null;
  onClose: () => void;
}) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [onClose]);

  const items = [
    { label: "Investigate", icon: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" },
    {
      label: "Contain",
      icon: "M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z",
    },
    {
      label: "Create Ticket",
      icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2",
    },
    {
      label: "Copy ID",
      icon: "M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3",
    },
    { label: "Export", icon: "M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" },
  ];

  return (
    <div ref={menuRef} className="fixed z-50 surface-fade-in" style={{ left: x, top: y }}>
      <div className="bg-gray-800 border border-gray-600 rounded-lg shadow-2xl py-1 min-w-[160px]">
        {nodeId && (
          <div className="px-3 py-1.5 text-[10px] text-gray-500 border-b border-gray-700 font-mono truncate max-w-[200px]">
            {nodeId}
          </div>
        )}
        {items.map((item) => (
          <button
            key={item.label}
            onClick={() => {
              if (item.label === "Copy ID" && nodeId) {
                navigator.clipboard?.writeText?.(nodeId);
              }
              console.log("[Surface] Context action:", item.label, nodeId);
              onClose();
            }}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
          >
            <svg
              className="w-4 h-4 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
            </svg>
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function SurfacePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const canvasRef = useRef<HTMLDivElement>(null);

  // Mode from URL param, default "surface"
  const currentMode = (searchParams.get("mode") as VisualMode) ?? "surface";

  // Layer state with localStorage persistence
  const [activeLayers, setActiveLayers] = useState<Set<LayerType>>(() => loadLayersFromStorage());

  // Selected asset for detail panel
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [isPanelPinned, setIsPanelPinned] = useState(false);

  // Multi-selection support
  const [selectedNodes, setSelectedNodes] = useState<Set<string>>(new Set());

  // Search input
  const [searchQuery, setSearchQuery] = useState("");

  // Global filters state
  const [globalFilters, setGlobalFilters] = useState<GlobalFilterState>(DEFAULT_GLOBAL_FILTERS);

  // Per-layer filters
  const [layerFilters, setLayerFilters] = useState<LayerFilterState>(DEFAULT_LAYER_FILTERS);

  // Time range (for BottomBar timeline)
  const [timeRange, setTimeRange] = useState<TimeRangeState>(DEFAULT_TIME_RANGE);

  // Query builder modal
  const [showQueryBuilder, setShowQueryBuilder] = useState(false);

  // Active layer for layer-specific filters (null = none expanded)
  const [expandedLayerFilter, setExpandedLayerFilter] = useState<LayerType | null>(null);

  // Toast notification (auto-dismiss)
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Mode transition animation
  const [modeTransition, setModeTransition] = useState<"idle" | "fading-out" | "fading-in">("idle");
  const prevModeRef = useRef(currentMode);

  // API data
  const { data: overview } = useSurfaceOverview();
  const { data: nodesData } = useSurfaceNodes();

  // Persist layers to localStorage on change
  useEffect(() => {
    saveLayersToStorage(activeLayers);
  }, [activeLayers]);

  // Mode transition effect
  useEffect(() => {
    if (prevModeRef.current !== currentMode) {
      setModeTransition("fading-out");
      const t1 = setTimeout(() => {
        setModeTransition("fading-in");
        prevModeRef.current = currentMode;
      }, 200);
      const t2 = setTimeout(() => {
        setModeTransition("idle");
      }, 500);
      return () => {
        clearTimeout(t1);
        clearTimeout(t2);
      };
    }
  }, [currentMode]);

  // Derive nodes array safely
  const nodes: any[] = useMemo(() => {
    if (Array.isArray(nodesData)) return nodesData;
    if (nodesData?.nodes && Array.isArray(nodesData.nodes)) return nodesData.nodes;
    if (nodesData?.items && Array.isArray(nodesData.items)) return nodesData.items;
    return [];
  }, [nodesData]);

  // Filter nodes by search query and global filters
  const filteredNodes = useMemo(() => {
    let result = nodes;

    // Apply search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter((n: any) => {
        const hostname = (n?.hostname ?? "").toLowerCase();
        const ip = (n?.ip ?? "").toLowerCase();
        const id = (n?.id ?? "").toLowerCase();
        return hostname.includes(q) || ip.includes(q) || id.includes(q);
      });
    }

    // Apply global filters
    if (globalFilters.assetTypes.length > 0) {
      result = result.filter((n: any) => globalFilters.assetTypes.includes(n?.type ?? ""));
    }
    if (globalFilters.riskMin > 0) {
      result = result.filter(
        (n: any) => (n?.risk_score ?? n?.riskScore ?? 0) >= globalFilters.riskMin,
      );
    }
    if (globalFilters.riskMax < 100) {
      result = result.filter(
        (n: any) => (n?.risk_score ?? n?.riskScore ?? 0) <= globalFilters.riskMax,
      );
    }
    if (globalFilters.severities.length > 0) {
      result = result.filter((n: any) => {
        const edrSev = n?.layers?.edr?.severity ?? "";
        const siemSev = n?.layers?.siem?.severity ?? "";
        return (
          globalFilters.severities.includes(edrSev) || globalFilters.severities.includes(siemSev)
        );
      });
    }

    return result;
  }, [nodes, searchQuery, globalFilters]);

  // Handle search result selection
  const handleSearchSelect = useCallback(
    (result: SearchResult) => {
      const matchNode = nodes.find(
        (n: any) =>
          (n?.id ?? "") === result.id ||
          (n?.hostname ?? "") === result.label ||
          (n?.ip ?? "") === result.label,
      );
      if (matchNode) {
        setSelectedNode(matchNode);
      }
    },
    [nodes],
  );

  // Handle query builder apply
  const handleQueryApply = useCallback((query: string) => {
    setSearchQuery(query);
    setShowQueryBuilder(false);
  }, []);

  // Show toast with auto-dismiss (3s)
  const showToast = useCallback((msg: string) => {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    setToastMessage(msg);
    toastTimerRef.current = setTimeout(() => setToastMessage(null), 3000);
  }, []);

  // High-density layer names and approximate element counts
  const HIGH_DENSITY_LAYERS: Partial<Record<LayerType, string>> = {
    vulnerabilities: "CVEs",
    threats: "IOCs",
    relations: "connections",
  };

  // Layer toggle handler
  const toggleLayer = useCallback(
    (layerId: LayerType) => {
      if (layerId === "base") return; // Base is always on
      setActiveLayers((prev) => {
        const next = new Set(prev);
        const isActivating = !next.has(layerId);
        if (isActivating) {
          next.add(layerId);
        } else {
          next.delete(layerId);
        }
        // Toast for high-density layers
        if (isActivating && layerId in HIGH_DENSITY_LAYERS) {
          const elementType = HIGH_DENSITY_LAYERS[layerId as keyof typeof HIGH_DENSITY_LAYERS];
          const count =
            layerId === "vulnerabilities"
              ? (overview?.total_vulnerabilities ?? overview?.vulnerabilities ?? 0)
              : layerId === "threats"
                ? (overview?.total_iocs ?? overview?.iocs ?? 0)
                : (overview?.total_connections ?? 0);
          showToast(
            `${LAYER_COLORS[layerId]?.label ?? layerId} layer activated — ${count} ${elementType} added to canvas`,
          );
        }
        return next;
      });
    },
    [overview, showToast],
  );

  // Handle KPI chip click (filters canvas to relevant subset)
  const handleKpiClick = useCallback(
    (kpiType: string) => {
      console.log("[Surface] KPI click:", kpiType);
      switch (kpiType) {
        case "contained":
          if (!activeLayers.has("containment")) toggleLayer("containment");
          break;
        case "iocs":
          if (!activeLayers.has("threats")) toggleLayer("threats");
          break;
      }
    },
    [activeLayers, toggleLayer],
  );

  // Preset handler
  const applyPreset = useCallback((presetKey: string) => {
    const preset = PRESETS[presetKey];
    if (!preset) return;
    setActiveLayers(new Set(preset.layers));
  }, []);

  // Reset layers to SOC default
  const resetLayers = useCallback(() => {
    setActiveLayers(new Set(PRESETS.soc.layers));
  }, []);

  // Export current view data as JSON or CSV
  const handleExport = useCallback(
    (format: "json" | "csv" = "json") => {
      const data = filteredNodes.map((n: any) => ({
        id: n?.id ?? "",
        hostname: n?.hostname ?? "",
        ip: n?.ip ?? "",
        type: n?.type ?? "",
        risk_score: n?.risk_score ?? n?.riskScore ?? 0,
        edr_detections: n?.layers?.edr?.detections ?? 0,
        siem_incidents: n?.layers?.siem?.incidents ?? 0,
        ctem_risk: n?.layers?.ctem?.riskLevel ?? "",
        contained: n?.layers?.containment?.isContained ?? false,
      }));

      let content: string;
      let mimeType: string;
      let ext: string;

      if (format === "csv") {
        const headers = Object.keys(data[0] ?? {});
        const rows = data.map((row: any) => headers.map((h) => String(row[h] ?? "")).join(","));
        content = [headers.join(","), ...rows].join("\n");
        mimeType = "text/csv";
        ext = "csv";
      } else {
        content = JSON.stringify(data, null, 2);
        mimeType = "application/json";
        ext = "json";
      }

      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `surface-export-${new Date().toISOString().slice(0, 10)}.${ext}`;
      a.click();
      URL.revokeObjectURL(url);
      showToast(`Exported ${data.length} assets as ${ext.toUpperCase()}`);
    },
    [filteredNodes, showToast],
  );

  // Mode switch
  const setMode = useCallback(
    (mode: VisualMode) => {
      setSearchParams({ mode });
    },
    [setSearchParams],
  );

  // Select/deselect node (with Ctrl+click for multi-select)
  const handleNodeClick = useCallback(
    (node: any, ctrlKey?: boolean) => {
      if (ctrlKey) {
        setSelectedNodes((prev) => {
          const next = new Set(prev);
          const id = node?.id ?? "";
          if (next.has(id)) {
            next.delete(id);
          } else {
            next.add(id);
          }
          return next;
        });
        return;
      }
      if (selectedNode?.id === node?.id && !isPanelPinned) {
        setSelectedNode(null);
      } else {
        setSelectedNode(node);
      }
      setSelectedNodes(new Set());
    },
    [selectedNode, isPanelPinned],
  );

  const closeDetail = useCallback(() => {
    setSelectedNode(null);
    setIsPanelPinned(false);
  }, []);

  const activeLayerCount = activeLayers.size;

  // Mode transition CSS class
  const modeTransitionClass = useMemo(() => {
    if (modeTransition === "fading-out") return "surface-mode-fade-out";
    if (modeTransition === "fading-in") return "surface-mode-fade-in";
    return "";
  }, [modeTransition]);

  return (
    <div className="flex flex-col h-full bg-gray-900 overflow-hidden">
      {/* ================================================================ */}
      {/* HEADER BAR */}
      {/* ================================================================ */}
      <header className="flex-shrink-0 flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        {/* Title */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center">
            <svg
              className="w-5 h-5 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h1 className="text-white font-bold text-lg hidden lg:block">
            Cyber Exposure Command Center
          </h1>
        </div>

        {/* Mode tabs */}
        <div className="flex items-center bg-gray-900 rounded-lg p-0.5">
          {MODE_TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setMode(tab.id)}
              className={clsx(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors",
                currentMode === tab.id
                  ? "bg-cyan-600 text-white shadow"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-700",
              )}
              title={tab.label}
            >
              <ModeIcon mode={tab.icon} className="w-4 h-4" />
              <span className="hidden xl:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Search + Query Builder + Export */}
        <div className="flex items-center gap-2">
          <SearchBar value={searchQuery} onChange={setSearchQuery} onSelect={handleSearchSelect} />
          <button
            onClick={() => setShowQueryBuilder(true)}
            className="p-1.5 bg-gray-700 hover:bg-gray-600 text-gray-400 hover:text-cyan-400 rounded-lg transition-colors"
            title="Advanced Query Builder"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
              />
            </svg>
          </button>
          <div className="relative group">
            <button
              onClick={() => handleExport("json")}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg text-sm transition-colors"
              title="Export as JSON (right-click for CSV)"
              onContextMenu={(e) => {
                e.preventDefault();
                handleExport("csv");
              }}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              <span className="hidden sm:inline">Export</span>
            </button>
          </div>
        </div>
      </header>

      {/* ================================================================ */}
      {/* MAIN CONTENT: Layer Panel + Canvas + Detail Panel */}
      {/* ================================================================ */}
      <div className="flex flex-1 overflow-hidden">
        {/* LEFT: Layer Panel */}
        <aside className="w-[240px] flex-shrink-0 bg-gray-800 border-r border-gray-700 flex flex-col overflow-y-auto">
          {/* Preset chips */}
          <div className="p-3 border-b border-gray-700">
            <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Presets</p>
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(PRESETS).map(([key, preset]) => {
                // Determine if this preset is currently active
                const isActive =
                  preset.layers.length === activeLayers.size &&
                  preset.layers.every((l) => activeLayers.has(l));
                return (
                  <button
                    key={key}
                    onClick={() => applyPreset(key)}
                    className={clsx(
                      "px-2.5 py-1 rounded text-xs font-medium transition-colors",
                      isActive
                        ? "bg-cyan-600 text-white"
                        : "bg-gray-700 text-gray-300 hover:bg-gray-600",
                    )}
                  >
                    {preset.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Layer toggles */}
          <div className="flex-1 p-3 space-y-1">
            <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Layers</p>
            {ALL_LAYERS.map((layerId) => {
              const config = LAYER_COLORS[layerId];
              const isEnabled = activeLayers.has(layerId);
              const isBase = layerId === "base";

              // Count badge - rough count from nodes matching this layer
              const count = nodes.filter((n: any) => {
                if (layerId === "base") return true;
                return n?.layers?.[layerId]?.active;
              }).length;

              return (
                <button
                  key={layerId}
                  onClick={() => toggleLayer(layerId)}
                  disabled={isBase}
                  className={clsx(
                    "w-full flex items-center gap-2 px-2.5 py-2 rounded-lg text-left transition-colors",
                    isBase && "opacity-70 cursor-default",
                    isEnabled && !isBase && "bg-gray-700/50",
                    !isEnabled && !isBase && "hover:bg-gray-700/30",
                  )}
                >
                  {/* Checkbox */}
                  <div
                    className={clsx(
                      "w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 transition-colors",
                      isEnabled ? "border-transparent" : "border-gray-600",
                    )}
                    style={isEnabled ? { backgroundColor: config.colorBase } : undefined}
                  >
                    {isEnabled && (
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </div>

                  {/* Color dot */}
                  <span
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: config.colorBase }}
                  />

                  {/* Label */}
                  <span
                    className={clsx(
                      "text-sm flex-1",
                      isEnabled ? "text-gray-200" : "text-gray-400",
                    )}
                  >
                    {config.label}
                  </span>

                  {/* Count badge */}
                  <span
                    className="text-[10px] px-1.5 py-0.5 rounded-full font-mono"
                    style={{
                      backgroundColor: `${config.colorBase}20`,
                      color: config.colorLight,
                    }}
                  >
                    {count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Layer-specific filters (shown when a filterable layer is active) */}
          {(activeLayers.has("vulnerabilities") ||
            activeLayers.has("threats") ||
            activeLayers.has("containment") ||
            activeLayers.has("relations")) && (
            <div className="border-t border-gray-700">
              {(["vulnerabilities", "threats", "containment", "relations"] as LayerType[])
                .filter((l) => activeLayers.has(l))
                .map((layerId) => (
                  <div key={layerId} className="border-b border-gray-700/50 last:border-b-0">
                    <button
                      onClick={() =>
                        setExpandedLayerFilter(expandedLayerFilter === layerId ? null : layerId)
                      }
                      className="w-full flex items-center justify-between px-3 py-1.5 text-[10px] text-gray-400 uppercase tracking-wider hover:text-gray-300 transition-colors"
                    >
                      <span style={{ color: LAYER_COLORS[layerId]?.colorLight }}>
                        {LAYER_COLORS[layerId]?.label} Filters
                      </span>
                      <svg
                        className={clsx(
                          "w-3 h-3 transition-transform",
                          expandedLayerFilter === layerId && "rotate-180",
                        )}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </button>
                    {expandedLayerFilter === layerId && (
                      <div className="px-1 pb-2">
                        <LayerFilters
                          activeLayer={layerId}
                          filters={layerFilters}
                          onFilterChange={setLayerFilters}
                        />
                      </div>
                    )}
                  </div>
                ))}
            </div>
          )}

          {/* Global filters section */}
          <div className="border-t border-gray-700">
            <GlobalFilters filters={globalFilters} onFilterChange={setGlobalFilters} />
          </div>

          {/* Footer: counter + reset */}
          <div className="p-3 border-t border-gray-700 flex items-center justify-between">
            <span className="text-xs text-gray-500">
              {activeLayerCount}/{ALL_LAYERS.length} layers active
            </span>
            <button
              onClick={resetLayers}
              className="text-xs text-gray-400 hover:text-cyan-400 transition-colors"
            >
              Reset
            </button>
          </div>
        </aside>

        {/* CENTER: Canvas */}
        <main className="flex-1 overflow-hidden relative" ref={canvasRef}>
          <div className={clsx("w-full h-full", modeTransitionClass)}>
            {currentMode === "surface" && (
              <SurfaceCanvas
                nodes={filteredNodes}
                activeLayers={activeLayers}
                selectedNode={selectedNode}
                selectedNodes={selectedNodes}
                onNodeClick={handleNodeClick}
              />
            )}
            {currentMode === "graph" && (
              <InvestigationGraph
                nodes={filteredNodes}
                activeLayers={activeLayers}
                selectedNode={selectedNode}
                onNodeClick={handleNodeClick}
              />
            )}
            {currentMode === "vulns" && <VulnerabilityLandscape nodes={filteredNodes} />}
            {currentMode === "threats" && <ThreatWorldMap />}
            {currentMode === "timeline" && <TimelineReplay nodes={filteredNodes} />}
          </div>
        </main>

        {/* RIGHT: Detail Panel (conditional) */}
        {selectedNode && (
          <DetailPanel
            node={selectedNode}
            activeLayers={activeLayers}
            onClose={closeDetail}
            isPinned={isPanelPinned}
            onTogglePin={() => setIsPanelPinned((p) => !p)}
          />
        )}
      </div>

      {/* ================================================================ */}
      {/* BOTTOM BAR: Enhanced KPIs + Timeline */}
      {/* ================================================================ */}
      <BottomBar
        overview={overview}
        onKpiClick={handleKpiClick}
        timeRange={timeRange}
        onTimeRangeChange={setTimeRange}
      />

      {/* ================================================================ */}
      {/* Toast Notification (auto-dismiss) */}
      {/* ================================================================ */}
      {toastMessage && (
        <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-[90] px-4 py-2.5 bg-gray-800 border border-cyan-500/40 text-cyan-300 text-sm rounded-lg shadow-lg animate-toast-in flex items-center gap-2">
          <svg
            className="w-4 h-4 flex-shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{toastMessage}</span>
          <button
            onClick={() => setToastMessage(null)}
            className="ml-2 text-gray-500 hover:text-white"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      )}

      {/* ================================================================ */}
      {/* Query Builder Modal */}
      {/* ================================================================ */}
      <QueryBuilder
        isOpen={showQueryBuilder}
        onClose={() => setShowQueryBuilder(false)}
        onApply={handleQueryApply}
      />

      {/* ================================================================ */}
      {/* WOW CSS animations */}
      {/* ================================================================ */}
      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        .animate-slide-in-right {
          animation: slideInRight 0.25s ease-out;
        }

        /* Toast notification slide up */
        @keyframes toastIn {
          from { opacity: 0; transform: translate(-50%, 12px); }
          to { opacity: 1; transform: translate(-50%, 0); }
        }
        .animate-toast-in {
          animation: toastIn 0.2s ease-out;
        }

        /* Glow pulse for critical nodes - 1Hz box-shadow pulse */
        @keyframes glowPulse {
          0%, 100% { box-shadow: 0 0 8px var(--glow-color, #ef4444), 0 0 16px color-mix(in srgb, var(--glow-color, #ef4444) 60%, transparent); }
          50% { box-shadow: 0 0 24px var(--glow-color, #ef4444), 0 0 48px color-mix(in srgb, var(--glow-color, #ef4444) 40%, transparent); }
        }
        .surface-glow-pulse {
          animation: glowPulse 1s ease-in-out infinite;
        }

        /* Gradient pulse for CTEM high risk - green to red rotation */
        @keyframes gradientPulse {
          0% { background: linear-gradient(0deg, #22c55e, #eab308, #ef4444); }
          33% { background: linear-gradient(120deg, #22c55e, #eab308, #ef4444); }
          66% { background: linear-gradient(240deg, #22c55e, #eab308, #ef4444); }
          100% { background: linear-gradient(360deg, #22c55e, #eab308, #ef4444); }
        }
        .surface-gradient-pulse {
          animation: gradientPulse 3s linear infinite;
        }

        /* Shake subtle for KEV CVE nodes */
        @keyframes shakeSubtle {
          0%, 100% { transform: translate(0, 0); }
          20% { transform: translate(-1px, 1px); }
          40% { transform: translate(2px, -1px); }
          60% { transform: translate(-2px, 0); }
          80% { transform: translate(1px, 1px); }
        }
        .surface-shake-subtle {
          animation: shakeSubtle 0.5s ease-in-out infinite;
        }

        /* Radar sweep for SOC target */
        @keyframes radarSweep {
          0% { transform: scale(0.3); opacity: 0.8; }
          100% { transform: scale(2.5); opacity: 0; }
        }
        .surface-radar-sweep::before,
        .surface-radar-sweep::after,
        .surface-radar-sweep > .radar-ring {
          position: absolute;
          inset: 0;
          border-radius: 50%;
          border: 2px solid #06b6d4;
          animation: radarSweep 3s ease-out infinite;
        }
        .surface-radar-sweep::before {
          content: '';
          animation-delay: 0s;
        }
        .surface-radar-sweep::after {
          content: '';
          animation-delay: 1s;
        }
        .surface-radar-sweep > .radar-ring {
          animation-delay: 2s;
        }

        /* Particle flow along connection lines */
        @keyframes particleFlow {
          0% { offset-distance: 0%; opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { offset-distance: 100%; opacity: 0; }
        }

        /* Fade in/out for layer toggle */
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .surface-fade-in {
          animation: fadeIn 0.2s ease-out;
        }

        @keyframes fadeOut {
          from { opacity: 1; }
          to { opacity: 0; }
        }
        .surface-fade-out {
          animation: fadeOut 0.15s ease-in forwards;
        }

        /* Mode transition animations */
        @keyframes modeFadeOut {
          from { opacity: 1; transform: scale(1); }
          to { opacity: 0; transform: scale(0.98); }
        }
        .surface-mode-fade-out {
          animation: modeFadeOut 0.2s ease-in forwards;
        }

        @keyframes modeFadeIn {
          from { opacity: 0; transform: scale(1.02); }
          to { opacity: 1; transform: scale(1); }
        }
        .surface-mode-fade-in {
          animation: modeFadeIn 0.3s ease-out forwards;
        }

        /* Animated attack line dash */
        @keyframes dashFlow {
          to { stroke-dashoffset: -20; }
        }
        .surface-dash-flow {
          animation: dashFlow 1s linear infinite;
        }

        /* Pulse for map markers */
        @keyframes mapPulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.5); opacity: 0.5; }
        }
        .surface-map-pulse {
          animation: mapPulse 2s ease-in-out infinite;
        }

        /* Timeline cursor blink */
        @keyframes cursorBlink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
        .surface-cursor-blink {
          animation: cursorBlink 1s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}

// ============================================================================
// Surface Canvas - Grid of asset nodes with semantic zoom + pan + context menu
// ============================================================================

function SurfaceCanvas({
  nodes,
  activeLayers,
  selectedNode,
  selectedNodes,
  onNodeClick,
}: {
  nodes: any[];
  activeLayers: Set<LayerType>;
  selectedNode: any;
  selectedNodes: Set<string>;
  onNodeClick: (node: any, ctrlKey?: boolean) => void;
}) {
  const [zoomLevel, setZoomLevel] = useState<ZoomLevel>("grouped");
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const panStartRef = useRef({ x: 0, y: 0 });
  const panOffsetStartRef = useRef({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{
    x: number;
    y: number;
    nodeId: string | null;
  } | null>(null);

  // Scroll to zoom
  const handleWheel = useCallback(
    (e: React.WheelEvent) => {
      e.preventDefault();
      const zoomOrder: ZoomLevel[] = ["clustered", "grouped", "detailed"];
      const currentIdx = zoomOrder.indexOf(zoomLevel);
      if (e.deltaY < 0 && currentIdx < zoomOrder.length - 1) {
        setZoomLevel(zoomOrder[currentIdx + 1] ?? "grouped");
      } else if (e.deltaY > 0 && currentIdx > 0) {
        setZoomLevel(zoomOrder[currentIdx - 1] ?? "grouped");
      }
    },
    [zoomLevel],
  );

  // Pan handlers
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      // Only start pan on left-click on the background
      if (e.button !== 0) return;
      if ((e.target as HTMLElement).closest("[data-node]")) return;
      setIsPanning(true);
      panStartRef.current = { x: e.clientX, y: e.clientY };
      panOffsetStartRef.current = { ...panOffset };
    },
    [panOffset],
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!isPanning) return;
      const dx = e.clientX - panStartRef.current.x;
      const dy = e.clientY - panStartRef.current.y;
      setPanOffset({
        x: panOffsetStartRef.current.x + dx,
        y: panOffsetStartRef.current.y + dy,
      });
    },
    [isPanning],
  );

  const handleMouseUp = useCallback(() => {
    setIsPanning(false);
  }, []);

  // Right-click context menu
  const handleContextMenu = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    const nodeEl = (e.target as HTMLElement).closest("[data-node]");
    const nodeId = nodeEl?.getAttribute("data-node") ?? null;
    setContextMenu({ x: e.clientX, y: e.clientY, nodeId });
  }, []);

  // Group nodes by type for clustered view
  const clusters = useMemo(() => {
    const groups: Record<string, any[]> = {};
    for (const n of nodes) {
      const t = n?.type ?? "unknown";
      if (!groups[t]) groups[t] = [];
      groups[t].push(n);
    }
    return groups;
  }, [nodes]);

  if (nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <svg
            className="w-16 h-16 text-gray-600 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
            />
          </svg>
          <p className="text-gray-400 font-medium">No assets to display</p>
          <p className="text-gray-500 text-sm mt-1">Generate data or adjust your search filter</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={clsx("h-full w-full overflow-hidden relative", isPanning && "cursor-grabbing")}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onContextMenu={handleContextMenu}
      ref={containerRef}
    >
      {/* Grid background */}
      <div
        className="absolute inset-0 opacity-10 pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(to right, #374151 1px, transparent 1px), linear-gradient(to bottom, #374151 1px, transparent 1px)",
          backgroundSize: "40px 40px",
          backgroundPosition: `${panOffset.x}px ${panOffset.y}px`,
        }}
      />

      {/* Zoom indicator */}
      <div className="absolute top-3 left-3 z-20 flex items-center gap-1.5 bg-gray-800/90 px-2.5 py-1 rounded-lg border border-gray-700 text-[10px] text-gray-400">
        <span className={clsx(zoomLevel === "clustered" && "text-cyan-400 font-bold")}>C</span>
        <span className="text-gray-600">/</span>
        <span className={clsx(zoomLevel === "grouped" && "text-cyan-400 font-bold")}>G</span>
        <span className="text-gray-600">/</span>
        <span className={clsx(zoomLevel === "detailed" && "text-cyan-400 font-bold")}>D</span>
        <span className="ml-1 text-gray-500">scroll to zoom</span>
      </div>

      {/* Multi-selection count */}
      {selectedNodes.size > 0 && (
        <div className="absolute top-3 right-3 z-20 bg-cyan-900/80 text-cyan-300 px-2.5 py-1 rounded-lg text-xs font-medium border border-cyan-700">
          {selectedNodes.size} selected
        </div>
      )}

      {/* Canvas content */}
      <div
        style={{
          transform: `translate(${panOffset.x}px, ${panOffset.y}px)`,
          transition: isPanning ? "none" : "transform 0.15s ease-out",
        }}
      >
        {/* Clustered view: aggregate circles */}
        {zoomLevel === "clustered" && (
          <div className="p-8 flex flex-wrap gap-8 content-start justify-center min-h-full">
            {Object.entries(clusters).map(([type, group]) => {
              const totalRisk = group.reduce(
                (sum: number, n: any) => sum + (n?.risk_score ?? n?.riskScore ?? 0),
                0,
              );
              const avgRisk = Math.round(totalRisk / (group.length || 1));
              const criticalCount = group.filter(
                (n: any) => (n?.risk_score ?? n?.riskScore ?? 0) >= 80,
              ).length;
              const size = 60 + group.length * 3;

              return (
                <div
                  key={type}
                  className="flex flex-col items-center cursor-pointer hover:scale-105 transition-transform"
                >
                  <div
                    className="rounded-full flex flex-col items-center justify-center text-white border-2"
                    style={{
                      width: size,
                      height: size,
                      backgroundColor:
                        avgRisk >= 70 ? "#ef444430" : avgRisk >= 40 ? "#eab30830" : "#22c55e30",
                      borderColor:
                        avgRisk >= 70 ? "#ef4444" : avgRisk >= 40 ? "#eab308" : "#22c55e",
                    }}
                  >
                    <span className="text-lg font-bold">{group.length}</span>
                    <span className="text-[9px] text-gray-400">
                      {criticalCount > 0 ? `${criticalCount} crit` : `avg ${avgRisk}`}
                    </span>
                  </div>
                  <span className="mt-2 text-xs text-gray-400 capitalize">
                    {type?.replace?.(/_/g, " ") ?? type}
                  </span>
                </div>
              );
            })}
          </div>
        )}

        {/* Grouped view: standard node grid */}
        {zoomLevel === "grouped" && (
          <div className="p-6 flex flex-wrap gap-4 content-start justify-center min-h-full">
            {nodes.map((node: any) => (
              <div key={node?.id ?? Math.random()} data-node={node?.id ?? ""}>
                <SurfaceAssetNode
                  node={node}
                  activeLayers={activeLayers}
                  isSelected={selectedNode?.id === node?.id || selectedNodes.has(node?.id ?? "")}
                  onClick={() => onNodeClick(node)}
                  zoomLevel="grouped"
                />
              </div>
            ))}
          </div>
        )}

        {/* Detailed view: full detail nodes with larger spacing */}
        {zoomLevel === "detailed" && (
          <div className="p-8 flex flex-wrap gap-6 content-start justify-center min-h-full">
            {nodes.map((node: any) => (
              <div key={node?.id ?? Math.random()} data-node={node?.id ?? ""}>
                <SurfaceAssetNode
                  node={node}
                  activeLayers={activeLayers}
                  isSelected={selectedNode?.id === node?.id || selectedNodes.has(node?.id ?? "")}
                  onClick={() => onNodeClick(node)}
                  zoomLevel="detailed"
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          nodeId={contextMenu.nodeId}
          onClose={() => setContextMenu(null)}
        />
      )}
    </div>
  );
}

// ============================================================================
// Mode B: Investigation Graph - force-directed layout
// ============================================================================

function InvestigationGraph({
  nodes,
  activeLayers,
  selectedNode,
  onNodeClick,
}: {
  nodes: any[];
  activeLayers: Set<LayerType>;
  selectedNode: any;
  onNodeClick: (node: any) => void;
}) {
  const { data: connectionsData } = useSurfaceConnections();
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // Measure container
  useEffect(() => {
    if (!containerRef.current) return;
    const obs = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setDimensions({
          width: entry.contentRect?.width ?? 800,
          height: entry.contentRect?.height ?? 600,
        });
      }
    });
    obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  // Parse connections
  const connections = useMemo(() => {
    if (Array.isArray(connectionsData)) return connectionsData;
    if (connectionsData?.connections) return connectionsData.connections;
    if (connectionsData?.items) return connectionsData.items;
    return [];
  }, [connectionsData]);

  // Calculate positions using simple circular / force-inspired layout
  const nodePositions = useMemo(() => {
    const positions = new Map<string, { x: number; y: number }>();
    const cx = dimensions.width / 2;
    const cy = dimensions.height / 2;
    const maxRadius = Math.min(cx, cy) * 0.75;
    const total = nodes.length || 1;

    nodes.forEach((n: any, i: number) => {
      const id = n?.id ?? `node-${i}`;
      const angle = (2 * Math.PI * i) / total - Math.PI / 2;
      // Nodes with higher risk score are closer to center
      const riskScore = n?.risk_score ?? n?.riskScore ?? 50;
      const radiusFactor = 1 - (riskScore / 100) * 0.5;
      const r = maxRadius * radiusFactor;
      positions.set(id, {
        x: cx + Math.cos(angle) * r,
        y: cy + Math.sin(angle) * r,
      });
    });

    return positions;
  }, [nodes, dimensions]);

  if (nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        No assets to visualize in graph mode
      </div>
    );
  }

  return (
    <div ref={containerRef} className="h-full w-full overflow-hidden relative bg-gray-900">
      <svg width={dimensions.width} height={dimensions.height} className="absolute inset-0">
        {/* Grid pattern */}
        <defs>
          <pattern id="graph-grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1f2937" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#graph-grid)" />

        {/* Connection lines */}
        {connections.map((conn: any, i: number) => {
          const sourceId = conn?.source_id ?? conn?.sourceId ?? "";
          const targetId = conn?.target_id ?? conn?.targetId ?? "";
          const connType = conn?.type ?? conn?.connection_type ?? "shared_ioc";
          const sourcePos = nodePositions.get(sourceId);
          const targetPos = nodePositions.get(targetId);
          if (!sourcePos || !targetPos) return null;

          const color = CONNECTION_COLORS[connType] ?? "#06b6d4";

          return (
            <g key={`conn-${i}`}>
              <line
                x1={sourcePos.x}
                y1={sourcePos.y}
                x2={targetPos.x}
                y2={targetPos.y}
                stroke={color}
                strokeWidth={1.5}
                strokeOpacity={0.4}
              />
              {/* Animated dash overlay */}
              <line
                x1={sourcePos.x}
                y1={sourcePos.y}
                x2={targetPos.x}
                y2={targetPos.y}
                stroke={color}
                strokeWidth={2}
                strokeDasharray="4 8"
                strokeOpacity={0.8}
                className="surface-dash-flow"
              />
            </g>
          );
        })}

        {/* Node circles */}
        {nodes.map((node: any) => {
          const id = node?.id ?? "";
          const pos = nodePositions.get(id);
          if (!pos) return null;
          const riskScore = node?.risk_score ?? node?.riskScore ?? 50;
          const isCritical = riskScore >= 80;
          const hostname = node?.hostname ?? "?";
          const isNodeSelected = selectedNode?.id === id;

          // Determine primary color from layers
          let color = LAYER_COLORS.base.colorBase;
          for (const layerId of LAYER_RENDER_ORDER) {
            if (!activeLayers.has(layerId) || layerId === "base") continue;
            if (node?.layers?.[layerId]?.active) {
              color = LAYER_COLORS[layerId].colorBase;
            }
          }

          const radius = 14 + (riskScore / 100) * 10;

          return (
            <g key={id} onClick={() => onNodeClick(node)} className="cursor-pointer">
              {/* Selection ring */}
              {isNodeSelected && (
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={radius + 6}
                  fill="none"
                  stroke="#22d3ee"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  className="surface-dash-flow"
                />
              )}
              {/* Glow for critical */}
              {isCritical && (
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={radius + 4}
                  fill="none"
                  stroke={color}
                  strokeWidth={1}
                  strokeOpacity={0.3}
                  className="surface-glow-pulse"
                  style={{ "--glow-color": color } as React.CSSProperties}
                />
              )}
              {/* Main circle */}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={radius}
                fill={color}
                fillOpacity={0.8}
                stroke={color}
                strokeWidth={isNodeSelected ? 2 : 1}
              />
              {/* Risk score text */}
              <text
                x={pos.x}
                y={pos.y + 1}
                textAnchor="middle"
                dominantBaseline="central"
                fill="white"
                fontSize="10"
                fontWeight="bold"
              >
                {riskScore}
              </text>
              {/* Hostname label below */}
              <text
                x={pos.x}
                y={pos.y + radius + 12}
                textAnchor="middle"
                fill="#9ca3af"
                fontSize="9"
                fontFamily="monospace"
              >
                {hostname.length > 12 ? hostname.substring(0, 12) + "..." : hostname}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-gray-800/90 border border-gray-700 rounded-lg p-3 z-10">
        <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Connection Types</p>
        <div className="space-y-1">
          {Object.entries(CONNECTION_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center gap-2 text-[10px] text-gray-400">
              <div className="w-4 h-0.5 rounded" style={{ backgroundColor: color }} />
              <span className="capitalize">{type.replace(/_/g, " ")}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Mode C: Vulnerability Landscape - Treemap grid
// ============================================================================

function VulnerabilityLandscape({ nodes }: { nodes: any[] }) {
  const [vulnData, setVulnData] = useState<any>(null);

  // Fetch vulnerability data
  useEffect(() => {
    let cancelled = false;
    api
      .getVulnerabilities({ page_size: 100 })
      .then((data) => {
        if (!cancelled) setVulnData(data);
      })
      .catch(() => {
        /* ignore */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Build vulnerability list from nodes or API data
  const vulns = useMemo(() => {
    const result: { cve: string; severity: string; cvss: number; asset: string }[] = [];

    // First try API data
    const items = vulnData?.data ?? vulnData?.items ?? vulnData?.vulnerabilities ?? [];
    if (items.length > 0) {
      for (const v of items) {
        result.push({
          cve: v?.cve_id ?? v?.cve ?? "CVE-XXXX-XXXX",
          severity: v?.severity ?? "medium",
          cvss: v?.cvss_score ?? v?.cvss ?? 5.0,
          asset: v?.hostname ?? v?.asset_id ?? "",
        });
      }
      return result;
    }

    // Fallback: extract from node layer data
    for (const n of nodes) {
      const vulnLayer = n?.layers?.vulnerabilities;
      const ctemLayer = n?.layers?.ctem;
      if (vulnLayer?.active) {
        const count = vulnLayer?.cveCount ?? 0;
        const critCount = vulnLayer?.criticalCount ?? 0;
        const hostname = n?.hostname ?? "unknown";
        // Generate synthetic CVE entries based on counts
        for (let i = 0; i < Math.min(count, 5); i++) {
          const isCrit = i < critCount;
          result.push({
            cve: `CVE-2024-${(1000 + result.length).toString()}`,
            severity: isCrit ? "critical" : i < critCount + 2 ? "high" : "medium",
            cvss: isCrit ? 9.0 + Math.random() : 5.0 + Math.random() * 4,
            asset: hostname,
          });
        }
      } else if (ctemLayer?.active && (ctemLayer?.cveCount ?? 0) > 0) {
        const count = ctemLayer?.cveCount ?? 0;
        const hostname = n?.hostname ?? "unknown";
        const risk = ctemLayer?.riskLevel ?? "medium";
        for (let i = 0; i < Math.min(count, 3); i++) {
          result.push({
            cve: `CVE-2024-${(2000 + result.length).toString()}`,
            severity: risk === "critical" ? "critical" : risk,
            cvss: risk === "critical" ? 9.5 : risk === "high" ? 7.5 : 5.0,
            asset: hostname,
          });
        }
      }
    }

    return result;
  }, [nodes, vulnData]);

  // Severity color mapping
  const severityColor = useCallback((severity: string) => {
    switch (severity) {
      case "critical":
        return { bg: "#dc2626", text: "#fecaca" };
      case "high":
        return { bg: "#f97316", text: "#fed7aa" };
      case "medium":
        return { bg: "#eab308", text: "#fef3c7" };
      case "low":
        return { bg: "#22c55e", text: "#bbf7d0" };
      default:
        return { bg: "#6b7280", text: "#e5e7eb" };
    }
  }, []);

  // Sort by CVSS descending
  const sortedVulns = useMemo(() => {
    return [...vulns].sort((a, b) => b.cvss - a.cvss);
  }, [vulns]);

  // Group by severity for summary
  const severityCounts = useMemo(() => {
    const counts: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0 };
    for (const v of vulns) {
      const s = v.severity ?? "medium";
      counts[s] = (counts[s] ?? 0) + 1;
    }
    return counts;
  }, [vulns]);

  if (vulns.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <div className="text-center">
          <svg
            className="w-16 h-16 text-gray-600 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-gray-400 font-medium">No vulnerability data available</p>
          <p className="text-gray-500 text-sm mt-1">
            Generate data to see the vulnerability landscape
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full overflow-auto bg-gray-900 p-6">
      {/* Summary bar */}
      <div className="flex items-center gap-4 mb-6">
        <h2 className="text-white font-bold text-lg">Vulnerability Landscape</h2>
        <div className="flex gap-2">
          {["critical", "high", "medium", "low"].map((sev) => {
            const count = severityCounts[sev] ?? 0;
            const colors = severityColor(sev);
            return (
              <div
                key={sev}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium"
                style={{ backgroundColor: `${colors.bg}20`, color: colors.text }}
              >
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: colors.bg }} />
                <span className="capitalize">{sev}</span>
                <span className="font-bold">{count}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Treemap grid */}
      <div className="flex flex-wrap gap-1.5">
        {sortedVulns.map((v, i) => {
          const colors = severityColor(v.severity);
          // Size based on CVSS score
          const minW = 80;
          const maxW = 180;
          const w = minW + (v.cvss / 10) * (maxW - minW);
          const h = 50 + (v.cvss / 10) * 30;

          return (
            <div
              key={`${v.cve}-${i}`}
              className="rounded-lg border flex flex-col items-center justify-center cursor-pointer hover:scale-105 transition-transform"
              style={{
                width: w,
                height: h,
                backgroundColor: `${colors.bg}25`,
                borderColor: `${colors.bg}60`,
              }}
              title={`${v.cve} | CVSS: ${v.cvss.toFixed(1)} | ${v.asset}`}
            >
              <span className="text-[10px] font-mono font-bold" style={{ color: colors.text }}>
                {v.cve}
              </span>
              <span className="text-[9px] mt-0.5" style={{ color: `${colors.text}99` }}>
                CVSS {v.cvss.toFixed(1)}
              </span>
              {v.asset && (
                <span className="text-[8px] text-gray-500 mt-0.5 truncate max-w-[90%]">
                  {v.asset}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ============================================================================
// Mode D: Threat World Map - stylized SVG map with animated attack lines
// ============================================================================

function ThreatWorldMap() {
  const [threatData, setThreatData] = useState<any>(null);

  useEffect(() => {
    let cancelled = false;
    api
      .getThreatMap()
      .then((data) => {
        if (!cancelled) setThreatData(data);
      })
      .catch(() => {
        /* ignore, use synthetic */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // SOC target position (center of US, roughly)
  const socTarget = { x: 250, y: 220 };

  // Threat origins - from API or synthetic
  const origins = useMemo(() => {
    const apiOrigins = threatData?.origins ?? threatData?.threat_origins ?? [];
    if (apiOrigins.length > 0) {
      return apiOrigins.map((o: any, i: number) => ({
        id: o?.id ?? `origin-${i}`,
        x: o?.x ?? o?.longitude ?? 400 + i * 50,
        y: o?.y ?? o?.latitude ?? 150 + i * 30,
        label: o?.country ?? o?.label ?? "Unknown",
        iocCount: o?.ioc_count ?? o?.count ?? 1,
        color:
          o?.severity === "critical" ? "#ef4444" : o?.severity === "high" ? "#f97316" : "#a855f7",
      }));
    }

    // Synthetic threat origins
    return [
      { id: "ru", x: 520, y: 140, label: "Russia", iocCount: 12, color: "#ef4444" },
      { id: "cn", x: 640, y: 220, label: "China", iocCount: 8, color: "#ef4444" },
      { id: "ir", x: 510, y: 240, label: "Iran", iocCount: 5, color: "#f97316" },
      { id: "kp", x: 660, y: 190, label: "N. Korea", iocCount: 3, color: "#f97316" },
      { id: "br", x: 310, y: 360, label: "Brazil", iocCount: 2, color: "#a855f7" },
      { id: "ng", x: 430, y: 300, label: "Nigeria", iocCount: 4, color: "#a855f7" },
      { id: "ua", x: 500, y: 170, label: "Ukraine", iocCount: 1, color: "#eab308" },
    ];
  }, [threatData]);

  const totalIOCs = useMemo(
    () => origins.reduce((s: number, o: any) => s + (o?.iocCount ?? 0), 0),
    [origins],
  );

  return (
    <div className="h-full w-full overflow-hidden relative bg-gray-900 flex items-center justify-center">
      <svg
        viewBox="0 0 800 500"
        className="w-full h-full max-w-[1200px]"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Simplified continent outlines */}
        <defs>
          <linearGradient id="attackLine" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ef4444" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.4" />
          </linearGradient>
        </defs>

        {/* North America */}
        <path
          d="M120,100 L200,80 L280,90 L300,130 L310,180 L290,210 L260,240 L230,260 L200,250 L170,230 L140,200 L120,160 Z"
          fill="#1f293740"
          stroke="#374151"
          strokeWidth="1"
        />
        {/* South America */}
        <path
          d="M230,280 L280,270 L320,300 L340,350 L330,400 L310,430 L280,440 L260,420 L240,380 L220,340 L220,300 Z"
          fill="#1f293740"
          stroke="#374151"
          strokeWidth="1"
        />
        {/* Europe */}
        <path
          d="M400,100 L440,90 L480,95 L510,110 L520,140 L510,170 L490,180 L460,190 L430,185 L410,170 L400,140 Z"
          fill="#1f293740"
          stroke="#374151"
          strokeWidth="1"
        />
        {/* Africa */}
        <path
          d="M410,200 L460,195 L490,210 L510,250 L500,310 L480,360 L450,390 L420,380 L400,340 L390,290 L395,240 Z"
          fill="#1f293740"
          stroke="#374151"
          strokeWidth="1"
        />
        {/* Asia */}
        <path
          d="M520,80 L600,70 L680,90 L720,130 L710,180 L680,220 L640,250 L590,260 L540,240 L510,200 L510,150 L515,110 Z"
          fill="#1f293740"
          stroke="#374151"
          strokeWidth="1"
        />
        {/* Australia */}
        <path
          d="M640,340 L700,330 L730,350 L720,390 L690,410 L650,400 L630,370 Z"
          fill="#1f293740"
          stroke="#374151"
          strokeWidth="1"
        />

        {/* Attack lines from origins to SOC target */}
        {origins.map((origin: any) => {
          const midX = (origin.x + socTarget.x) / 2;
          const midY =
            Math.min(origin.y, socTarget.y) - 30 - Math.abs(origin.x - socTarget.x) * 0.1;

          return (
            <g key={origin.id}>
              {/* Line shadow */}
              <path
                d={`M${origin.x},${origin.y} Q${midX},${midY} ${socTarget.x},${socTarget.y}`}
                fill="none"
                stroke={origin.color}
                strokeWidth={1 + (origin.iocCount ?? 0) * 0.3}
                strokeOpacity={0.15}
              />
              {/* Animated dashed line */}
              <path
                d={`M${origin.x},${origin.y} Q${midX},${midY} ${socTarget.x},${socTarget.y}`}
                fill="none"
                stroke={origin.color}
                strokeWidth={1 + Math.min((origin.iocCount ?? 0) * 0.2, 2)}
                strokeDasharray="6 6"
                strokeOpacity={0.7}
                className="surface-dash-flow"
              />
            </g>
          );
        })}

        {/* SOC target with radar sweep */}
        <g>
          {/* Radar rings */}
          <circle
            cx={socTarget.x}
            cy={socTarget.y}
            r="20"
            fill="none"
            stroke="#06b6d4"
            strokeWidth="1"
            strokeOpacity="0.3"
          >
            <animate attributeName="r" from="10" to="60" dur="3s" repeatCount="indefinite" />
            <animate attributeName="opacity" from="0.8" to="0" dur="3s" repeatCount="indefinite" />
          </circle>
          <circle
            cx={socTarget.x}
            cy={socTarget.y}
            r="20"
            fill="none"
            stroke="#06b6d4"
            strokeWidth="1"
            strokeOpacity="0.3"
          >
            <animate
              attributeName="r"
              from="10"
              to="60"
              dur="3s"
              begin="1s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="opacity"
              from="0.8"
              to="0"
              dur="3s"
              begin="1s"
              repeatCount="indefinite"
            />
          </circle>
          <circle
            cx={socTarget.x}
            cy={socTarget.y}
            r="20"
            fill="none"
            stroke="#06b6d4"
            strokeWidth="1"
            strokeOpacity="0.3"
          >
            <animate
              attributeName="r"
              from="10"
              to="60"
              dur="3s"
              begin="2s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="opacity"
              from="0.8"
              to="0"
              dur="3s"
              begin="2s"
              repeatCount="indefinite"
            />
          </circle>
          {/* SOC core */}
          <circle cx={socTarget.x} cy={socTarget.y} r="8" fill="#06b6d4" fillOpacity="0.9" />
          <circle cx={socTarget.x} cy={socTarget.y} r="4" fill="white" fillOpacity="0.9" />
          <text
            x={socTarget.x}
            y={socTarget.y + 24}
            textAnchor="middle"
            fill="#06b6d4"
            fontSize="10"
            fontWeight="bold"
          >
            SOC
          </text>
        </g>

        {/* Origin markers */}
        {origins.map((origin: any) => (
          <g key={`marker-${origin.id}`}>
            {/* Pulse effect */}
            <circle cx={origin.x} cy={origin.y} r="4" fill={origin.color} fillOpacity="0.3">
              <animate attributeName="r" from="4" to="16" dur="2s" repeatCount="indefinite" />
              <animate
                attributeName="opacity"
                from="0.6"
                to="0"
                dur="2s"
                repeatCount="indefinite"
              />
            </circle>
            {/* Marker dot */}
            <circle
              cx={origin.x}
              cy={origin.y}
              r="5"
              fill={origin.color}
              stroke="white"
              strokeWidth="1"
            />
            {/* IOC count badge */}
            <circle
              cx={origin.x + 10}
              cy={origin.y - 10}
              r="8"
              fill="#1f2937"
              stroke={origin.color}
              strokeWidth="1"
            />
            <text
              x={origin.x + 10}
              y={origin.y - 7}
              textAnchor="middle"
              fill="white"
              fontSize="8"
              fontWeight="bold"
            >
              {origin.iocCount}
            </text>
            {/* Country label */}
            <text x={origin.x} y={origin.y + 18} textAnchor="middle" fill="#9ca3af" fontSize="8">
              {origin.label}
            </text>
          </g>
        ))}
      </svg>

      {/* Stats overlay */}
      <div className="absolute top-4 left-4 bg-gray-800/90 border border-gray-700 rounded-lg p-3 z-10">
        <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
          Threat Intelligence
        </p>
        <div className="space-y-1.5">
          <div className="flex items-center justify-between gap-4 text-xs">
            <span className="text-gray-400">Active Origins</span>
            <span className="text-white font-bold">{origins.length}</span>
          </div>
          <div className="flex items-center justify-between gap-4 text-xs">
            <span className="text-gray-400">Total IOCs</span>
            <span className="text-red-400 font-bold">{totalIOCs}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Mode E: Timeline Replay - horizontal timeline with play controls
// ============================================================================

function TimelineReplay({ nodes }: { nodes: any[] }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [cursorPos, setCursorPos] = useState(0); // 0-100 percent
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Generate timeline events from nodes
  const events = useMemo(() => {
    const result: {
      time: number;
      type: string;
      label: string;
      severity: string;
      nodeId: string;
    }[] = [];
    const rand = seededRandom(42);

    for (const n of nodes) {
      const id = n?.id ?? "";
      const hostname = n?.hostname ?? "unknown";
      const edr = n?.layers?.edr;
      const siem = n?.layers?.siem;

      if (edr?.active && (edr?.detectionCount ?? 0) > 0) {
        const count = Math.min(edr.detectionCount ?? 1, 3);
        for (let i = 0; i < count; i++) {
          result.push({
            time: rand() * 100,
            type: "detection",
            label: `Detection on ${hostname}`,
            severity: edr?.severity ?? "medium",
            nodeId: id,
          });
        }
      }

      if (siem?.active && (siem?.incidentCount ?? 0) > 0) {
        const count = Math.min(siem.incidentCount ?? 1, 2);
        for (let i = 0; i < count; i++) {
          result.push({
            time: rand() * 100,
            type: "incident",
            label: `Incident involving ${hostname}`,
            severity: siem?.status === "open" ? "high" : "medium",
            nodeId: id,
          });
        }
      }

      if (n?.layers?.containment?.isContained) {
        result.push({
          time: 60 + rand() * 40,
          type: "containment",
          label: `${hostname} contained`,
          severity: "info",
          nodeId: id,
        });
      }
    }

    // Sort by time
    result.sort((a, b) => a.time - b.time);
    return result;
  }, [nodes]);

  // Play/pause logic
  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        setCursorPos((prev) => {
          const next = prev + 0.5 * speed;
          if (next >= 100) {
            setIsPlaying(false);
            return 100;
          }
          return next;
        });
      }, 50);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPlaying, speed]);

  // Event color
  const eventColor = useCallback((type: string, severity: string) => {
    if (type === "containment") return "#3b82f6";
    switch (severity) {
      case "critical":
        return "#ef4444";
      case "high":
        return "#f97316";
      case "medium":
        return "#eab308";
      case "low":
        return "#22c55e";
      default:
        return "#6b7280";
    }
  }, []);

  // Events at or before cursor
  const visibleEvents = useMemo(() => {
    return events.filter((e) => e.time <= cursorPos);
  }, [events, cursorPos]);

  // Speed options
  const speeds = [1, 2, 5, 10];

  // Click on timeline to set position
  const handleTimelineClick = useCallback((e: React.MouseEvent) => {
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const pct = ((e.clientX - rect.left) / rect.width) * 100;
    setCursorPos(Math.max(0, Math.min(100, pct)));
  }, []);

  return (
    <div className="h-full w-full overflow-hidden bg-gray-900 flex flex-col" ref={containerRef}>
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700">
        <h2 className="text-white font-bold text-lg">Timeline Replay</h2>
        <div className="flex items-center gap-3">
          {/* Play/Pause */}
          <button
            onClick={() => {
              if (cursorPos >= 100) setCursorPos(0);
              setIsPlaying((p) => !p);
            }}
            className={clsx(
              "px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
              isPlaying
                ? "bg-orange-600 text-white hover:bg-orange-500"
                : "bg-cyan-600 text-white hover:bg-cyan-500",
            )}
          >
            {isPlaying ? "Pause" : cursorPos >= 100 ? "Replay" : "Play"}
          </button>
          {/* Speed control */}
          <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-0.5">
            {speeds.map((s) => (
              <button
                key={s}
                onClick={() => setSpeed(s)}
                className={clsx(
                  "px-2 py-1 rounded text-xs font-medium transition-colors",
                  speed === s ? "bg-cyan-600 text-white" : "text-gray-400 hover:text-white",
                )}
              >
                {s}x
              </button>
            ))}
          </div>
          {/* Event counter */}
          <span className="text-xs text-gray-400">
            {visibleEvents.length}/{events.length} events
          </span>
        </div>
      </div>

      {/* Event feed - scrollable area showing events at/before cursor */}
      <div className="flex-1 overflow-auto px-6 py-4">
        {visibleEvents.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-500 text-sm">
            {events.length === 0 ? "No events to display" : "Press Play to start timeline replay"}
          </div>
        )}
        <div className="space-y-2">
          {visibleEvents.map((ev, i) => {
            const color = eventColor(ev.type, ev.severity);
            return (
              <div
                key={`${ev.nodeId}-${ev.type}-${i}`}
                className="flex items-center gap-3 surface-fade-in"
              >
                {/* Time marker */}
                <span className="text-[10px] text-gray-500 font-mono w-12 text-right flex-shrink-0">
                  {Math.round(ev.time)}%
                </span>
                {/* Dot */}
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: color }}
                />
                {/* Event type badge */}
                <span
                  className="text-[10px] px-1.5 py-0.5 rounded font-medium flex-shrink-0 capitalize"
                  style={{ backgroundColor: `${color}20`, color }}
                >
                  {ev.type}
                </span>
                {/* Label */}
                <span className="text-xs text-gray-300">{ev.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Timeline bar at bottom */}
      <div className="px-6 py-4 border-t border-gray-700">
        <div
          className="relative h-8 bg-gray-800 rounded-lg cursor-pointer"
          onClick={handleTimelineClick}
        >
          {/* Event markers on the timeline */}
          {events.map((ev, i) => {
            const color = eventColor(ev.type, ev.severity);
            return (
              <div
                key={`marker-${i}`}
                className="absolute top-0 bottom-0 w-0.5"
                style={{ left: `${ev.time}%`, backgroundColor: `${color}60` }}
                title={ev.label}
              >
                <div
                  className="absolute top-1 w-2 h-2 rounded-full -translate-x-1/2"
                  style={{ backgroundColor: color, opacity: ev.time <= cursorPos ? 1 : 0.3 }}
                />
              </div>
            );
          })}

          {/* Cursor line */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-cyan-400 z-10 surface-cursor-blink"
            style={{ left: `${cursorPos}%` }}
          >
            <div className="absolute -top-1 w-3 h-3 bg-cyan-400 rounded-full -translate-x-1/2" />
            <div className="absolute -bottom-1 w-3 h-3 bg-cyan-400 rounded-full -translate-x-1/2" />
          </div>

          {/* Progress fill */}
          <div
            className="absolute top-0 left-0 bottom-0 rounded-l-lg"
            style={{
              width: `${cursorPos}%`,
              background: "linear-gradient(90deg, #06b6d420, #06b6d440)",
            }}
          />

          {/* Time labels */}
          <div className="absolute -bottom-5 left-0 text-[9px] text-gray-500">T0</div>
          <div className="absolute -bottom-5 left-1/4 text-[9px] text-gray-500">25%</div>
          <div className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-[9px] text-gray-500">
            50%
          </div>
          <div className="absolute -bottom-5 left-3/4 text-[9px] text-gray-500">75%</div>
          <div className="absolute -bottom-5 right-0 text-[9px] text-gray-500">T+</div>
        </div>
      </div>
    </div>
  );
}
