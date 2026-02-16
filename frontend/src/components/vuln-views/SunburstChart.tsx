/**
 * SunburstChart Component
 *
 * Hierarchical CWE visualization in a radial sunburst format
 * with zoom capabilities and severity-based coloring
 */

import { useState, useMemo, useCallback } from "react";
import type { SunburstChartData, SunburstNode, VulnViewCommonProps } from "../../types/vulnerabilityViews";

// Severity color mapping
const SEVERITY_COLORS = {
  critical: "#dc2626",
  high: "#f97316",
  medium: "#eab308",
  low: "#22c55e",
};

// Default colors for categories
const CATEGORY_COLORS = [
  "#3b82f6", // blue
  "#8b5cf6", // violet
  "#ec4899", // pink
  "#14b8a6", // teal
  "#f59e0b", // amber
  "#10b981", // emerald
  "#6366f1", // indigo
  "#f43f5e", // rose
];

interface SunburstChartProps extends VulnViewCommonProps {
  data: SunburstChartData;
  onCWEClick?: (cweId: string) => void;
}

interface TooltipData {
  name: string;
  value: number;
  cwe_id?: string;
  severity_counts?: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}

interface ArcData {
  node: SunburstNode;
  depth: number;
  startAngle: number;
  endAngle: number;
  innerRadius: number;
  outerRadius: number;
  color: string;
  dominantSeverity?: string;
}

export function SunburstChart({
  data,
  className = "",
  onCWEClick,
  isLoading = false,
  error = null,
}: SunburstChartProps) {
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const [zoomedNode, setZoomedNode] = useState<SunburstNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<SunburstNode | null>(null);

  // Calculate arc data from hierarchical structure
  const arcs = useMemo(() => {
    const result: ArcData[] = [];
    const root = zoomedNode || data.root;

    if (!root.children || root.children.length === 0) return result;

    const totalValue = root.children.reduce((sum, child) => sum + child.value, 0);
    let currentAngle = 0;

    const processNode = (
      node: SunburstNode,
      startAngle: number,
      angleRange: number,
      depth: number,
      colorIndex: number
    ) => {
      const endAngle = startAngle + angleRange;
      const innerRadius = 60 + depth * 40;
      const outerRadius = innerRadius + 35;

      // Determine dominant severity
      let dominantSeverity: string | undefined;
      if (node.severity_counts) {
        const counts = node.severity_counts;
        const maxCount = Math.max(counts.critical, counts.high, counts.medium, counts.low);
        if (counts.critical === maxCount) dominantSeverity = "critical";
        else if (counts.high === maxCount) dominantSeverity = "high";
        else if (counts.medium === maxCount) dominantSeverity = "medium";
        else dominantSeverity = "low";
      }

      // Determine color
      const color = dominantSeverity
        ? SEVERITY_COLORS[dominantSeverity as keyof typeof SEVERITY_COLORS]
        : CATEGORY_COLORS[colorIndex % CATEGORY_COLORS.length];

      result.push({
        node,
        depth: zoomedNode ? depth : depth + 1,
        startAngle,
        endAngle,
        innerRadius,
        outerRadius,
        color,
        dominantSeverity,
      });

      // Process children
      if (node.children && node.children.length > 0) {
        const childTotal = node.children.reduce((sum, child) => sum + child.value, 0);
        let childAngle = startAngle;

        node.children.forEach((child) => {
          const childRange = (child.value / childTotal) * angleRange;
          processNode(child, childAngle, childRange, depth + 1, colorIndex);
          childAngle += childRange;
        });
      }
    };

    root.children.forEach((child, index) => {
      const angleRange = (child.value / totalValue) * 360;
      processNode(child, currentAngle, angleRange, 0, index);
      currentAngle += angleRange;
    });

    return result;
  }, [data.root, zoomedNode]);

  // Convert polar to Cartesian coordinates
  const polarToCartesian = (cx: number, cy: number, radius: number, angleInDegrees: number) => {
    const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180;
    return {
      x: cx + radius * Math.cos(angleInRadians),
      y: cy + radius * Math.sin(angleInRadians),
    };
  };

  // Create arc path
  const describeArc = useCallback((cx: number, cy: number, innerRadius: number, outerRadius: number, startAngle: number, endAngle: number) => {
    const start1 = polarToCartesian(cx, cy, outerRadius, startAngle);
    const end1 = polarToCartesian(cx, cy, outerRadius, endAngle);
    const start2 = polarToCartesian(cx, cy, innerRadius, endAngle);
    const end2 = polarToCartesian(cx, cy, innerRadius, startAngle);

    const largeArcFlag = endAngle - startAngle > 180 ? 1 : 0;

    return [
      "M", start1.x, start1.y,
      "A", outerRadius, outerRadius, 0, largeArcFlag, 1, end1.x, end1.y,
      "L", start2.x, start2.y,
      "A", innerRadius, innerRadius, 0, largeArcFlag, 0, end2.x, end2.y,
      "Z"
    ].join(" ");
  }, []);

  // Handle arc click
  const handleArcClick = (arc: ArcData) => {
    if (arc.node.cwe_id) {
      onCWEClick?.(arc.node.cwe_id);
    }
  };

  // Handle double click to zoom
  const handleArcDoubleClick = (arc: ArcData) => {
    if (arc.node.children && arc.node.children.length > 0) {
      setZoomedNode(arc.node);
    }
  };

  // Handle center click to reset zoom
  const handleCenterClick = () => {
    setZoomedNode(null);
  };

  // Handle mouse enter for tooltip
  const handleMouseEnter = (arc: ArcData, event: React.MouseEvent) => {
    setHoveredNode(arc.node);
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltipPosition({
      x: rect.left + rect.width / 2,
      y: rect.top,
    });
    setTooltip({
      name: arc.node.name,
      value: arc.node.value,
      cwe_id: arc.node.cwe_id,
      severity_counts: arc.node.severity_counts,
    });
  };

  // Build breadcrumb
  const breadcrumb = useMemo(() => {
    if (!zoomedNode) return [];
    const trail: SunburstNode[] = [data.root];

    const findPath = (node: SunburstNode, target: SunburstNode, path: SunburstNode[]): boolean => {
      if (node === target) return true;
      if (node.children) {
        for (const child of node.children) {
          if (findPath(child, target, path)) {
            path.unshift(child);
            return true;
          }
        }
      }
      return false;
    };

    findPath(data.root, zoomedNode, trail);
    return trail;
  }, [data.root, zoomedNode]);

  // Loading state
  if (isLoading) {
    return (
      <div
        data-testid="sunburst-loading"
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
  if (!data.root.children || data.root.children.length === 0) {
    return (
      <div
        data-testid="sunburst-chart"
        className={`flex items-center justify-center h-96 bg-gray-900 rounded-lg ${className}`}
        aria-label="CWE Sunburst chart - no data"
      >
        <div className="text-center text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
          </svg>
          <p>No CWE data available</p>
        </div>
      </div>
    );
  }

  const cx = 200;
  const cy = 200;
  const displayNode = hoveredNode || zoomedNode || data.root;

  return (
    <div
      data-testid="sunburst-chart"
      className={`bg-gray-900 rounded-lg p-4 ${className}`}
      aria-label="CWE Sunburst chart showing vulnerability categories"
    >
      {/* Breadcrumb */}
      {zoomedNode && breadcrumb.length > 0 && (
        <div data-testid="sunburst-breadcrumb" className="flex items-center gap-2 mb-4 text-sm">
          {breadcrumb.map((node, idx) => (
            <span key={idx} className="flex items-center gap-2">
              {idx > 0 && <span className="text-gray-500">/</span>}
              <button
                className="text-gray-400 hover:text-cyan-400 transition-colors"
                onClick={() => setZoomedNode(idx === 0 ? null : node)}
              >
                {node.name}
              </button>
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-center">
        <svg
          data-testid="sunburst-svg"
          width="400"
          height="400"
          viewBox="0 0 400 400"
          className="overflow-visible"
        >
          {/* Arcs */}
          {arcs.map((arc, idx) => (
            <path
              key={`${arc.node.cwe_id || arc.node.name}-${idx}`}
              data-testid={`sunburst-arc-${arc.node.cwe_id || arc.node.name}`}
              data-value={arc.node.value}
              data-depth={arc.depth}
              data-dominant-severity={arc.dominantSeverity}
              data-zoomed={zoomedNode ? "true" : "false"}
              d={describeArc(cx, cy, arc.innerRadius, arc.outerRadius, arc.startAngle, arc.endAngle)}
              fill={arc.color}
              stroke="#1f2937"
              strokeWidth="1"
              opacity={hoveredNode && hoveredNode !== arc.node ? 0.5 : 0.85}
              className="cursor-pointer transition-all duration-200 hover:opacity-100"
              tabIndex={0}
              role="button"
              aria-label={`${arc.node.name}: ${arc.node.value} CVEs`}
              onClick={() => handleArcClick(arc)}
              onDoubleClick={() => handleArcDoubleClick(arc)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleArcClick(arc);
              }}
              onMouseEnter={(e) => handleMouseEnter(arc, e)}
              onMouseLeave={() => {
                setHoveredNode(null);
                setTooltip(null);
              }}
            />
          ))}

          {/* Center circle */}
          <circle
            data-testid="sunburst-center"
            cx={cx}
            cy={cy}
            r="55"
            fill="#111827"
            stroke="#374151"
            strokeWidth="2"
            className="cursor-pointer hover:fill-gray-800 transition-colors"
            onClick={handleCenterClick}
          />

          {/* Center text */}
          <text
            x={cx}
            y={cy - 10}
            textAnchor="middle"
            fill="white"
            fontSize="24"
            fontWeight="bold"
          >
            {displayNode.value}
          </text>
          <text
            x={cx}
            y={cy + 15}
            textAnchor="middle"
            fill="#9ca3af"
            fontSize="12"
          >
            {displayNode.name.length > 12 ? displayNode.name.substring(0, 12) + "..." : displayNode.name}
          </text>
        </svg>
      </div>

      {/* Legend */}
      <div className="flex justify-center gap-4 mt-4 text-xs">
        {Object.entries(SEVERITY_COLORS).map(([severity, color]) => (
          <div key={severity} className="flex items-center gap-1">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-gray-300 capitalize">{severity}</span>
          </div>
        ))}
      </div>

      {/* Stats */}
      <div className="flex justify-center gap-8 mt-4 pt-4 border-t border-gray-700">
        <div className="text-center">
          <div className="text-xl font-bold text-white">{data.total_cves}</div>
          <div className="text-xs text-gray-400">Total CVEs</div>
        </div>
        <div className="text-center">
          <div className="text-xl font-bold text-cyan-400">{data.total_cwes}</div>
          <div className="text-xs text-gray-400">CWE Categories</div>
        </div>
      </div>

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
          <div className="font-medium text-white">{tooltip.name}</div>
          {tooltip.cwe_id && (
            <div className="text-cyan-400">{tooltip.cwe_id}</div>
          )}
          <div className="text-gray-300">{tooltip.value} CVEs</div>
          {tooltip.severity_counts && (
            <div className="flex gap-2 mt-1 text-xs">
              <span className="text-red-400">{tooltip.severity_counts.critical} Crit</span>
              <span className="text-orange-400">{tooltip.severity_counts.high} High</span>
              <span className="text-yellow-400">{tooltip.severity_counts.medium} Med</span>
              <span className="text-green-400">{tooltip.severity_counts.low} Low</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
