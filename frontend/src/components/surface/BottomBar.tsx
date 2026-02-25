/**
 * BottomBar - Enhanced bottom bar with KPIs, timeline slider, and replay controls
 *
 * Features:
 * - 7 clickable KPI chips with count-up animation and blink effect
 * - Timeline range slider from 1h to 30d
 * - Time range preset chips
 * - Play/Pause replay button
 * - Speed control selector (1x, 2x, 5x, 10x)
 */

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import clsx from "clsx";

// ============================================================================
// Types
// ============================================================================

export interface TimeRangeState {
  preset: string; // "1h" | "6h" | "24h" | "7d" | "30d" | "custom"
  from?: Date;
  to?: Date;
  isPlaying: boolean;
  speed: number; // 1, 2, 5, 10
}

export const DEFAULT_TIME_RANGE: TimeRangeState = {
  preset: "24h",
  isPlaying: false,
  speed: 1,
};

interface Props {
  overview: any;
  onKpiClick: (kpiType: string) => void;
  timeRange: TimeRangeState;
  onTimeRangeChange: (range: TimeRangeState) => void;
}

// ============================================================================
// Constants
// ============================================================================

interface KpiDef {
  key: string;
  label: string;
  color: string;
  icon: JSX.Element;
}

const KPI_DEFS: KpiDef[] = [
  {
    key: "assets",
    label: "Assets",
    color: "#06b6d4",
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
        />
      </svg>
    ),
  },
  {
    key: "detections",
    label: "Detections",
    color: "#ef4444",
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
    ),
  },
  {
    key: "incidents",
    label: "Incidents",
    color: "#f97316",
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13 10V3L4 14h7v7l9-11h-7z"
        />
      </svg>
    ),
  },
  {
    key: "critical",
    label: "Critical",
    color: "#dc2626",
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01M5.07 19H19a2 2 0 001.75-2.96l-6.93-12a2 2 0 00-3.5 0l-6.93 12A2 2 0 005.07 19z"
        />
      </svg>
    ),
  },
  {
    key: "kevs",
    label: "CVE-K",
    color: "#eab308",
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  },
  {
    key: "iocs",
    label: "IOC",
    color: "#a855f7",
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  },
  {
    key: "contained",
    label: "Contained",
    color: "#3b82f6",
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
        />
      </svg>
    ),
  },
];

const TIME_PRESETS = ["1h", "6h", "24h", "7d", "30d"] as const;
const SPEEDS = [1, 2, 5, 10] as const;

// ============================================================================
// Sub-components
// ============================================================================

/** KPI chip with count-up animation and blink on change */
function KPIChipEnhanced({
  def,
  value,
  isActive,
  onClick,
}: {
  def: KpiDef;
  value: number;
  isActive: boolean;
  onClick: () => void;
}) {
  const [displayed, setDisplayed] = useState(0);
  const [blink, setBlink] = useState(false);
  const prevValueRef = useRef(value);
  const animatedRef = useRef(false);

  // Count-up animation on mount
  useEffect(() => {
    if (animatedRef.current) {
      // Value changed after initial animation - trigger blink
      if (value !== prevValueRef.current) {
        setBlink(true);
        const timer = setTimeout(() => setBlink(false), 600);
        prevValueRef.current = value;
        setDisplayed(value);
        return () => clearTimeout(timer);
      }
      return;
    }

    if (value === 0) {
      setDisplayed(0);
      animatedRef.current = true;
      return;
    }

    animatedRef.current = true;
    const duration = 600;
    const steps = 20;
    const increment = value / steps;
    let step = 0;
    const timer = setInterval(() => {
      step++;
      setDisplayed(Math.min(Math.round(increment * step), value));
      if (step >= steps) {
        clearInterval(timer);
        setDisplayed(value);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value]);

  return (
    <button
      onClick={onClick}
      className={clsx(
        "flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs transition-all duration-200 flex-shrink-0",
        isActive && "ring-1 ring-offset-1 ring-offset-gray-800",
        blink && "animate-pulse",
      )}
      style={{
        backgroundColor: isActive ? `${def.color}25` : `${def.color}10`,
        borderColor: isActive ? def.color : `${def.color}30`,
        ...(isActive ? { ringColor: def.color } : {}),
      }}
    >
      <span style={{ color: def.color }}>{def.icon}</span>
      <span className="font-bold tabular-nums" style={{ color: def.color }}>
        {displayed.toLocaleString()}
      </span>
      <span className="text-secondary text-[10px] hidden sm:inline">{def.label}</span>
    </button>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function BottomBar({ overview, onKpiClick, timeRange, onTimeRangeChange }: Props) {
  const [activeKpi, setActiveKpi] = useState<string | null>(null);

  // Extract KPI values safely from overview
  const kpiValues = useMemo(() => {
    const o = overview ?? {};
    return {
      assets: o?.total_assets ?? o?.assets ?? 0,
      detections: o?.total_detections ?? o?.detections ?? 0,
      incidents: o?.total_incidents ?? o?.incidents ?? 0,
      critical: o?.critical_assets ?? o?.critical ?? 0,
      kevs: o?.kev_count ?? o?.kevs ?? 0,
      iocs: o?.ioc_count ?? o?.iocs ?? 0,
      contained: o?.contained_count ?? o?.contained ?? 0,
    } as Record<string, number>;
  }, [overview]);

  const handleKpiClick = useCallback(
    (key: string) => {
      const newActive = activeKpi === key ? null : key;
      setActiveKpi(newActive);
      onKpiClick(newActive ?? "");
    },
    [activeKpi, onKpiClick],
  );

  const updateTimeRange = useCallback(
    (partial: Partial<TimeRangeState>) => {
      onTimeRangeChange({ ...timeRange, ...partial });
    },
    [timeRange, onTimeRangeChange],
  );

  const togglePlay = useCallback(() => {
    updateTimeRange({ isPlaying: !timeRange.isPlaying });
  }, [timeRange.isPlaying, updateTimeRange]);

  const cycleSpeed = useCallback(() => {
    const currentIdx = SPEEDS.indexOf(timeRange.speed as (typeof SPEEDS)[number]);
    const nextIdx = (currentIdx + 1) % SPEEDS.length;
    updateTimeRange({ speed: SPEEDS[nextIdx] ?? 1 });
  }, [timeRange.speed, updateTimeRange]);

  // Map slider position (0-100) to time range labels
  const sliderMarks = [
    { pos: 0, label: "1h" },
    { pos: 20, label: "6h" },
    { pos: 40, label: "12h" },
    { pos: 60, label: "24h" },
    { pos: 80, label: "7d" },
    { pos: 100, label: "30d" },
  ];

  const presetToSlider: Record<string, number> = {
    "1h": 0,
    "6h": 20,
    "12h": 40,
    "24h": 60,
    "7d": 80,
    "30d": 100,
  };

  const sliderToPreset = (val: number): string => {
    // Snap to nearest mark
    let closest = sliderMarks[0]!;
    for (const mark of sliderMarks) {
      if (Math.abs(val - mark.pos) < Math.abs(val - closest.pos)) {
        closest = mark;
      }
    }
    return closest.label;
  };

  const sliderValue = presetToSlider[timeRange.preset] ?? 60;

  return (
    <footer className="flex-shrink-0 bg-secondary border-t border-primary">
      {/* Main row: KPIs + Timeline controls */}
      <div className="flex items-center gap-2 px-3 py-2">
        {/* KPI chips section */}
        <div className="flex items-center gap-1.5 overflow-x-auto flex-shrink-0 pr-3 border-r border-primary">
          {KPI_DEFS.map((def) => (
            <KPIChipEnhanced
              key={def.key}
              def={def}
              value={kpiValues[def.key] ?? 0}
              isActive={activeKpi === def.key}
              onClick={() => handleKpiClick(def.key)}
            />
          ))}
        </div>

        {/* Timeline controls */}
        <div className="flex items-center gap-2 flex-1 min-w-0 pl-2">
          {/* Play/Pause */}
          <button
            onClick={togglePlay}
            className={clsx(
              "p-1.5 rounded-md transition-colors flex-shrink-0",
              timeRange.isPlaying
                ? "bg-cyan-600 text-primary"
                : "bg-tertiary text-secondary hover:text-primary",
            )}
            title={timeRange.isPlaying ? "Pause replay" : "Play replay"}
          >
            {timeRange.isPlaying ? (
              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
              </svg>
            ) : (
              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>

          {/* Speed control */}
          <button
            onClick={cycleSpeed}
            className="px-1.5 py-1 bg-tertiary rounded text-[10px] font-mono text-secondary hover:bg-tertiary transition-colors flex-shrink-0"
            title="Change playback speed"
          >
            {timeRange.speed}x
          </button>

          {/* Timeline slider */}
          <div className="flex-1 min-w-[120px] relative px-1">
            <input
              type="range"
              min={0}
              max={100}
              step={1}
              value={sliderValue}
              onChange={(e) => {
                const preset = sliderToPreset(Number(e.target.value));
                updateTimeRange({ preset });
              }}
              className="w-full h-1 bg-tertiary rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            {/* Marks below slider */}
            <div className="relative h-3 mt-0.5">
              {sliderMarks.map((mark) => (
                <span
                  key={mark.label}
                  className={clsx(
                    "absolute text-[8px] -translate-x-1/2 transition-colors",
                    timeRange.preset === mark.label ? "text-cyan-400 font-bold" : "text-tertiary",
                  )}
                  style={{ left: `${mark.pos}%` }}
                >
                  {mark.label}
                </span>
              ))}
            </div>
          </div>

          {/* Time range preset chips */}
          <div className="flex items-center gap-1 flex-shrink-0">
            {TIME_PRESETS.map((preset) => (
              <button
                key={preset}
                onClick={() => updateTimeRange({ preset })}
                className={clsx(
                  "px-2 py-0.5 rounded text-[10px] font-medium transition-colors",
                  timeRange.preset === preset
                    ? "bg-cyan-600 text-primary"
                    : "bg-tertiary text-secondary hover:text-primary",
                )}
              >
                {preset}
              </button>
            ))}
            <button
              onClick={() => updateTimeRange({ preset: "custom" })}
              className={clsx(
                "px-2 py-0.5 rounded text-[10px] font-medium transition-colors",
                timeRange.preset === "custom"
                  ? "bg-cyan-600 text-primary"
                  : "bg-tertiary text-secondary hover:text-primary",
              )}
            >
              Custom
            </button>
          </div>

          {/* Current time indicator */}
          <div className="flex-shrink-0 text-[10px] text-tertiary font-mono pl-2 border-l border-primary">
            {new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </div>
        </div>
      </div>
    </footer>
  );
}
