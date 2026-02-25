import { useState, useMemo } from "react";
import clsx from "clsx";
import { useCTEMFindings, useCTEMSummary } from "../hooks/useApi";
import type { CTEMFinding } from "../types";

// ---------------------------------------------------------------------------
// Helper components
// ---------------------------------------------------------------------------

function SeverityBadge({ severity }: { severity: string }) {
  let color = "bg-[var(--badge-low-bg)] text-[var(--badge-low-text)]";

  if (severity === "critical") {
    color = "bg-[var(--badge-critical-bg)] text-[var(--badge-critical-text)]";
  } else if (severity === "high") {
    color = "bg-[var(--badge-high-bg)] text-[var(--badge-high-text)]";
  } else if (severity === "medium") {
    color = "bg-[var(--badge-medium-bg)] text-[var(--badge-medium-text)]";
  }

  return (
    <span className={clsx("px-2 py-1 rounded text-xs font-medium capitalize", color)}>
      {severity}
    </span>
  );
}

function ScoreBadge({ score, max }: { score: number | undefined; max: number }) {
  if (score == null) {
    return <span className="text-tertiary text-sm">--</span>;
  }

  const ratio = score / max;
  let color = "text-[var(--score-low)]";
  if (ratio >= 0.8) {
    color = "text-[var(--score-critical)]";
  } else if (ratio >= 0.6) {
    color = "text-[var(--score-high)]";
  } else if (ratio >= 0.4) {
    color = "text-[var(--score-medium)]";
  }

  return <span className={clsx("font-mono text-sm font-semibold", color)}>{score.toFixed(2)}</span>;
}

function ExposureBadge({ exposure }: { exposure: string }) {
  let color = "bg-tertiary text-secondary";

  if (exposure === "public") {
    color = "bg-[var(--ctem-exposure-public-bg)] text-[var(--ctem-exposure-public-text)]";
  } else if (exposure === "internal") {
    color = "bg-[var(--ctem-exposure-internal-bg)] text-[var(--ctem-exposure-internal-text)]";
  }

  return (
    <span className={clsx("px-2 py-0.5 rounded text-xs font-medium capitalize", color)}>
      {exposure}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  let color = "bg-tertiary text-secondary";

  if (status === "open" || status === "new") {
    color = "bg-[var(--ctem-status-open-bg)] text-[var(--ctem-status-open-text)]";
  } else if (status === "in_progress" || status === "investigating") {
    color = "bg-[var(--ctem-status-inprogress-bg)] text-[var(--ctem-status-inprogress-text)]";
  } else if (status === "resolved" || status === "mitigated") {
    color = "bg-[var(--ctem-status-resolved-bg)] text-[var(--ctem-status-resolved-text)]";
  } else if (status === "accepted") {
    color = "bg-[var(--ctem-status-accepted-bg)] text-[var(--ctem-status-accepted-text)]";
  }

  return (
    <span className={clsx("px-2 py-0.5 rounded text-xs font-medium capitalize", color)}>
      {status?.replace("_", " ") ?? "unknown"}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Summary cards
// ---------------------------------------------------------------------------

interface SummaryCardProps {
  label: string;
  value: number;
  color: string;
}

function SummaryCard({ label, value, color }: SummaryCardProps) {
  return (
    <div className="bg-secondary rounded-lg p-4 border border-primary">
      <p className="text-secondary text-sm">{label}</p>
      <p className={clsx("text-2xl font-bold mt-1", color)}>{value}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export function CTEMPage() {
  const [page, setPage] = useState(1);
  const [severityFilter, setSeverityFilter] = useState("");
  const [exposureFilter, setExposureFilter] = useState("");
  const pageSize = 20;

  const queryParams = useMemo(
    () => ({
      page,
      page_size: pageSize,
      severity: severityFilter || undefined,
      exposure: exposureFilter || undefined,
    }),
    [page, severityFilter, exposureFilter],
  );

  const { data: findingsData, isLoading, error } = useCTEMFindings(queryParams);
  const { data: summary } = useCTEMSummary();

  const findings = findingsData?.findings ?? [];
  const total = findingsData?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  // Derive summary counts from the summary endpoint with defensive access
  const criticalCount = summary?.severity_distribution?.critical ?? 0;
  const highCount = summary?.severity_distribution?.high ?? 0;
  const mediumCount = summary?.severity_distribution?.medium ?? 0;
  const lowCount = summary?.severity_distribution?.low ?? 0;
  const publicExposed = summary?.exposure_distribution?.public ?? 0;

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <svg
            className="w-12 h-12 animate-spin text-[var(--accent-link)] mx-auto mb-4"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p className="text-secondary">Loading CTEM findings...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center bg-[var(--error-bg)] border border-[var(--error-border)] rounded-lg p-8">
          <svg
            className="w-12 h-12 text-[var(--error-text)] mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <p className="text-[var(--error-text)] font-medium">Failed to load CTEM data</p>
          <p className="text-tertiary text-sm mt-2">{error?.message ?? "Unknown error"}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-primary">CTEM - Vulnerability Exposure</h1>
        <p className="text-secondary mt-1">
          Continuous Threat Exposure Management - enriched vulnerability findings
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <SummaryCard label="Critical" value={criticalCount} color="text-[var(--score-critical)]" />
        <SummaryCard label="High" value={highCount} color="text-[var(--score-high)]" />
        <SummaryCard label="Medium" value={mediumCount} color="text-[var(--score-medium)]" />
        <SummaryCard label="Low" value={lowCount} color="text-[var(--score-low)]" />
        <SummaryCard label="Public Exposed" value={publicExposed} color="text-[var(--kpi-purple)]" />
      </div>

      {/* Filters */}
      <div className="bg-secondary rounded-lg p-4 border border-primary">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-secondary mb-1">Severity</label>
            <select
              value={severityFilter}
              onChange={(e) => {
                setSeverityFilter(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-tertiary border border-primary rounded-lg text-primary focus:outline-none focus:ring-2 focus:ring-[var(--border-focus)]"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-secondary mb-1">Exposure</label>
            <select
              value={exposureFilter}
              onChange={(e) => {
                setExposureFilter(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-tertiary border border-primary rounded-lg text-primary focus:outline-none focus:ring-2 focus:ring-[var(--border-focus)]"
            >
              <option value="">All Exposures</option>
              <option value="public">Public</option>
              <option value="internal">Internal</option>
              <option value="none">None</option>
            </select>
          </div>
        </div>
      </div>

      {/* Findings Table */}
      <div className="bg-secondary rounded-lg border border-primary overflow-hidden">
        {findings.length > 0 && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-primary">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      CVE ID
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Severity
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      CVSS Score
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      EPSS Score
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Risk Score
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Threat Actors
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Exposure
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--border-primary)]">
                  {findings.map((finding: CTEMFinding) => (
                    <tr
                      key={finding?.finding_id ?? finding?.cve_id}
                      className="hover:bg-hover transition-colors"
                    >
                      <td className="px-4 py-3">
                        <span className="text-[var(--accent-link)] font-mono text-sm">
                          {finding?.cve_id ?? "--"}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <SeverityBadge severity={finding?.severity ?? "low"} />
                      </td>
                      <td className="px-4 py-3">
                        <ScoreBadge score={finding?.cvss_score} max={10} />
                      </td>
                      <td className="px-4 py-3">
                        <ScoreBadge score={finding?.epss_score} max={1} />
                      </td>
                      <td className="px-4 py-3">
                        <ScoreBadge score={finding?.risk_score} max={100} />
                      </td>
                      <td className="px-4 py-3">
                        <ThreatActorsList actors={finding?.threat_actors} />
                      </td>
                      <td className="px-4 py-3">
                        <ExposureBadge exposure={finding?.exposure ?? "none"} />
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={finding?.status ?? "unknown"} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 bg-primary border-t border-primary flex items-center justify-between">
              <div className="text-sm text-secondary">
                Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total}{" "}
                findings
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 bg-tertiary text-secondary rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-tertiary"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page >= totalPages}
                  className="px-3 py-1 bg-tertiary text-secondary rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-tertiary"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}

        {findings.length === 0 && !isLoading && (
          <div className="p-8 text-center">
            <svg
              className="w-12 h-12 text-tertiary mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
            <p className="text-secondary">No CTEM findings found</p>
            <p className="text-tertiary text-sm mt-1">
              Generate data and run enrichment to populate vulnerability findings
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Threat Actors inline list
// ---------------------------------------------------------------------------

function ThreatActorsList({ actors }: { actors: string[] | undefined }) {
  if (!actors || actors.length === 0) {
    return <span className="text-tertiary text-sm">--</span>;
  }

  const visible = actors.slice(0, 2);
  const remaining = actors.length - visible.length;

  return (
    <div className="flex flex-wrap gap-1">
      {visible.map((actor) => (
        <span
          key={actor}
          className="px-1.5 py-0.5 bg-[var(--ctem-actor-bg)] text-[var(--ctem-actor-text)] rounded text-xs"
        >
          {actor}
        </span>
      ))}
      {remaining > 0 && <span className="px-1.5 py-0.5 text-tertiary text-xs">+{remaining}</span>}
    </div>
  );
}
