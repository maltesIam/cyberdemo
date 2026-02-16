import { useState, useMemo } from "react";
import clsx from "clsx";
import { format } from "date-fns";
import { useAssets, useAsset } from "../hooks/useApi";
import type { Asset } from "../types";

// Layer types and column definitions
export type AssetLayer = "base" | "edr" | "siem" | "ctem";

export const LAYER_COLUMNS: Record<AssetLayer, string[]> = {
  base: ["hostname", "os", "owner", "network"],
  edr: ["detectionCount", "lastAlert"],
  siem: ["incidentCount", "severity"],
  ctem: ["riskColor", "cveCount"],
};

const LAYER_LABELS: Record<AssetLayer, string> = {
  base: "Base",
  edr: "EDR",
  siem: "SIEM",
  ctem: "CTEM",
};

interface FilterState {
  search: string;
  type: string;
  os: string;
  riskMin: number;
  riskMax: number;
  tags: string[];
}

function RiskBadge({ score }: { score: number }) {
  let color = "bg-green-900 text-green-300";
  let label = "Low";

  if (score >= 80) {
    color = "bg-red-900 text-red-300";
    label = "Critical";
  } else if (score >= 60) {
    color = "bg-orange-900 text-orange-300";
    label = "High";
  } else if (score >= 40) {
    color = "bg-yellow-900 text-yellow-300";
    label = "Medium";
  }

  return (
    <span className={clsx("px-2 py-1 rounded text-xs font-medium", color)}>
      {label} ({score})
    </span>
  );
}

function AssetDetailPanel({ assetId, onClose }: { assetId: string; onClose: () => void }) {
  const { data: asset, isLoading, error } = useAsset(assetId);

  if (isLoading) {
    return (
      <div className="fixed inset-y-0 right-0 w-96 bg-gray-800 border-l border-gray-700 shadow-xl z-50 overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-center h-64">
            <svg className="w-8 h-8 animate-spin text-cyan-500" fill="none" viewBox="0 0 24 24">
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
          </div>
        </div>
      </div>
    );
  }

  if (error || !asset) {
    return (
      <div className="fixed inset-y-0 right-0 w-96 bg-gray-800 border-l border-gray-700 shadow-xl z-50">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-white">Asset Details</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white">
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
          <div className="text-red-400">Failed to load asset details</div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-gray-800 border-l border-gray-700 shadow-xl z-50 overflow-y-auto">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-white">Asset Details</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
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

        <div className="space-y-6">
          {/* Basic Info */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-3">Basic Information</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-500">Hostname</span>
                <span className="text-white font-mono">{asset.hostname}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">IP Address</span>
                <span className="text-white font-mono">{asset.ip}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">MAC Address</span>
                <span className="text-white font-mono text-sm">{asset.mac}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Type</span>
                <span className="text-white capitalize">{asset.type.replace("_", " ")}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">OS</span>
                <span className="text-white">
                  {asset.os} {asset.os_version}
                </span>
              </div>
            </div>
          </div>

          {/* Owner Info */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-3">Ownership</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-500">Owner</span>
                <span className="text-white">{asset.owner}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Department</span>
                <span className="text-white">{asset.department}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Site</span>
                <span className="text-white">{asset.site}</span>
              </div>
            </div>
          </div>

          {/* Risk Score */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-3">Risk Assessment</h3>
            <div className="flex items-center justify-between">
              <span className="text-gray-500">Risk Score</span>
              <RiskBadge score={asset.risk_score} />
            </div>
          </div>

          {/* Tags */}
          {asset.tags.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-3">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {asset.tags.map((tag) => (
                  <span key={tag} className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Open Ports */}
          {asset.open_ports.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-3">Open Ports</h3>
              <div className="flex flex-wrap gap-2">
                {asset.open_ports.map((port) => (
                  <span
                    key={port}
                    className="px-2 py-1 bg-cyan-900/50 text-cyan-300 rounded text-xs font-mono"
                  >
                    {port}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Vulnerabilities */}
          {asset.vulnerabilities.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-3">
                Vulnerabilities ({asset.vulnerabilities.length})
              </h3>
              <div className="space-y-2">
                {asset.vulnerabilities.slice(0, 5).map((vuln) => (
                  <div key={vuln.cve_id} className="p-2 bg-gray-900 rounded border border-gray-700">
                    <div className="flex items-center justify-between">
                      <span className="text-cyan-400 font-mono text-sm">{vuln.cve_id}</span>
                      <span
                        className={clsx(
                          "text-xs px-1.5 py-0.5 rounded",
                          vuln.severity === "critical" && "bg-red-900 text-red-300",
                          vuln.severity === "high" && "bg-orange-900 text-orange-300",
                          vuln.severity === "medium" && "bg-yellow-900 text-yellow-300",
                          vuln.severity === "low" && "bg-green-900 text-green-300",
                        )}
                      >
                        CVSS {vuln.cvss_score.toFixed(1)}
                      </span>
                    </div>
                    <p className="text-gray-400 text-xs mt-1 line-clamp-2">{vuln.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Last Seen */}
          <div className="pt-4 border-t border-gray-700">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Last Seen</span>
              <span className="text-gray-400">{format(new Date(asset.last_seen), "PPpp")}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Layer Toggle Button Component
function LayerToggle({
  activeLayers,
  onToggle,
}: {
  activeLayers: AssetLayer[];
  onToggle: (layer: AssetLayer) => void;
}) {
  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm text-gray-400 mr-2">Layers:</span>
      {(Object.keys(LAYER_LABELS) as AssetLayer[]).map((layer) => {
        const isActive = activeLayers.includes(layer);
        return (
          <button
            key={layer}
            onClick={() => onToggle(layer)}
            className={clsx(
              "px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
              isActive ? "bg-cyan-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600",
            )}
          >
            {LAYER_LABELS[layer]}
          </button>
        );
      })}
    </div>
  );
}

export function AssetsPage() {
  const [filters, setFilters] = useState<FilterState>({
    search: "",
    type: "",
    os: "",
    riskMin: 0,
    riskMax: 100,
    tags: [],
  });
  const [page, setPage] = useState(1);
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const [activeLayers, setActiveLayers] = useState<AssetLayer[]>(["base"]);

  // Toggle layer function
  const handleLayerToggle = (layer: AssetLayer) => {
    setActiveLayers((prev) => {
      if (prev.includes(layer)) {
        // Don't allow removing all layers - keep at least base
        if (prev.length === 1 && layer === "base") return prev;
        return prev.filter((l) => l !== layer);
      }
      return [...prev, layer];
    });
  };

  // Get visible columns based on active layers
  const visibleColumns = useMemo(() => {
    const columns: string[] = [];
    activeLayers.forEach((layer) => {
      LAYER_COLUMNS[layer].forEach((col) => {
        if (!columns.includes(col)) {
          columns.push(col);
        }
      });
    });
    return columns;
  }, [activeLayers]);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 20,
      search: filters.search || undefined,
      type: filters.type || undefined,
      os: filters.os || undefined,
      risk_min: filters.riskMin > 0 ? filters.riskMin : undefined,
      risk_max: filters.riskMax < 100 ? filters.riskMax : undefined,
    }),
    [page, filters],
  );

  const { data: assetsData, isLoading, error } = useAssets(queryParams);

  const handleFilterChange = (key: keyof FilterState, value: string | number) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Assets</h1>
        <p className="text-gray-400 mt-1">Manage and monitor your infrastructure assets</p>
      </div>

      {/* Layer Toggle */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <LayerToggle activeLayers={activeLayers} onToggle={handleLayerToggle} />
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Search */}
          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-400 mb-1">Search</label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => handleFilterChange("search", e.target.value)}
              placeholder="Hostname, IP, owner..."
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>

          {/* Type Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Type</label>
            <select
              value={filters.type}
              onChange={(e) => handleFilterChange("type", e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All Types</option>
              <option value="workstation">Workstation</option>
              <option value="server">Server</option>
              <option value="laptop">Laptop</option>
              <option value="virtual_machine">Virtual Machine</option>
              <option value="container">Container</option>
            </select>
          </div>

          {/* OS Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">OS</label>
            <select
              value={filters.os}
              onChange={(e) => handleFilterChange("os", e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All OS</option>
              <option value="Windows">Windows</option>
              <option value="Linux">Linux</option>
              <option value="macOS">macOS</option>
            </select>
          </div>

          {/* Risk Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Risk Score</label>
            <select
              value={`${filters.riskMin}-${filters.riskMax}`}
              onChange={(e) => {
                const [min, max] = e.target.value.split("-").map(Number);
                setFilters((prev) => ({ ...prev, riskMin: min, riskMax: max }));
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="0-100">All Risk Levels</option>
              <option value="80-100">Critical (80-100)</option>
              <option value="60-79">High (60-79)</option>
              <option value="40-59">Medium (40-59)</option>
              <option value="0-39">Low (0-39)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <svg className="w-8 h-8 animate-spin text-cyan-500" fill="none" viewBox="0 0 24 24">
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
          </div>
        )}

        {error && (
          <div className="p-8 text-center">
            <p className="text-red-400">Failed to load assets: {error.message}</p>
          </div>
        )}

        {assetsData && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-900">
                  <tr>
                    {/* Base Layer Columns */}
                    {visibleColumns.includes("hostname") && (
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Hostname
                      </th>
                    )}
                    {visibleColumns.includes("network") && (
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        IP
                      </th>
                    )}
                    {visibleColumns.includes("os") && (
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        OS
                      </th>
                    )}
                    {visibleColumns.includes("owner") && (
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Owner
                      </th>
                    )}
                    {/* EDR Layer Columns */}
                    {visibleColumns.includes("detectionCount") && (
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Detection Count
                      </th>
                    )}
                    {visibleColumns.includes("lastAlert") && (
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Last Alert
                      </th>
                    )}
                    {/* SIEM Layer Columns */}
                    {visibleColumns.includes("incidentCount") && (
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Incident Count
                      </th>
                    )}
                    {visibleColumns.includes("severity") && (
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Severity
                      </th>
                    )}
                    {/* CTEM Layer Columns */}
                    {visibleColumns.includes("riskColor") && (
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Risk
                      </th>
                    )}
                    {visibleColumns.includes("cveCount") && (
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        CVE Count
                      </th>
                    )}
                    {/* Always show tags */}
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Tags
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {assetsData.data.map((asset: Asset) => (
                    <tr
                      key={asset.id}
                      onClick={() => setSelectedAssetId(asset.id)}
                      className="hover:bg-gray-750 cursor-pointer transition-colors"
                    >
                      {/* Base Layer Cells */}
                      {visibleColumns.includes("hostname") && (
                        <td className="px-4 py-3">
                          <div className="flex items-center space-x-2">
                            <svg
                              className="w-4 h-4 text-gray-500"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                              />
                            </svg>
                            <span className="text-white font-mono">{asset.hostname}</span>
                          </div>
                        </td>
                      )}
                      {visibleColumns.includes("network") && (
                        <td className="px-4 py-3 text-gray-300 font-mono text-sm">{asset.ip}</td>
                      )}
                      {visibleColumns.includes("os") && (
                        <td className="px-4 py-3 text-gray-300">{asset.os}</td>
                      )}
                      {visibleColumns.includes("owner") && (
                        <td className="px-4 py-3 text-gray-300">{asset.owner}</td>
                      )}
                      {/* EDR Layer Cells - Using synthetic data */}
                      {visibleColumns.includes("detectionCount") && (
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 bg-purple-900/50 text-purple-300 rounded text-sm font-medium">
                            {Math.floor(asset.risk_score / 10)}
                          </span>
                        </td>
                      )}
                      {visibleColumns.includes("lastAlert") && (
                        <td className="px-4 py-3 text-gray-400 text-sm">
                          {asset.risk_score > 50
                            ? format(new Date(asset.last_seen), "MMM d, HH:mm")
                            : "-"}
                        </td>
                      )}
                      {/* SIEM Layer Cells - Using synthetic data */}
                      {visibleColumns.includes("incidentCount") && (
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 bg-blue-900/50 text-blue-300 rounded text-sm font-medium">
                            {Math.floor(asset.risk_score / 20)}
                          </span>
                        </td>
                      )}
                      {visibleColumns.includes("severity") && (
                        <td className="px-4 py-3">
                          <span
                            className={clsx(
                              "px-2 py-1 rounded text-xs font-medium",
                              asset.risk_score >= 80 && "bg-red-900 text-red-300",
                              asset.risk_score >= 60 &&
                                asset.risk_score < 80 &&
                                "bg-orange-900 text-orange-300",
                              asset.risk_score >= 40 &&
                                asset.risk_score < 60 &&
                                "bg-yellow-900 text-yellow-300",
                              asset.risk_score < 40 && "bg-green-900 text-green-300",
                            )}
                          >
                            {asset.risk_score >= 80
                              ? "Critical"
                              : asset.risk_score >= 60
                                ? "High"
                                : asset.risk_score >= 40
                                  ? "Medium"
                                  : "Low"}
                          </span>
                        </td>
                      )}
                      {/* CTEM Layer Cells */}
                      {visibleColumns.includes("riskColor") && (
                        <td className="px-4 py-3">
                          <RiskBadge score={asset.risk_score} />
                        </td>
                      )}
                      {visibleColumns.includes("cveCount") && (
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 bg-red-900/50 text-red-300 rounded text-sm font-medium">
                            {asset.vulnerabilities?.length ?? 0}
                          </span>
                        </td>
                      )}
                      {/* Tags - Always visible */}
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-1">
                          {asset.tags.slice(0, 3).map((tag) => (
                            <span
                              key={tag}
                              className="px-1.5 py-0.5 bg-gray-700 text-gray-400 rounded text-xs"
                            >
                              {tag}
                            </span>
                          ))}
                          {asset.tags.length > 3 && (
                            <span className="px-1.5 py-0.5 text-gray-500 text-xs">
                              +{asset.tags.length - 3}
                            </span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 bg-gray-900 border-t border-gray-700 flex items-center justify-between">
              <div className="text-sm text-gray-400">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, assetsData.total)} of{" "}
                {assetsData.total} assets
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
                  disabled={page >= assetsData.total_pages}
                  className="px-3 py-1 bg-gray-700 text-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}

        {assetsData?.data.length === 0 && (
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
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
            <p className="text-gray-400">No assets found</p>
            <p className="text-gray-500 text-sm mt-1">
              Try adjusting your filters or generate some data
            </p>
          </div>
        )}
      </div>

      {/* Detail Panel */}
      {selectedAssetId && (
        <AssetDetailPanel assetId={selectedAssetId} onClose={() => setSelectedAssetId(null)} />
      )}
    </div>
  );
}
