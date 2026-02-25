/**
 * LayerFilters - Per-layer filter controls for the Surface Command Center
 *
 * Shows context-specific filters when a particular layer is active.
 * Supports Vulnerabilities, Threats, Containment, and Relations layers.
 */

import { useState, useCallback } from "react";
import clsx from "clsx";
import type { LayerType } from "../AttackSurface/types";

// ============================================================================
// Types
// ============================================================================

export interface LayerFilterState {
  vulnerabilities: {
    cvssMin?: number;
    cvssMax?: number;
    epssMin?: number;
    epssMax?: number;
    kevOnly?: boolean;
    exploitAvailable?: boolean;
    vendor?: string;
    product?: string;
  };
  threats: {
    iocType?: string[];
    riskMin?: number;
    actor?: string;
    malware?: string;
    country?: string;
    technique?: string;
  };
  containment: {
    status?: string;
    dateFrom?: string;
    dateTo?: string;
  };
  relations: {
    types?: string[];
    strengthMin?: number;
  };
}

export const DEFAULT_LAYER_FILTERS: LayerFilterState = {
  vulnerabilities: {},
  threats: {},
  containment: {},
  relations: {},
};

interface Props {
  activeLayer: LayerType;
  filters: LayerFilterState;
  onFilterChange: (filters: LayerFilterState) => void;
}

// ============================================================================
// Constants
// ============================================================================

const IOC_TYPES = [
  { id: "ip", label: "IP" },
  { id: "domain", label: "Domain" },
  { id: "hash_md5", label: "MD5" },
  { id: "hash_sha256", label: "SHA256" },
  { id: "url", label: "URL" },
  { id: "email", label: "Email" },
] as const;

const RELATION_TYPES = [
  { id: "lateral_movement", label: "Lateral Movement" },
  { id: "c2", label: "C2 Communication" },
  { id: "exfil", label: "Data Exfiltration" },
  { id: "shared_ioc", label: "Shared IOC" },
] as const;

const TACTICS = [
  "Initial Access",
  "Execution",
  "Persistence",
  "Privilege Escalation",
  "Defense Evasion",
  "Credential Access",
  "Discovery",
  "Lateral Movement",
  "Collection",
  "Exfiltration",
  "Command and Control",
  "Impact",
] as const;

// ============================================================================
// Sub-components
// ============================================================================

/** Range slider with label */
function RangeInput({
  label,
  min,
  max,
  step,
  value,
  onChange,
}: {
  label: string;
  min: number;
  max: number;
  step?: number;
  value: number | undefined;
  onChange: (v: number) => void;
}) {
  const currentValue = value ?? min;
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-[11px]">
        <span className="text-secondary">{label}</span>
        <span className="text-secondary font-mono">
          {currentValue.toFixed(step && step < 1 ? 2 : 0)}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step ?? 1}
        value={currentValue}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-1 bg-tertiary rounded-lg appearance-none cursor-pointer accent-cyan-500"
      />
    </div>
  );
}

/** Toggle switch */
function Toggle({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label className="flex items-center justify-between cursor-pointer">
      <span className="text-[11px] text-secondary">{label}</span>
      <div
        onClick={() => onChange(!checked)}
        className={clsx(
          "relative w-8 h-4 rounded-full transition-colors",
          checked ? "bg-cyan-600" : "bg-tertiary",
        )}
      >
        <div
          className={clsx(
            "absolute top-0.5 w-3 h-3 bg-white rounded-full transition-transform",
            checked ? "translate-x-4" : "translate-x-0.5",
          )}
        />
      </div>
    </label>
  );
}

/** Searchable dropdown */
function SearchableDropdown({
  label,
  placeholder,
  value,
  options,
  onChange,
}: {
  label: string;
  placeholder: string;
  value: string | undefined;
  options: readonly string[];
  onChange: (v: string) => void;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");

  const filtered = options.filter((o) => o.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="space-y-1 relative">
      <span className="text-[11px] text-secondary">{label}</span>
      <div className="relative">
        <input
          type="text"
          value={value ?? query}
          placeholder={placeholder}
          onChange={(e) => {
            setQuery(e.target.value);
            onChange(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onBlur={() => setTimeout(() => setIsOpen(false), 200)}
          className="w-full px-2 py-1 bg-tertiary border border-primary rounded text-[11px] text-primary placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-colors"
        />
        {value && (
          <button
            onClick={() => {
              onChange("");
              setQuery("");
            }}
            className="absolute right-1.5 top-1/2 -translate-y-1/2 text-tertiary hover:text-secondary"
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>
      {isOpen && filtered.length > 0 && (
        <div className="absolute z-20 w-full mt-1 bg-tertiary border border-primary rounded shadow-lg max-h-32 overflow-y-auto">
          {filtered.slice(0, 10).map((opt) => (
            <button
              key={opt}
              onMouseDown={() => {
                onChange(opt);
                setQuery("");
                setIsOpen(false);
              }}
              className="w-full text-left px-2 py-1 text-[11px] text-secondary hover:bg-tertiary transition-colors"
            >
              {opt}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/** Multi-select chip group for layer filters */
function LayerChipGroup({
  options,
  selected,
  onToggle,
}: {
  options: readonly { id: string; label: string }[];
  selected: string[];
  onToggle: (id: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-1">
      {options.map((opt) => {
        const isActive = selected.includes(opt.id);
        return (
          <button
            key={opt.id}
            onClick={() => onToggle(opt.id)}
            className={clsx(
              "px-2 py-0.5 rounded text-[10px] font-medium transition-colors border",
              isActive
                ? "border-cyan-500/50 bg-cyan-900/30 text-cyan-300"
                : "border-primary bg-tertiary/40 text-secondary hover:text-primary",
            )}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}

// ============================================================================
// Layer-specific filter panels
// ============================================================================

function VulnFilters({
  state,
  onChange,
}: {
  state: LayerFilterState["vulnerabilities"];
  onChange: (s: LayerFilterState["vulnerabilities"]) => void;
}) {
  // Sample vendor/product lists (in production, fetched from API)
  const vendors = [
    "Microsoft",
    "Apache",
    "Google",
    "Oracle",
    "Adobe",
    "Cisco",
    "VMware",
    "Linux",
    "Mozilla",
  ];
  const products = [
    "Windows",
    "Chrome",
    "Java",
    "Apache HTTP",
    "Exchange",
    "Firefox",
    "vCenter",
    "Office",
  ];

  return (
    <div className="space-y-3">
      <RangeInput
        label="CVSS Min"
        min={0}
        max={10}
        step={0.1}
        value={state?.cvssMin}
        onChange={(v) => onChange({ ...state, cvssMin: v })}
      />
      <RangeInput
        label="CVSS Max"
        min={0}
        max={10}
        step={0.1}
        value={state?.cvssMax}
        onChange={(v) => onChange({ ...state, cvssMax: v })}
      />
      <RangeInput
        label="EPSS Min"
        min={0}
        max={1}
        step={0.01}
        value={state?.epssMin}
        onChange={(v) => onChange({ ...state, epssMin: v })}
      />
      <RangeInput
        label="EPSS Max"
        min={0}
        max={1}
        step={0.01}
        value={state?.epssMax}
        onChange={(v) => onChange({ ...state, epssMax: v })}
      />
      <Toggle
        label="KEV Only"
        checked={state?.kevOnly ?? false}
        onChange={(v) => onChange({ ...state, kevOnly: v })}
      />
      <Toggle
        label="Exploit Available"
        checked={state?.exploitAvailable ?? false}
        onChange={(v) => onChange({ ...state, exploitAvailable: v })}
      />
      <SearchableDropdown
        label="Vendor"
        placeholder="Search vendor..."
        value={state?.vendor}
        options={vendors}
        onChange={(v) => onChange({ ...state, vendor: v })}
      />
      <SearchableDropdown
        label="Product"
        placeholder="Search product..."
        value={state?.product}
        options={products}
        onChange={(v) => onChange({ ...state, product: v })}
      />
    </div>
  );
}

function ThreatFilters({
  state,
  onChange,
}: {
  state: LayerFilterState["threats"];
  onChange: (s: LayerFilterState["threats"]) => void;
}) {
  const actors = ["APT28", "APT29", "Lazarus Group", "FIN7", "Conti", "REvil", "DarkSide"];
  const malwareList = ["Cobalt Strike", "Mimikatz", "Emotet", "TrickBot", "Ryuk", "WannaCry"];
  const countries = ["Russia", "China", "North Korea", "Iran", "United States", "Unknown"];

  const toggleIocType = useCallback(
    (id: string) => {
      const current = state?.iocType ?? [];
      const next = current.includes(id) ? current.filter((v) => v !== id) : [...current, id];
      onChange({ ...state, iocType: next });
    },
    [state, onChange],
  );

  return (
    <div className="space-y-3">
      <div>
        <span className="text-[11px] text-secondary mb-1 block">IOC Type</span>
        <LayerChipGroup
          options={IOC_TYPES}
          selected={state?.iocType ?? []}
          onToggle={toggleIocType}
        />
      </div>
      <RangeInput
        label="Risk Score Min"
        min={0}
        max={100}
        value={state?.riskMin}
        onChange={(v) => onChange({ ...state, riskMin: v })}
      />
      <SearchableDropdown
        label="Actor"
        placeholder="Search actor..."
        value={state?.actor}
        options={actors}
        onChange={(v) => onChange({ ...state, actor: v })}
      />
      <SearchableDropdown
        label="Malware"
        placeholder="Search malware..."
        value={state?.malware}
        options={malwareList}
        onChange={(v) => onChange({ ...state, malware: v })}
      />
      <SearchableDropdown
        label="Country"
        placeholder="Select country..."
        value={state?.country}
        options={countries}
        onChange={(v) => onChange({ ...state, country: v })}
      />
      <SearchableDropdown
        label="ATT&CK Tactic"
        placeholder="Select tactic..."
        value={state?.technique}
        options={TACTICS}
        onChange={(v) => onChange({ ...state, technique: v })}
      />
    </div>
  );
}

function ContainmentFilters({
  state,
  onChange,
}: {
  state: LayerFilterState["containment"];
  onChange: (s: LayerFilterState["containment"]) => void;
}) {
  return (
    <div className="space-y-3">
      <div>
        <span className="text-[11px] text-secondary mb-1 block">Status</span>
        <div className="flex gap-1.5">
          {["contained", "lifted"].map((s) => (
            <button
              key={s}
              onClick={() => onChange({ ...state, status: state?.status === s ? undefined : s })}
              className={clsx(
                "px-2.5 py-1 rounded text-[11px] font-medium transition-colors border",
                state?.status === s
                  ? "border-cyan-500/50 bg-cyan-900/30 text-cyan-300"
                  : "border-primary bg-tertiary/40 text-secondary hover:text-primary",
              )}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
      </div>
      <div className="space-y-1">
        <span className="text-[11px] text-secondary">Date From</span>
        <input
          type="date"
          value={state?.dateFrom ?? ""}
          onChange={(e) => onChange({ ...state, dateFrom: e.target.value })}
          className="w-full px-2 py-1 bg-tertiary border border-primary rounded text-[11px] text-primary focus:outline-none focus:border-cyan-500"
        />
      </div>
      <div className="space-y-1">
        <span className="text-[11px] text-secondary">Date To</span>
        <input
          type="date"
          value={state?.dateTo ?? ""}
          onChange={(e) => onChange({ ...state, dateTo: e.target.value })}
          className="w-full px-2 py-1 bg-tertiary border border-primary rounded text-[11px] text-primary focus:outline-none focus:border-cyan-500"
        />
      </div>
    </div>
  );
}

function RelationFilters({
  state,
  onChange,
}: {
  state: LayerFilterState["relations"];
  onChange: (s: LayerFilterState["relations"]) => void;
}) {
  const toggleType = useCallback(
    (id: string) => {
      const current = state?.types ?? [];
      const next = current.includes(id) ? current.filter((v) => v !== id) : [...current, id];
      onChange({ ...state, types: next });
    },
    [state, onChange],
  );

  return (
    <div className="space-y-3">
      <div>
        <span className="text-[11px] text-secondary mb-1 block">Relation Type</span>
        <LayerChipGroup
          options={RELATION_TYPES}
          selected={state?.types ?? []}
          onToggle={toggleType}
        />
      </div>
      <RangeInput
        label="Strength Min"
        min={0}
        max={100}
        value={state?.strengthMin}
        onChange={(v) => onChange({ ...state, strengthMin: v })}
      />
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

/** Map of which layers have dedicated filter panels */
const FILTERABLE_LAYERS: LayerType[] = ["vulnerabilities", "threats", "containment", "relations"];

export function LayerFilters({ activeLayer, filters, onFilterChange }: Props) {
  if (!FILTERABLE_LAYERS.includes(activeLayer)) {
    return null;
  }

  const updateLayer = <K extends keyof LayerFilterState>(key: K, value: LayerFilterState[K]) => {
    onFilterChange({ ...filters, [key]: value });
  };

  return (
    <div className="bg-secondary/50 border-t border-primary p-3">
      <div className="flex items-center gap-2 mb-3">
        <svg
          className="w-3 h-3 text-cyan-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
          />
        </svg>
        <span className="text-[11px] font-medium text-secondary capitalize">
          {activeLayer} Filters
        </span>
      </div>

      {activeLayer === "vulnerabilities" && (
        <VulnFilters
          state={filters.vulnerabilities}
          onChange={(v) => updateLayer("vulnerabilities", v)}
        />
      )}
      {activeLayer === "threats" && (
        <ThreatFilters state={filters.threats} onChange={(v) => updateLayer("threats", v)} />
      )}
      {activeLayer === "containment" && (
        <ContainmentFilters
          state={filters.containment}
          onChange={(v) => updateLayer("containment", v)}
        />
      )}
      {activeLayer === "relations" && (
        <RelationFilters state={filters.relations} onChange={(v) => updateLayer("relations", v)} />
      )}
    </div>
  );
}
