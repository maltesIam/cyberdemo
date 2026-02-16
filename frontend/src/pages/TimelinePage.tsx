import { useState, useMemo } from "react";
import clsx from "clsx";
import { format, formatDuration, intervalToDuration } from "date-fns";
import { useAgentActions } from "../hooks/useApi";
import type { AgentAction } from "../types";

function ActionTypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    query: "bg-blue-900/50 text-blue-300",
    containment: "bg-red-900/50 text-red-300",
    enrichment: "bg-purple-900/50 text-purple-300",
    notification: "bg-green-900/50 text-green-300",
    analysis: "bg-cyan-900/50 text-cyan-300",
  };

  return (
    <span
      className={clsx(
        "px-2 py-1 rounded text-xs font-medium capitalize",
        colors[type] || "bg-gray-700 text-gray-300",
      )}
    >
      {type}
    </span>
  );
}

function StatusIndicator({ status }: { status: string }) {
  const indicators: Record<string, { color: string; icon: React.ReactNode }> = {
    pending: {
      color: "text-gray-400",
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
    running: {
      color: "text-yellow-400",
      icon: (
        <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
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
      ),
    },
    completed: {
      color: "text-green-400",
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      ),
    },
    failed: {
      color: "text-red-400",
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      ),
    },
  };

  const { color, icon } = indicators[status] || indicators.pending;

  return (
    <div className={clsx("flex items-center space-x-1", color)}>
      {icon}
      <span className="text-xs capitalize">{status}</span>
    </div>
  );
}

function WaterfallBar({ action, maxDuration }: { action: AgentAction; maxDuration: number }) {
  const duration = action.duration_ms || 0;
  const barWidth = maxDuration > 0 ? (duration / maxDuration) * 100 : 0;

  const statusColors: Record<string, string> = {
    pending: "bg-gray-500",
    running: "bg-yellow-500",
    completed: "bg-cyan-500",
    failed: "bg-red-500",
  };

  const formatMs = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    const duration = intervalToDuration({ start: 0, end: ms });
    return formatDuration(duration, { format: ["minutes", "seconds"] });
  };

  return (
    <div className="flex items-center space-x-2 w-full">
      <div className="flex-1 h-6 bg-gray-700 rounded-full overflow-hidden relative">
        <div
          className={clsx(
            "h-full rounded-full transition-all duration-300",
            statusColors[action.status],
          )}
          style={{ width: `${Math.max(barWidth, 2)}%` }}
        />
        {duration > 0 && (
          <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-300">
            {formatMs(duration)}
          </span>
        )}
      </div>
    </div>
  );
}

function ActionDetailPanel({ action, onClose }: { action: AgentAction; onClose: () => void }) {
  return (
    <div className="fixed inset-y-0 right-0 w-[480px] bg-gray-800 border-l border-gray-700 shadow-xl z-50 overflow-y-auto">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-white">Action Details</h2>
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
            <h3 className="text-sm font-medium text-gray-400 mb-3">Action Information</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-500">Type</span>
                <ActionTypeBadge type={action.action_type} />
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Status</span>
                <StatusIndicator status={action.status} />
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Incident ID</span>
                <span className="text-cyan-400 font-mono text-sm">
                  {action.incident_id.slice(0, 8)}
                </span>
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-2">Description</h3>
            <p className="text-gray-300">{action.description}</p>
          </div>

          {/* Timing */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-3">Timing</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Started</span>
                <span className="text-gray-300">
                  {format(new Date(action.started_at), "HH:mm:ss.SSS")}
                </span>
              </div>
              {action.completed_at && (
                <div className="flex justify-between">
                  <span className="text-gray-500">Completed</span>
                  <span className="text-gray-300">
                    {format(new Date(action.completed_at), "HH:mm:ss.SSS")}
                  </span>
                </div>
              )}
              {action.duration_ms !== null && (
                <div className="flex justify-between">
                  <span className="text-gray-500">Duration</span>
                  <span className="text-cyan-400">{action.duration_ms}ms</span>
                </div>
              )}
            </div>
          </div>

          {/* Input */}
          {Object.keys(action.input).length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-2">Input</h3>
              <pre className="bg-gray-900 rounded-lg p-3 text-xs text-gray-300 overflow-x-auto">
                {JSON.stringify(action.input, null, 2)}
              </pre>
            </div>
          )}

          {/* Output */}
          {Object.keys(action.output).length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-2">Output</h3>
              <pre className="bg-gray-900 rounded-lg p-3 text-xs text-gray-300 overflow-x-auto max-h-64">
                {JSON.stringify(action.output, null, 2)}
              </pre>
            </div>
          )}

          {/* Error */}
          {action.error && (
            <div>
              <h3 className="text-sm font-medium text-red-400 mb-2">Error</h3>
              <pre className="bg-red-900/30 border border-red-700 rounded-lg p-3 text-xs text-red-300 overflow-x-auto">
                {action.error}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function TimelinePage() {
  const [filters, setFilters] = useState({ incident_id: "", action_type: "", status: "" });
  const [page, setPage] = useState(1);
  const [selectedAction, setSelectedAction] = useState<AgentAction | null>(null);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 30,
      incident_id: filters.incident_id || undefined,
      action_type: filters.action_type || undefined,
      status: filters.status || undefined,
    }),
    [page, filters],
  );

  const { data: actionsData, isLoading, error } = useAgentActions(queryParams);

  const maxDuration = useMemo(() => {
    if (!actionsData?.data) return 0;
    return Math.max(...actionsData.data.map((a: AgentAction) => a.duration_ms || 0));
  }, [actionsData]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Agent Timeline</h1>
        <p className="text-gray-400 mt-1">Waterfall view of agent actions and operations</p>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Incident ID</label>
            <input
              type="text"
              value={filters.incident_id}
              onChange={(e) => handleFilterChange("incident_id", e.target.value)}
              placeholder="Filter by incident..."
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Action Type</label>
            <select
              value={filters.action_type}
              onChange={(e) => handleFilterChange("action_type", e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All Types</option>
              <option value="query">Query</option>
              <option value="containment">Containment</option>
              <option value="enrichment">Enrichment</option>
              <option value="notification">Notification</option>
              <option value="analysis">Analysis</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange("status", e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Timeline */}
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
            <p className="text-red-400">Failed to load timeline: {error.message}</p>
          </div>
        )}

        {actionsData && actionsData.data.length > 0 && (
          <div className="divide-y divide-gray-700">
            {actionsData.data.map((action: AgentAction) => (
              <div
                key={action.id}
                onClick={() => setSelectedAction(action)}
                className="p-4 hover:bg-gray-750 cursor-pointer transition-colors"
              >
                <div className="flex items-start space-x-4">
                  {/* Left: Time & Type */}
                  <div className="w-32 flex-shrink-0">
                    <p className="text-gray-400 text-sm">
                      {format(new Date(action.started_at), "HH:mm:ss")}
                    </p>
                    <ActionTypeBadge type={action.action_type} />
                  </div>

                  {/* Middle: Description & Status */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <StatusIndicator status={action.status} />
                      <span className="text-cyan-400 font-mono text-xs">
                        {action.incident_id.slice(0, 8)}
                      </span>
                    </div>
                    <p className="text-white truncate">{action.description}</p>
                  </div>

                  {/* Right: Waterfall Bar */}
                  <div className="w-48 flex-shrink-0">
                    <WaterfallBar action={action} maxDuration={maxDuration} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {actionsData?.data.length === 0 && (
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
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-gray-400">No agent actions found</p>
            <p className="text-gray-500 text-sm mt-1">
              Agent actions will appear here when incidents are processed
            </p>
          </div>
        )}

        {/* Pagination */}
        {actionsData && actionsData.total > 0 && (
          <div className="px-4 py-3 bg-gray-900 border-t border-gray-700 flex items-center justify-between">
            <div className="text-sm text-gray-400">
              Showing {(page - 1) * 30 + 1} to {Math.min(page * 30, actionsData.total)} of{" "}
              {actionsData.total} actions
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
                disabled={page >= actionsData.total_pages}
                className="px-3 py-1 bg-gray-700 text-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail Panel */}
      {selectedAction && (
        <ActionDetailPanel action={selectedAction} onClose={() => setSelectedAction(null)} />
      )}
    </div>
  );
}
