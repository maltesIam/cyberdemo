import { useState, useMemo } from "react";
import clsx from "clsx";
import { format } from "date-fns";
import { useDetections, useDetection } from "../hooks/useApi";
import type { Detection } from "../types";

function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    critical: "bg-red-900 text-red-300",
    high: "bg-orange-900 text-orange-300",
    medium: "bg-yellow-900 text-yellow-300",
    low: "bg-green-900 text-green-300",
  };

  return (
    <span
      className={clsx(
        "px-2 py-1 rounded text-xs font-medium",
        colors[severity] || "bg-gray-700 text-gray-300",
      )}
    >
      {severity.toUpperCase()}
    </span>
  );
}

function ProcessTreeModal({ detectionId, onClose }: { detectionId: string; onClose: () => void }) {
  const { data: detection, isLoading, error } = useDetection(detectionId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-gray-800 rounded-lg border border-gray-700 shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Detection Details & Process Tree</h2>
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

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
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
            <div className="text-red-400 text-center py-8">
              Failed to load detection details: {error.message}
            </div>
          )}

          {detection && (
            <div className="space-y-6">
              {/* Detection Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-1">Detection</h4>
                  <p className="text-white font-medium">{detection.technique_name}</p>
                  <p className="text-gray-400 text-sm">{detection.description}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-1">Hostname</h4>
                  <p className="text-cyan-400 font-mono">{detection.hostname}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-1">Detected At</h4>
                  <p className="text-gray-300">{format(new Date(detection.detected_at), "PPpp")}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-1">Severity</h4>
                  <SeverityBadge severity={detection.severity} />
                </div>
              </div>

              {/* MITRE ATT&CK */}
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">MITRE ATT&CK</h4>
                <div className="flex flex-wrap gap-2">
                  <span className="px-2 py-1 bg-purple-900/50 text-purple-300 rounded text-xs">
                    {detection.tactic}
                  </span>
                  <span className="px-2 py-1 bg-cyan-900/50 text-cyan-300 rounded text-xs font-mono">
                    {detection.technique_id}
                  </span>
                </div>
              </div>

              {/* Process Info */}
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-3">Process Information</h4>
                <div className="bg-gray-900 rounded-lg border border-gray-700 p-4 font-mono text-sm">
                  {/* Parent Process */}
                  <div className="mb-4">
                    <div className="flex items-center space-x-2 text-gray-400">
                      <svg
                        className="w-4 h-4"
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
                      <span className="text-orange-400">Parent Process</span>
                    </div>
                    <div className="ml-6 mt-2 space-y-1">
                      <p>
                        <span className="text-gray-500">Name:</span>{" "}
                        <span className="text-white">{detection.parent_process}</span>
                      </p>
                    </div>
                  </div>

                  {/* Current Process */}
                  <div className="ml-8 border-l-2 border-red-700 pl-4">
                    <div className="flex items-center space-x-2 text-red-400">
                      <svg
                        className="w-4 h-4"
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
                      <span>Suspicious Process</span>
                    </div>
                    <div className="mt-2 space-y-1">
                      <p>
                        <span className="text-gray-500">Name:</span>{" "}
                        <span className="text-white">{detection.process_name}</span>
                      </p>
                      <p>
                        <span className="text-gray-500">Path:</span>{" "}
                        <span className="text-gray-300">{detection.process_path}</span>
                      </p>
                      <p>
                        <span className="text-gray-500">User:</span>{" "}
                        <span className="text-cyan-400">{detection.user}</span>
                      </p>
                      <p>
                        <span className="text-gray-500">Hash:</span>{" "}
                        <span className="text-gray-400 text-xs">{detection.process_hash}</span>
                      </p>
                      <p className="text-red-300 text-xs break-all">
                        <span className="text-gray-500">CMD:</span> {detection.command_line}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Status */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-1">Status</h4>
                  <p className="text-gray-300 capitalize">{detection.status}</p>
                </div>
                {detection.assigned_to && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-1">Assigned To</h4>
                    <p className="text-gray-300">{detection.assigned_to}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-700 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export function DetectionsPage() {
  const [filters, setFilters] = useState({ severity: "", hostname: "" });
  const [page, setPage] = useState(1);
  const [selectedDetectionId, setSelectedDetectionId] = useState<string | null>(null);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 20,
      severity: filters.severity || undefined,
      hostname: filters.hostname || undefined,
    }),
    [page, filters],
  );

  const { data: detectionsData, isLoading, error } = useDetections(queryParams);

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Detections</h1>
        <p className="text-gray-400 mt-1">EDR detections and alerts</p>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Hostname Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Hostname</label>
            <input
              type="text"
              value={filters.hostname}
              onChange={(e) => handleFilterChange("hostname", e.target.value)}
              placeholder="Filter by hostname..."
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>

          {/* Severity Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Severity</label>
            <select
              value={filters.severity}
              onChange={(e) => handleFilterChange("severity", e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
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
            <p className="text-red-400">Failed to load detections: {error.message}</p>
          </div>
        )}

        {detectionsData && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-900">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Timestamp
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Rule
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Severity
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Hostname
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Process
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      MITRE
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {detectionsData.data.map((detection: Detection) => (
                    <tr key={detection.detection_id} className="hover:bg-gray-750">
                      <td className="px-4 py-3 text-gray-400 text-sm whitespace-nowrap">
                        {format(new Date(detection.detected_at), "MMM d, HH:mm:ss")}
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-white font-medium truncate max-w-xs">
                          {detection.technique_name}
                        </p>
                      </td>
                      <td className="px-4 py-3">
                        <SeverityBadge severity={detection.severity} />
                      </td>
                      <td className="px-4 py-3 text-cyan-400 font-mono text-sm">
                        {detection.hostname}
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-gray-300 font-mono text-sm truncate max-w-[150px]">
                          {detection.process_name}
                        </p>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-1">
                          <span className="px-1.5 py-0.5 bg-cyan-900/50 text-cyan-300 rounded text-xs font-mono">
                            {detection.technique_id}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => setSelectedDetectionId(detection.detection_id)}
                          className="text-cyan-400 hover:text-cyan-300 text-sm flex items-center space-x-1"
                        >
                          <svg
                            className="w-4 h-4"
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
                          <span>View Details</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 bg-gray-900 border-t border-gray-700 flex items-center justify-between">
              <div className="text-sm text-gray-400">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, detectionsData.total)} of{" "}
                {detectionsData.total} detections
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
                  disabled={page >= detectionsData.total_pages}
                  className="px-3 py-1 bg-gray-700 text-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}

        {detectionsData?.data.length === 0 && (
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
            <p className="text-gray-400">No detections found</p>
            <p className="text-gray-500 text-sm mt-1">
              Try adjusting your filters or generate some data
            </p>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedDetectionId && (
        <ProcessTreeModal
          detectionId={selectedDetectionId}
          onClose={() => setSelectedDetectionId(null)}
        />
      )}
    </div>
  );
}
