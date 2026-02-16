/**
 * GlobalFilters - Filter bar for the Surface Command Center
 *
 * Provides global filtering controls: time range, asset type,
 * risk range, severity, status, and search.
 * Sits below the Layer Panel in the left sidebar.
 */

import { useState, useCallback } from "react";
import clsx from "clsx";

// ============================================================================
// Types
// ============================================================================

export interface GlobalFilterState {
  timeRange: string; // "1h" | "6h" | "12h" | "24h" | "7d" | "30d" | "custom"
  assetTypes: string[];
  riskMin: number;
  riskMax: number;
  severities: string[];
  statuses: string[];
  search: string;
}

export const DEFAULT_GLOBAL_FILTERS: GlobalFilterState = {
  timeRange: "24h",
  assetTypes: [],
  riskMin: 0,
  riskMax: 100,
  severities: [],
  statuses: [],
  search: "",
};

interface Props {
  filters: GlobalFilterState;
  onFilterChange: (filters: GlobalFilterState) => void;
}

// ============================================================================
// Constants
// ============================================================================

const TIME_RANGES = ["1h", "6h", "12h", "24h", "7d", "30d", "custom"] as const;

const ASSET_TYPES = [
  { id: "server", label: "Server" },
  { id: "workstation", label: "Workstation" },
  { id: "laptop", label: "Laptop" },
  { id: "vm", label: "VM" },
  { id: "container", label: "Container" },
  { id: "other", label: "Other" },
] as const;

const SEVERITIES = [
  { id: "critical", label: "Critical", color: "#dc2626" },
  { id: "high", label: "High", color: "#f97316" },
  { id: "medium", label: "Medium", color: "#eab308" },
  { id: "low", label: "Low", color: "#22c55e" },
  { id: "informational", label: "Info", color: "#6b7280" },
] as const;

const STATUSES = [
  { id: "open", label: "Open" },
  { id: "investigating", label: "Investigating" },
  { id: "contained", label: "Contained" },
  { id: "resolved", label: "Resolved" },
  { id: "closed", label: "Closed" },
] as const;

// ============================================================================
// Sub-components
// ============================================================================

/** Collapsible section with chevron toggle */
function FilterSection({
  title,
  children,
  defaultOpen = true,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-gray-700 last:border-b-0">
      <button
        onClick={() => setIsOpen((o) => !o)}
        className="w-full flex items-center justify-between px-3 py-2 text-xs font-medium text-gray-400 uppercase tracking-wider hover:text-gray-200 transition-colors"
      >
        <span>{title}</span>
        <svg
          className={clsx("w-3.5 h-3.5 transition-transform duration-200", isOpen && "rotate-180")}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      <div
        className={clsx(
          "overflow-hidden transition-all duration-200",
          isOpen ? "max-h-96 opacity-100 pb-3 px-3" : "max-h-0 opacity-0",
        )}
      >
        {children}
      </div>
    </div>
  );
}

/** Multi-select chip group */
function ChipGroup({
  options,
  selected,
  onToggle,
}: {
  options: readonly { id: string; label: string; color?: string }[];
  selected: string[];
  onToggle: (id: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {options.map((opt) => {
        const isActive = selected.includes(opt.id);
        return (
          <button
            key={opt.id}
            onClick={() => onToggle(opt.id)}
            className={clsx(
              "px-2 py-1 rounded text-[11px] font-medium transition-colors border",
              isActive
                ? "border-cyan-500/50 bg-cyan-900/30 text-cyan-300"
                : "border-gray-600 bg-gray-700/50 text-gray-400 hover:text-gray-200 hover:border-gray-500",
            )}
            style={
              isActive && opt.color
                ? {
                    borderColor: `${opt.color}60`,
                    backgroundColor: `${opt.color}20`,
                    color: opt.color,
                  }
                : undefined
            }
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function GlobalFilters({ filters, onFilterChange }: Props) {
  const update = useCallback(
    (partial: Partial<GlobalFilterState>) => {
      onFilterChange({ ...filters, ...partial });
    },
    [filters, onFilterChange],
  );

  const toggleArrayItem = useCallback(
    (key: "assetTypes" | "severities" | "statuses", id: string) => {
      const current = filters[key];
      const next = current.includes(id) ? current.filter((v) => v !== id) : [...current, id];
      update({ [key]: next });
    },
    [filters, update],
  );

  const activeCount =
    (filters.timeRange !== "24h" ? 1 : 0) +
    filters.assetTypes.length +
    (filters.riskMin > 0 || filters.riskMax < 100 ? 1 : 0) +
    filters.severities.length +
    filters.statuses.length +
    (filters.search.trim() ? 1 : 0);

  const handleReset = useCallback(() => {
    onFilterChange(DEFAULT_GLOBAL_FILTERS);
  }, [onFilterChange]);

  return (
    <div className="flex flex-col bg-gray-800 border-t border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <svg
            className="w-3.5 h-3.5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
            />
          </svg>
          <span className="text-xs font-medium text-gray-300">Filters</span>
          {activeCount > 0 && (
            <span className="px-1.5 py-0.5 bg-cyan-600 text-white text-[10px] rounded-full font-bold">
              {activeCount}
            </span>
          )}
        </div>
        {activeCount > 0 && (
          <button
            onClick={handleReset}
            className="text-[10px] text-gray-500 hover:text-cyan-400 transition-colors"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Filter sections */}
      <div className="overflow-y-auto max-h-[400px]">
        {/* Time Range */}
        <FilterSection title="Time Range">
          <div className="flex flex-wrap gap-1.5">
            {TIME_RANGES.map((tr) => (
              <button
                key={tr}
                onClick={() => update({ timeRange: tr })}
                className={clsx(
                  "px-2 py-1 rounded text-[11px] font-medium transition-colors border",
                  filters.timeRange === tr
                    ? "border-cyan-500/50 bg-cyan-900/30 text-cyan-300"
                    : "border-gray-600 bg-gray-700/50 text-gray-400 hover:text-gray-200 hover:border-gray-500",
                )}
              >
                {tr}
              </button>
            ))}
          </div>
        </FilterSection>

        {/* Asset Types */}
        <FilterSection title="Asset Type" defaultOpen={false}>
          <ChipGroup
            options={ASSET_TYPES}
            selected={filters.assetTypes}
            onToggle={(id) => toggleArrayItem("assetTypes", id)}
          />
        </FilterSection>

        {/* Risk Range */}
        <FilterSection title="Risk Range" defaultOpen={false}>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-[11px] text-gray-400">
              <span>Min: {filters.riskMin}</span>
              <span>Max: {filters.riskMax}</span>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="range"
                min={0}
                max={100}
                value={filters.riskMin}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  update({ riskMin: Math.min(val, filters.riskMax) });
                }}
                className="flex-1 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
              <input
                type="range"
                min={0}
                max={100}
                value={filters.riskMax}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  update({ riskMax: Math.max(val, filters.riskMin) });
                }}
                className="flex-1 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
            </div>
          </div>
        </FilterSection>

        {/* Severity */}
        <FilterSection title="Severity" defaultOpen={false}>
          <ChipGroup
            options={SEVERITIES}
            selected={filters.severities}
            onToggle={(id) => toggleArrayItem("severities", id)}
          />
        </FilterSection>

        {/* Status */}
        <FilterSection title="Status" defaultOpen={false}>
          <ChipGroup
            options={STATUSES}
            selected={filters.statuses}
            onToggle={(id) => toggleArrayItem("statuses", id)}
          />
        </FilterSection>
      </div>
    </div>
  );
}
