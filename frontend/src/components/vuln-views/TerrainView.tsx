/**
 * TerrainView Component
 *
 * 3D terrain visualization where:
 * - Height = CVSS score
 * - Color = severity level
 * - Fire animation on KEV CVEs
 */

import { useState, useMemo } from "react";
import type { TerrainViewData, VulnViewCommonProps } from "../../types/vulnerabilityViews";

// Severity color mapping
const SEVERITY_COLORS = {
  Critical: { bg: "#dc2626", glow: "rgba(220, 38, 38, 0.5)" },
  High: { bg: "#f97316", glow: "rgba(249, 115, 22, 0.5)" },
  Medium: { bg: "#eab308", glow: "rgba(234, 179, 8, 0.5)" },
  Low: { bg: "#22c55e", glow: "rgba(34, 197, 94, 0.5)" },
};

interface TerrainViewProps extends VulnViewCommonProps {
  data: TerrainViewData;
}

interface TooltipData {
  cve_id: string;
  cvss_score: number;
  epss_score: number;
  severity: string;
  is_kev: boolean;
  exploit_count: number;
  x: number;
  y: number;
}

export function TerrainView({
  data,
  className = "",
  onCVEClick,
  isLoading = false,
  error = null,
}: TerrainViewProps) {
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  // Calculate peak heights based on CVSS
  const peaks = useMemo(() => {
    return data.points.map((point) => ({
      ...point,
      heightPercent: (point.cvss_score / (data.max_cvss || 10)) * 100,
    }));
  }, [data.points, data.max_cvss]);

  // Handle peak click
  const handlePeakClick = (cveId: string) => {
    onCVEClick?.(cveId);
  };

  // Handle peak keyboard interaction
  const handlePeakKeyDown = (e: React.KeyboardEvent, cveId: string) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onCVEClick?.(cveId);
    }
  };

  // Handle mouse enter for tooltip
  const handleMouseEnter = (point: typeof data.points[0], event: React.MouseEvent) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltipPosition({
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
    });
    setTooltip({
      cve_id: point.cve_id,
      cvss_score: point.cvss_score,
      epss_score: point.epss_score,
      severity: point.severity,
      is_kev: point.is_kev,
      exploit_count: point.exploit_count,
      x: point.x,
      y: point.y,
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div
        data-testid="terrain-loading"
        className={`flex items-center justify-center h-96 bg-gray-900 rounded-lg ${className}`}
      >
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div
        className={`flex items-center justify-center h-96 bg-gray-900 rounded-lg ${className}`}
      >
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
  if (data.points.length === 0) {
    return (
      <div
        data-testid="terrain-view"
        className={`flex items-center justify-center h-96 bg-gray-900 rounded-lg ${className}`}
        aria-label="Vulnerability terrain visualization - no data"
      >
        <div className="text-center text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p>No vulnerability data available</p>
        </div>
      </div>
    );
  }

  const gridSize = data.grid_size || Math.ceil(Math.sqrt(data.points.length));
  const cellSize = 100 / gridSize;

  return (
    <div
      data-testid="terrain-view"
      className={`relative h-96 bg-gradient-to-b from-gray-900 to-gray-950 rounded-lg overflow-hidden ${className}`}
      aria-label="vulnerability terrain visualization showing CVE severity distribution"
      style={{ perspective: "1000px" }}
    >
      {/* 3D Terrain Grid */}
      <div
        className="absolute inset-0 transform-gpu"
        style={{
          transform: "rotateX(60deg) rotateZ(-45deg)",
          transformOrigin: "center center",
        }}
      >
        <div
          className="relative w-full h-full"
          style={{ transformStyle: "preserve-3d" }}
        >
          {/* Grid floor */}
          <div
            className="absolute inset-0 opacity-20"
            style={{
              background: `
                linear-gradient(90deg, rgba(100, 255, 218, 0.1) 1px, transparent 1px),
                linear-gradient(rgba(100, 255, 218, 0.1) 1px, transparent 1px)
              `,
              backgroundSize: `${cellSize}% ${cellSize}%`,
            }}
          />

          {/* Terrain peaks */}
          {peaks.map((point) => {
            const colors = SEVERITY_COLORS[point.severity as keyof typeof SEVERITY_COLORS] || SEVERITY_COLORS.Medium;
            const height = Math.max(10, point.heightPercent * 1.5);
            const left = (point.x / gridSize) * 100;
            const top = (point.y / gridSize) * 100;

            return (
              <div
                key={point.cve_id}
                data-testid={`terrain-peak-${point.cve_id}`}
                data-severity={point.severity}
                data-height={height}
                className="absolute cursor-pointer transition-all duration-300 hover:scale-110 focus:scale-110 focus:outline-none"
                style={{
                  left: `${left}%`,
                  top: `${top}%`,
                  width: `${cellSize * 0.8}%`,
                  height: `${height}px`,
                  transform: `translateZ(${height / 2}px)`,
                  transformStyle: "preserve-3d",
                }}
                tabIndex={0}
                role="button"
                aria-label={`CVE ${point.cve_id}, CVSS ${point.cvss_score}, ${point.severity} severity${point.is_kev ? ", Known Exploited" : ""}`}
                onClick={() => handlePeakClick(point.cve_id)}
                onKeyDown={(e) => handlePeakKeyDown(e, point.cve_id)}
                onMouseEnter={(e) => handleMouseEnter(point, e)}
                onMouseLeave={() => setTooltip(null)}
              >
                {/* Peak body */}
                <div
                  className="absolute inset-0 rounded-t-sm"
                  style={{
                    background: `linear-gradient(to top, ${colors.bg}80, ${colors.bg})`,
                    boxShadow: `0 0 ${height / 4}px ${colors.glow}`,
                  }}
                />

                {/* Peak glow */}
                <div
                  className="absolute -inset-1 rounded-t-sm opacity-50 blur-sm"
                  style={{ background: colors.glow }}
                />

                {/* KEV Fire indicator */}
                {point.is_kev && (
                  <div
                    data-fire
                    className="absolute -top-4 left-1/2 -translate-x-1/2 animate-pulse"
                  >
                    <svg
                      className="w-4 h-4 text-orange-500"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                )}
              </div>
            );
          })}
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
          <div className="font-mono text-cyan-400">{tooltip.cve_id}</div>
          <div className="text-gray-300">CVSS: {tooltip.cvss_score.toFixed(1)}</div>
          <div className="text-gray-300">EPSS: {(tooltip.epss_score * 100).toFixed(1)}%</div>
          <div className={`text-${tooltip.severity === "Critical" ? "red" : tooltip.severity === "High" ? "orange" : tooltip.severity === "Medium" ? "yellow" : "green"}-400`}>
            {tooltip.severity}
          </div>
          {tooltip.is_kev && (
            <div className="text-orange-400 flex items-center gap-1">
              <span>KEV</span>
            </div>
          )}
          {tooltip.exploit_count > 0 && (
            <div className="text-purple-400">{tooltip.exploit_count} exploits</div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-gray-900/80 backdrop-blur-sm rounded-lg p-3 border border-gray-700">
        <div className="text-xs text-gray-400 mb-2">Severity</div>
        <div className="flex gap-3">
          {Object.entries(SEVERITY_COLORS).map(([severity, colors]) => (
            <div key={severity} className="flex items-center gap-1">
              <div
                className="w-3 h-3 rounded-sm"
                style={{ background: colors.bg }}
              />
              <span className="text-xs text-gray-300">{severity}</span>
            </div>
          ))}
        </div>
        <div className="mt-2 flex items-center gap-1 text-xs text-orange-400">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z"
              clipRule="evenodd"
            />
          </svg>
          <span>KEV</span>
        </div>
      </div>

      {/* Stats */}
      <div className="absolute top-4 left-4 bg-gray-900/80 backdrop-blur-sm rounded-lg p-3 border border-gray-700">
        <div className="text-2xl font-bold text-white">{data.total_cves}</div>
        <div className="text-xs text-gray-400">Total CVEs</div>
      </div>
    </div>
  );
}
