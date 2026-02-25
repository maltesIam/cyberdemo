/**
 * RiskPanel Component - Left Sidebar Filter Panel
 *
 * Features:
 * - SSVC Filter checkboxes with counts and glow effects
 * - Quick Filters (KEV, Exploitable, etc.) with fire animation
 * - Severity filters with counts and pulse animation
 * - Product/Vendor search
 * - Ecosystem checkboxes
 * - CWE Category checkboxes
 * - Filter presets dropdown
 */

import { useState, useCallback } from "react";
import clsx from "clsx";

// ============================================================================
// Types
// ============================================================================

export interface FilterCounts {
  ssvc: {
    act: number;
    attend: number;
    trackStar: number;
    track: number;
  };
  severity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  quickFilters: {
    kevOnly: number;
    exploitable: number;
    hasPublicExploit: number;
    patchOverdue: number;
  };
  ecosystems: {
    npm: number;
    pip: number;
    maven: number;
    go: number;
  };
  cweCategories: {
    injection: number;
    xss: number;
    auth: number;
    crypto: number;
    config: number;
  };
}

export interface RiskFilters {
  ssvc: string[];
  severity: string[];
  quickFilters: string[];
  ecosystems: string[];
  cweCategories: string[];
  productSearch: string;
}

interface RiskPanelProps {
  filterCounts: FilterCounts;
  filters: RiskFilters;
  onFilterChange: (filters: RiskFilters) => void;
  className?: string;
}

// ============================================================================
// Filter Presets
// ============================================================================

const FILTER_PRESETS = [
  {
    name: "Urgent Triage",
    filters: {
      ssvc: ["Act"],
      severity: ["Critical"],
      quickFilters: ["kevOnly"],
      ecosystems: [],
      cweCategories: [],
      productSearch: "",
    },
  },
  {
    name: "Patch Tuesday",
    filters: {
      ssvc: ["Act", "Attend"],
      severity: ["Critical", "High"],
      quickFilters: ["patchOverdue"],
      ecosystems: [],
      cweCategories: [],
      productSearch: "",
    },
  },
  {
    name: "Open Source Risk",
    filters: {
      ssvc: [],
      severity: [],
      quickFilters: ["exploitable"],
      ecosystems: ["npm", "pip", "maven", "go"],
      cweCategories: [],
      productSearch: "",
    },
  },
  {
    name: "Zero-Day Focus",
    filters: {
      ssvc: ["Act"],
      severity: ["Critical", "High"],
      quickFilters: ["hasPublicExploit"],
      ecosystems: [],
      cweCategories: [],
      productSearch: "",
    },
  },
];

// ============================================================================
// Component
// ============================================================================

export function RiskPanel({
  filterCounts,
  filters,
  onFilterChange,
  className = "",
}: RiskPanelProps) {
  const [collapsedSections, setCollapsedSections] = useState<Record<string, boolean>>({});
  const [presetsOpen, setPresetsOpen] = useState(false);

  // Toggle section collapse
  const toggleSection = useCallback((section: string) => {
    setCollapsedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  }, []);

  // Toggle array filter
  const toggleArrayFilter = useCallback(
    (key: keyof RiskFilters, value: string) => {
      const currentArray = filters[key] as string[];
      const newArray = currentArray.includes(value)
        ? currentArray.filter((v) => v !== value)
        : [...currentArray, value];

      onFilterChange({
        ...filters,
        [key]: newArray,
      });
    },
    [filters, onFilterChange]
  );

  // Update search
  const updateSearch = useCallback(
    (value: string) => {
      onFilterChange({
        ...filters,
        productSearch: value,
      });
    },
    [filters, onFilterChange]
  );

  // Apply preset
  const applyPreset = useCallback(
    (preset: (typeof FILTER_PRESETS)[0]) => {
      onFilterChange(preset.filters);
      setPresetsOpen(false);
    },
    [onFilterChange]
  );

  // Reset all filters
  const resetFilters = useCallback(() => {
    onFilterChange({
      ssvc: [],
      severity: [],
      quickFilters: [],
      ecosystems: [],
      cweCategories: [],
      productSearch: "",
    });
  }, [onFilterChange]);

  return (
    <aside
      data-testid="risk-panel"
      className={clsx(
        "w-72 bg-secondary rounded-lg overflow-y-auto",
        className
      )}
      aria-label="Risk filters panel"
    >
      {/* Header */}
      <div className="p-4 border-b border-primary flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
          <svg className="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          Risk Filters
        </h2>
        <button
          onClick={resetFilters}
          aria-label="Reset filters"
          className="text-xs text-secondary hover:text-primary transition-colors"
        >
          Reset
        </button>
      </div>

      {/* Presets Dropdown */}
      <div className="p-4 border-b border-primary">
        <div className="relative">
          <button
            data-testid="presets-dropdown"
            onClick={() => setPresetsOpen(!presetsOpen)}
            className="w-full px-3 py-2 bg-tertiary rounded-lg text-sm text-primary flex items-center justify-between hover:bg-tertiary transition-colors"
          >
            <span>Filter Presets</span>
            <svg
              className={clsx("w-4 h-4 transition-transform", presetsOpen && "rotate-180")}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {presetsOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-tertiary rounded-lg shadow-lg z-10 overflow-hidden">
              {FILTER_PRESETS.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => applyPreset(preset)}
                  className="w-full px-3 py-2 text-sm text-left text-secondary hover:bg-tertiary hover:text-primary transition-colors"
                >
                  {preset.name}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* SSVC Decision Section */}
      <FilterSection
        title="SSVC Decision"
        sectionKey="ssvc"
        isCollapsed={collapsedSections.ssvc}
        onToggle={() => toggleSection("ssvc")}
      >
        <div className="space-y-2">
          {[
            { value: "Act", count: filterCounts.ssvc.act, color: "red", glow: "glow-red" },
            { value: "Attend", count: filterCounts.ssvc.attend, color: "orange", glow: "glow-orange" },
            { value: "Track*", count: filterCounts.ssvc.trackStar, color: "yellow", glow: "glow-yellow" },
            { value: "Track", count: filterCounts.ssvc.track, color: "green", glow: "glow-green" },
          ].map(({ value, count, color, glow }) => (
            <FilterCheckbox
              key={value}
              label={value}
              count={count}
              checked={filters.ssvc.includes(value)}
              onChange={() => toggleArrayFilter("ssvc", value)}
              color={color}
              testId={`ssvc-${value.toLowerCase().replace("*", "-star")}-label`}
              glowClass={value === "Act" ? glow : undefined}
            />
          ))}
        </div>
      </FilterSection>

      {/* Quick Filters Section */}
      <FilterSection
        title="Quick Filters"
        sectionKey="quickFilters"
        isCollapsed={collapsedSections.quickFilters}
        onToggle={() => toggleSection("quickFilters")}
      >
        <div className="space-y-2">
          <FilterCheckbox
            label="KEV Only"
            count={filterCounts.quickFilters.kevOnly}
            checked={filters.quickFilters.includes("kevOnly")}
            onChange={() => toggleArrayFilter("quickFilters", "kevOnly")}
            color="orange"
            testId="quick-filter-kev"
            animateClass="animate-fire"
          />
          <FilterCheckbox
            label="Exploitable"
            count={filterCounts.quickFilters.exploitable}
            checked={filters.quickFilters.includes("exploitable")}
            onChange={() => toggleArrayFilter("quickFilters", "exploitable")}
            color="purple"
          />
          <FilterCheckbox
            label="Has Public Exploit"
            count={filterCounts.quickFilters.hasPublicExploit}
            checked={filters.quickFilters.includes("hasPublicExploit")}
            onChange={() => toggleArrayFilter("quickFilters", "hasPublicExploit")}
            color="red"
          />
          <FilterCheckbox
            label="Patch Overdue"
            count={filterCounts.quickFilters.patchOverdue}
            checked={filters.quickFilters.includes("patchOverdue")}
            onChange={() => toggleArrayFilter("quickFilters", "patchOverdue")}
            color="red"
          />
        </div>
      </FilterSection>

      {/* Severity Section */}
      <FilterSection
        title="Severity"
        sectionKey="severity"
        isCollapsed={collapsedSections.severity}
        onToggle={() => toggleSection("severity")}
      >
        <div className="space-y-2">
          <FilterCheckbox
            label="Critical"
            count={filterCounts.severity.critical}
            checked={filters.severity.includes("Critical")}
            onChange={() => toggleArrayFilter("severity", "Critical")}
            color="red"
            testId="severity-critical-label"
            animateClass="animate-pulse-critical"
          />
          <FilterCheckbox
            label="High"
            count={filterCounts.severity.high}
            checked={filters.severity.includes("High")}
            onChange={() => toggleArrayFilter("severity", "High")}
            color="orange"
          />
          <FilterCheckbox
            label="Medium"
            count={filterCounts.severity.medium}
            checked={filters.severity.includes("Medium")}
            onChange={() => toggleArrayFilter("severity", "Medium")}
            color="yellow"
          />
          <FilterCheckbox
            label="Low"
            count={filterCounts.severity.low}
            checked={filters.severity.includes("Low")}
            onChange={() => toggleArrayFilter("severity", "Low")}
            color="green"
          />
        </div>
      </FilterSection>

      {/* Product/Vendor Search */}
      <div className="p-4 border-b border-primary">
        <label className="block text-sm font-semibold text-secondary uppercase mb-2">
          Product/Vendor
        </label>
        <input
          type="text"
          placeholder="Search product or vendor..."
          value={filters.productSearch}
          onChange={(e) => updateSearch(e.target.value)}
          className="w-full px-3 py-2 bg-tertiary border border-primary rounded-lg text-primary text-sm placeholder-gray-500 focus:outline-none focus:border-cyan-500"
        />
      </div>

      {/* Ecosystem Section */}
      <FilterSection
        title="Ecosystem"
        sectionKey="ecosystems"
        isCollapsed={collapsedSections.ecosystems}
        onToggle={() => toggleSection("ecosystems")}
      >
        <div className="grid grid-cols-2 gap-2">
          {[
            { value: "npm", count: filterCounts.ecosystems.npm, icon: "npm" },
            { value: "pip", count: filterCounts.ecosystems.pip, icon: "python" },
            { value: "maven", count: filterCounts.ecosystems.maven, icon: "java" },
            { value: "go", count: filterCounts.ecosystems.go, icon: "go" },
          ].map(({ value, count }) => (
            <FilterCheckbox
              key={value}
              label={value}
              count={count}
              checked={filters.ecosystems.includes(value)}
              onChange={() => toggleArrayFilter("ecosystems", value)}
              color="cyan"
              compact
            />
          ))}
        </div>
      </FilterSection>

      {/* CWE Category Section */}
      <FilterSection
        title="CWE Category"
        sectionKey="cweCategories"
        isCollapsed={collapsedSections.cweCategories}
        onToggle={() => toggleSection("cweCategories")}
      >
        <div className="space-y-2">
          {[
            { value: "injection", label: "Injection", count: filterCounts.cweCategories.injection },
            { value: "xss", label: "XSS", count: filterCounts.cweCategories.xss },
            { value: "auth", label: "Auth", count: filterCounts.cweCategories.auth },
            { value: "crypto", label: "Crypto", count: filterCounts.cweCategories.crypto },
            { value: "config", label: "Config", count: filterCounts.cweCategories.config },
          ].map(({ value, label, count }) => (
            <FilterCheckbox
              key={value}
              label={label}
              count={count}
              checked={filters.cweCategories.includes(value)}
              onChange={() => toggleArrayFilter("cweCategories", value)}
              color="purple"
            />
          ))}
        </div>
      </FilterSection>
    </aside>
  );
}

// ============================================================================
// Sub-components
// ============================================================================

interface FilterSectionProps {
  title: string;
  sectionKey: string;
  isCollapsed?: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

function FilterSection({
  title,
  sectionKey,
  isCollapsed = false,
  onToggle,
  children,
}: FilterSectionProps) {
  return (
    <div className="border-b border-primary">
      <button
        data-testid={`${sectionKey}-section-header`}
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between hover:bg-tertiary/50 transition-colors"
      >
        <h3 className="text-sm font-semibold text-secondary uppercase">{title}</h3>
        <svg
          className={clsx("w-4 h-4 text-tertiary transition-transform", isCollapsed && "rotate-180")}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      <div
        data-testid={`${sectionKey}-section-content`}
        className={clsx(
          "px-4 pb-4 transition-all duration-200",
          isCollapsed && "collapsed hidden"
        )}
      >
        {children}
      </div>
    </div>
  );
}

interface FilterCheckboxProps {
  label: string;
  count: number;
  checked: boolean;
  onChange: () => void;
  color?: string;
  testId?: string;
  glowClass?: string;
  animateClass?: string;
  compact?: boolean;
}

function FilterCheckbox({
  label,
  count,
  checked,
  onChange,
  color = "cyan",
  testId,
  glowClass,
  animateClass,
  compact = false,
}: FilterCheckboxProps) {
  const colorClasses: Record<string, string> = {
    red: "text-red-400",
    orange: "text-orange-400",
    yellow: "text-yellow-400",
    green: "text-green-400",
    purple: "text-purple-400",
    cyan: "text-cyan-400",
  };

  return (
    <label
      data-testid={testId}
      className={clsx(
        "flex items-center gap-2 cursor-pointer group",
        glowClass,
        animateClass,
        compact && "text-xs"
      )}
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        aria-label={label}
        className={clsx(
          "w-4 h-4 rounded border-primary bg-tertiary focus:ring-2 focus:ring-offset-0",
          `text-${color}-500 focus:ring-${color}-500`
        )}
      />
      <span className={clsx("text-sm group-hover:text-primary transition-colors", colorClasses[color])}>
        {label}
      </span>
      <span
        className="text-xs text-tertiary ml-auto"
        aria-label={`${label} count: ${count}`}
      >
        {count}
      </span>
    </label>
  );
}
