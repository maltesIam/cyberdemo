import { useState, useMemo } from "react";
import clsx from "clsx";
import { format } from "date-fns";
import { useIncidents, useIncident } from "../hooks/useApi";
import type { Incident } from "../types";

function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    critical: "bg-red-900 text-red-300 border-red-700",
    high: "bg-orange-900 text-orange-300 border-orange-700",
    medium: "bg-yellow-900 text-yellow-300 border-yellow-700",
    low: "bg-green-900 text-green-300 border-green-700",
  };

  return (
    <span
      className={clsx(
        "px-2 py-1 rounded text-xs font-medium border",
        colors[severity] || "bg-gray-700 text-gray-300",
      )}
    >
      {severity.toUpperCase()}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    open: "bg-red-900/50 text-red-300",
    investigating: "bg-yellow-900/50 text-yellow-300",
    contained: "bg-orange-900/50 text-orange-300",
    resolved: "bg-green-900/50 text-green-300",
    closed: "bg-gray-700 text-gray-400",
  };

  return (
    <span
      className={clsx(
        "px-2 py-1 rounded text-xs font-medium capitalize",
        colors[status] || "bg-gray-700 text-gray-300",
      )}
    >
      {status}
    </span>
  );
}

function IncidentDetailModal({ incidentId, onClose }: { incidentId: string; onClose: () => void }) {
  const { data: incident, isLoading, error } = useIncident(incidentId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-gray-800 rounded-lg border border-gray-700 shadow-xl w-full max-w-3xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Incident Details</h2>
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
              Failed to load incident details: {error.message}
            </div>
          )}

          {incident && (
            <div className="space-y-6">
              {/* Header Info */}
              <div>
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-xl font-semibold text-white">{incident.title}</h3>
                  <span className="text-gray-500 font-mono text-sm">{incident.incident_id}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <SeverityBadge severity={incident.severity} />
                  <StatusBadge status={incident.status} />
                  {incident.assigned_to && (
                    <span className="text-gray-400 text-sm">
                      Assigned to: <span className="text-white">{incident.assigned_to}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* Description */}
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Description</h4>
                <p className="text-gray-300">{incident.description}</p>
              </div>

              {/* Timestamps */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-1">Created</h4>
                  <p className="text-gray-300">{format(new Date(incident.created_at), "PPpp")}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-1">Last Updated</h4>
                  <p className="text-gray-300">{format(new Date(incident.updated_at), "PPpp")}</p>
                </div>
              </div>

              {/* Affected Assets */}
              {incident.asset_ids?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-2">
                    Affected Assets ({incident.asset_ids.length})
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {incident.asset_ids.map((asset) => (
                      <span
                        key={asset}
                        className="px-2 py-1 bg-gray-700 text-cyan-400 rounded text-sm font-mono"
                      >
                        {asset.slice(0, 8)}...
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Detections */}
              {incident.detection_ids?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-2">
                    Related Detections ({incident.detection_ids.length})
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {incident.detection_ids.map((detection) => (
                      <span
                        key={detection}
                        className="px-2 py-1 bg-red-900/30 text-red-400 rounded text-sm font-mono"
                      >
                        {detection.slice(0, 8)}...
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Tags */}
              {incident.tags?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {incident.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Additional Info */}
              <div className="grid grid-cols-2 gap-4">
                {incident.category && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-1">Category</h4>
                    <p className="text-gray-300 capitalize">
                      {incident.category.replace("_", " ")}
                    </p>
                  </div>
                )}
                {incident.source && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-1">Source</h4>
                    <p className="text-gray-300">{incident.source}</p>
                  </div>
                )}
                {incident.ttd_minutes && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-1">Time to Detect</h4>
                    <p className="text-gray-300">{incident.ttd_minutes} minutes</p>
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

export function IncidentsPage() {
  const [filters, setFilters] = useState({ status: "", severity: "", search: "" });
  const [page, setPage] = useState(1);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 20,
      status: filters.status || undefined,
      severity: filters.severity || undefined,
      search: filters.search || undefined,
    }),
    [page, filters],
  );

  const { data: incidentsData, isLoading, error } = useIncidents(queryParams);

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Incidents</h1>
        <p className="text-gray-400 mt-1">Track and manage security incidents</p>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-400 mb-1">Search</label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => handleFilterChange("search", e.target.value)}
              placeholder="Search incidents..."
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange("status", e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All Status</option>
              <option value="open">Open</option>
              <option value="investigating">Investigating</option>
              <option value="contained">Contained</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
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
            <p className="text-red-400">Failed to load incidents: {error.message}</p>
          </div>
        )}

        {incidentsData && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-900">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Severity
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Assets
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {incidentsData.data.map((incident: Incident) => (
                    <tr
                      key={incident.incident_id}
                      onClick={() => setSelectedIncidentId(incident.incident_id)}
                      className="hover:bg-gray-750 cursor-pointer transition-colors"
                    >
                      <td className="px-4 py-3">
                        <span className="text-cyan-400 font-mono text-sm">
                          {incident.incident_id}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="max-w-md">
                          <p className="text-white font-medium truncate">{incident.title}</p>
                          {incident.assigned_to && (
                            <p className="text-gray-500 text-xs mt-0.5">
                              Assigned: {incident.assigned_to}
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <SeverityBadge severity={incident.severity} />
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={incident.status} />
                      </td>
                      <td className="px-4 py-3 text-gray-400 text-sm">
                        {format(new Date(incident.created_at), "MMM d, HH:mm")}
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-gray-400">{incident.asset_ids?.length ?? 0}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 bg-gray-900 border-t border-gray-700 flex items-center justify-between">
              <div className="text-sm text-gray-400">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, incidentsData.total)} of{" "}
                {incidentsData.total} incidents
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
                  disabled={page >= incidentsData.total_pages}
                  className="px-3 py-1 bg-gray-700 text-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}

        {incidentsData?.data.length === 0 && (
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
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <p className="text-gray-400">No incidents found</p>
            <p className="text-gray-500 text-sm mt-1">
              Try adjusting your filters or generate some data
            </p>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedIncidentId && (
        <IncidentDetailModal
          incidentId={selectedIncidentId}
          onClose={() => setSelectedIncidentId(null)}
        />
      )}
    </div>
  );
}
