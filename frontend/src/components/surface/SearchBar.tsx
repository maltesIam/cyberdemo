/**
 * SearchBar - Enhanced search with auto-detect, autosuggest, and keyboard navigation
 *
 * Features:
 * - Auto-detects search type (hostname, IP, CVE-ID, hash, domain, actor)
 * - Dropdown with grouped results as user types
 * - Keyboard navigation (up/down arrows, Enter, Escape)
 * - Ctrl+K shortcut to focus
 * - 300ms debounced search
 */

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import clsx from "clsx";

// ============================================================================
// Types
// ============================================================================

export interface SearchResult {
  type: "asset" | "cve" | "ioc" | "incident";
  id: string;
  label: string;
  sublabel: string;
}

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSelect: (result: SearchResult) => void;
}

// ============================================================================
// Helpers
// ============================================================================

type SearchType = "hostname" | "ip" | "cve" | "hash" | "domain" | "actor" | "generic";

const SEARCH_TYPE_LABELS: Record<SearchType, { label: string; color: string }> = {
  hostname: { label: "HOST", color: "#06b6d4" },
  ip: { label: "IP", color: "#3b82f6" },
  cve: { label: "CVE", color: "#ef4444" },
  hash: { label: "HASH", color: "#a855f7" },
  domain: { label: "DOMAIN", color: "#f97316" },
  actor: { label: "ACTOR", color: "#22c55e" },
  generic: { label: "SEARCH", color: "#6b7280" },
};

/** Detect the type of search query */
function detectSearchType(query: string): SearchType {
  const q = query.trim();
  if (!q) return "generic";

  // CVE pattern: CVE-YYYY-NNNNN
  if (/^CVE-\d{4}-\d{4,}$/i.test(q)) return "cve";

  // IPv4
  if (/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(q)) return "ip";

  // MD5 hash (32 hex chars)
  if (/^[a-f0-9]{32}$/i.test(q)) return "hash";

  // SHA256 hash (64 hex chars)
  if (/^[a-f0-9]{64}$/i.test(q)) return "hash";

  // SHA1 hash (40 hex chars)
  if (/^[a-f0-9]{40}$/i.test(q)) return "hash";

  // Domain pattern
  if (/^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$/.test(q)) return "domain";

  // Known actor prefixes
  if (/^(APT|FIN|TA)\d+/i.test(q)) return "actor";

  // Hostname pattern (contains dots or dashes, not an IP)
  if (/^[a-zA-Z][a-zA-Z0-9-]*(\.[a-zA-Z0-9-]+)*$/.test(q) && q.includes("-")) return "hostname";

  return "generic";
}

/** Generate mock results based on query (in production, this calls the API) */
function generateMockResults(query: string): SearchResult[] {
  if (!query.trim() || query.length < 2) return [];

  const q = query.toLowerCase();
  const results: SearchResult[] = [];
  const type = detectSearchType(query);

  // Generate contextual mock results
  if (type === "cve" || q.startsWith("cve")) {
    results.push(
      {
        type: "cve",
        id: "CVE-2024-3400",
        label: "CVE-2024-3400",
        sublabel: "Palo Alto PAN-OS Command Injection (CVSS 10.0)",
      },
      {
        type: "cve",
        id: "CVE-2024-21887",
        label: "CVE-2024-21887",
        sublabel: "Ivanti Connect Secure RCE (CVSS 9.1)",
      },
    );
  } else if (type === "ip") {
    results.push(
      { type: "asset", id: `asset-${q}`, label: q, sublabel: "srv-web-01.corp.local" },
      { type: "ioc", id: `ioc-${q}`, label: q, sublabel: "Known C2 indicator" },
    );
  } else if (type === "hash") {
    results.push({
      type: "ioc",
      id: `ioc-hash-1`,
      label: query.slice(0, 16) + "...",
      sublabel: "Cobalt Strike beacon",
    });
  } else {
    // Generic results
    results.push(
      {
        type: "asset",
        id: `asset-${q}-1`,
        label: `srv-${q}-01`,
        sublabel: `10.0.1.${Math.floor(Math.random() * 254) + 1}`,
      },
      {
        type: "asset",
        id: `asset-${q}-2`,
        label: `ws-${q}-02`,
        sublabel: `10.0.2.${Math.floor(Math.random() * 254) + 1}`,
      },
      {
        type: "incident",
        id: `inc-${q}`,
        label: `INC-${Math.floor(Math.random() * 9000) + 1000}`,
        sublabel: `Suspicious activity on ${q}`,
      },
    );
  }

  return results;
}

/** Group results by type for display */
function groupResults(results: SearchResult[]): Map<string, SearchResult[]> {
  const groups = new Map<string, SearchResult[]>();
  for (const r of results) {
    const key = r.type;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(r);
  }
  return groups;
}

const GROUP_LABELS: Record<string, string> = {
  asset: "Assets",
  cve: "CVEs",
  ioc: "IOCs",
  incident: "Incidents",
};

const GROUP_ICONS: Record<string, JSX.Element> = {
  asset: (
    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
      />
    </svg>
  ),
  cve: (
    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  ),
  ioc: (
    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 9v2m0 4h.01M5.07 19H19a2 2 0 001.75-2.96l-6.93-12a2 2 0 00-3.5 0l-6.93 12A2 2 0 005.07 19z"
      />
    </svg>
  ),
  incident: (
    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M13 10V3L4 14h7v7l9-11h-7z"
      />
    </svg>
  ),
};

// ============================================================================
// Main Component
// ============================================================================

export function SearchBar({ value, onChange, onSelect }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  // Debounced results
  const [debouncedQuery, setDebouncedQuery] = useState(value);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedQuery(value);
    }, 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [value]);

  const results = useMemo(() => generateMockResults(debouncedQuery), [debouncedQuery]);
  const grouped = useMemo(() => groupResults(results), [results]);
  const flatResults = results; // Flat list for keyboard navigation

  // Detect current search type
  const searchType = useMemo(() => detectSearchType(value), [value]);
  const typeInfo = SEARCH_TYPE_LABELS[searchType];

  // Ctrl+K global shortcut
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        inputRef.current?.focus();
        setIsOpen(true);
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange(e.target.value);
      setIsOpen(true);
      setActiveIndex(-1);
    },
    [onChange],
  );

  const handleSelect = useCallback(
    (result: SearchResult) => {
      onSelect(result);
      setIsOpen(false);
      setActiveIndex(-1);
    },
    [onSelect],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!isOpen || flatResults.length === 0) {
        if (e.key === "ArrowDown" && value.trim()) {
          setIsOpen(true);
        }
        return;
      }

      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setActiveIndex((prev) => (prev + 1) % flatResults.length);
          break;
        case "ArrowUp":
          e.preventDefault();
          setActiveIndex((prev) => (prev - 1 + flatResults.length) % flatResults.length);
          break;
        case "Enter":
          e.preventDefault();
          if (activeIndex >= 0 && activeIndex < flatResults.length) {
            handleSelect(flatResults[activeIndex]!);
          }
          break;
        case "Escape":
          setIsOpen(false);
          setActiveIndex(-1);
          break;
      }
    },
    [isOpen, flatResults, activeIndex, handleSelect, value],
  );

  const showDropdown = isOpen && results.length > 0 && value.trim().length >= 2;

  return (
    <div ref={containerRef} className="relative">
      {/* Input with type badge */}
      <div className="relative flex items-center">
        <svg
          className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>

        {/* Type badge inside input */}
        {value.trim() && searchType !== "generic" && (
          <span
            className="absolute left-8 top-1/2 -translate-y-1/2 px-1 py-0.5 rounded text-[8px] font-bold uppercase"
            style={{ backgroundColor: `${typeInfo.color}20`, color: typeInfo.color }}
          >
            {typeInfo.label}
          </span>
        )}

        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          onFocus={() => value.trim().length >= 2 && setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="Search hostname, IP, CVE, hash..."
          className={clsx(
            "w-48 lg:w-72 py-1.5 pr-16 bg-gray-900 border border-gray-600 rounded-lg text-sm text-gray-200",
            "placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-colors",
            value.trim() && searchType !== "generic" ? "pl-[4.5rem]" : "pl-8",
          )}
        />

        {/* Ctrl+K hint */}
        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-0.5">
          {!value && (
            <span className="hidden md:flex items-center gap-0.5 text-[10px] text-gray-600 bg-gray-800 px-1.5 py-0.5 rounded border border-gray-700">
              <kbd>Ctrl</kbd>+<kbd>K</kbd>
            </span>
          )}
          {value && (
            <button
              onClick={() => {
                onChange("");
                setIsOpen(false);
                inputRef.current?.focus();
              }}
              className="text-gray-500 hover:text-gray-300 transition-colors"
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
          )}
        </div>
      </div>

      {/* Dropdown results */}
      {showDropdown && (
        <div className="absolute z-50 top-full mt-1 w-full min-w-[320px] bg-gray-800 border border-gray-600 rounded-lg shadow-xl overflow-hidden">
          {Array.from(grouped.entries()).map(([groupKey, items]) => {
            const groupLabel = GROUP_LABELS[groupKey] ?? groupKey;
            const icon = GROUP_ICONS[groupKey] ?? null;

            return (
              <div key={groupKey}>
                {/* Group header */}
                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-750 border-b border-gray-700">
                  <span className="text-gray-500">{icon}</span>
                  <span className="text-[10px] font-medium text-gray-400 uppercase tracking-wider">
                    {groupLabel}
                  </span>
                  <span className="text-[10px] text-gray-600">({items.length})</span>
                </div>

                {/* Results */}
                {items.map((result) => {
                  const globalIdx = flatResults.indexOf(result);
                  const isActive = globalIdx === activeIndex;

                  return (
                    <button
                      key={result.id}
                      onClick={() => handleSelect(result)}
                      onMouseEnter={() => setActiveIndex(globalIdx)}
                      className={clsx(
                        "w-full text-left px-3 py-2 flex items-center gap-2 transition-colors",
                        isActive ? "bg-gray-700" : "hover:bg-gray-700/50",
                      )}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-gray-200 truncate">{result.label}</div>
                        <div className="text-[11px] text-gray-500 truncate">{result.sublabel}</div>
                      </div>
                      <svg
                        className="w-3.5 h-3.5 text-gray-600 flex-shrink-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </button>
                  );
                })}
              </div>
            );
          })}

          {/* Footer hint */}
          <div className="px-3 py-1.5 border-t border-gray-700 flex items-center justify-between text-[10px] text-gray-600">
            <span>
              <kbd className="px-1 bg-gray-700 rounded">Up</kbd> /{" "}
              <kbd className="px-1 bg-gray-700 rounded">Down</kbd> to navigate
            </span>
            <span>
              <kbd className="px-1 bg-gray-700 rounded">Enter</kbd> to select
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
