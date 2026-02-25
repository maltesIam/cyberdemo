import { useState, useMemo } from "react";
import clsx from "clsx";
import { format } from "date-fns";
import {
  useAuditLogs,
  useAuditUsers,
  useAuditActionTypes,
  useAuditOutcomes,
  useExportAuditLogs,
} from "../hooks/useApi";
import type { AuditLog, AuditActionType, AuditOutcome } from "../types";

function OutcomeBadge({ outcome }: { outcome: AuditOutcome }) {
  const colors: Record<AuditOutcome, string> = {
    success: "bg-green-900/50 text-green-300",
    failure: "bg-red-900/50 text-red-300",
    pending: "bg-yellow-900/50 text-yellow-300",
    denied: "bg-red-900/50 text-red-300",
    approved: "bg-green-900/50 text-green-300",
  };

  return (
    <span
      className={clsx(
        "px-2 py-0.5 rounded text-xs font-medium capitalize",
        colors[outcome] ?? "bg-tertiary text-secondary",
      )}
    >
      {outcome}
    </span>
  );
}

function ActionTypeBadge({ actionType }: { actionType: AuditActionType }) {
  const colors: Record<string, string> = {
    containment: "bg-red-900/50 text-red-300",
    approval: "bg-purple-900/50 text-purple-300",
    investigation: "bg-blue-900/50 text-blue-300",
    config_change: "bg-orange-900/50 text-orange-300",
    alert_update: "bg-cyan-900/50 text-cyan-300",
    escalation: "bg-yellow-900/50 text-yellow-300",
    notification: "bg-indigo-900/50 text-indigo-300",
    playbook_execution: "bg-pink-900/50 text-pink-300",
    user_login: "bg-tertiary/50 text-secondary",
    data_export: "bg-teal-900/50 text-teal-300",
  };

  return (
    <span
      className={clsx(
        "px-2 py-0.5 rounded text-xs font-medium",
        colors[actionType] ?? "bg-tertiary text-secondary",
      )}
    >
      {actionType.replace(/_/g, " ")}
    </span>
  );
}

function AuditLogDetailRow({ log }: { log: AuditLog }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <>
      <tr className="hover:bg-hover cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
        <td className="px-4 py-3 text-secondary text-sm whitespace-nowrap">
          {format(new Date(log.timestamp), "MMM d, yyyy HH:mm:ss")}
        </td>
        <td className="px-4 py-3 text-primary">{log.user}</td>
        <td className="px-4 py-3">
          <ActionTypeBadge actionType={log.action_type} />
        </td>
        <td className="px-4 py-3 text-secondary font-mono text-sm max-w-xs truncate">
          {log.target}
        </td>
        <td className="px-4 py-3 text-secondary text-sm">{log.policy_decision ?? "-"}</td>
        <td className="px-4 py-3">
          <OutcomeBadge outcome={log.outcome} />
        </td>
        <td className="px-4 py-3">
          <button className="text-secondary hover:text-primary">
            <svg
              className={clsx("w-5 h-5 transition-transform", isExpanded && "rotate-180")}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
        </td>
      </tr>
      {isExpanded && (
        <tr className="bg-primary">
          <td colSpan={7} className="px-4 py-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="text-secondary font-medium mb-2">Event Details</h4>
                <dl className="space-y-1">
                  <div className="flex">
                    <dt className="text-tertiary w-32">ID:</dt>
                    <dd className="text-secondary font-mono">{log.id}</dd>
                  </div>
                  <div className="flex">
                    <dt className="text-tertiary w-32">Target Type:</dt>
                    <dd className="text-secondary">{log.target_type || "N/A"}</dd>
                  </div>
                  <div className="flex">
                    <dt className="text-tertiary w-32">IP Address:</dt>
                    <dd className="text-secondary font-mono">{log.ip_address ?? "N/A"}</dd>
                  </div>
                  <div className="flex">
                    <dt className="text-tertiary w-32">Session ID:</dt>
                    <dd className="text-secondary font-mono">{log.session_id ?? "N/A"}</dd>
                  </div>
                </dl>
              </div>
              <div>
                <h4 className="text-secondary font-medium mb-2">Additional Details</h4>
                {Object.keys(log.details).length > 0 ? (
                  <pre className="bg-secondary rounded p-3 text-xs text-secondary overflow-x-auto max-h-32">
                    {JSON.stringify(log.details, null, 2)}
                  </pre>
                ) : (
                  <p className="text-tertiary">No additional details</p>
                )}
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

export function AuditPage() {
  const [page, setPage] = useState(1);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [selectedUser, setSelectedUser] = useState("");
  const [selectedActionType, setSelectedActionType] = useState("");
  const [selectedOutcome, setSelectedOutcome] = useState("");
  const [targetSearch, setTargetSearch] = useState("");

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 20,
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
      user: selectedUser || undefined,
      action_type: (selectedActionType || undefined) as AuditActionType | undefined,
      target: targetSearch || undefined,
      outcome: (selectedOutcome || undefined) as AuditOutcome | undefined,
    }),
    [page, dateFrom, dateTo, selectedUser, selectedActionType, targetSearch, selectedOutcome],
  );

  const { data: auditData, isLoading, error } = useAuditLogs(queryParams);
  const { data: usersData } = useAuditUsers();
  const { data: actionTypesData } = useAuditActionTypes();
  const { data: outcomesData } = useAuditOutcomes();
  const exportMutation = useExportAuditLogs();

  const handleExport = async (format: "csv" | "json") => {
    try {
      const blob = await exportMutation.mutateAsync({
        format,
        params: {
          date_from: dateFrom || undefined,
          date_to: dateTo || undefined,
          user: selectedUser || undefined,
          action_type: (selectedActionType || undefined) as AuditActionType | undefined,
          target: targetSearch || undefined,
          outcome: (selectedOutcome || undefined) as AuditOutcome | undefined,
        },
      });

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `audit_logs_${format === "csv" ? "csv" : "json"}_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export failed:", err);
    }
  };

  const handleClearFilters = () => {
    setDateFrom("");
    setDateTo("");
    setSelectedUser("");
    setSelectedActionType("");
    setSelectedOutcome("");
    setTargetSearch("");
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-primary">Audit Log</h1>
          <p className="text-secondary mt-1">Compliance tracking and action history</p>
        </div>

        {/* Export Dropdown */}
        <div className="relative group">
          <button
            className="flex items-center space-x-2 px-4 py-2 bg-cyan-600 text-primary rounded-lg hover:bg-cyan-500 transition-colors"
            disabled={exportMutation.isPending}
          >
            {exportMutation.isPending ? (
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
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
            )}
            <span>Export</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
          <div className="absolute right-0 mt-2 w-32 bg-secondary border border-primary rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
            <button
              onClick={() => handleExport("csv")}
              className="w-full px-4 py-2 text-left text-secondary hover:bg-tertiary hover:text-primary rounded-t-lg"
            >
              CSV
            </button>
            <button
              onClick={() => handleExport("json")}
              className="w-full px-4 py-2 text-left text-secondary hover:bg-tertiary hover:text-primary rounded-b-lg"
            >
              JSON
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-secondary rounded-lg border border-primary p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-primary">Filters</h2>
          <button onClick={handleClearFilters} className="text-sm text-secondary hover:text-primary">
            Clear all
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {/* Date From */}
          <div>
            <label className="block text-sm text-secondary mb-1">From Date</label>
            <input
              type="datetime-local"
              value={dateFrom}
              onChange={(e) => {
                setDateFrom(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-primary border border-primary rounded-lg text-primary text-sm focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
          </div>

          {/* Date To */}
          <div>
            <label className="block text-sm text-secondary mb-1">To Date</label>
            <input
              type="datetime-local"
              value={dateTo}
              onChange={(e) => {
                setDateTo(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-primary border border-primary rounded-lg text-primary text-sm focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
          </div>

          {/* User Dropdown */}
          <div>
            <label className="block text-sm text-secondary mb-1">User</label>
            <select
              value={selectedUser}
              onChange={(e) => {
                setSelectedUser(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-primary border border-primary rounded-lg text-primary text-sm focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            >
              <option value="">All Users</option>
              {usersData?.users?.map((user) => (
                <option key={user} value={user}>
                  {user}
                </option>
              ))}
            </select>
          </div>

          {/* Action Type Dropdown */}
          <div>
            <label className="block text-sm text-secondary mb-1">Action Type</label>
            <select
              value={selectedActionType}
              onChange={(e) => {
                setSelectedActionType(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-primary border border-primary rounded-lg text-primary text-sm focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            >
              <option value="">All Types</option>
              {actionTypesData?.action_types?.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Outcome Dropdown */}
          <div>
            <label className="block text-sm text-secondary mb-1">Outcome</label>
            <select
              value={selectedOutcome}
              onChange={(e) => {
                setSelectedOutcome(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 bg-primary border border-primary rounded-lg text-primary text-sm focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            >
              <option value="">All Outcomes</option>
              {outcomesData?.outcomes?.map((outcome) => (
                <option key={outcome.value} value={outcome.value}>
                  {outcome.label}
                </option>
              ))}
            </select>
          </div>

          {/* Target Search */}
          <div>
            <label className="block text-sm text-secondary mb-1">Target</label>
            <input
              type="text"
              value={targetSearch}
              onChange={(e) => {
                setTargetSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search target..."
              className="w-full px-3 py-2 bg-primary border border-primary rounded-lg text-primary text-sm placeholder-gray-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-secondary rounded-lg border border-primary overflow-hidden">
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
            <p className="text-red-400">Failed to load audit logs: {error.message}</p>
          </div>
        )}

        {auditData && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-primary">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Timestamp
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Action Type
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Target
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Policy Decision
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Outcome
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider w-12">
                      {/* Expand column */}
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {auditData.data.map((log: AuditLog) => (
                    <AuditLogDetailRow key={log.id} log={log} />
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 bg-primary border-t border-primary flex items-center justify-between">
              <div className="text-sm text-secondary">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, auditData.total)} of{" "}
                {auditData.total} entries
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
                  disabled={page >= auditData.total_pages}
                  className="px-3 py-1 bg-tertiary text-secondary rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-tertiary"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}

        {auditData?.data.length === 0 && (
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
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
              />
            </svg>
            <p className="text-secondary">No audit logs found</p>
            <p className="text-tertiary text-sm mt-1">Adjust your filters or check back later</p>
          </div>
        )}
      </div>
    </div>
  );
}
