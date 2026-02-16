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
    pending: "bg-yellow-900/50 text-yellow-300",
    in_progress: "bg-blue-900/50 text-blue-300",
    completed: "bg-green-900/50 text-green-300",
  };

  return (
    <span
      className={clsx(
        "px-2 py-0.5 rounded text-xs font-medium",
        colors[status] || "bg-gray-700 text-gray-300",
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
      <div className="bg-gray-800 rounded-lg border border-gray-700 shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden print:bg-white print:shadow-none print:border-none print:max-h-none print:rounded-none">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between print:border-gray-300">
          <h2 className="text-lg font-semibold text-white print:text-black">Postmortem Report</h2>
          <div className="flex items-center space-x-3 print:hidden">
            {/* Export PDF Button */}
            <button
              onClick={handleExportPDF}
              className="flex items-center space-x-2 px-3 py-1.5 bg-cyan-600 text-white rounded-lg hover:bg-cyan-500 transition-colors"
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
        </div>

        {/* Content */}
        <div
          ref={contentRef}
          className="p-6 overflow-y-auto max-h-[calc(90vh-120px)] print:max-h-none print:overflow-visible"
        >
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
              Failed to load postmortem: {error.message}
            </div>
          )}

          {postmortem && (
            <div className="space-y-8">
              {/* Title & Metadata */}
              <div>
                <h3 className="text-2xl font-bold text-white mb-2">{postmortem.title}</h3>
                <div className="flex items-center space-x-4 text-sm text-gray-400">
                  <span>
                    Incident:{" "}
                    <span className="text-cyan-400 font-mono">
                      {postmortem.incident_id.slice(0, 8)}
                    </span>
                  </span>
                  <span>
                    Author: <span className="text-white">{postmortem.author}</span>
                  </span>
                  <span>Created: {format(new Date(postmortem.created_at), "PPP")}</span>
                </div>
              </div>

              {/* Summary */}
              <div>
                <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                  <svg
                    className="w-5 h-5 mr-2 text-cyan-400"
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
                <p className="text-gray-300 leading-relaxed">{postmortem.summary}</p>
              </div>

              {/* Root Cause */}
              <div>
                <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                  <svg
                    className="w-5 h-5 mr-2 text-red-400"
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
                <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
                  <p className="text-gray-300 leading-relaxed">{postmortem.root_cause}</p>
                </div>
              </div>

              {/* Impact */}
              <div>
                <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                  <svg
                    className="w-5 h-5 mr-2 text-orange-400"
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
                <p className="text-gray-300 leading-relaxed">{postmortem.impact}</p>
              </div>

              {/* Timeline with Chart */}
              {postmortem.timeline.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3 flex items-center print:text-black">
                    <svg
                      className="w-5 h-5 mr-2 text-purple-400"
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
                  <div className="bg-gray-900 rounded-lg p-4 mb-4 print:bg-gray-100">
                    <IncidentTimelineChart
                      phases={convertTimelineToPhases(postmortem.timeline)}
                      showDurations
                    />
                  </div>

                  {/* Detailed Timeline List */}
                  <h5 className="text-md font-medium text-gray-400 mb-2 print:text-gray-600">
                    Detailed Events
                  </h5>
                  <div className="space-y-3">
                    {postmortem.timeline.map((entry, index) => (
                      <div key={index} className="flex space-x-4">
                        <div className="flex-shrink-0 w-24 text-sm text-gray-500">
                          {format(new Date(entry.timestamp), "HH:mm")}
                        </div>
                        <div className="flex-shrink-0 w-2 h-2 mt-2 rounded-full bg-purple-500" />
                        <div className="flex-1">
                          <p className="text-gray-300 print:text-gray-700">{entry.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Lessons Learned */}
              {postmortem.lessons_learned.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                    <svg
                      className="w-5 h-5 mr-2 text-green-400"
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
                          className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5"
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
                        <span className="text-gray-300">{lesson}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Items */}
              {postmortem.action_items.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                    <svg
                      className="w-5 h-5 mr-2 text-yellow-400"
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
                        className="bg-gray-900 rounded-lg p-4 border border-gray-700"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <p className="text-white">{item.description}</p>
                          <ActionItemStatusBadge status={item.status} />
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>
                            Owner: <span className="text-gray-300">{item.owner}</span>
                          </span>
                          <span>
                            Due:{" "}
                            <span className="text-gray-300">
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
        <h1 className="text-2xl font-bold text-white">Postmortems</h1>
        <p className="text-gray-400 mt-1">Incident analysis reports and lessons learned</p>
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
            <p className="text-red-400">Failed to load postmortems: {error.message}</p>
          </div>
        )}

        {postmortemsData && (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-900">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Incident
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Author
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Action Items
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {postmortemsData.data.map((postmortem: Postmortem) => {
                    const completedItems = postmortem.action_items.filter(
                      (i) => i.status === "completed",
                    ).length;
                    const totalItems = postmortem.action_items.length;

                    return (
                      <tr key={postmortem.id} className="hover:bg-gray-750">
                        <td className="px-4 py-3">
                          <p className="text-white font-medium truncate max-w-md">
                            {postmortem.title}
                          </p>
                          <p className="text-gray-500 text-xs mt-0.5 truncate max-w-md">
                            {postmortem.summary}
                          </p>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-cyan-400 font-mono text-sm">
                            {postmortem.incident_id.slice(0, 8)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-gray-300">{postmortem.author}</td>
                        <td className="px-4 py-3 text-gray-400 text-sm">
                          {format(new Date(postmortem.created_at), "MMM d, yyyy")}
                        </td>
                        <td className="px-4 py-3">
                          {totalItems > 0 ? (
                            <div className="flex items-center space-x-2">
                              <div className="w-24 bg-gray-700 rounded-full h-2">
                                <div
                                  className="bg-green-500 h-2 rounded-full"
                                  style={{ width: `${(completedItems / totalItems) * 100}%` }}
                                />
                              </div>
                              <span className="text-gray-400 text-sm">
                                {completedItems}/{totalItems}
                              </span>
                            </div>
                          ) : (
                            <span className="text-gray-500 text-sm">None</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => setSelectedPostmortemId(postmortem.id)}
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
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-4 py-3 bg-gray-900 border-t border-gray-700 flex items-center justify-between">
              <div className="text-sm text-gray-400">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, postmortemsData.total)} of{" "}
                {postmortemsData.total} postmortems
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
                  disabled={page >= postmortemsData.total_pages}
                  className="px-3 py-1 bg-gray-700 text-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
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
              className="w-12 h-12 text-gray-600 mx-auto mb-4"
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
            <p className="text-gray-400">No postmortem reports found</p>
            <p className="text-gray-500 text-sm mt-1">
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
