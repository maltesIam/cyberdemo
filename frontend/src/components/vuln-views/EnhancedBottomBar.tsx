/**
 * EnhancedBottomBar Component
 *
 * Features:
 * - Animated count-up for KPIs
 * - Segmented remediation progress bar
 * - Time range selector (7d, 30d, 90d, All, Custom)
 * - WOW effects and animations
 */

import { useState, useEffect, useCallback, useRef } from "react";
import clsx from "clsx";

// ============================================================================
// Types
// ============================================================================

export interface BottomBarStats {
  total_cves: number;
  remediated_count: number;
  in_progress_count: number;
  open_count: number;
  critical_count: number;
  kev_count: number;
  exploitable_count: number;
  mttr_days: number;
  sla_compliance_percent: number;
}

export type TimeRange = "7d" | "30d" | "90d" | "all" | "custom";

interface EnhancedBottomBarProps {
  stats: BottomBarStats;
  selectedTimeRange: TimeRange;
  onTimeRangeChange: (range: TimeRange) => void;
  onRefresh: () => void;
  onEnrich: () => void;
  isLoading?: boolean;
  className?: string;
}

// ============================================================================
// Animated Counter Hook
// ============================================================================

function useAnimatedCounter(targetValue: number, duration: number = 1000): { value: number; isAnimating: boolean } {
  const [value, setValue] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);
  const startTimeRef = useRef<number | null>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    startTimeRef.current = null;
    setIsAnimating(true);

    const animate = (timestamp: number) => {
      if (!startTimeRef.current) {
        startTimeRef.current = timestamp;
      }

      const elapsed = timestamp - startTimeRef.current;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function (ease-out)
      const easedProgress = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(targetValue * easedProgress));

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        setIsAnimating(false);
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [targetValue, duration]);

  return { value, isAnimating };
}

// ============================================================================
// Component
// ============================================================================

export function EnhancedBottomBar({
  stats,
  selectedTimeRange,
  onTimeRangeChange,
  onRefresh,
  onEnrich,
  isLoading = false,
  className = "",
}: EnhancedBottomBarProps) {
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [hoveredSegment, setHoveredSegment] = useState<string | null>(null);

  // Animated counters
  const totalCounter = useAnimatedCounter(stats.total_cves);
  const criticalCounter = useAnimatedCounter(stats.critical_count);
  const kevCounter = useAnimatedCounter(stats.kev_count);

  // Calculate progress percentages
  const total = stats.total_cves || 1;
  const remediatedPercent = (stats.remediated_count / total) * 100;
  const inProgressPercent = (stats.in_progress_count / total) * 100;
  const openPercent = (stats.open_count / total) * 100;

  // Handle time range click
  const handleTimeRangeClick = useCallback(
    (range: TimeRange) => {
      if (range === "custom") {
        setShowDatePicker(true);
      } else {
        onTimeRangeChange(range);
        setShowDatePicker(false);
      }
    },
    [onTimeRangeChange]
  );

  // Handle date picker apply
  const handleDatePickerApply = useCallback(() => {
    onTimeRangeChange("custom");
    setShowDatePicker(false);
  }, [onTimeRangeChange]);

  return (
    <div
      data-testid="enhanced-bottom-bar"
      className={clsx(
        "bg-gray-800 rounded-lg px-4 py-3 transition-all duration-300 glow-subtle",
        className
      )}
    >
      <div className="flex items-center justify-between gap-4">
        {/* KPIs */}
        <div
          data-testid="kpi-container"
          className="flex items-center gap-4 flex-wrap"
        >
          {/* Total CVEs */}
          <div
            data-testid="kpi-total"
            aria-label="Total CVEs"
            className="flex flex-col items-center"
          >
            <span
              data-testid="kpi-total-value"
              data-animating={totalCounter.isAnimating.toString()}
              className="text-xl font-bold text-cyan-400"
            >
              {totalCounter.value}
            </span>
            <span className="text-xs text-gray-400">Total</span>
          </div>

          {/* Critical */}
          <div
            data-testid="kpi-critical"
            aria-label="Critical CVEs"
            className="flex flex-col items-center animate-pulse-critical"
          >
            <span className="text-xl font-bold text-red-500">
              {criticalCounter.value}
            </span>
            <span className="text-xs text-gray-400">Critical</span>
          </div>

          {/* KEV */}
          <div
            data-testid="kpi-kev"
            aria-label="KEV CVEs"
            className="flex flex-col items-center animate-fire"
          >
            <span className="text-xl font-bold text-orange-500">
              {kevCounter.value}
            </span>
            <span className="text-xs text-gray-400">KEV</span>
          </div>

          {/* MTTR */}
          <div
            data-testid="kpi-mttr"
            aria-label="Mean Time to Remediate"
            className="flex flex-col items-center hidden sm:flex"
          >
            <span className="text-xl font-bold text-blue-400">
              {stats.mttr_days.toFixed(1)}d
            </span>
            <span className="text-xs text-gray-400">MTTR</span>
          </div>

          {/* SLA */}
          <div
            data-testid="kpi-sla"
            aria-label="SLA Compliance"
            className={clsx(
              "flex flex-col items-center hidden sm:flex",
              stats.sla_compliance_percent >= 85 ? "text-green-400" : "text-red-400"
            )}
          >
            <span className="text-xl font-bold">
              {stats.sla_compliance_percent.toFixed(1)}%
            </span>
            <span className="text-xs text-gray-400">SLA</span>
          </div>
        </div>

        {/* Remediation Progress Bar */}
        <div className="flex-1 max-w-xs">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-gray-400">Remediation</span>
          </div>
          <div
            data-testid="remediation-progress"
            role="progressbar"
            aria-valuenow={remediatedPercent}
            aria-valuemin={0}
            aria-valuemax={100}
            className="h-3 bg-gray-700 rounded-full overflow-hidden flex animate-progress-fill"
          >
            {/* Remediated Segment */}
            <div
              data-testid="segment-remediated"
              className="bg-green-500 h-full transition-all duration-500 relative"
              style={{ width: `${remediatedPercent}%` }}
              onMouseEnter={() => setHoveredSegment("remediated")}
              onMouseLeave={() => setHoveredSegment(null)}
            />
            {/* In Progress Segment */}
            <div
              data-testid="segment-in-progress"
              className="bg-blue-500 h-full transition-all duration-500"
              style={{ width: `${inProgressPercent}%` }}
              onMouseEnter={() => setHoveredSegment("in_progress")}
              onMouseLeave={() => setHoveredSegment(null)}
            />
            {/* Open Segment */}
            <div
              data-testid="segment-open"
              className="bg-gray-600 h-full transition-all duration-500"
              style={{ width: `${openPercent}%` }}
              onMouseEnter={() => setHoveredSegment("open")}
              onMouseLeave={() => setHoveredSegment(null)}
            />
          </div>

          {/* Legend */}
          <div data-testid="progress-legend" className="flex items-center gap-3 mt-1 text-xs">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-gray-400">{stats.remediated_count}</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              <span className="text-gray-400">{stats.in_progress_count}</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-gray-600" />
              <span className="text-gray-400">{stats.open_count}</span>
            </span>
          </div>

          {/* Tooltip */}
          {hoveredSegment && (
            <div role="tooltip" className="absolute -mt-8 bg-gray-900 text-white text-xs px-2 py-1 rounded shadow-lg">
              {hoveredSegment === "remediated" && `Remediated: ${stats.remediated_count}`}
              {hoveredSegment === "in_progress" && `In Progress: ${stats.in_progress_count}`}
              {hoveredSegment === "open" && `Open: ${stats.open_count}`}
            </div>
          )}
        </div>

        {/* Time Range Selector */}
        <div data-testid="time-range-selector" className="flex items-center gap-1 relative">
          {(["7d", "30d", "90d", "all", "custom"] as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => handleTimeRangeClick(range)}
              aria-label={range === "all" ? "All time" : range === "custom" ? "Custom range" : `Last ${range}`}
              className={clsx(
                "px-3 py-1.5 text-xs font-medium rounded transition-colors",
                selectedTimeRange === range
                  ? "bg-cyan-600 text-white"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              )}
            >
              {range === "all" ? "All" : range === "custom" ? "Custom" : range}
            </button>
          ))}

          {/* Date Range Picker */}
          {showDatePicker && (
            <div
              data-testid="date-range-picker"
              className="absolute bottom-full right-0 mb-2 p-4 bg-gray-900 rounded-lg shadow-xl border border-gray-700 z-10"
            >
              <div className="flex gap-4 mb-4">
                <div>
                  <label className="block text-xs text-gray-400 mb-1">From</label>
                  <input
                    type="date"
                    className="px-2 py-1 bg-gray-800 border border-gray-600 rounded text-white text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-1">To</label>
                  <input
                    type="date"
                    className="px-2 py-1 bg-gray-800 border border-gray-600 rounded text-white text-sm"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowDatePicker(false)}
                  className="px-3 py-1 text-xs text-gray-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDatePickerApply}
                  aria-label="Apply date range"
                  className="px-3 py-1 text-xs bg-cyan-600 text-white rounded hover:bg-cyan-700"
                >
                  Apply
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={onRefresh}
            aria-label="Refresh"
            className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <svg
              className={clsx("w-4 h-4", isLoading && "animate-spin")}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            <span className="hidden sm:inline text-sm">Refresh</span>
          </button>

          <button
            onClick={onEnrich}
            aria-label="Enrich vulnerabilities"
            className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
            <span className="hidden sm:inline text-sm">Enrich</span>
          </button>
        </div>
      </div>
    </div>
  );
}
