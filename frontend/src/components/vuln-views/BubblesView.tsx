/**
 * BubblesView Component
 *
 * Animated bubbles visualization where:
 * - Size = risk score
 * - Color = severity level
 * - With SSVC decision indicators and KEV markers
 */

import { useState, useEffect, useMemo, useRef } from "react";
import type { BubblesViewData, BubbleData, VulnViewCommonProps } from "../../types/vulnerabilityViews";

// Severity color mapping
const SEVERITY_COLORS = {
  Critical: "#dc2626",
  High: "#f97316",
  Medium: "#eab308",
  Low: "#22c55e",
};

// SSVC decision colors
const SSVC_COLORS = {
  Act: "#dc2626",
  Attend: "#f97316",
  "Track*": "#eab308",
  Track: "#22c55e",
};

interface BubblesViewProps extends VulnViewCommonProps {
  data: BubblesViewData;
  filterSSVC?: string[];
  filterSeverity?: string[];
}

interface TooltipData {
  cve_id: string;
  risk_score: number;
  cvss_score: number;
  epss_score: number;
  severity: string;
  is_kev: boolean;
  ssvc_decision: string;
  title: string;
  affected_asset_count: number;
}

interface BubblePosition extends BubbleData {
  x: number;
  y: number;
  radius: number;
  vx: number;
  vy: number;
}

export function BubblesView({
  data,
  className = "",
  onCVEClick,
  isLoading = false,
  error = null,
  filterSSVC,
  filterSeverity,
}: BubblesViewProps) {
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const [highlightedCVE, setHighlightedCVE] = useState<string | null>(null);
  const [positions, setPositions] = useState<BubblePosition[]>([]);
  const svgRef = useRef<SVGSVGElement>(null);
  const animationRef = useRef<number>();

  const width = 600;
  const height = 400;

  // Filter bubbles based on props
  const filteredBubbles = useMemo(() => {
    return data.bubbles.filter((bubble) => {
      if (filterSSVC && filterSSVC.length > 0 && !filterSSVC.includes(bubble.ssvc_decision)) {
        return false;
      }
      if (filterSeverity && filterSeverity.length > 0 && !filterSeverity.includes(bubble.severity)) {
        return false;
      }
      return true;
    });
  }, [data.bubbles, filterSSVC, filterSeverity]);

  // Calculate bubble radius from risk score
  const getRadius = (riskScore: number): number => {
    const minRadius = 15;
    const maxRadius = 50;
    return minRadius + (riskScore / 100) * (maxRadius - minRadius);
  };

  // Initialize positions with simple force simulation
  useEffect(() => {
    if (filteredBubbles.length === 0) return;

    // Initialize positions
    const initialPositions: BubblePosition[] = filteredBubbles.map((bubble) => ({
      ...bubble,
      x: width / 2 + (Math.random() - 0.5) * 200,
      y: height / 2 + (Math.random() - 0.5) * 200,
      radius: getRadius(bubble.risk_score),
      vx: (Math.random() - 0.5) * 2,
      vy: (Math.random() - 0.5) * 2,
    }));

    setPositions(initialPositions);

    // Simple force simulation
    let frame = 0;
    const maxFrames = 100;

    const simulate = () => {
      if (frame >= maxFrames) return;

      setPositions((prev) => {
        const next = prev.map((bubble) => {
          let { x, y, vx, vy, radius } = bubble;

          // Gravity towards center
          const centerX = width / 2;
          const centerY = height / 2;
          const dx = centerX - x;
          const dy = centerY - y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          vx += (dx / dist) * 0.1;
          vy += (dy / dist) * 0.1;

          // Damping
          vx *= 0.95;
          vy *= 0.95;

          // Update position
          x += vx;
          y += vy;

          // Bounds
          x = Math.max(radius, Math.min(width - radius, x));
          y = Math.max(radius, Math.min(height - radius, y));

          return { ...bubble, x, y, vx, vy };
        });

        // Collision detection
        for (let i = 0; i < next.length; i++) {
          for (let j = i + 1; j < next.length; j++) {
            const a = next[i];
            const b = next[j];
            const dx = b.x - a.x;
            const dy = b.y - a.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const minDist = a.radius + b.radius + 2;

            if (dist < minDist) {
              const overlap = minDist - dist;
              const nx = dx / dist;
              const ny = dy / dist;

              a.x -= nx * overlap * 0.5;
              a.y -= ny * overlap * 0.5;
              b.x += nx * overlap * 0.5;
              b.y += ny * overlap * 0.5;
            }
          }
        }

        return next;
      });

      frame++;
      animationRef.current = requestAnimationFrame(simulate);
    };

    animationRef.current = requestAnimationFrame(simulate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [filteredBubbles, width, height]);

  // Handle bubble click
  const handleBubbleClick = (cveId: string) => {
    onCVEClick?.(cveId);
  };

  // Handle keyboard interaction
  const handleKeyDown = (e: React.KeyboardEvent, cveId: string) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onCVEClick?.(cveId);
    }
  };

  // Handle mouse enter for tooltip
  const handleMouseEnter = (bubble: BubbleData, event: React.MouseEvent) => {
    setHighlightedCVE(bubble.cve_id);
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltipPosition({
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
    });
    setTooltip({
      cve_id: bubble.cve_id,
      risk_score: bubble.risk_score,
      cvss_score: bubble.cvss_score,
      epss_score: bubble.epss_score,
      severity: bubble.severity,
      is_kev: bubble.is_kev,
      ssvc_decision: bubble.ssvc_decision,
      title: bubble.title,
      affected_asset_count: bubble.affected_asset_count,
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div
        data-testid="bubbles-loading"
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
  if (data.bubbles.length === 0) {
    return (
      <div
        data-testid="bubbles-view"
        className={`flex items-center justify-center h-96 bg-gray-900 rounded-lg ${className}`}
        aria-label="Bubbles visualization - no data"
      >
        <div className="text-center text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 10a1 1 0 11-2 0 1 1 0 012 0zm8 0a1 1 0 11-2 0 1 1 0 012 0z" />
          </svg>
          <p>No vulnerability data available</p>
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="bubbles-view"
      className={`bg-gray-900 rounded-lg p-4 ${className}`}
      aria-label="vulnerability bubbles visualization showing CVE risk distribution"
    >
      {/* SVG Canvas */}
      <svg
        ref={svgRef}
        data-testid="bubbles-svg"
        width="100%"
        height="400"
        viewBox={`0 0 ${width} ${height}`}
        className="overflow-visible"
      >
        {/* Background gradient */}
        <defs>
          <radialGradient id="bubbleGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(0,255,255,0.3)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0)" />
          </radialGradient>
        </defs>

        {/* Bubbles */}
        {positions.map((bubble) => {
          const isHidden = (filterSSVC && filterSSVC.length > 0 && !filterSSVC.includes(bubble.ssvc_decision)) ||
            (filterSeverity && filterSeverity.length > 0 && !filterSeverity.includes(bubble.severity));
          const isHighlighted = highlightedCVE === bubble.cve_id;

          return (
            <g
              key={bubble.cve_id}
              className={isHidden ? "hidden" : ""}
              style={{ opacity: isHidden ? 0 : 1 }}
            >
              {/* Outer glow for highlighted */}
              {isHighlighted && (
                <circle
                  cx={bubble.x}
                  cy={bubble.y}
                  r={bubble.radius + 5}
                  fill="none"
                  stroke={SEVERITY_COLORS[bubble.severity]}
                  strokeWidth="2"
                  opacity="0.5"
                />
              )}

              {/* Main bubble */}
              <circle
                data-testid={`bubble-${bubble.cve_id}`}
                data-severity={bubble.severity}
                data-ssvc={bubble.ssvc_decision}
                data-highlighted={isHighlighted.toString()}
                cx={bubble.x}
                cy={bubble.y}
                r={bubble.radius}
                fill={SEVERITY_COLORS[bubble.severity]}
                opacity={isHighlighted ? 1 : 0.75}
                stroke={isHighlighted ? "white" : "none"}
                strokeWidth={isHighlighted ? 2 : 0}
                className="cursor-pointer transition-all duration-200 hover:opacity-100"
                tabIndex={0}
                role="button"
                aria-label={`${bubble.cve_id}, Risk ${bubble.risk_score}, ${bubble.severity}`}
                onClick={() => handleBubbleClick(bubble.cve_id)}
                onKeyDown={(e) => handleKeyDown(e, bubble.cve_id)}
                onMouseEnter={(e) => handleMouseEnter(bubble, e)}
                onMouseLeave={() => {
                  setHighlightedCVE(null);
                  setTooltip(null);
                }}
              />

              {/* KEV indicator */}
              {bubble.is_kev && (
                <g data-kev transform={`translate(${bubble.x + bubble.radius * 0.6}, ${bubble.y - bubble.radius * 0.6})`}>
                  <circle r="8" fill="#f97316" stroke="white" strokeWidth="1" />
                  <text
                    textAnchor="middle"
                    dominantBaseline="central"
                    fill="white"
                    fontSize="8"
                    fontWeight="bold"
                  >
                    K
                  </text>
                </g>
              )}

              {/* CVE ID label (for larger bubbles) */}
              {bubble.radius > 30 && (
                <text
                  x={bubble.x}
                  y={bubble.y}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fill="white"
                  fontSize="10"
                  fontWeight="medium"
                  className="pointer-events-none"
                >
                  {bubble.cve_id.replace("CVE-", "")}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div data-testid="bubbles-legend" className="flex flex-wrap justify-center gap-4 mt-4 text-xs">
        <div className="flex items-center gap-4">
          <span className="text-gray-400">Severity:</span>
          {Object.entries(SEVERITY_COLORS).map(([severity, color]) => (
            <div key={severity} className="flex items-center gap-1">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: color }}
              />
              <span className="text-gray-300">
                {severity} ({data.severity_distribution[severity.toLowerCase() as keyof typeof data.severity_distribution] || 0})
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* SSVC Legend */}
      <div className="flex justify-center gap-4 mt-2 text-xs">
        <span className="text-gray-400">SSVC:</span>
        {Object.entries(SSVC_COLORS).map(([decision, color]) => (
          <div key={decision} className="flex items-center gap-1">
            <div
              className="w-2 h-2 rounded-full border-2"
              style={{ borderColor: color }}
            />
            <span className="text-gray-300">{decision}</span>
          </div>
        ))}
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div
          role="tooltip"
          className="fixed z-50 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl text-sm pointer-events-none max-w-xs"
          style={{
            left: `${tooltipPosition.x}px`,
            top: `${tooltipPosition.y}px`,
            transform: "translate(-50%, -100%)",
          }}
        >
          <div className="font-mono text-cyan-400">{tooltip.cve_id}</div>
          <div className="text-gray-300 truncate">{tooltip.title}</div>
          <div className="flex gap-3 mt-1">
            <span className="text-red-400">Risk: {tooltip.risk_score}</span>
            <span className="text-orange-400">CVSS: {tooltip.cvss_score}</span>
          </div>
          <div className="flex gap-3">
            <span className="text-purple-400">EPSS: {(tooltip.epss_score * 100).toFixed(1)}%</span>
            <span className="text-blue-400">{tooltip.affected_asset_count} assets</span>
          </div>
          <div className="flex gap-2 mt-1">
            <span
              className="px-1.5 py-0.5 rounded text-xs"
              style={{ backgroundColor: SEVERITY_COLORS[tooltip.severity as keyof typeof SEVERITY_COLORS] + "40" }}
            >
              {tooltip.severity}
            </span>
            <span
              className="px-1.5 py-0.5 rounded text-xs"
              style={{ backgroundColor: SSVC_COLORS[tooltip.ssvc_decision as keyof typeof SSVC_COLORS] + "40" }}
            >
              {tooltip.ssvc_decision}
            </span>
            {tooltip.is_kev && (
              <span className="px-1.5 py-0.5 rounded text-xs bg-orange-600/40">KEV</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
