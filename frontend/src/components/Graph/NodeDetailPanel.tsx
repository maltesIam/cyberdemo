/**
 * NodeDetailPanel Component
 *
 * Side panel showing details of the selected node with 4 sections:
 * (a) Asset Info - Who is the asset
 * (b) Threat Info - What is the threat
 * (c) Recommendation - Agent's recommendation
 * (d) Status - Containment/ticket status
 */

import type { SelectedNode } from "./types";

interface NodeDetailPanelProps {
  node: SelectedNode | null;
  onClose: () => void;
  className?: string;
}

export function NodeDetailPanel({ node, onClose, className = "" }: NodeDetailPanelProps) {
  if (!node) return null;

  return (
    <div
      data-testid="node-detail-panel"
      className={`w-80 bg-slate-800 border-l border-slate-700 overflow-y-auto ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        <h3 className="text-lg font-semibold text-white">{node.label}</h3>
        <button
          onClick={onClose}
          className="p-1 hover:bg-slate-700 rounded"
          aria-label="Close panel"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 text-slate-400"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>

      {/* Node Type Badge */}
      <div className="px-4 py-2">
        <span
          className={`inline-block px-2 py-1 text-xs font-medium rounded ${getNodeTypeBadgeClass(node.type)}`}
        >
          {node.type.toUpperCase()}
        </span>
        <span
          className={`inline-block ml-2 px-2 py-1 text-xs font-medium rounded ${getColorBadgeClass(node.color)}`}
        >
          {node.riskLevel || node.color}
        </span>
      </div>

      {/* Section (a): Asset Info */}
      {node.assetInfo && (
        <section data-testid="section-asset-info" className="p-4 border-b border-slate-700">
          <h4 className="text-sm font-medium text-slate-400 mb-2">Asset Information</h4>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-slate-400">Hostname</dt>
              <dd className="text-white">{node.assetInfo.hostname}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-400">IP Address</dt>
              <dd className="text-white">{node.assetInfo.ip}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-400">OS</dt>
              <dd className="text-white">{node.assetInfo.os}</dd>
            </div>
            {node.assetInfo.owner && (
              <div className="flex justify-between">
                <dt className="text-slate-400">Owner</dt>
                <dd className="text-white">{node.assetInfo.owner}</dd>
              </div>
            )}
            {node.assetInfo.department && (
              <div className="flex justify-between">
                <dt className="text-slate-400">Department</dt>
                <dd className="text-white">{node.assetInfo.department}</dd>
              </div>
            )}
            <div className="pt-2">
              <dt className="text-slate-400 mb-1">Tags</dt>
              <dd className="flex flex-wrap gap-1">
                {node.assetInfo.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 bg-slate-700 text-slate-300 text-xs rounded"
                  >
                    {tag}
                  </span>
                ))}
              </dd>
            </div>
          </dl>
        </section>
      )}

      {/* Section (b): Threat Info */}
      {node.threatInfo && (
        <section data-testid="section-threat" className="p-4 border-b border-slate-700">
          <h4 className="text-sm font-medium text-slate-400 mb-2">Threat Information</h4>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-slate-400">Type</dt>
              <dd className="text-white">{node.threatInfo.threatType}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-400">Severity</dt>
              <dd className={getSeverityClass(node.threatInfo.severity)}>
                {node.threatInfo.severity.toUpperCase()}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-400">Confidence</dt>
              <dd className="text-white">{node.threatInfo.confidence}%</dd>
            </div>
            <div className="pt-2">
              <dt className="text-slate-400 mb-1">Indicators</dt>
              <dd className="space-y-1">
                {node.threatInfo.indicators.map((indicator, idx) => (
                  <div
                    key={idx}
                    className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded font-mono"
                  >
                    {indicator}
                  </div>
                ))}
              </dd>
            </div>
            {node.threatInfo.mitreTechniques && node.threatInfo.mitreTechniques.length > 0 && (
              <div className="pt-2">
                <dt className="text-slate-400 mb-1">MITRE ATT&CK</dt>
                <dd className="flex flex-wrap gap-1">
                  {node.threatInfo.mitreTechniques.map((tech) => (
                    <span
                      key={tech}
                      className="px-2 py-0.5 bg-red-900/50 text-red-300 text-xs rounded"
                    >
                      {tech}
                    </span>
                  ))}
                </dd>
              </div>
            )}
          </dl>
        </section>
      )}

      {/* Section (c): Recommendation */}
      {node.recommendation && (
        <section data-testid="section-recommendation" className="p-4 border-b border-slate-700">
          <h4 className="text-sm font-medium text-slate-400 mb-2">Agent Recommendation</h4>
          <div className="space-y-3">
            <div>
              <span className={getUrgencyBadgeClass(node.recommendation.urgency)}>
                {node.recommendation.urgency.toUpperCase()}
              </span>
            </div>
            <div className="text-white font-medium">{node.recommendation.action}</div>
            <p className="text-slate-400 text-sm">{node.recommendation.reason}</p>
            <div>
              <h5 className="text-slate-400 text-xs mb-1">Recommended Steps:</h5>
              <ol className="list-decimal list-inside text-sm text-slate-300 space-y-1">
                {node.recommendation.steps.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            </div>
          </div>
        </section>
      )}

      {/* Section (d): Status */}
      {node.statusInfo && (
        <section data-testid="section-status" className="p-4">
          <h4 className="text-sm font-medium text-slate-400 mb-2">Status</h4>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-slate-400">Containment</dt>
              <dd className={getContainmentStatusClass(node.statusInfo.containmentStatus)}>
                {node.statusInfo.containmentStatus.toUpperCase()}
              </dd>
            </div>
            {node.statusInfo.ticketId && (
              <div className="flex justify-between">
                <dt className="text-slate-400">Ticket</dt>
                <dd className="text-white">
                  <a
                    href={`/tickets/${node.statusInfo.ticketId}`}
                    className="text-blue-400 hover:underline"
                  >
                    {node.statusInfo.ticketId}
                  </a>
                </dd>
              </div>
            )}
            {node.statusInfo.ticketStatus && (
              <div className="flex justify-between">
                <dt className="text-slate-400">Ticket Status</dt>
                <dd className="text-white">{node.statusInfo.ticketStatus}</dd>
              </div>
            )}
            {node.statusInfo.approvalStatus && node.statusInfo.approvalStatus !== "none" && (
              <div className="flex justify-between">
                <dt className="text-slate-400">Approval</dt>
                <dd className={getApprovalStatusClass(node.statusInfo.approvalStatus)}>
                  {node.statusInfo.approvalStatus.toUpperCase()}
                </dd>
              </div>
            )}
          </dl>
        </section>
      )}

      {/* Fallback if no detailed info */}
      {!node.assetInfo && !node.threatInfo && !node.recommendation && !node.statusInfo && (
        <div className="p-4 text-slate-400 text-sm">
          <p>No additional details available for this node.</p>
          <p className="mt-2">Node ID: {node.id}</p>
        </div>
      )}
    </div>
  );
}

function getNodeTypeBadgeClass(type: string): string {
  const classes: Record<string, string> = {
    incident: "bg-purple-900/50 text-purple-300",
    detection: "bg-orange-900/50 text-orange-300",
    asset: "bg-cyan-900/50 text-cyan-300",
    process: "bg-emerald-900/50 text-emerald-300",
    hash: "bg-pink-900/50 text-pink-300",
  };
  return classes[type] || "bg-slate-700 text-slate-300";
}

function getColorBadgeClass(color: string): string {
  const classes: Record<string, string> = {
    green: "bg-green-900/50 text-green-300",
    yellow: "bg-yellow-900/50 text-yellow-300",
    red: "bg-red-900/50 text-red-300",
    blue: "bg-blue-900/50 text-blue-300",
  };
  return classes[color] || "bg-slate-700 text-slate-300";
}

function getSeverityClass(severity: string): string {
  const classes: Record<string, string> = {
    critical: "text-red-400 font-bold",
    high: "text-orange-400",
    medium: "text-yellow-400",
    low: "text-green-400",
  };
  return classes[severity.toLowerCase()] || "text-slate-300";
}

function getUrgencyBadgeClass(urgency: string): string {
  const classes: Record<string, string> = {
    immediate: "px-2 py-1 bg-red-900/50 text-red-300 text-xs rounded font-bold",
    high: "px-2 py-1 bg-orange-900/50 text-orange-300 text-xs rounded",
    medium: "px-2 py-1 bg-yellow-900/50 text-yellow-300 text-xs rounded",
    low: "px-2 py-1 bg-green-900/50 text-green-300 text-xs rounded",
  };
  return classes[urgency] || "px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded";
}

function getContainmentStatusClass(status: string): string {
  const classes: Record<string, string> = {
    none: "text-slate-400",
    pending: "text-yellow-400",
    contained: "text-blue-400 font-medium",
    lifted: "text-green-400",
  };
  return classes[status] || "text-slate-300";
}

function getApprovalStatusClass(status: string): string {
  const classes: Record<string, string> = {
    requested: "text-yellow-400",
    approved: "text-green-400 font-medium",
    rejected: "text-red-400",
  };
  return classes[status] || "text-slate-300";
}
