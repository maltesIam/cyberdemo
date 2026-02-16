/**
 * QueryBuilder - Advanced query builder modal for the Surface Command Center
 *
 * Features:
 * - Add condition rows: field + operator + value
 * - Combine with AND/OR/NOT
 * - Live query preview as text
 * - Save/load favorites (localStorage)
 * - Preset queries for common use cases
 */

import { useState, useCallback, useEffect, useMemo } from "react";

// ============================================================================
// Types
// ============================================================================

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onApply: (query: string) => void;
}

interface Condition {
  id: string;
  field: string;
  operator: string;
  value: string;
  combinator: "AND" | "OR" | "NOT";
}

interface SavedQuery {
  name: string;
  conditions: Condition[];
}

// ============================================================================
// Constants
// ============================================================================

const FIELDS = [
  {
    id: "severity",
    label: "Severity",
    type: "select",
    options: ["critical", "high", "medium", "low", "informational"],
  },
  { id: "kev", label: "KEV", type: "boolean", options: ["true", "false"] },
  { id: "cvss", label: "CVSS", type: "number", options: [] },
  { id: "risk_score", label: "Risk Score", type: "number", options: [] },
  {
    id: "asset.type",
    label: "Asset Type",
    type: "select",
    options: ["server", "workstation", "laptop", "vm", "container"],
  },
  {
    id: "asset.department",
    label: "Department",
    type: "select",
    options: ["IT", "Engineering", "Finance", "HR", "Sales", "Executive"],
  },
  {
    id: "ioc.type",
    label: "IOC Type",
    type: "select",
    options: ["ip", "domain", "hash_md5", "hash_sha256", "url", "email"],
  },
  { id: "actor", label: "Threat Actor", type: "text", options: [] },
  {
    id: "status",
    label: "Status",
    type: "select",
    options: ["open", "investigating", "contained", "resolved", "closed"],
  },
  { id: "hostname", label: "Hostname", type: "text", options: [] },
  { id: "ip", label: "IP Address", type: "text", options: [] },
] as const;

const OPERATORS: Record<string, { id: string; label: string; symbol: string }[]> = {
  select: [
    { id: "equals", label: "equals", symbol: ":" },
    { id: "not_equals", label: "not equals", symbol: "!:" },
  ],
  boolean: [{ id: "equals", label: "is", symbol: ":" }],
  number: [
    { id: "equals", label: "equals", symbol: ":" },
    { id: "greater_than", label: "greater than", symbol: ">" },
    { id: "less_than", label: "less than", symbol: "<" },
  ],
  text: [
    { id: "equals", label: "equals", symbol: ":" },
    { id: "not_equals", label: "not equals", symbol: "!:" },
    { id: "contains", label: "contains", symbol: "~" },
  ],
};

const PRESET_QUERIES: { name: string; conditions: Condition[] }[] = [
  {
    name: "Critical CVEs with exploit on VIP assets",
    conditions: [
      { id: "p1", field: "severity", operator: "equals", value: "critical", combinator: "AND" },
      { id: "p2", field: "kev", operator: "equals", value: "true", combinator: "AND" },
      { id: "p3", field: "asset.type", operator: "equals", value: "server", combinator: "AND" },
    ],
  },
  {
    name: "High-risk IOCs from last 24h",
    conditions: [
      { id: "p4", field: "risk_score", operator: "greater_than", value: "80", combinator: "AND" },
      { id: "p5", field: "ioc.type", operator: "equals", value: "ip", combinator: "OR" },
      { id: "p6", field: "ioc.type", operator: "equals", value: "domain", combinator: "AND" },
    ],
  },
  {
    name: "Contained assets with open incidents",
    conditions: [
      { id: "p7", field: "status", operator: "equals", value: "contained", combinator: "AND" },
      { id: "p8", field: "severity", operator: "equals", value: "critical", combinator: "OR" },
      { id: "p9", field: "severity", operator: "equals", value: "high", combinator: "AND" },
    ],
  },
];

const STORAGE_KEY = "surface-saved-queries";

// ============================================================================
// Helpers
// ============================================================================

function generateId(): string {
  return `c-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

function conditionToString(c: Condition): string {
  const fieldDef = FIELDS.find((f) => f.id === c.field);
  const fieldType = fieldDef?.type ?? "text";
  const opDef = (OPERATORS[fieldType] ?? OPERATORS.text)?.find((o) => o.id === c.operator);
  const symbol = opDef?.symbol ?? ":";
  return `${c.field}${symbol}${c.value}`;
}

function buildQueryString(conditions: Condition[]): string {
  if (conditions.length === 0) return "";

  return conditions
    .map((c, i) => {
      const expr = conditionToString(c);
      if (i === 0) return expr;
      return `${c.combinator} ${expr}`;
    })
    .join(" ");
}

function loadSavedQueries(): SavedQuery[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return JSON.parse(stored) as SavedQuery[];
  } catch {
    // Ignore
  }
  return [];
}

function saveSavedQueries(queries: SavedQuery[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(queries));
  } catch {
    // Ignore
  }
}

// ============================================================================
// Sub-components
// ============================================================================

/** Single condition row */
function ConditionRow({
  condition,
  isFirst,
  onChange,
  onRemove,
}: {
  condition: Condition;
  isFirst: boolean;
  onChange: (c: Condition) => void;
  onRemove: () => void;
}) {
  const fieldDef = FIELDS.find((f) => f.id === condition.field);
  const fieldType = fieldDef?.type ?? "text";
  const operators = OPERATORS[fieldType] ?? OPERATORS.text ?? [];

  return (
    <div className="flex items-center gap-2">
      {/* Combinator (hidden for first row) */}
      <div className="w-14 flex-shrink-0">
        {!isFirst ? (
          <select
            value={condition.combinator}
            onChange={(e) =>
              onChange({ ...condition, combinator: e.target.value as "AND" | "OR" | "NOT" })
            }
            className="w-full px-1 py-1 bg-gray-700 border border-gray-600 rounded text-[11px] text-cyan-300 font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="AND">AND</option>
            <option value="OR">OR</option>
            <option value="NOT">NOT</option>
          </select>
        ) : (
          <span className="text-[11px] text-gray-500 font-mono pl-1">WHERE</span>
        )}
      </div>

      {/* Field selector */}
      <select
        value={condition.field}
        onChange={(e) => onChange({ ...condition, field: e.target.value, value: "" })}
        className="flex-1 min-w-0 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-[11px] text-gray-200 focus:outline-none focus:border-cyan-500"
      >
        {FIELDS.map((f) => (
          <option key={f.id} value={f.id}>
            {f.label}
          </option>
        ))}
      </select>

      {/* Operator selector */}
      <select
        value={condition.operator}
        onChange={(e) => onChange({ ...condition, operator: e.target.value })}
        className="w-24 flex-shrink-0 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-[11px] text-gray-200 focus:outline-none focus:border-cyan-500"
      >
        {operators.map((op) => (
          <option key={op.id} value={op.id}>
            {op.label}
          </option>
        ))}
      </select>

      {/* Value input */}
      {(fieldDef?.options?.length ?? 0) > 0 ? (
        <select
          value={condition.value}
          onChange={(e) => onChange({ ...condition, value: e.target.value })}
          className="flex-1 min-w-0 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-[11px] text-gray-200 focus:outline-none focus:border-cyan-500"
        >
          <option value="">Select...</option>
          {(fieldDef?.options ?? []).map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      ) : (
        <input
          type={fieldType === "number" ? "number" : "text"}
          value={condition.value}
          onChange={(e) => onChange({ ...condition, value: e.target.value })}
          placeholder="Value..."
          className="flex-1 min-w-0 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-[11px] text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500"
        />
      )}

      {/* Remove button */}
      <button
        onClick={onRemove}
        className="p-1 text-gray-500 hover:text-red-400 transition-colors flex-shrink-0"
        title="Remove condition"
      >
        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function QueryBuilder({ isOpen, onClose, onApply }: Props) {
  const [conditions, setConditions] = useState<Condition[]>([
    { id: generateId(), field: "severity", operator: "equals", value: "", combinator: "AND" },
  ]);
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>(() => loadSavedQueries());
  const [saveName, setSaveName] = useState("");
  const [showSave, setShowSave] = useState(false);

  // Build preview string
  const queryPreview = useMemo(() => buildQueryString(conditions), [conditions]);

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  const addCondition = useCallback(() => {
    setConditions((prev) => [
      ...prev,
      { id: generateId(), field: "severity", operator: "equals", value: "", combinator: "AND" },
    ]);
  }, []);

  const updateCondition = useCallback((id: string, updated: Condition) => {
    setConditions((prev) => prev.map((c) => (c.id === id ? updated : c)));
  }, []);

  const removeCondition = useCallback((id: string) => {
    setConditions((prev) => {
      if (prev.length <= 1) return prev; // Keep at least one
      return prev.filter((c) => c.id !== id);
    });
  }, []);

  const handleApply = useCallback(() => {
    const validConditions = conditions.filter((c) => c.value.trim());
    const query = buildQueryString(validConditions);
    onApply(query);
    onClose();
  }, [conditions, onApply, onClose]);

  const handleSave = useCallback(() => {
    if (!saveName.trim()) return;
    const newQueries = [...savedQueries, { name: saveName.trim(), conditions: [...conditions] }];
    setSavedQueries(newQueries);
    saveSavedQueries(newQueries);
    setSaveName("");
    setShowSave(false);
  }, [saveName, conditions, savedQueries]);

  const handleLoadPreset = useCallback((preset: { conditions: Condition[] }) => {
    setConditions(preset.conditions.map((c) => ({ ...c, id: generateId() })));
  }, []);

  const handleDeleteSaved = useCallback(
    (idx: number) => {
      const newQueries = savedQueries.filter((_, i) => i !== idx);
      setSavedQueries(newQueries);
      saveSavedQueries(newQueries);
    },
    [savedQueries],
  );

  const handleClear = useCallback(() => {
    setConditions([
      { id: generateId(), field: "severity", operator: "equals", value: "", combinator: "AND" },
    ]);
  }, []);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-gray-800 border border-gray-600 rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col animate-query-builder-in">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <svg
              className="w-5 h-5 text-cyan-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
            <h2 className="text-white font-semibold">Advanced Query Builder</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-500 hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {/* Preset queries */}
          <div>
            <span className="text-[11px] text-gray-400 uppercase tracking-wider mb-2 block">
              Presets
            </span>
            <div className="flex flex-wrap gap-1.5">
              {PRESET_QUERIES.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => handleLoadPreset(preset)}
                  className="px-2.5 py-1 bg-gray-700 border border-gray-600 rounded text-[11px] text-gray-300 hover:bg-gray-600 hover:text-white transition-colors"
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          {/* Saved queries */}
          {savedQueries.length > 0 && (
            <div>
              <span className="text-[11px] text-gray-400 uppercase tracking-wider mb-2 block">
                Saved
              </span>
              <div className="flex flex-wrap gap-1.5">
                {savedQueries.map((sq, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-1 bg-gray-700 border border-gray-600 rounded overflow-hidden"
                  >
                    <button
                      onClick={() => handleLoadPreset(sq)}
                      className="px-2.5 py-1 text-[11px] text-cyan-300 hover:bg-gray-600 transition-colors"
                    >
                      {sq.name}
                    </button>
                    <button
                      onClick={() => handleDeleteSaved(idx)}
                      className="px-1.5 py-1 text-gray-500 hover:text-red-400 hover:bg-gray-600 transition-colors"
                    >
                      <svg
                        className="w-3 h-3"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Condition rows */}
          <div className="space-y-2">
            <span className="text-[11px] text-gray-400 uppercase tracking-wider block">
              Conditions
            </span>
            {conditions.map((condition, idx) => (
              <ConditionRow
                key={condition.id}
                condition={condition}
                isFirst={idx === 0}
                onChange={(c) => updateCondition(condition.id, c)}
                onRemove={() => removeCondition(condition.id)}
              />
            ))}
            <button
              onClick={addCondition}
              className="flex items-center gap-1.5 text-[11px] text-cyan-400 hover:text-cyan-300 transition-colors mt-2"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Add condition
            </button>
          </div>

          {/* Query preview */}
          <div>
            <span className="text-[11px] text-gray-400 uppercase tracking-wider mb-1 block">
              Query Preview
            </span>
            <div className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg font-mono text-sm text-cyan-300 min-h-[36px]">
              {queryPreview || (
                <span className="text-gray-600 italic">Add conditions to build query...</span>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-gray-700">
          <div className="flex items-center gap-2">
            <button
              onClick={handleClear}
              className="px-3 py-1.5 text-xs text-gray-400 hover:text-gray-200 transition-colors"
            >
              Clear All
            </button>
            {showSave ? (
              <div className="flex items-center gap-1.5">
                <input
                  type="text"
                  value={saveName}
                  onChange={(e) => setSaveName(e.target.value)}
                  placeholder="Query name..."
                  className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500 w-40"
                  onKeyDown={(e) => e.key === "Enter" && handleSave()}
                  autoFocus
                />
                <button
                  onClick={handleSave}
                  disabled={!saveName.trim()}
                  className="px-2 py-1 bg-cyan-600 text-white rounded text-xs disabled:opacity-50 hover:bg-cyan-500 transition-colors"
                >
                  Save
                </button>
                <button
                  onClick={() => setShowSave(false)}
                  className="text-xs text-gray-500 hover:text-gray-300"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowSave(true)}
                className="flex items-center gap-1 px-3 py-1.5 text-xs text-gray-400 hover:text-cyan-400 transition-colors"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
                  />
                </svg>
                Save as favorite
              </button>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-1.5 bg-gray-700 text-gray-300 rounded-lg text-xs hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleApply}
              className="px-4 py-1.5 bg-cyan-600 text-white rounded-lg text-xs font-medium hover:bg-cyan-500 transition-colors"
            >
              Apply Query
            </button>
          </div>
        </div>
      </div>

      {/* Inline CSS for animation */}
      <style>{`
        @keyframes queryBuilderIn {
          from {
            opacity: 0;
            transform: scale(0.95) translateY(8px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
        .animate-query-builder-in {
          animation: queryBuilderIn 0.2s ease-out;
        }
      `}</style>
    </div>
  );
}
