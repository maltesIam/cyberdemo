/**
 * CVEDetailPage - Full-page CVE detail view
 *
 * Features:
 * - Route param :cveId extraction
 * - Fetch from /api/vulnerabilities/enriched/:cve_id
 * - All CVE detail sections
 * - Navigation breadcrumbs
 * - Back button
 */

import { useParams, Link, useNavigate } from "react-router-dom";
import clsx from "clsx";
import { useVulnerabilityDetail } from "../../hooks/useVulnerabilities";
import { Breadcrumbs } from "../../components/vuln-views/Breadcrumbs";

export function CVEDetailPage() {
  const { cveId } = useParams<{ cveId: string }>();
  const navigate = useNavigate();
  const { data: cve, isLoading, error } = useVulnerabilityDetail(cveId ?? null);

  if (isLoading) {
    return (
      <div className="h-full flex flex-col">
        <div className="mb-4">
          <Breadcrumbs
            items={[
              { label: "Vulnerabilities", href: "/vulnerabilities" },
              { label: cveId ?? "Loading..." },
            ]}
          />
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <svg
              className="w-12 h-12 text-cyan-500 animate-spin"
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
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            <span className="text-gray-400">Loading CVE details...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !cve) {
    return (
      <div className="h-full flex flex-col">
        <div className="mb-4">
          <Breadcrumbs
            items={[
              { label: "Vulnerabilities", href: "/vulnerabilities" },
              { label: cveId ?? "Error" },
            ]}
          />
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-500 text-xl mb-2">Error</div>
            <p className="text-gray-400">
              {error instanceof Error ? error.message : "CVE not found"}
            </p>
            <button
              onClick={() => navigate("/vulnerabilities")}
              className="mt-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg"
            >
              Back to Vulnerabilities
            </button>
          </div>
        </div>
      </div>
    );
  }

  const severityColors = {
    Critical: "text-red-500 bg-red-500/10 border-red-500/30",
    High: "text-orange-500 bg-orange-500/10 border-orange-500/30",
    Medium: "text-yellow-500 bg-yellow-500/10 border-yellow-500/30",
    Low: "text-green-500 bg-green-500/10 border-green-500/30",
  };

  const ssvcColors = {
    Act: "text-red-400 bg-red-500/10 border-red-500/30",
    Attend: "text-orange-400 bg-orange-500/10 border-orange-500/30",
    "Track*": "text-yellow-400 bg-yellow-500/10 border-yellow-500/30",
    Track: "text-green-400 bg-green-500/10 border-green-500/30",
  };

  const statusColors = {
    open: "text-gray-400 bg-gray-500/10",
    in_progress: "text-blue-400 bg-blue-500/10",
    remediated: "text-green-400 bg-green-500/10",
    accepted_risk: "text-yellow-400 bg-yellow-500/10",
    false_positive: "text-purple-400 bg-purple-500/10",
  };

  return (
    <div className="h-full flex flex-col space-y-4 overflow-auto">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: "Vulnerabilities", href: "/vulnerabilities" },
          { label: cve.cve_id },
        ]}
      />

      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-white">{cve.cve_id}</h1>
            <span
              className={clsx(
                "px-2 py-1 rounded text-xs font-medium border",
                severityColors[cve.severity]
              )}
            >
              {cve.severity}
            </span>
            {cve.is_kev && (
              <span className="px-2 py-1 rounded text-xs font-medium bg-orange-500/20 text-orange-400 border border-orange-500/30 animate-pulse">
                KEV
              </span>
            )}
            <span
              className={clsx(
                "px-2 py-1 rounded text-xs font-medium border",
                ssvcColors[cve.ssvc_decision]
              )}
            >
              SSVC: {cve.ssvc_decision}
            </span>
          </div>
          <h2 className="text-lg text-gray-300 mb-4">{cve.title}</h2>
        </div>
        <button
          onClick={() => navigate(-1)}
          aria-label="Back"
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back
        </button>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 flex-1">
        {/* Left Column - Main Info */}
        <div className="lg:col-span-2 space-y-4">
          {/* Description */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">
              Description
            </h3>
            <p className="text-gray-300">
              {cve.description ?? "No description available."}
            </p>
          </div>

          {/* Scores Section */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">
              Risk Scores
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <ScoreCard
                label="CVSS v3"
                value={cve.cvss_v3_score.toFixed(1)}
                subtext={cve.cvss_v3_vector}
                color={cve.cvss_v3_score >= 9 ? "red" : cve.cvss_v3_score >= 7 ? "orange" : "yellow"}
              />
              <ScoreCard
                label="EPSS"
                value={`${(cve.epss_score * 100).toFixed(1)}%`}
                subtext={cve.epss_percentile ? `${cve.epss_percentile}th percentile` : undefined}
                color={cve.epss_score >= 0.9 ? "red" : cve.epss_score >= 0.5 ? "orange" : "cyan"}
              />
              <ScoreCard
                label="Risk Score"
                value={cve.risk_score?.toString() ?? "N/A"}
                color="purple"
              />
              <ScoreCard
                label="Exploits"
                value={`${cve.exploit_count} exploit${cve.exploit_count !== 1 ? "s" : ""}`}
                subtext={cve.exploit_maturity ?? undefined}
                color={cve.exploit_count > 0 ? "red" : "green"}
              />
            </div>
          </div>

          {/* CWE & Ecosystems */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">
              Technical Details
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-gray-500 text-sm">CWE IDs:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {cve.cwe_ids?.map((cwe) => (
                    <span
                      key={cwe}
                      className="px-2 py-1 bg-gray-700 rounded text-xs text-cyan-400"
                    >
                      {cwe}
                    </span>
                  )) ?? <span className="text-gray-500">None</span>}
                </div>
              </div>
              <div>
                <span className="text-gray-500 text-sm">Ecosystems:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {cve.ecosystems?.map((eco) => (
                    <span
                      key={eco}
                      className="px-2 py-1 bg-gray-700 rounded text-xs text-purple-400"
                    >
                      {eco}
                    </span>
                  )) ?? <span className="text-gray-500">None</span>}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Metadata */}
        <div className="space-y-4">
          {/* KEV Info */}
          {cve.is_kev && (
            <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-orange-400 uppercase mb-3 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Known Exploited Vulnerability
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Added:</span>
                  <span className="text-white">{cve.kev_date_added}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Due Date:</span>
                  <span className="text-white">{cve.kev_due_date}</span>
                </div>
                {cve.kev_ransomware_use && (
                  <div className="flex items-center gap-2 text-red-400 mt-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    Known Ransomware Use
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Remediation Status */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">
              Remediation
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Status:</span>
                <span
                  className={clsx(
                    "px-2 py-1 rounded text-xs font-medium",
                    statusColors[cve.remediation_status]
                  )}
                >
                  {cve.remediation_status.replace("_", " ")}
                </span>
              </div>
              {cve.assigned_to && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Assigned:</span>
                  <span className="text-white">{cve.assigned_to}</span>
                </div>
              )}
              {cve.sla_due_date && (
                <div className="flex justify-between">
                  <span className="text-gray-400">SLA Due:</span>
                  <span
                    className={clsx(
                      "text-sm",
                      cve.sla_status === "overdue" && "text-red-400",
                      cve.sla_status === "at_risk" && "text-yellow-400",
                      cve.sla_status === "on_track" && "text-green-400"
                    )}
                  >
                    {cve.sla_due_date}
                  </span>
                </div>
              )}
              {cve.patch_available && (
                <div className="flex items-center gap-2 text-green-400 text-sm">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Patch Available
                </div>
              )}
            </div>
          </div>

          {/* Affected Assets */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">
              Affected Assets
            </h3>
            <div className="text-center mb-4">
              <div className="text-3xl font-bold text-cyan-400">
                {cve.affected_asset_count ?? 0}
              </div>
              <div className="text-sm text-gray-500">Total Assets</div>
              {(cve.affected_critical_assets ?? 0) > 0 && (
                <div className="text-sm text-red-400 mt-1">
                  {cve.affected_critical_assets} Critical
                </div>
              )}
            </div>
            <Link
              to={`/vulnerabilities/cves/${cve.cve_id}/assets`}
              aria-label="View Affected Assets"
              className="block w-full text-center px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              View Assets
            </Link>
          </div>

          {/* Exploits */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">
              Exploits
            </h3>
            <div className="text-center mb-4">
              <div
                className={clsx(
                  "text-3xl font-bold",
                  cve.exploit_count > 0 ? "text-red-400" : "text-green-400"
                )}
              >
                {cve.exploit_count}
              </div>
              <div className="text-sm text-gray-500">Known Exploits</div>
              {cve.has_nuclei_template && (
                <div className="text-sm text-purple-400 mt-1 flex items-center justify-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  Nuclei Template
                </div>
              )}
            </div>
            <Link
              to={`/vulnerabilities/cves/${cve.cve_id}/exploits`}
              aria-label="View Exploits"
              className="block w-full text-center px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              View Exploits
            </Link>
          </div>

          {/* Metadata */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">
              Metadata
            </h3>
            <div className="space-y-2 text-sm">
              {cve.published_date && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Published:</span>
                  <span className="text-white">{cve.published_date}</span>
                </div>
              )}
              {cve.last_enriched_at && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Last Enriched:</span>
                  <span className="text-white">
                    {new Date(cve.last_enriched_at).toLocaleDateString()}
                  </span>
                </div>
              )}
              {cve.enrichment_level && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Enrichment:</span>
                  <span className="text-cyan-400 capitalize">
                    {cve.enrichment_level}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Sub-components
// ============================================================================

interface ScoreCardProps {
  label: string;
  value: string;
  subtext?: string;
  color: "red" | "orange" | "yellow" | "green" | "cyan" | "purple";
}

function ScoreCard({ label, value, subtext, color }: ScoreCardProps) {
  const colorClasses = {
    red: "text-red-400",
    orange: "text-orange-400",
    yellow: "text-yellow-400",
    green: "text-green-400",
    cyan: "text-cyan-400",
    purple: "text-purple-400",
  };

  return (
    <div className="bg-gray-900/50 rounded-lg p-3 text-center">
      <div className={clsx("text-2xl font-bold", colorClasses[color])}>
        {value}
      </div>
      <div className="text-xs text-gray-500 uppercase">{label}</div>
      {subtext && (
        <div className="text-xs text-gray-600 mt-1 truncate" title={subtext}>
          {subtext}
        </div>
      )}
    </div>
  );
}
