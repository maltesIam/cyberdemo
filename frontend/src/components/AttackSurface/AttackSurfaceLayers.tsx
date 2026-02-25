/**
 * AttackSurfaceLayers Component
 *
 * Main visualization component for the attack surface with multiple layers.
 * Renders assets as nodes with color-coded layers and connections.
 */

import { useState, useMemo, useCallback, useRef } from "react";
import clsx from "clsx";
import { format, subHours } from "date-fns";
import { LayerToggle } from "./LayerToggle";
import { TimeSlider } from "./TimeSlider";
import type {
  LayerType,
  LayerState,
  VisualAsset,
  TimeRange,
  ZoomLevel,
  AssetConnection,
  ExportData,
} from "./types";
import { LAYER_COLORS, LAYER_RENDER_ORDER } from "./types";

interface AttackSurfaceLayersProps {
  // Asset data
  assets: VisualAsset[];
  connections?: AssetConnection[];
  // Callbacks
  onAssetSelect?: (asset: VisualAsset | null) => void;
  onExport?: (data: ExportData) => void;
  // Configuration
  initialLayers?: LayerType[];
  showControls?: boolean;
  showTimeline?: boolean;
  className?: string;
}

// Default layer states
const createDefaultLayerStates = (enabledLayers: LayerType[]): LayerState[] =>
  LAYER_RENDER_ORDER.map((id) => ({
    id,
    enabled: enabledLayers.includes(id),
    opacity: 1,
  }));

// Asset node component
function AssetNode({
  asset,
  layers,
  isSelected,
  isHovered,
  onClick,
  onMouseEnter,
  onMouseLeave,
  zoomLevel,
}: {
  asset: VisualAsset;
  layers: LayerState[];
  isSelected: boolean;
  isHovered: boolean;
  onClick: () => void;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
  zoomLevel: ZoomLevel;
}) {
  // Determine which layers are active for this asset
  const activeLayers = useMemo(() => {
    return layers.filter((l) => {
      if (!l.enabled) return false;
      switch (l.id) {
        case "base":
          return asset.layers.base;
        case "edr":
          return asset.layers.edr?.active;
        case "siem":
          return asset.layers.siem?.active;
        case "ctem":
          return asset.layers.ctem?.active;
        case "vulnerabilities":
          return asset.layers.vulnerabilities?.active;
        case "threats":
          return asset.layers.threats?.active;
        case "containment":
          return asset.layers.containment?.active;
        case "relations":
          return asset.layers.relations?.active;
        default:
          return false;
      }
    });
  }, [layers, asset]);

  // Determine primary color (topmost active layer)
  const primaryLayer = useMemo(() => {
    const reversed = [...activeLayers].reverse();
    return reversed[0] ?? null;
  }, [activeLayers]);

  const primaryColor = primaryLayer
    ? LAYER_COLORS[primaryLayer.id].colorBase
    : LAYER_COLORS.base.colorBase;

  // Node size based on risk/importance and zoom level
  const nodeSize = useMemo(() => {
    const baseSize = zoomLevel === "detailed" ? 48 : zoomLevel === "grouped" ? 36 : 24;
    const riskMultiplier = 1 + (asset.riskScore / 100) * 0.5;
    return Math.round(baseSize * riskMultiplier);
  }, [zoomLevel, asset.riskScore]);

  // Calculate stacked layer rings
  const layerRings = useMemo(() => {
    return activeLayers.map((layer, index) => ({
      layer: layer.id,
      color: LAYER_COLORS[layer.id].colorBase,
      offset: index * 3,
    }));
  }, [activeLayers]);

  return (
    <div
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className={clsx(
        "absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-200",
        isSelected && "z-20",
        isHovered && "z-10",
      )}
      style={{
        left: asset.position?.x ?? 0,
        top: asset.position?.y ?? 0,
      }}
    >
      {/* Layer rings (outer to inner) */}
      {layerRings
        .slice()
        .reverse()
        .map((ring) => (
          <div
            key={ring.layer}
            className="absolute rounded-full transition-all duration-200"
            style={{
              width: nodeSize + ring.offset * 2 + 8,
              height: nodeSize + ring.offset * 2 + 8,
              left: -(ring.offset + 4),
              top: -(ring.offset + 4),
              backgroundColor: `${ring.color}20`,
              borderWidth: 2,
              borderColor: `${ring.color}60`,
              borderStyle: "solid",
            }}
          />
        ))}

      {/* Main node */}
      <div
        className={clsx(
          "relative rounded-full flex items-center justify-center transition-all duration-200",
          isSelected && "ring-2 ring-white ring-offset-2 ring-offset-gray-900",
          isHovered && "scale-110",
        )}
        style={{
          width: nodeSize,
          height: nodeSize,
          backgroundColor: primaryColor,
          boxShadow: `0 0 ${isHovered || isSelected ? 20 : 10}px ${primaryColor}80`,
        }}
      >
        {/* Asset type icon */}
        <AssetTypeIcon type={asset.type} className="w-1/2 h-1/2 text-primary opacity-80" />

        {/* Badge indicators */}
        {asset.layers.containment.isContained && (
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center border-2 border-gray-900">
            <svg className="w-3 h-3 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                clipRule="evenodd"
              />
            </svg>
          </div>
        )}

        {asset.layers.edr.detectionCount > 0 && (
          <div className="absolute -bottom-1 -right-1 min-w-5 h-5 px-1 bg-red-500 rounded-full flex items-center justify-center text-xs font-bold text-primary border-2 border-gray-900">
            {asset.layers.edr.detectionCount}
          </div>
        )}
      </div>

      {/* Label (only in detailed zoom) */}
      {zoomLevel === "detailed" && (
        <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 whitespace-nowrap">
          <span className="text-xs font-mono text-secondary bg-primary/80 px-1.5 py-0.5 rounded">
            {asset.hostname}
          </span>
        </div>
      )}
    </div>
  );
}

// Asset type icon component
function AssetTypeIcon({ type, className }: { type: string; className?: string }) {
  switch (type) {
    case "server":
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"
          />
        </svg>
      );
    case "laptop":
    case "workstation":
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
          />
        </svg>
      );
    case "container":
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
          />
        </svg>
      );
    case "virtual_machine":
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6a2 2 0 012-2h12a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 9a2 2 0 11-4 0 2 2 0 014 0zm-6 6h8"
          />
        </svg>
      );
    default:
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z"
          />
        </svg>
      );
  }
}

// Connection line component
function ConnectionLine({
  connection,
  sourceAsset,
  targetAsset,
  isHighlighted,
}: {
  connection: AssetConnection;
  sourceAsset: VisualAsset;
  targetAsset: VisualAsset;
  isHighlighted: boolean;
}) {
  const sourcePos = sourceAsset.position ?? { x: 0, y: 0 };
  const targetPos = targetAsset.position ?? { x: 0, y: 0 };

  // Calculate line direction
  const dx = targetPos.x - sourcePos.x;
  const dy = targetPos.y - sourcePos.y;

  const connectionColor = LAYER_COLORS.threats.colorBase;

  return (
    <svg
      className="absolute inset-0 pointer-events-none overflow-visible"
      style={{ zIndex: isHighlighted ? 5 : 1 }}
    >
      <defs>
        <linearGradient
          id={`gradient-${connection.sourceId}-${connection.targetId}`}
          x1={sourcePos.x}
          y1={sourcePos.y}
          x2={targetPos.x}
          y2={targetPos.y}
          gradientUnits="userSpaceOnUse"
        >
          <stop offset="0%" stopColor={connectionColor} stopOpacity={0.3} />
          <stop offset="50%" stopColor={connectionColor} stopOpacity={0.8} />
          <stop offset="100%" stopColor={connectionColor} stopOpacity={0.3} />
        </linearGradient>
      </defs>
      <line
        x1={sourcePos.x}
        y1={sourcePos.y}
        x2={targetPos.x}
        y2={targetPos.y}
        stroke={`url(#gradient-${connection.sourceId}-${connection.targetId})`}
        strokeWidth={isHighlighted ? 3 : 2}
        strokeDasharray={connection.type === "c2_communication" ? "5,5" : undefined}
        className="transition-all duration-200"
      />
      {/* Arrow marker */}
      <circle
        cx={sourcePos.x + dx * 0.5}
        cy={sourcePos.y + dy * 0.5}
        r={4}
        fill={connectionColor}
        className={isHighlighted ? "animate-pulse" : ""}
      />
    </svg>
  );
}

// Main component
export function AttackSurfaceLayers({
  assets,
  connections = [],
  onAssetSelect,
  onExport,
  initialLayers = ["base"],
  showControls = true,
  showTimeline = true,
  className,
}: AttackSurfaceLayersProps) {
  // State
  const [layers, setLayers] = useState<LayerState[]>(() => createDefaultLayerStates(initialLayers));
  const [timeRange, setTimeRange] = useState<TimeRange>({
    start: subHours(new Date(), 24),
    end: new Date(),
  });
  const [zoomLevel, setZoomLevel] = useState<ZoomLevel>("detailed");
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const [hoveredAssetId, setHoveredAssetId] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Toggle layer
  const handleLayerToggle = useCallback((layerId: LayerType) => {
    setLayers((prev) => prev.map((l) => (l.id === layerId ? { ...l, enabled: !l.enabled } : l)));
  }, []);

  // Handle asset selection
  const handleAssetSelect = useCallback(
    (asset: VisualAsset) => {
      setSelectedAssetId((prev) => (prev === asset.id ? null : asset.id));
      onAssetSelect?.(asset);
    },
    [onAssetSelect],
  );

  // Handle export
  const handleExport = useCallback(() => {
    const enabledLayers = layers.filter((l) => l.enabled).map((l) => l.id);
    const exportData: ExportData = {
      timestamp: new Date().toISOString(),
      layers: enabledLayers,
      timeRange,
      assets,
      connections,
    };
    onExport?.(exportData);

    // If no custom handler, download as JSON
    if (!onExport) {
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `attack-surface-${format(new Date(), "yyyy-MM-dd-HHmm")}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  }, [layers, timeRange, assets, connections, onExport]);

  // Calculate asset positions (simple grid layout if not provided)
  const positionedAssets = useMemo(() => {
    return assets.map((asset, index) => {
      if (asset.position) return asset;

      const containerWidth = containerRef.current?.clientWidth ?? 800;
      const containerHeight = containerRef.current?.clientHeight ?? 600;
      const cols = Math.ceil(Math.sqrt(assets.length));
      const rows = Math.ceil(assets.length / cols);
      const cellWidth = containerWidth / (cols + 1);
      const cellHeight = containerHeight / (rows + 1);
      const col = index % cols;
      const row = Math.floor(index / cols);

      return {
        ...asset,
        position: {
          x: cellWidth * (col + 1) + (Math.random() - 0.5) * 40,
          y: cellHeight * (row + 1) + (Math.random() - 0.5) * 40,
        },
      };
    });
  }, [assets]);

  // Get selected asset for detail panel
  const selectedAsset = useMemo(
    () => positionedAssets.find((a) => a.id === selectedAssetId) ?? null,
    [positionedAssets, selectedAssetId],
  );

  // Filter connections based on enabled layers
  const visibleConnections = useMemo(() => {
    const threatsEnabled = layers.find((l) => l.id === "threats")?.enabled;
    if (!threatsEnabled) return [];
    return connections;
  }, [connections, layers]);

  return (
    <div className={clsx("flex flex-col h-full bg-primary rounded-lg overflow-hidden", className)}>
      {/* Controls header */}
      {showControls && (
        <div className="flex-shrink-0 p-4 border-b border-primary space-y-4">
          {/* Layer toggles */}
          <LayerToggle layers={layers} onToggle={handleLayerToggle} compact />

          {/* Timeline */}
          {showTimeline && <TimeSlider timeRange={timeRange} onChange={setTimeRange} />}

          {/* Toolbar */}
          <div className="flex items-center justify-between">
            {/* Zoom level selector */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-tertiary">Zoom:</span>
              {(["clustered", "grouped", "detailed"] as ZoomLevel[]).map((level) => (
                <button
                  key={level}
                  onClick={() => setZoomLevel(level)}
                  className={clsx(
                    "px-2 py-1 rounded text-xs font-medium transition-colors capitalize",
                    zoomLevel === level
                      ? "bg-cyan-600 text-primary"
                      : "bg-tertiary text-secondary hover:bg-tertiary",
                  )}
                >
                  {level}
                </button>
              ))}
            </div>

            {/* Export button */}
            <button
              onClick={handleExport}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-tertiary hover:bg-tertiary text-secondary rounded-lg text-sm transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Export View
            </button>
          </div>
        </div>
      )}

      {/* Visualization area */}
      <div
        ref={containerRef}
        className="relative flex-1 overflow-hidden"
        onClick={(e) => {
          // Deselect on background click
          if (e.target === e.currentTarget) {
            setSelectedAssetId(null);
            onAssetSelect?.(null);
          }
        }}
      >
        {/* Grid background */}
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage:
              "linear-gradient(to right, #374151 1px, transparent 1px), linear-gradient(to bottom, #374151 1px, transparent 1px)",
            backgroundSize: "40px 40px",
          }}
        />

        {/* Connections */}
        {visibleConnections.map((conn) => {
          const source = positionedAssets.find((a) => a.id === conn.sourceId);
          const target = positionedAssets.find((a) => a.id === conn.targetId);
          if (!source || !target) return null;

          const isHighlighted =
            selectedAssetId === conn.sourceId ||
            selectedAssetId === conn.targetId ||
            hoveredAssetId === conn.sourceId ||
            hoveredAssetId === conn.targetId;

          return (
            <ConnectionLine
              key={`${conn.sourceId}-${conn.targetId}`}
              connection={conn}
              sourceAsset={source}
              targetAsset={target}
              isHighlighted={isHighlighted}
            />
          );
        })}

        {/* Asset nodes */}
        {positionedAssets.map((asset) => (
          <AssetNode
            key={asset.id}
            asset={asset}
            layers={layers}
            isSelected={selectedAssetId === asset.id}
            isHovered={hoveredAssetId === asset.id}
            onClick={() => handleAssetSelect(asset)}
            onMouseEnter={() => setHoveredAssetId(asset.id)}
            onMouseLeave={() => setHoveredAssetId(null)}
            zoomLevel={zoomLevel}
          />
        ))}

        {/* Empty state */}
        {assets.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <svg
                className="w-16 h-16 text-tertiary mx-auto mb-4"
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
              <p className="text-secondary font-medium">No assets to display</p>
              <p className="text-tertiary text-sm mt-1">
                Generate some data to visualize the attack surface
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Asset detail panel */}
      {selectedAsset && (
        <AssetDetailPanel
          asset={selectedAsset}
          layers={layers}
          onClose={() => {
            setSelectedAssetId(null);
            onAssetSelect?.(null);
          }}
        />
      )}

      {/* Stats bar */}
      <div className="flex-shrink-0 px-4 py-2 bg-secondary border-t border-primary flex items-center justify-between text-xs text-secondary">
        <div className="flex items-center gap-4">
          <span>{assets.length} assets</span>
          <span>{visibleConnections.length} connections</span>
          <span>
            {layers.filter((l) => l.enabled).length} / {layers.length} layers
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-tertiary">Last updated:</span>
          <span>{format(new Date(), "HH:mm:ss")}</span>
        </div>
      </div>
    </div>
  );
}

// Asset detail panel
function AssetDetailPanel({
  asset,
  layers,
  onClose,
}: {
  asset: VisualAsset;
  layers: LayerState[];
  onClose: () => void;
}) {
  const enabledLayers = layers.filter((l) => l.enabled);

  return (
    <div className="absolute right-0 top-0 bottom-0 w-80 bg-secondary border-l border-primary shadow-xl overflow-y-auto">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-medium text-primary">{asset.hostname}</h3>
          <button
            onClick={onClose}
            className="p-1 text-secondary hover:text-primary transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Basic info */}
        <div className="space-y-3 mb-4">
          <div className="flex justify-between text-sm">
            <span className="text-tertiary">IP</span>
            <span className="text-secondary font-mono">{asset.ip}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-tertiary">Type</span>
            <span className="text-secondary capitalize">{asset.type.replace("_", " ")}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-tertiary">Risk Score</span>
            <span
              className={clsx(
                "px-2 py-0.5 rounded text-xs font-medium",
                asset.riskScore >= 80 && "bg-red-900 text-red-300",
                asset.riskScore >= 60 && asset.riskScore < 80 && "bg-orange-900 text-orange-300",
                asset.riskScore >= 40 && asset.riskScore < 60 && "bg-yellow-900 text-yellow-300",
                asset.riskScore < 40 && "bg-green-900 text-green-300",
              )}
            >
              {asset.riskScore}
            </span>
          </div>
        </div>

        {/* Layer-specific details */}
        <div className="space-y-4">
          {enabledLayers.map((layer) => {
            const config = LAYER_COLORS[layer.id];
            const layerData = asset.layers[layer.id];

            // Skip if layer not active for this asset
            if (layer.id !== "base" && !(layerData as any)?.active) return null;

            return (
              <div
                key={layer.id}
                className="p-3 rounded-lg border"
                style={{
                  backgroundColor: `${config.colorBase}10`,
                  borderColor: `${config.colorBase}40`,
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
                  {layer.id === "edr" && asset.layers.edr.active && (
                    <>
                      <div className="flex justify-between text-secondary">
                        <span>Detections</span>
                        <span className="text-primary">{asset.layers.edr.detectionCount}</span>
                      </div>
                      {asset.layers.edr.severity && (
                        <div className="flex justify-between text-secondary">
                          <span>Severity</span>
                          <span className="text-primary capitalize">{asset.layers.edr.severity}</span>
                        </div>
                      )}
                    </>
                  )}

                  {layer.id === "siem" && asset.layers.siem.active && (
                    <>
                      <div className="flex justify-between text-secondary">
                        <span>Incidents</span>
                        <span className="text-primary">{asset.layers.siem.incidentCount}</span>
                      </div>
                      {asset.layers.siem.status && (
                        <div className="flex justify-between text-secondary">
                          <span>Status</span>
                          <span className="text-primary capitalize">{asset.layers.siem.status}</span>
                        </div>
                      )}
                    </>
                  )}

                  {layer.id === "ctem" && asset.layers.ctem.active && (
                    <>
                      <div className="flex justify-between text-secondary">
                        <span>CVEs</span>
                        <span className="text-primary">{asset.layers.ctem.cveCount}</span>
                      </div>
                      <div className="flex justify-between text-secondary">
                        <span>Risk Level</span>
                        <span className="text-primary capitalize">{asset.layers.ctem.riskLevel}</span>
                      </div>
                    </>
                  )}

                  {layer.id === "threats" && asset.layers.threats.active && (
                    <>
                      <div className="flex justify-between text-secondary">
                        <span>IOCs</span>
                        <span className="text-primary">{asset.layers.threats.iocCount}</span>
                      </div>
                      {asset.layers.threats.threatActors.length > 0 && (
                        <div className="mt-1">
                          <span className="text-tertiary">Threat Actors:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {asset.layers.threats.threatActors.map((actor) => (
                              <span
                                key={actor}
                                className="px-1.5 py-0.5 bg-purple-900/50 text-purple-300 rounded"
                              >
                                {actor}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}

                  {layer.id === "vulnerabilities" && asset.layers.vulnerabilities?.active && (
                    <>
                      <div className="flex justify-between text-secondary">
                        <span>CVEs</span>
                        <span className="text-primary">{asset.layers.vulnerabilities.cveCount}</span>
                      </div>
                      <div className="flex justify-between text-secondary">
                        <span>Critical</span>
                        <span className="text-primary">
                          {asset.layers.vulnerabilities.criticalCount}
                        </span>
                      </div>
                      <div className="flex justify-between text-secondary">
                        <span>KEV</span>
                        <span className="text-primary">{asset.layers.vulnerabilities.kevCount}</span>
                      </div>
                    </>
                  )}

                  {layer.id === "containment" && asset.layers.containment?.active && (
                    <>
                      <div className="flex justify-between text-secondary">
                        <span>Status</span>
                        <span className="text-primary">
                          {asset.layers.containment.isContained ? "Contained" : "Not Contained"}
                        </span>
                      </div>
                      {asset.layers.containment.containedAt && (
                        <div className="flex justify-between text-secondary">
                          <span>Since</span>
                          <span className="text-primary">
                            {format(new Date(asset.layers.containment.containedAt), "MMM d, HH:mm")}
                          </span>
                        </div>
                      )}
                    </>
                  )}

                  {layer.id === "relations" && asset.layers.relations?.active && (
                    <div className="flex justify-between text-secondary">
                      <span>Connections</span>
                      <span className="text-primary">{asset.layers.relations.connectionCount}</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
