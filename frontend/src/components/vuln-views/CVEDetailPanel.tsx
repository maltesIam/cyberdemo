/**
 * CVEDetailPanel Component - Right Slide-in Panel
 *
 * Features:
 * - Header with CVE-ID, Pin, Expand, Close buttons
 * - Risk Profile section with CVSS/EPSS bars, KEV badge, SSVC decision
 * - Risk Radar mini chart (5 axes)
 * - Description with CWE links
 * - Enrichment Sources grid of badges
 * - Affected Assets list with "View All" link
 * - Exploits list with "View All" link
 * - Attack Chain visualization (CWE -> T-code -> Actor)
 * - Vendor Patches section
 * - Actions: Create Ticket, Escalate, Accept Risk, Add Watchlist, Export
 */

import { useEffect, useCallback, useRef } from "react";
import clsx from "clsx";

// ============================================================================
// Types
// ============================================================================

interface AffectedAsset {
  id: string;
  hostname: string;
  criticality: string;
}

interface Exploit {
  id: string;
  name: string;
  source: string;
  url: string;
}

interface AttackChain {
  cwe: string;
  technique: string;
  actor: string;
}

interface Patch {
  vendor: string;
  version: string;
  url: string;
  date: string;
}

export interface CVEDetail {
  cve_id: string;
  title: string;
  description: string;
  cvss_v3_score: number;
  cvss_v3_vector?: string;
  epss_score: number;
  epss_percentile?: number;
  risk_score?: number;
  severity: "Critical" | "High" | "Medium" | "Low";
  is_kev: boolean;
  kev_date_added?: string;
  kev_due_date?: string;
  kev_ransomware_use?: boolean;
  ssvc_decision: "Act" | "Attend" | "Track*" | "Track";
  ssvc_exploitation?: string;
  ssvc_automatable?: boolean;
  exploit_count: number;
  exploit_maturity?: string;
  has_nuclei_template?: boolean;
  affected_asset_count?: number;
  affected_critical_assets?: number;
  cwe_ids?: string[];
  ecosystems?: string[];
  patch_available?: boolean;
  published_date?: string;
  last_enriched_at?: string;
  enrichment_level?: string;
  enrichment_sources?: string[];
  affected_assets?: AffectedAsset[];
  exploits?: Exploit[];
  attack_chain?: AttackChain;
  patches?: Patch[];
}

interface CVEDetailPanelProps {
  cve: CVEDetail | null;
  isOpen: boolean;
  isLoading?: boolean;
  onClose: () => void;
  onPin: (cveId: string) => void;
  onExpand: (cveId: string) => void;
  onAction: (action: string, cveId: string) => void;
  className?: string;
}

// ============================================================================
// SSVC/Severity Colors
// ============================================================================

const SSVC_COLORS: Record<string, { bg: string; glow: string }> = {
  Act: { bg: "bg-red-500", glow: "glow-red" },
  Attend: { bg: "bg-orange-500", glow: "glow-orange" },
  "Track*": { bg: "bg-yellow-500", glow: "glow-yellow" },
  Track: { bg: "bg-green-500", glow: "glow-green" },
};

const SEVERITY_COLORS: Record<string, string> = {
  Critical: "bg-red-500",
  High: "bg-orange-500",
  Medium: "bg-yellow-500",
  Low: "bg-green-500",
};

// ============================================================================
// Component
// ============================================================================

export function CVEDetailPanel({
  cve,
  isOpen,
  isLoading = false,
  onClose,
  onPin,
  onExpand,
  onAction,
  className = "",
}: CVEDetailPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  // Handle Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  // Focus trap
  useEffect(() => {
    if (isOpen && panelRef.current) {
      const firstFocusable = panelRef.current.querySelector<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      firstFocusable?.focus();
    }
  }, [isOpen]);

  const handleAction = useCallback(
    (action: string) => {
      if (cve) {
        onAction(action, cve.cve_id);
      }
    },
    [cve, onAction]
  );

  if (!isOpen) return null;

  // Loading state
  if (isLoading || !cve) {
    return (
      <div
        data-testid="cve-detail-loading"
        className={clsx(
          "fixed right-0 top-0 h-full w-96 bg-gray-800 shadow-2xl z-50 p-6",
          "animate-slide-in-right",
          className
        )}
      >
        <div className="space-y-4">
          <div data-testid="skeleton-header" className="h-8 bg-gray-700 rounded animate-pulse" />
          <div data-testid="skeleton-title" className="h-6 bg-gray-700 rounded animate-pulse w-3/4" />
          <div data-testid="skeleton-content" className="h-32 bg-gray-700 rounded animate-pulse" />
          <div data-testid="skeleton-chart" className="h-48 bg-gray-700 rounded animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div
      ref={panelRef}
      data-testid="cve-detail-panel"
      role="dialog"
      aria-labelledby="cve-detail-title"
      aria-describedby="cve-detail-description"
      className={clsx(
        "fixed right-0 top-0 h-full w-[420px] bg-gray-800 shadow-2xl z-50 overflow-y-auto",
        "animate-slide-in-right border-l border-gray-700",
        className
      )}
    >
      {/* Header */}
      <div className="sticky top-0 bg-gray-800 border-b border-gray-700 p-4 z-10">
        <div className="flex items-center justify-between mb-2">
          <h2
            id="cve-detail-title"
            className="text-lg font-mono font-bold text-cyan-400"
          >
            {cve.cve_id}
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onPin(cve.cve_id)}
              aria-label="Pin CVE"
              className="p-2 hover:bg-gray-700 rounded transition-colors"
            >
              <svg className="w-4 h-4 text-gray-400 hover:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </button>
            <button
              onClick={() => onExpand(cve.cve_id)}
              aria-label="Expand CVE"
              className="p-2 hover:bg-gray-700 rounded transition-colors"
            >
              <svg className="w-4 h-4 text-gray-400 hover:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <button
              onClick={onClose}
              aria-label="Close panel"
              className="p-2 hover:bg-gray-700 rounded transition-colors"
            >
              <svg className="w-4 h-4 text-gray-400 hover:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <p className="text-sm text-gray-300 line-clamp-2">{cve.title}</p>
      </div>

      {/* Content */}
      <div className="p-4 space-y-6">
        {/* Risk Profile Section */}
        <section>
          <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">Risk Profile</h3>

          {/* CVSS Bar */}
          <div className="mb-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-400">CVSS</span>
              <span className="text-sm font-bold text-white">{cve.cvss_v3_score}</span>
            </div>
            <div data-testid="cvss-bar" className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={clsx("h-full transition-all duration-500", SEVERITY_COLORS[cve.severity])}
                style={{ width: `${(cve.cvss_v3_score / 10) * 100}%` }}
              />
            </div>
          </div>

          {/* EPSS Bar */}
          <div className="mb-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-400">EPSS</span>
              <span className="text-sm font-bold text-white">{(cve.epss_score * 100).toFixed(1)}%</span>
            </div>
            <div data-testid="epss-bar" className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-500 transition-all duration-500"
                style={{ width: `${cve.epss_score * 100}%` }}
              />
            </div>
          </div>

          {/* Badges Row */}
          <div className="flex flex-wrap gap-2 mt-3">
            {cve.is_kev && (
              <span
                data-testid="kev-badge"
                className="px-2 py-1 bg-orange-600 text-white text-xs font-bold rounded animate-fire flex items-center gap-1"
              >
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
                </svg>
                KEV
              </span>
            )}
            <span
              data-testid="ssvc-badge"
              className={clsx(
                "px-2 py-1 text-white text-xs font-bold rounded",
                SSVC_COLORS[cve.ssvc_decision]?.bg,
                SSVC_COLORS[cve.ssvc_decision]?.glow
              )}
            >
              {cve.ssvc_decision}
            </span>
            {cve.kev_ransomware_use && (
              <span className="px-2 py-1 bg-red-700 text-white text-xs font-bold rounded">
                Ransomware
              </span>
            )}
          </div>
        </section>

        {/* Risk Radar Chart */}
        <section>
          <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">Risk Radar</h3>
          <div
            data-testid="risk-radar"
            data-axes="5"
            className="h-40 bg-gray-900 rounded-lg flex items-center justify-center relative"
          >
            <RiskRadarMini
              cvss={cve.cvss_v3_score}
              epss={cve.epss_score}
              isKev={cve.is_kev}
              exploitCount={cve.exploit_count}
              assetCount={cve.affected_asset_count ?? 0}
            />
          </div>
        </section>

        {/* Description */}
        <section id="cve-detail-description">
          <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">Description</h3>
          <p className="text-sm text-gray-300 leading-relaxed">{cve.description}</p>

          {/* CWE Links */}
          {cve.cwe_ids && cve.cwe_ids.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {cve.cwe_ids.map((cweId) => (
                <a
                  key={cweId}
                  data-testid={`cwe-link-${cweId}`}
                  href={`https://cwe.mitre.org/data/definitions/${cweId.replace("CWE-", "")}.html`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-cyan-400 hover:text-cyan-300 bg-cyan-900/30 px-2 py-1 rounded"
                >
                  {cweId}
                </a>
              ))}
            </div>
          )}
        </section>

        {/* Enrichment Sources */}
        <section>
          <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">Enrichment Sources</h3>
          <div data-testid="enrichment-sources-grid" className="flex flex-wrap gap-2">
            {cve.enrichment_sources?.map((source) => (
              <span
                key={source}
                className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded"
              >
                {source}
              </span>
            ))}
          </div>
          {cve.last_enriched_at && (
            <p className="text-xs text-gray-500 mt-2">
              Last enriched: {new Date(cve.last_enriched_at).toLocaleString()}
            </p>
          )}
        </section>

        {/* Affected Assets */}
        <section>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-400 uppercase">Affected Assets</h3>
            <span className="text-xs bg-cyan-600 text-white px-2 py-0.5 rounded-full">
              {cve.affected_asset_count}
            </span>
          </div>
          <div className="space-y-2">
            {cve.affected_assets?.slice(0, 3).map((asset) => (
              <div
                key={asset.id}
                data-testid={`asset-${asset.id}`}
                className="flex items-center justify-between p-2 bg-gray-900 rounded text-sm"
              >
                <span className="text-gray-300 font-mono">{asset.hostname}</span>
                <span
                  className={clsx(
                    "text-xs px-2 py-0.5 rounded",
                    asset.criticality === "Critical" && "bg-red-600 text-white",
                    asset.criticality === "High" && "bg-orange-600 text-white",
                    asset.criticality === "Low" && "bg-gray-600 text-gray-300"
                  )}
                >
                  {asset.criticality}
                </span>
              </div>
            ))}
          </div>
          {(cve.affected_asset_count ?? 0) > 3 && (
            <button className="w-full mt-2 text-xs text-cyan-400 hover:text-cyan-300">
              View All ({cve.affected_asset_count} assets)
            </button>
          )}
        </section>

        {/* Exploits */}
        <section>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-400 uppercase">Exploits</h3>
            <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">
              {cve.exploit_count}
            </span>
          </div>
          <div className="space-y-2">
            {cve.exploits?.slice(0, 3).map((exploit) => (
              <div
                key={exploit.id}
                className="flex items-center justify-between p-2 bg-gray-900 rounded text-sm"
              >
                <span className="text-gray-300 truncate max-w-[200px]">{exploit.name}</span>
                <span className="text-xs text-gray-400">{exploit.source}</span>
              </div>
            ))}
          </div>
          {cve.exploit_count > 3 && (
            <button className="w-full mt-2 text-xs text-cyan-400 hover:text-cyan-300">
              View All ({cve.exploit_count} exploits)
            </button>
          )}
        </section>

        {/* Attack Chain */}
        {cve.attack_chain && (
          <section>
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">Attack Chain</h3>
            <div
              data-testid="attack-chain"
              className="flex items-center justify-between p-3 bg-gray-900 rounded"
            >
              <div className="flex flex-col items-center">
                <span className="text-xs text-gray-400">CWE</span>
                <span className="text-sm text-cyan-400 font-mono">{cve.attack_chain.cwe}</span>
              </div>
              <div data-testid="attack-chain-arrow" className="text-gray-600">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
              <div className="flex flex-col items-center">
                <span className="text-xs text-gray-400">MITRE</span>
                <span className="text-sm text-orange-400 font-mono">{cve.attack_chain.technique}</span>
              </div>
              <div data-testid="attack-chain-arrow" className="text-gray-600">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
              <div className="flex flex-col items-center">
                <span className="text-xs text-gray-400">Actor</span>
                <span className="text-sm text-red-400 font-mono">{cve.attack_chain.actor}</span>
              </div>
            </div>
          </section>
        )}

        {/* Vendor Patches */}
        <section>
          <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">Vendor Patches</h3>
          {cve.patch_available ? (
            <>
              <div
                data-testid="patch-available"
                className="flex items-center gap-2 mb-2 text-sm text-green-400 bg-green-500/10 px-3 py-2 rounded"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Patch Available
              </div>
              <div className="space-y-2">
                {cve.patches?.map((patch, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 bg-gray-900 rounded text-sm"
                  >
                    <div>
                      <span className="text-gray-300">{patch.vendor}</span>
                      <span className="text-gray-500 ml-2">v{patch.version}</span>
                    </div>
                    <a
                      data-testid={`patch-link-${idx}`}
                      href={patch.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-400 hover:text-cyan-300"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </a>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-sm text-gray-500 bg-gray-900 px-3 py-2 rounded">
              No patches available
            </div>
          )}
        </section>

        {/* Actions */}
        <section className="border-t border-gray-700 pt-4">
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => handleAction("create_ticket")}
              aria-label="Create Ticket"
              className="px-3 py-2 bg-cyan-600 hover:bg-cyan-700 text-white text-sm rounded transition-colors"
            >
              Create Ticket
            </button>
            <button
              onClick={() => handleAction("escalate")}
              aria-label="Escalate"
              className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
            >
              Escalate
            </button>
            <button
              onClick={() => handleAction("accept_risk")}
              aria-label="Accept Risk"
              className="px-3 py-2 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded transition-colors"
            >
              Accept Risk
            </button>
            <button
              onClick={() => handleAction("watchlist")}
              aria-label="Add to Watchlist"
              className="px-3 py-2 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded transition-colors"
            >
              Watchlist
            </button>
          </div>
          <button
            onClick={() => handleAction("export")}
            aria-label="Export CVE"
            className="w-full mt-2 px-3 py-2 border border-gray-600 hover:border-gray-500 text-gray-300 text-sm rounded transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export
          </button>
        </section>
      </div>
    </div>
  );
}

// ============================================================================
// Risk Radar Mini Chart
// ============================================================================

interface RiskRadarMiniProps {
  cvss: number;
  epss: number;
  isKev: boolean;
  exploitCount: number;
  assetCount: number;
}

function RiskRadarMini({ cvss, epss, isKev, exploitCount, assetCount }: RiskRadarMiniProps) {
  const centerX = 80;
  const centerY = 60;
  const maxRadius = 50;

  // Normalize values (0-1)
  const values = [
    cvss / 10, // CVSS
    epss, // EPSS
    isKev ? 1 : 0, // KEV
    Math.min(exploitCount / 10, 1), // Exploitability
    Math.min(assetCount / 100, 1), // Asset Impact
  ];

  const labels = ["CVSS", "EPSS", "KEV", "Exploits", "Assets"];
  const angleStep = (Math.PI * 2) / 5;

  // Calculate polygon points
  const points = values
    .map((value, i) => {
      const angle = i * angleStep - Math.PI / 2;
      const radius = value * maxRadius;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      return `${x},${y}`;
    })
    .join(" ");

  // Grid circles
  const gridCircles = [0.25, 0.5, 0.75, 1].map((scale) => (
    <circle
      key={scale}
      cx={centerX}
      cy={centerY}
      r={maxRadius * scale}
      fill="none"
      stroke="#374151"
      strokeWidth="1"
    />
  ));

  // Axis lines
  const axisLines = labels.map((_, i) => {
    const angle = i * angleStep - Math.PI / 2;
    const x2 = centerX + Math.cos(angle) * maxRadius;
    const y2 = centerY + Math.sin(angle) * maxRadius;
    return (
      <line
        key={i}
        x1={centerX}
        y1={centerY}
        x2={x2}
        y2={y2}
        stroke="#374151"
        strokeWidth="1"
      />
    );
  });

  // Labels
  const labelElements = labels.map((label, i) => {
    const angle = i * angleStep - Math.PI / 2;
    const x = centerX + Math.cos(angle) * (maxRadius + 15);
    const y = centerY + Math.sin(angle) * (maxRadius + 15);
    return (
      <text
        key={i}
        x={x}
        y={y}
        textAnchor="middle"
        dominantBaseline="middle"
        className="text-[8px] fill-gray-500"
      >
        {label}
      </text>
    );
  });

  return (
    <svg width="160" height="120" viewBox="0 0 160 120">
      {gridCircles}
      {axisLines}
      <polygon
        points={points}
        fill="rgba(6, 182, 212, 0.3)"
        stroke="#06b6d4"
        strokeWidth="2"
      />
      {/* Data points */}
      {values.map((value, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const radius = value * maxRadius;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        return (
          <circle
            key={i}
            cx={x}
            cy={y}
            r="3"
            fill="#06b6d4"
          />
        );
      })}
      {labelElements}
    </svg>
  );
}
