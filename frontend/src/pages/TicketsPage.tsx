import { useState, useMemo } from "react";
import clsx from "clsx";
import { format } from "date-fns";
import { useTickets, useTicket } from "../hooks/useApi";
import type { Ticket } from "../types";

function PriorityBadge({ priority }: { priority: string }) {
  const colors: Record<string, string> = {
    urgent: "bg-red-900 text-red-300 border-red-700",
    high: "bg-orange-900 text-orange-300 border-orange-700",
    medium: "bg-yellow-900 text-yellow-300 border-yellow-700",
    low: "bg-green-900 text-green-300 border-green-700",
  };

  return (
    <span
      className={clsx(
        "px-2 py-1 rounded text-xs font-medium border",
        colors[priority] || "bg-tertiary text-secondary",
      )}
    >
      {priority.toUpperCase()}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    open: "bg-blue-900/50 text-blue-300",
    in_progress: "bg-yellow-900/50 text-yellow-300",
    pending: "bg-purple-900/50 text-purple-300",
    resolved: "bg-green-900/50 text-green-300",
    closed: "bg-tertiary text-secondary",
  };

  return (
    <span
      className={clsx(
        "px-2 py-1 rounded text-xs font-medium capitalize",
        colors[status] || "bg-tertiary text-secondary",
      )}
    >
      {status.replace("_", " ")}
    </span>
  );
}

function SystemBadge({ system }: { system: string }) {
  const configs: Record<string, { bg: string; icon: React.ReactNode }> = {
    jira: {
      bg: "bg-blue-600",
      icon: (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M11.571 11.513H0a5.218 5.218 0 0 0 5.232 5.215h2.13v2.057A5.215 5.215 0 0 0 12.575 24V12.518a1.005 1.005 0 0 0-1.005-1.005zm5.723-5.756H5.736a5.215 5.215 0 0 0 5.215 5.214h2.129v2.058a5.218 5.218 0 0 0 5.215 5.214V6.758a1.001 1.001 0 0 0-1.001-1.001zM23.013 0H11.455a5.215 5.215 0 0 0 5.215 5.215h2.129v2.057A5.215 5.215 0 0 0 24 12.483V1.005A1.005 1.005 0 0 0 23.013 0z" />
        </svg>
      ),
    },
    servicenow: {
      bg: "bg-green-600",
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
          />
        </svg>
      ),
    },
    pagerduty: {
      bg: "bg-emerald-600",
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
      ),
    },
  };

  const config = configs[system] || { bg: "bg-tertiary", icon: null };

  return (
    <div
      className={clsx(
        "inline-flex items-center space-x-1.5 px-2 py-1 rounded text-xs font-medium text-primary",
        config.bg,
      )}
    >
      {config.icon}
      <span className="capitalize">{system}</span>
    </div>
  );
}

function TicketDetailModal({ ticketId, onClose }: { ticketId: string; onClose: () => void }) {
  const { data: ticket, isLoading, error } = useTicket(ticketId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-secondary rounded-lg border border-primary shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-primary flex items-center justify-between">
          <h2 className="text-lg font-semibold text-primary">Ticket Details</h2>
          <button onClick={onClose} className="text-secondary hover:text-primary">
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
              Failed to load ticket: {error.message}
            </div>
          )}

          {ticket && (
            <div className="space-y-6">
              {/* Title & System */}
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <SystemBadge system={ticket.system} />
                  <span className="text-tertiary font-mono text-sm">{ticket.external_id}</span>
                </div>
                <h3 className="text-xl font-semibold text-primary">{ticket.title}</h3>
              </div>

              {/* Status & Priority */}
              <div className="flex items-center space-x-4">
                <div>
                  <span className="text-tertiary text-xs">Status</span>
                  <div className="mt-1">
                    <StatusBadge status={ticket.status} />
                  </div>
                </div>
                <div>
                  <span className="text-tertiary text-xs">Priority</span>
                  <div className="mt-1">
                    <PriorityBadge priority={ticket.priority} />
                  </div>
                </div>
              </div>

              {/* Description */}
              <div>
                <h4 className="text-sm font-medium text-secondary mb-2">Description</h4>
                <p className="text-secondary whitespace-pre-wrap">{ticket.description}</p>
              </div>

              {/* Metadata */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-secondary mb-1">Incident ID</h4>
                  <span className="text-cyan-400 font-mono">{ticket.incident_id.slice(0, 8)}</span>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-secondary mb-1">Assigned To</h4>
                  <span className="text-primary">{ticket.assigned_to || "Unassigned"}</span>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-secondary mb-1">Created</h4>
                  <span className="text-secondary">
                    {format(new Date(ticket.created_at), "PPpp")}
                  </span>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-secondary mb-1">Last Updated</h4>
                  <span className="text-secondary">
                    {format(new Date(ticket.updated_at), "PPpp")}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-primary flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-tertiary text-secondary rounded-lg hover:bg-tertiary transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export function TicketsPage() {
  const [filters, setFilters] = useState({ status: "", priority: "", system: "" });
  const [page, setPage] = useState(1);
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 20,
      status: filters.status || undefined,
      priority: filters.priority || undefined,
      system: filters.system || undefined,
    }),
    [page, filters],
  );

  const { data: ticketsData, isLoading, error } = useTickets(queryParams);

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-primary">Tickets</h1>
        <p className="text-secondary mt-1">Track tickets created across external systems</p>
      </div>

      {/* Filters */}
      <div className="bg-secondary rounded-lg p-4 border border-primary">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-secondary mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange("status", e.target.value)}
              className="w-full px-3 py-2 bg-tertiary border border-primary rounded-lg text-primary focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All Status</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="pending">Pending</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-secondary mb-1">Priority</label>
            <select
              value={filters.priority}
              onChange={(e) => handleFilterChange("priority", e.target.value)}
              className="w-full px-3 py-2 bg-tertiary border border-primary rounded-lg text-primary focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All Priorities</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-secondary mb-1">System</label>
            <select
              value={filters.system}
              onChange={(e) => handleFilterChange("system", e.target.value)}
              className="w-full px-3 py-2 bg-tertiary border border-primary rounded-lg text-primary focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">All Systems</option>
              <option value="jira">Jira</option>
              <option value="servicenow">ServiceNow</option>
              <option value="pagerduty">PagerDuty</option>
            </select>
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
            <p className="text-red-400">Failed to load tickets: {error.message}</p>
          </div>
        )}

        {ticketsData && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-primary">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      System
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      External ID
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Priority
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Assigned
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {ticketsData.data.map((ticket: Ticket) => (
                    <tr key={ticket.id} className="hover:bg-hover">
                      <td className="px-4 py-3">
                        <SystemBadge system={ticket.system} />
                      </td>
                      <td className="px-4 py-3 text-cyan-400 font-mono text-sm">
                        {ticket.external_id}
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-primary font-medium truncate max-w-xs">{ticket.title}</p>
                      </td>
                      <td className="px-4 py-3">
                        <PriorityBadge priority={ticket.priority} />
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={ticket.status} />
                      </td>
                      <td className="px-4 py-3 text-secondary text-sm">
                        {ticket.assigned_to || "-"}
                      </td>
                      <td className="px-4 py-3 text-secondary text-sm">
                        {format(new Date(ticket.created_at), "MMM d, HH:mm")}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => setSelectedTicketId(ticket.id)}
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
                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                            />
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                            />
                          </svg>
                          <span>View</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 bg-primary border-t border-primary flex items-center justify-between">
              <div className="text-sm text-secondary">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, ticketsData.total)} of{" "}
                {ticketsData.total} tickets
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
                  disabled={page >= ticketsData.total_pages}
                  className="px-3 py-1 bg-tertiary text-secondary rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-tertiary"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}

        {ticketsData?.data.length === 0 && (
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
                d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"
              />
            </svg>
            <p className="text-secondary">No tickets found</p>
            <p className="text-tertiary text-sm mt-1">
              Tickets will appear here when incidents are processed
            </p>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedTicketId && (
        <TicketDetailModal ticketId={selectedTicketId} onClose={() => setSelectedTicketId(null)} />
      )}
    </div>
  );
}
