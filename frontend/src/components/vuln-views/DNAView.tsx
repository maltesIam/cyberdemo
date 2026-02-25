/**
 * DNAView Component
 *
 * Double helix visualization showing CVE-Asset pairs
 * with rotation animation and severity-based coloring
 */

import { useState, useMemo } from "react";
import type { DNAViewData, DNAStrand, VulnViewCommonProps } from "../../types/vulnerabilityViews";

// Severity color mapping
const SEVERITY_COLORS = {
  Critical: "#dc2626",
  High: "#f97316",
  Medium: "#eab308",
  Low: "#22c55e",
};

interface DNAViewProps extends VulnViewCommonProps {
  data: DNAViewData;
  onAssetClick?: (assetId: string) => void;
}

interface TooltipData {
  cve_id: string;
  asset_id: string;
  asset_hostname: string;
  cvss_score: number;
  severity: string;
  is_kev: boolean;
  exploit_available: boolean;
}

export function DNAView({
  data,
  className = "",
  onCVEClick,
  onAssetClick,
  isLoading = false,
  error = null,
}: DNAViewProps) {
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const [highlightedCVE, setHighlightedCVE] = useState<string | null>(null);
  const [isPaused, setIsPaused] = useState(false);

  const width = 600;
  const height = 400;
  const centerX = width / 2;
  const helixRadius = 100;

  // Calculate helix positions
  const nodes = useMemo(() => {
    return data.strands.map((strand, idx) => {
      const angle = (idx / data.strands.length) * Math.PI * 4; // Two full rotations
      const y = 50 + (idx / data.strands.length) * (height - 100);

      // Alternating sides of helix
      const side = idx % 2 === 0 ? 1 : -1;
      const x = centerX + Math.cos(angle) * helixRadius * side;

      // Node radius based on CVSS
      const radius = 8 + (strand.cvss_score / 10) * 8;

      return {
        ...strand,
        x,
        y,
        radius,
        angle,
        side,
      };
    });
  }, [data.strands, height, centerX]);

  // Generate backbone path
  const generateHelixPath = (side: number) => {
    if (nodes.length < 2) return "";

    const points = nodes
      .filter((_, idx) => idx % 2 === (side === 1 ? 0 : 1))
      .map((n) => `${n.x},${n.y}`);

    if (points.length < 2) return "";

    return `M ${points.join(" L ")}`;
  };

  // Handle node click
  const handleNodeClick = (cveId: string) => {
    onCVEClick?.(cveId);
  };

  // Handle keyboard interaction
  const handleKeyDown = (e: React.KeyboardEvent, cveId: string) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onCVEClick?.(cveId);
    }
  };

  // Handle mouse enter for tooltip and highlighting
  const handleMouseEnter = (strand: DNAStrand & { x: number; y: number }, event: React.MouseEvent) => {
    setHighlightedCVE(strand.cve_id);
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltipPosition({
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
    });
    setTooltip({
      cve_id: strand.cve_id,
      asset_id: strand.asset_id,
      asset_hostname: strand.asset_hostname,
      cvss_score: strand.cvss_score,
      severity: strand.severity,
      is_kev: strand.is_kev,
      exploit_available: strand.exploit_available,
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div
        data-testid="dna-loading"
        className={`flex items-center justify-center h-96 bg-primary rounded-lg ${className}`}
      >
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`flex items-center justify-center h-96 bg-primary rounded-lg ${className}`}>
        <div className="text-center">
          <svg className="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (data.strands.length === 0) {
    return (
      <div
        data-testid="dna-view"
        className={`flex items-center justify-center h-96 bg-primary rounded-lg ${className}`}
        aria-label="DNA view - no data"
      >
        <div className="text-center text-tertiary">
          <svg className="w-16 h-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
          <p>No CVE-Asset pairs available</p>
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="dna-view"
      className={`bg-primary rounded-lg p-4 ${className}`}
      aria-label="CVE-Asset DNA helix visualization"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Stats bar */}
      <div className="flex justify-center gap-6 mb-4 text-sm">
        <div className="text-center">
          <span className="text-cyan-400 font-bold">{data.total_pairs} pairs</span>
        </div>
        <div className="text-center">
          <span className="text-orange-400 font-bold">{data.kev_pairs} KEV</span>
        </div>
        <div className="text-center">
          <span className="text-purple-400 font-bold">{data.exploitable_pairs} exploitable</span>
        </div>
      </div>

      {/* SVG Canvas */}
      <svg
        data-testid="dna-svg"
        width="100%"
        height="400"
        viewBox={`0 0 ${width} ${height}`}
        className="overflow-visible"
      >
        {/* Definitions */}
        <defs>
          <linearGradient id="strandGradient1" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.8" />
          </linearGradient>
          <linearGradient id="strandGradient2" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.8" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Helix group with rotation animation */}
        <g
          data-testid="dna-helix-group"
          className="animate-dna-rotate"
          data-paused={isPaused.toString()}
          style={{
            transformOrigin: "center center",
            animation: isPaused ? "none" : undefined,
          }}
        >
          {/* Backbone strands */}
          <path
            data-testid="dna-strand-1"
            d={generateHelixPath(1)}
            fill="none"
            stroke="url(#strandGradient1)"
            strokeWidth="3"
            strokeLinecap="round"
            opacity="0.7"
          />
          <path
            data-testid="dna-strand-2"
            d={generateHelixPath(-1)}
            fill="none"
            stroke="url(#strandGradient2)"
            strokeWidth="3"
            strokeLinecap="round"
            opacity="0.7"
          />

          {/* Rungs connecting strands */}
          {nodes.filter((_, i) => i % 2 === 0 && i < nodes.length - 1).map((node, idx) => {
            const nextNode = nodes[idx * 2 + 1];
            if (!nextNode) return null;

            return (
              <line
                key={`rung-${idx}`}
                data-testid={`dna-rung-${idx}`}
                x1={node.x}
                y1={node.y}
                x2={nextNode.x}
                y2={nextNode.y}
                stroke="#4b5563"
                strokeWidth="2"
                strokeDasharray="4 2"
                opacity="0.5"
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node, idx) => {
            const isHighlighted = highlightedCVE === node.cve_id;
            const color = SEVERITY_COLORS[node.severity];

            return (
              <g key={`node-${idx}`}>
                {/* Glow for highlighted/KEV */}
                {(isHighlighted || node.is_kev) && (
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={node.radius + 4}
                    fill="none"
                    stroke={node.is_kev ? "#f97316" : color}
                    strokeWidth="2"
                    opacity="0.5"
                    filter="url(#glow)"
                  />
                )}

                {/* Main node */}
                <circle
                  data-testid={`dna-node-${idx}`}
                  data-severity={node.severity}
                  data-kev={node.is_kev.toString()}
                  data-exploit={node.exploit_available.toString()}
                  data-highlighted={isHighlighted.toString()}
                  cx={node.x}
                  cy={node.y}
                  r={node.radius}
                  fill={color}
                  stroke={isHighlighted ? "white" : "rgba(255,255,255,0.3)"}
                  strokeWidth={isHighlighted ? 2 : 1}
                  className="cursor-pointer transition-all duration-200"
                  tabIndex={0}
                  role="button"
                  aria-label={`${node.cve_id} on ${node.asset_hostname}, CVSS ${node.cvss_score}`}
                  onClick={() => handleNodeClick(node.cve_id)}
                  onKeyDown={(e) => handleKeyDown(e, node.cve_id)}
                  onMouseEnter={(e) => handleMouseEnter(node, e)}
                  onMouseLeave={() => {
                    setHighlightedCVE(null);
                    setTooltip(null);
                  }}
                />

                {/* Exploit skull indicator */}
                {node.exploit_available && (
                  <text
                    x={node.x}
                    y={node.y + 3}
                    textAnchor="middle"
                    fill="white"
                    fontSize="10"
                    className="pointer-events-none"
                  >
                    !
                  </text>
                )}
              </g>
            );
          })}
        </g>

        {/* Asset labels on the left */}
        {nodes.filter((_, i) => i % 4 === 0).slice(0, 5).map((node, idx) => (
          <text
            key={`asset-label-${idx}`}
            x={40}
            y={node.y}
            textAnchor="start"
            dominantBaseline="middle"
            fill="#9ca3af"
            fontSize="11"
            className="cursor-pointer hover:fill-cyan-400 transition-colors"
            onClick={() => onAssetClick?.(node.asset_id)}
          >
            {node.asset_hostname.length > 15
              ? node.asset_hostname.substring(0, 15) + "..."
              : node.asset_hostname}
          </text>
        ))}

        {/* CVE labels on the right */}
        {nodes.filter((_, i) => i % 4 === 2).slice(0, 5).map((node, idx) => (
          <text
            key={`cve-label-${idx}`}
            x={width - 40}
            y={node.y}
            textAnchor="end"
            dominantBaseline="middle"
            fill="#9ca3af"
            fontSize="11"
            className="cursor-pointer hover:fill-cyan-400 transition-colors"
            onClick={() => onCVEClick?.(node.cve_id)}
          >
            {node.cve_id}
          </text>
        ))}
      </svg>

      {/* Legend */}
      <div className="flex justify-center gap-4 mt-4 text-xs">
        {Object.entries(SEVERITY_COLORS).map(([severity, color]) => (
          <div key={severity} className="flex items-center gap-1">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-secondary">{severity}</span>
          </div>
        ))}
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full border-2 border-orange-500" />
          <span className="text-secondary">KEV</span>
        </div>
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div
          role="tooltip"
          className="fixed z-50 px-3 py-2 bg-secondary border border-primary rounded-lg shadow-xl text-sm pointer-events-none"
          style={{
            left: `${tooltipPosition.x}px`,
            top: `${tooltipPosition.y}px`,
            transform: "translate(-50%, -100%)",
          }}
        >
          <div className="font-mono text-cyan-400">{tooltip.cve_id}</div>
          <div className="text-secondary">{tooltip.asset_hostname}</div>
          <div className="text-secondary text-xs">Asset: {tooltip.asset_id}</div>
          <div className="flex gap-2 mt-1">
            <span className="text-orange-400">CVSS: {tooltip.cvss_score}</span>
            <span
              className="px-1.5 py-0.5 rounded text-xs"
              style={{ backgroundColor: SEVERITY_COLORS[tooltip.severity as keyof typeof SEVERITY_COLORS] + "40" }}
            >
              {tooltip.severity}
            </span>
          </div>
          <div className="flex gap-2 mt-1">
            {tooltip.is_kev && (
              <span className="px-1.5 py-0.5 rounded text-xs bg-orange-600/40">KEV</span>
            )}
            {tooltip.exploit_available && (
              <span className="px-1.5 py-0.5 rounded text-xs bg-purple-600/40">Exploit</span>
            )}
          </div>
        </div>
      )}

      {/* CSS for DNA rotation animation */}
      <style>{`
        @keyframes dna-rotate {
          from {
            transform: rotateY(0deg);
          }
          to {
            transform: rotateY(360deg);
          }
        }
        .animate-dna-rotate {
          animation: dna-rotate 20s linear infinite;
          transform-style: preserve-3d;
        }
        .animate-dna-rotate[data-paused="true"] {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
}
