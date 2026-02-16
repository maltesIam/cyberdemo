/**
 * CVEAssetsPage - Table of affected assets for a CVE
 *
 * Features:
 * - Table of affected assets
 * - Pagination
 * - Asset criticality badges
 * - Link back to CVE
 * - Remediation status
 */

import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import clsx from "clsx";
import { useQuery } from "@tanstack/react-query";
import { Breadcrumbs } from "../../components/vuln-views/Breadcrumbs";
import * as api from "../../services/api";

interface AffectedAsset {
  asset_id: string;
  hostname: string;
  ip_address: string;
  asset_type: string;
  criticality: "critical" | "high" | "medium" | "low";
  business_unit: string;
  detection_date: string;
  remediation_status: string;
}

interface CVEAssetsResponse {
  cve_id: string;
  assets: AffectedAsset[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export function CVEAssetsPage() {
  const { cveId } = useParams<{ cveId: string }>();
  const navigate = useNavigate();
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useQuery<CVEAssetsResponse>({
    queryKey: ["cve-assets", cveId, page],
    queryFn: async () => {
      if (!cveId) throw new Error("CVE ID required");
      return api.getCVEAffectedAssets(cveId, { page, page_size: 10 });
    },
    enabled: !!cveId,
  });

  const criticalityColors = {
    critical: "text-red-400 bg-red-500/10 border-red-500/30",
    high: "text-orange-400 bg-orange-500/10 border-orange-500/30",
    medium: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30",
    low: "text-green-400 bg-green-500/10 border-green-500/30",
  };

  const statusColors: Record<string, string> = {
    pending: "text-gray-400 bg-gray-500/10",
    in_progress: "text-blue-400 bg-blue-500/10",
    remediated: "text-green-400 bg-green-500/10",
    accepted_risk: "text-yellow-400 bg-yellow-500/10",
  };

  if (isLoading) {
    return (
      <div className="h-full flex flex-col">
        <div className="mb-4">
          <Breadcrumbs
            items={[
              { label: "Vulnerabilities", href: "/vulnerabilities" },
              { label: cveId ?? "Loading...", href: `/vulnerabilities/cves/${cveId}` },
              { label: "Affected Assets" },
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
            <span className="text-gray-400">Loading affected assets...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex flex-col">
        <div className="mb-4">
          <Breadcrumbs
            items={[
              { label: "Vulnerabilities", href: "/vulnerabilities" },
              { label: cveId ?? "Error" },
              { label: "Affected Assets" },
            ]}
          />
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-500 text-xl mb-2">Error</div>
            <p className="text-gray-400">
              {error instanceof Error ? error.message : "Failed to load assets"}
            </p>
            <button
              onClick={() => navigate(`/vulnerabilities/cves/${cveId}`)}
              className="mt-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg"
            >
              Back to CVE Details
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: "Vulnerabilities", href: "/vulnerabilities" },
          { label: cveId ?? "", href: `/vulnerabilities/cves/${cveId}` },
          { label: "Affected Assets" },
        ]}
      />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Link
              to={`/vulnerabilities/cves/${cveId}`}
              className="text-cyan-400 hover:text-cyan-300"
            >
              {cveId}
            </Link>
            <span className="text-gray-500">/</span>
            <span>Affected Assets</span>
          </h1>
          <p className="text-gray-400 mt-1">
            <span className="text-cyan-400 font-medium">{data?.total ?? 0}</span> assets affected by this vulnerability
          </p>
        </div>
        <button
          onClick={() => navigate(-1)}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back
        </button>
      </div>

      {/* Table */}
      <div className="flex-1 bg-gray-800 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900/50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  Hostname
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  IP Address
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  Type
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  Criticality
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  Business Unit
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  Detected
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {data?.assets.map((asset) => (
                <tr
                  key={asset.asset_id}
                  className="hover:bg-gray-700/50 transition-colors"
                >
                  <td className="px-4 py-3 text-sm text-white font-mono">
                    {asset.hostname}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-300 font-mono">
                    {asset.ip_address}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-400 capitalize">
                    {asset.asset_type}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={clsx(
                        "px-2 py-1 rounded text-xs font-medium border capitalize",
                        criticalityColors[asset.criticality]
                      )}
                    >
                      {asset.criticality}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-300">
                    {asset.business_unit}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-400">
                    {asset.detection_date}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={clsx(
                        "px-2 py-1 rounded text-xs font-medium capitalize",
                        statusColors[asset.remediation_status] ?? "text-gray-400 bg-gray-500/10"
                      )}
                    >
                      {asset.remediation_status.replace("_", " ")}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Empty State */}
        {data?.assets.length === 0 && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <svg
                className="w-12 h-12 text-gray-600 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
              <p className="text-gray-500">No affected assets found</p>
            </div>
          </div>
        )}
      </div>

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <nav
          aria-label="Pagination"
          className="flex items-center justify-between bg-gray-800 rounded-lg px-4 py-3"
        >
          <div className="text-sm text-gray-400">
            Page {data.page} of {data.total_pages}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              aria-label="Previous"
              className={clsx(
                "px-3 py-1 rounded text-sm",
                page === 1
                  ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                  : "bg-gray-700 hover:bg-gray-600 text-white"
              )}
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
              disabled={page === data.total_pages}
              aria-label="Next"
              className={clsx(
                "px-3 py-1 rounded text-sm",
                page === data.total_pages
                  ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                  : "bg-gray-700 hover:bg-gray-600 text-white"
              )}
            >
              Next
            </button>
          </div>
        </nav>
      )}
    </div>
  );
}
