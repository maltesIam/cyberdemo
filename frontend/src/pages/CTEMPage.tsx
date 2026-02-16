import { useState, useMemo } from "react";
import clsx from "clsx";
import { useCTEMFindings, useCTEMSummary } from "../hooks/useApi";
import type { CTEMFinding } from "../types";

// ---------------------------------------------------------------------------
// Helper components
// ---------------------------------------------------------------------------

function SeverityBadge({ severity }: { severity: string }) {
  let color = "bg-green-900 text-green-300";

  if (severity === "critical") {
    color = "bg-red-900 text-red-300";
  } else if (severity === "high") {
    color = "bg-orange-900 text-orange-300";
  } else if (severity === "medium") {
    color = "bg-yellow-900 text-yellow-300";
  }

  return (
    <span className={clsx("px-2 py-1 rounded text-xs font-medium capitalize", color)}>
      {severity}
    </span>
  );
}

function ScoreBadge({ score, max }: { score: number | undefined; max: number }) {
  if (score == null) {
    return <span className="text-gray-500 text-sm">--</span>;
  }

  const ratio = score / max;
  let color = "text-green-400";
  if (ratio >= 0.8) {
    color = "text-red-400";
  } else if (ratio >= 0.6) {
    color = "text-orange-400";
  } else if (ratio >= 0.4) {
    color = "text-yellow-400";
  }

  return <span className={clsx("font-mono text-sm font-semibold", color)}>{score.toFixed(2)}</span>;
}

function ExposureBadge({ exposure }: { exposure: string }) {
  let color = "bg-gray-700 text-gray-300";

  if (exposure === "public") {
    color = "bg-red-900/60 text-red-300";
  } else if (exposure === "internal") {
    color = "bg-yellow-900/60 text-yellow-300";
  }

  return (
    <span className={clsx("px-2 py-0.5 rounded text-xs font-medium capitalize", color)}>
      {exposure}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  let color = "bg-gray-700 text-gray-300";

  if (status === "open" || status === "new") {
    color = "bg-cyan-900/60 text-cyan-300";
  } else if (status === "in_progress" || status === "investigating") {
    color = "bg-blue-900/60 text-blue-300";
  } else if (status === "resolved" || status === "mitigated") {
    color = "bg-green-900/60 text-green-300";
  } else if (status === "accepted") {
    color = "bg-yellow-900/60 text-yellow-300";
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
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <p className="text-gray-400 text-sm">{label}</p>
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
            className="w-12 h-12 animate-spin text-cyan-500 mx-auto mb-4"
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
          <p className="text-gray-400">Loading CTEM findings...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center bg-red-900/20 border border-red-700 rounded-lg p-8">
          <svg
            className="w-12 h-12 text-red-500 mx-auto mb-4"
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
          <p className="text-red-400 font-medium">Failed to load CTEM data</p>
          <p className="text-gray-500 text-sm mt-2">{error?.message ?? "Unknown error"}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">CTEM - Vulnerability Exposure</h1>
        <p className="text-gray-400 mt-1">
          Continuous Threat Exposure Management - enriched vulnerability findings
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <SummaryCard label="Critical" value={criticalCount} color="text-red-400" />
        <SummaryCard label="High" value={highCount} color="text-orange-400" />
        <SummaryCard label="Medium" value={mediumCount} color="text-yellow-400" />
        <SummaryCard label="Low" value={lowCount} color="text-green-400" />
        <SummaryCard label="Public Exposed" value={publicExposed} color="text-purple-400" />
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Severity</label>
            <select
              value={severityFilter}
              onChange={(e) => {
                setSeverityFilter(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Exposure</label>
            <select
              value={exposureFilter}
              onChange={(e) => {
                setExposureFilter(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
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
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        {findings.length > 0 && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-900">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      CVE ID
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Severity
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      CVSS Score
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      EPSS Score
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Risk Score
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Threat Actors
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Exposure
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {findings.map((finding: CTEMFinding) => (
                    <tr
                      key={finding?.finding_id ?? finding?.cve_id}
                      className="hover:bg-gray-750 transition-colors"
                    >
                      <td className="px-4 py-3">
                        <span className="text-cyan-400 font-mono text-sm">
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
            <div className="px-4 py-3 bg-gray-900 border-t border-gray-700 flex items-center justify-between">
              <div className="text-sm text-gray-400">
                Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total}{" "}
                findings
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 bg-gray-700 text-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page >= totalPages}
                  className="px-3 py-1 bg-gray-700 text-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
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
              className="w-12 h-12 text-gray-600 mx-auto mb-4"
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
            <p className="text-gray-400">No CTEM findings found</p>
            <p className="text-gray-500 text-sm mt-1">
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
    return <span className="text-gray-500 text-sm">--</span>;
  }

  const visible = actors.slice(0, 2);
  const remaining = actors.length - visible.length;

  return (
    <div className="flex flex-wrap gap-1">
      {visible.map((actor) => (
        <span
          key={actor}
          className="px-1.5 py-0.5 bg-purple-900/50 text-purple-300 rounded text-xs"
        >
          {actor}
        </span>
      ))}
      {remaining > 0 && <span className="px-1.5 py-0.5 text-gray-500 text-xs">+{remaining}</span>}
    </div>
  );
}
