import { useState, useMemo, useRef } from "react";
import clsx from "clsx";
import { format } from "date-fns";
import { usePostmortems, usePostmortem } from "../hooks/useApi";
import type { Postmortem } from "../types";
import {
  IncidentTimelineChart,
  convertTimelineToPhases,
} from "../components/IncidentTimelineChart";

function ActionItemStatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: "bg-[var(--badge-investigating-bg)] text-[var(--badge-investigating-text)]",
    in_progress: "bg-[var(--badge-query-bg)] text-[var(--badge-query-text)]",
    completed: "bg-[var(--badge-resolved-bg)] text-[var(--badge-resolved-text)]",
  };

  return (
    <span
      className={clsx(
        "px-2 py-0.5 rounded text-xs font-medium",
        colors[status] || "bg-tertiary text-secondary",
      )}
    >
      {status.replace("_", " ")}
    </span>
  );
}

function PostmortemDetailModal({
  postmortemId,
  onClose,
}: {
  postmortemId: string;
  onClose: () => void;
}) {
  const { data: postmortem, isLoading, error } = usePostmortem(postmortemId);
  const contentRef = useRef<HTMLDivElement>(null);

  // Handle PDF export via browser print
  const handleExportPDF = () => {
    window.print();
  };

  return (
    <div
      role="dialog"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 print:bg-white print:p-0"
    >
      <div className="bg-secondary rounded-lg border border-primary shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden print:bg-white print:shadow-none print:border-none print:max-h-none print:rounded-none">
        {/* Header */}
        <div className="px-6 py-4 border-b border-primary flex items-center justify-between print:border-[var(--border-secondary)]">
          <h2 className="text-lg font-semibold text-primary print:text-[var(--text-primary)]">Postmortem Report</h2>
          <div className="flex items-center space-x-3 print:hidden">
            {/* Export PDF Button */}
            <button
              onClick={handleExportPDF}
              className="flex items-center space-x-2 px-3 py-1.5 bg-[var(--accent-button-bg)] text-primary rounded-lg hover:bg-[var(--accent-button-hover)] transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <span>Export PDF</span>
            </button>
            {/* Close Button */}
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
        </div>

        {/* Content */}
        <div
          ref={contentRef}
          className="p-6 overflow-y-auto max-h-[calc(90vh-120px)] print:max-h-none print:overflow-visible"
        >
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <svg className="w-8 h-8 animate-spin text-[var(--accent-link)]" fill="none" viewBox="0 0 24 24">
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
            <div className="text-[var(--error-text)] text-center py-8">
              Failed to load postmortem: {error.message}
            </div>
          )}

          {postmortem && (
            <div className="space-y-8">
              {/* Title & Metadata */}
              <div>
                <h3 className="text-2xl font-bold text-primary mb-2">{postmortem.title}</h3>
                <div className="flex items-center space-x-4 text-sm text-secondary">
                  <span>
                    Incident:{" "}
                    <span className="text-[var(--accent-link)] font-mono">
                      {postmortem.incident_id.slice(0, 8)}
                    </span>
                  </span>
                  <span>
                    Author: <span className="text-primary">{postmortem.author}</span>
                  </span>
                  <span>Created: {format(new Date(postmortem.created_at), "PPP")}</span>
                </div>
              </div>

              {/* Summary */}
              <div>
                <h4 className="text-lg font-semibold text-primary mb-3 flex items-center">
                  <svg
                    className="w-5 h-5 mr-2 text-[var(--accent-link)]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  Summary
                </h4>
                <p className="text-secondary leading-relaxed">{postmortem.summary}</p>
              </div>

              {/* Root Cause */}
              <div>
                <h4 className="text-lg font-semibold text-primary mb-3 flex items-center">
                  <svg
                    className="w-5 h-5 mr-2 text-[var(--error-text)]"
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
                  Root Cause
                </h4>
                <div className="bg-[var(--error-bg)] border border-[var(--error-border)] rounded-lg p-4">
                  <p className="text-secondary leading-relaxed">{postmortem.root_cause}</p>
                </div>
              </div>

              {/* Impact */}
              <div>
                <h4 className="text-lg font-semibold text-primary mb-3 flex items-center">
                  <svg
                    className="w-5 h-5 mr-2 text-[var(--badge-high-text)]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                  Impact
                </h4>
                <p className="text-secondary leading-relaxed">{postmortem.impact}</p>
              </div>

              {/* Timeline with Chart */}
              {postmortem.timeline.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-primary mb-3 flex items-center print:text-[var(--text-primary)]">
                    <svg
                      className="w-5 h-5 mr-2 text-[var(--badge-tactic-text)]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    Incident Progression
                  </h4>

                  {/* Visual Timeline Chart */}
                  <div className="bg-primary rounded-lg p-4 mb-4 print:bg-tertiary">
                    <IncidentTimelineChart
                      phases={convertTimelineToPhases(postmortem.timeline)}
                      showDurations
                    />
                  </div>

                  {/* Detailed Timeline List */}
                  <h5 className="text-md font-medium text-secondary mb-2 print:text-tertiary">
                    Detailed Events
                  </h5>
                  <div className="space-y-3">
                    {postmortem.timeline.map((entry, index) => (
                      <div key={index} className="flex space-x-4">
                        <div className="flex-shrink-0 w-24 text-sm text-tertiary">
                          {format(new Date(entry.timestamp), "HH:mm")}
                        </div>
                        <div className="flex-shrink-0 w-2 h-2 mt-2 rounded-full bg-[var(--badge-tactic-text)]" />
                        <div className="flex-1">
                          <p className="text-secondary print:text-[var(--text-secondary)]">{entry.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Lessons Learned */}
              {postmortem.lessons_learned.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-primary mb-3 flex items-center">
                    <svg
                      className="w-5 h-5 mr-2 text-[var(--status-completed)]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                      />
                    </svg>
                    Lessons Learned
                  </h4>
                  <ul className="space-y-2">
                    {postmortem.lessons_learned.map((lesson, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <svg
                          className="w-5 h-5 text-[var(--status-completed)] flex-shrink-0 mt-0.5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        <span className="text-secondary">{lesson}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Items */}
              {postmortem.action_items.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-primary mb-3 flex items-center">
                    <svg
                      className="w-5 h-5 mr-2 text-[var(--status-running)]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                      />
                    </svg>
                    Action Items
                  </h4>
                  <div className="space-y-3">
                    {postmortem.action_items.map((item) => (
                      <div
                        key={item.id}
                        className="bg-primary rounded-lg p-4 border border-primary"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <p className="text-primary">{item.description}</p>
                          <ActionItemStatusBadge status={item.status} />
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-tertiary">
                          <span>
                            Owner: <span className="text-secondary">{item.owner}</span>
                          </span>
                          <span>
                            Due:{" "}
                            <span className="text-secondary">
                              {format(new Date(item.due_date), "PP")}
                            </span>
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
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

export function PostmortemsPage() {
  const [page, setPage] = useState(1);
  const [selectedPostmortemId, setSelectedPostmortemId] = useState<string | null>(null);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 20,
    }),
    [page],
  );

  const { data: postmortemsData, isLoading, error } = usePostmortems(queryParams);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-primary">Postmortems</h1>
        <p className="text-secondary mt-1">Incident analysis reports and lessons learned</p>
      </div>

      {/* Table */}
      <div className="bg-secondary rounded-lg border border-primary overflow-hidden">
        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <svg className="w-8 h-8 animate-spin text-[var(--accent-link)]" fill="none" viewBox="0 0 24 24">
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
            <p className="text-[var(--error-text)]">Failed to load postmortems: {error.message}</p>
          </div>
        )}

        {postmortemsData && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-primary">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Incident
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Author
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Action Items
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--border-primary)]">
                  {postmortemsData.data.map((postmortem: Postmortem) => {
                    const completedItems = postmortem.action_items.filter(
                      (i) => i.status === "completed",
                    ).length;
                    const totalItems = postmortem.action_items.length;

                    return (
                      <tr key={postmortem.id} className="hover:bg-hover">
                        <td className="px-4 py-3">
                          <p className="text-primary font-medium truncate max-w-md">
                            {postmortem.title}
                          </p>
                          <p className="text-tertiary text-xs mt-0.5 truncate max-w-md">
                            {postmortem.summary}
                          </p>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-[var(--accent-link)] font-mono text-sm">
                            {postmortem.incident_id.slice(0, 8)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-secondary">{postmortem.author}</td>
                        <td className="px-4 py-3 text-secondary text-sm">
                          {format(new Date(postmortem.created_at), "MMM d, yyyy")}
                        </td>
                        <td className="px-4 py-3">
                          {totalItems > 0 ? (
                            <div className="flex items-center space-x-2">
                              <div className="w-24 bg-tertiary rounded-full h-2">
                                <div
                                  className="bg-[var(--progress-success)] h-2 rounded-full"
                                  style={{ width: `${(completedItems / totalItems) * 100}%` }}
                                />
                              </div>
                              <span className="text-secondary text-sm">
                                {completedItems}/{totalItems}
                              </span>
                            </div>
                          ) : (
                            <span className="text-tertiary text-sm">None</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => setSelectedPostmortemId(postmortem.id)}
                            className="text-[var(--accent-link)] hover:text-[var(--accent-link-hover)] text-sm flex items-center space-x-1"
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
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 bg-primary border-t border-primary flex items-center justify-between">
              <div className="text-sm text-secondary">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, postmortemsData.total)} of{" "}
                {postmortemsData.total} postmortems
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
                  disabled={page >= postmortemsData.total_pages}
                  className="px-3 py-1 bg-tertiary text-secondary rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-tertiary"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}

        {postmortemsData?.data.length === 0 && (
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
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="text-secondary">No postmortem reports found</p>
            <p className="text-tertiary text-sm mt-1">
              Reports will be generated after incident resolution
            </p>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedPostmortemId && (
        <PostmortemDetailModal
          postmortemId={selectedPostmortemId}
          onClose={() => setSelectedPostmortemId(null)}
        />
      )}
    </div>
  );
}
