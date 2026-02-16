/**
 * SankeyFlow Component
 *
 * Remediation workflow visualization using Sankey diagram
 * with animated flow particles and time period filtering
 */

import { useState, useMemo, useRef } from "react";
import type { SankeyFlowData, SankeyNode, SankeyLink, VulnViewCommonProps } from "../../types/vulnerabilityViews";

// Default node colors
const DEFAULT_NODE_COLORS: Record<string, string> = {
  discovered: "#6b7280",
  triaged: "#3b82f6",
  assigned: "#8b5cf6",
  in_progress: "#f59e0b",
  remediated: "#22c55e",
  accepted_risk: "#ef4444",
  false_positive: "#9ca3af",
};

interface SankeyFlowProps extends VulnViewCommonProps {
  data: SankeyFlowData;
  onNodeClick?: (nodeId: string) => void;
  onTimePeriodChange?: (period: string) => void;
  showParticles?: boolean;
}

interface TooltipData {
  type: "node" | "link";
  name?: string;
  count?: number;
  source?: string;
  target?: string;
  value?: number;
}

interface ProcessedNode extends SankeyNode {
  x: number;
  y: number;
  height: number;
}

interface ProcessedLink extends SankeyLink {
  sourceY: number;
  targetY: number;
  strokeWidth: number;
}

const TIME_PERIODS = ["7d", "30d", "90d", "All"];

export function SankeyFlow({
  data,
  className = "",
  onNodeClick,
  onTimePeriodChange,
  showParticles = true,
  isLoading = false,
  error = null,
}: SankeyFlowProps) {
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const [highlightedNode, setHighlightedNode] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState("30d");
  const svgRef = useRef<SVGSVGElement>(null);

  const width = 700;
  const height = 400;
  const nodeWidth = 20;
  const nodePadding = 20;

  // Process nodes and links for layout
  const { processedNodes, processedLinks } = useMemo(() => {
    if (data.nodes.length === 0) {
      return { processedNodes: [], processedLinks: [] };
    }

    // Group nodes by stage (column)
    const stages = [
      ["discovered"],
      ["triaged"],
      ["assigned"],
      ["in_progress"],
      ["remediated", "accepted_risk", "false_positive"],
    ];

    const nodeMap = new Map(data.nodes.map((n) => [n.id, n]));
    const totalHeight = height - 80;
    const columnWidth = (width - 100) / (stages.length - 1);

    // Position nodes
    const processed: ProcessedNode[] = [];

    stages.forEach((stageIds, colIdx) => {
      const stageNodes = stageIds
        .map((id) => nodeMap.get(id))
        .filter(Boolean) as SankeyNode[];

      const maxCount = Math.max(...data.nodes.map((n) => n.count), 1);

      let yOffset = 40;
      stageNodes.forEach((node) => {
        const nodeHeight = Math.max(20, (node.count / maxCount) * (totalHeight * 0.6));
        processed.push({
          ...node,
          x: 50 + colIdx * columnWidth,
          y: yOffset,
          height: nodeHeight,
        });
        yOffset += nodeHeight + nodePadding;
      });
    });

    // Create a lookup for processed nodes
    const processedMap = new Map(processed.map((n) => [n.id, n]));

    // Process links
    const links: ProcessedLink[] = [];
    const sourceOffsets = new Map<string, number>();
    const targetOffsets = new Map<string, number>();

    data.links.forEach((link) => {
      const sourceNode = processedMap.get(link.source);
      const targetNode = processedMap.get(link.target);

      if (!sourceNode || !targetNode) return;

      const sourceOffset = sourceOffsets.get(link.source) || 0;
      const targetOffset = targetOffsets.get(link.target) || 0;

      const maxValue = Math.max(...data.links.map((l) => l.value), 1);
      const strokeWidth = Math.max(2, (link.value / maxValue) * 30);

      links.push({
        ...link,
        sourceY: sourceNode.y + sourceOffset + strokeWidth / 2,
        targetY: targetNode.y + targetOffset + strokeWidth / 2,
        strokeWidth,
      });

      sourceOffsets.set(link.source, sourceOffset + strokeWidth + 2);
      targetOffsets.set(link.target, targetOffset + strokeWidth + 2);
    });

    return { processedNodes: processed, processedLinks: links };
  }, [data, width, height]);

  // Generate link path
  const generateLinkPath = (link: ProcessedLink): string => {
    const sourceNode = processedNodes.find((n) => n.id === link.source);
    const targetNode = processedNodes.find((n) => n.id === link.target);

    if (!sourceNode || !targetNode) return "";

    const x1 = sourceNode.x + nodeWidth;
    const y1 = link.sourceY;
    const x2 = targetNode.x;
    const y2 = link.targetY;
    const midX = (x1 + x2) / 2;

    return `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`;
  };

  // Handle time period change
  const handlePeriodChange = (period: string) => {
    setSelectedPeriod(period);
    onTimePeriodChange?.(period);
  };

  // Handle node click
  const handleNodeClick = (nodeId: string) => {
    onNodeClick?.(nodeId);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent, nodeId: string) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onNodeClick?.(nodeId);
    } else if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
      e.preventDefault();
      const currentIdx = processedNodes.findIndex((n) => n.id === nodeId);
      const newIdx = e.key === "ArrowRight"
        ? Math.min(currentIdx + 1, processedNodes.length - 1)
        : Math.max(currentIdx - 1, 0);
      const nextNode = processedNodes[newIdx];
      if (nextNode) {
        const element = document.querySelector(`[data-testid="sankey-node-${nextNode.id}"]`) as HTMLElement;
        element?.focus();
      }
    }
  };

  // Handle mouse enter for tooltip
  const handleNodeMouseEnter = (node: ProcessedNode, event: React.MouseEvent) => {
    setHighlightedNode(node.id);
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltipPosition({
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
    });
    setTooltip({
      type: "node",
      name: node.name,
      count: node.count,
    });
  };

  const handleLinkMouseEnter = (link: ProcessedLink, event: React.MouseEvent) => {
    setHighlightedNode(null);
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltipPosition({
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
    });
    setTooltip({
      type: "link",
      source: link.source,
      target: link.target,
      value: link.value,
    });
  };

  // Calculate remediation percentage
  const remediationPercentage = data.total_cves > 0
    ? Math.round((data.remediated_count / data.total_cves) * 100)
    : 0;

  // Loading state
  if (isLoading) {
    return (
      <div
        data-testid="sankey-loading"
        className={`flex items-center justify-center h-96 bg-gray-900 rounded-lg ${className}`}
      >
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`flex items-center justify-center h-96 bg-gray-900 rounded-lg ${className}`}>
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
  if (data.nodes.length === 0) {
    return (
      <div
        data-testid="sankey-flow"
        className={`flex items-center justify-center h-96 bg-gray-900 rounded-lg ${className}`}
        aria-label="Sankey flow - no data"
      >
        <div className="text-center text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p>No remediation data available</p>
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="sankey-flow"
      className={`bg-gray-900 rounded-lg p-4 ${className}`}
      aria-label="remediation workflow Sankey diagram"
    >
      {/* Header with time selector and stats */}
      <div className="flex items-center justify-between mb-4">
        {/* Time period selector */}
        <div data-testid="sankey-time-selector" className="flex gap-1">
          {TIME_PERIODS.map((period) => (
            <button
              key={period}
              className={`px-3 py-1 text-sm rounded transition-colors ${selectedPeriod === period
                  ? "bg-cyan-600 text-white"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                }`}
              onClick={() => handlePeriodChange(period)}
            >
              {period}
            </button>
          ))}
        </div>

        {/* Stats */}
        <div className="flex gap-6 text-sm">
          <div data-testid="sankey-stat-total" className="text-center">
            <div className="text-xl font-bold text-white">{data.total_cves}</div>
            <div className="text-xs text-gray-400">Total</div>
          </div>
          <div data-testid="sankey-stat-remediated" className="text-center">
            <div className="text-xl font-bold text-green-400">{data.remediated_count}</div>
            <div className="text-xs text-gray-400">Remediated</div>
          </div>
          <div data-testid="sankey-stat-progress" className="text-center">
            <div className="text-xl font-bold text-amber-400">{data.in_progress_count}</div>
            <div className="text-xs text-gray-400">In Progress</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-cyan-400">{remediationPercentage}%</div>
            <div className="text-xs text-gray-400">Complete</div>
          </div>
        </div>
      </div>

      {/* SVG Canvas */}
      <svg
        ref={svgRef}
        data-testid="sankey-svg"
        width="100%"
        height="400"
        viewBox={`0 0 ${width} ${height}`}
        className="overflow-visible"
      >
        {/* Definitions */}
        <defs>
          {/* Gradients for links */}
          {processedLinks.map((link, idx) => {
            const sourceNode = processedNodes.find((n) => n.id === link.source);
            const targetNode = processedNodes.find((n) => n.id === link.target);
            const sourceColor = sourceNode?.color || DEFAULT_NODE_COLORS[link.source] || "#6b7280";
            const targetColor = targetNode?.color || DEFAULT_NODE_COLORS[link.target] || "#6b7280";

            return (
              <linearGradient
                key={`gradient-${idx}`}
                id={`link-gradient-${link.source}-${link.target}`}
                x1="0%"
                y1="0%"
                x2="100%"
                y2="0%"
              >
                <stop offset="0%" stopColor={sourceColor} stopOpacity="0.5" />
                <stop offset="100%" stopColor={targetColor} stopOpacity="0.5" />
              </linearGradient>
            );
          })}
        </defs>

        {/* Links */}
        {processedLinks.map((link, idx) => {
          const isHighlighted = highlightedNode === link.source || highlightedNode === link.target;

          return (
            <path
              key={`link-${idx}`}
              data-testid={`sankey-link-${link.source}-${link.target}`}
              data-source={link.source}
              data-target={link.target}
              data-highlighted={isHighlighted.toString()}
              d={generateLinkPath(link)}
              fill="none"
              stroke={`url(#link-gradient-${link.source}-${link.target})`}
              strokeWidth={link.strokeWidth}
              strokeLinecap="round"
              opacity={isHighlighted ? 0.8 : 0.4}
              className={`animate-sankey-flow cursor-pointer transition-opacity duration-200 hover:opacity-80`}
              onMouseEnter={(e) => handleLinkMouseEnter(link, e)}
              onMouseLeave={() => setTooltip(null)}
            />
          );
        })}

        {/* Particles (animated dots flowing along links) */}
        {showParticles && processedLinks.slice(0, 5).map((link, idx) => (
          <circle
            key={`particle-${idx}`}
            data-testid={`sankey-particle-${idx}`}
            r="3"
            fill="white"
            opacity="0.6"
          >
            <animateMotion
              dur={`${3 + idx * 0.5}s`}
              repeatCount="indefinite"
              path={generateLinkPath(link)}
            />
          </circle>
        ))}

        {/* Nodes */}
        {processedNodes.map((node) => {
          const color = node.color || DEFAULT_NODE_COLORS[node.id] || "#6b7280";
          const isHighlighted = highlightedNode === node.id;

          return (
            <g key={node.id}>
              {/* Node rectangle */}
              <rect
                data-testid={`sankey-node-${node.id}`}
                x={node.x}
                y={node.y}
                width={nodeWidth}
                height={node.height}
                fill={color}
                stroke={isHighlighted ? "white" : "none"}
                strokeWidth={isHighlighted ? 2 : 0}
                rx="3"
                className="cursor-pointer transition-all duration-200"
                tabIndex={0}
                role="button"
                aria-label={`${node.name}: ${node.count} CVEs`}
                onClick={() => handleNodeClick(node.id)}
                onKeyDown={(e) => handleKeyDown(e, node.id)}
                onMouseEnter={(e) => handleNodeMouseEnter(node, e)}
                onMouseLeave={() => {
                  setHighlightedNode(null);
                  setTooltip(null);
                }}
              />

              {/* Node label */}
              <text
                x={node.x + nodeWidth + 5}
                y={node.y + node.height / 2}
                dominantBaseline="middle"
                fill="#d1d5db"
                fontSize="11"
                className="pointer-events-none"
              >
                {node.name}
              </text>

              {/* Count */}
              <text
                x={node.x + nodeWidth / 2}
                y={node.y + node.height / 2}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="white"
                fontSize="10"
                fontWeight="bold"
                className="pointer-events-none"
              >
                {node.count}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Tooltip */}
      {tooltip && (
        <div
          role="tooltip"
          className="fixed z-50 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl text-sm pointer-events-none"
          style={{
            left: `${tooltipPosition.x}px`,
            top: `${tooltipPosition.y}px`,
            transform: "translate(-50%, -100%)",
          }}
        >
          {tooltip.type === "node" ? (
            <>
              <div className="font-medium text-white">{tooltip.name}</div>
              <div className="text-cyan-400">{tooltip.count} CVEs</div>
            </>
          ) : (
            <>
              <div className="text-gray-300">
                {tooltip.source} → {tooltip.target}
              </div>
              <div className="text-cyan-400">{tooltip.value} CVEs</div>
            </>
          )}
        </div>
      )}

      {/* CSS for flow animation */}
      <style>{`
        @keyframes sankey-flow {
          0% {
            stroke-dashoffset: 20;
          }
          100% {
            stroke-dashoffset: 0;
          }
        }
        .animate-sankey-flow {
          stroke-dasharray: 5 5;
          animation: sankey-flow 1s linear infinite;
        }
      `}</style>
    </div>
  );
}
