/**
 * AipAssistWidget Component
 *
 * Widget for displaying AI assistant suggestions with
 * accept/reject tracking and session statistics.
 *
 * aIP = Artificial Intelligence Person
 *
 * Requirements:
 * - REQ-004-002-004: UI widget for showing suggestions
 * - REQ-004-002-005: Tracking of acceptance/rejection by session
 * - TECH-012: New component AipAssistWidget.tsx
 */

import { useCallback } from "react";
import type {
  AipAssistWidgetProps,
  AipSuggestion,
  SuggestionConfidence,
  SuggestionType,
} from "./types";
import {
  getSuggestionTypeColor,
  getConfidenceColor,
  getSuggestionTypeLabel,
} from "./types";

/** Get confidence label */
const getConfidenceLabel = (confidence: SuggestionConfidence): string => {
  return confidence.charAt(0).toUpperCase() + confidence.slice(1);
};

/** Check icon */
const CheckIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

/** X icon */
const XIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

/** Question icon */
const QuestionIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
    />
  </svg>
);

/** Chevron icon */
const ChevronIcon = ({ isExpanded }: { isExpanded: boolean }) => (
  <svg
    className={`w-5 h-5 transition-transform ${isExpanded ? "rotate-180" : ""}`}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
);

/** Robot/AI icon */
const AipIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
    />
  </svg>
);

/** Single suggestion item component */
interface SuggestionItemProps {
  suggestion: AipSuggestion;
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
  onExplainWhy?: (id: string) => void;
}

const SuggestionItem = ({
  suggestion,
  onAccept,
  onReject,
  onExplainWhy,
}: SuggestionItemProps) => {
  const handleAccept = useCallback(() => {
    onAccept(suggestion.id);
  }, [onAccept, suggestion.id]);

  const handleReject = useCallback(() => {
    onReject(suggestion.id);
  }, [onReject, suggestion.id]);

  const handleExplainWhy = useCallback(() => {
    onExplainWhy?.(suggestion.id);
  }, [onExplainWhy, suggestion.id]);

  return (
    <li
      role="listitem"
      className="p-3 bg-tertiary/50 rounded-lg border border-primary space-y-2"
    >
      {/* Header with type and confidence */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span
            className={`px-2 py-0.5 rounded text-xs font-medium text-primary ${getSuggestionTypeColor(
              suggestion.type
            )}`}
          >
            {getSuggestionTypeLabel(suggestion.type)}
          </span>
          <span
            className={`text-xs font-medium ${getConfidenceColor(
              suggestion.confidence
            )}`}
          >
            {getConfidenceLabel(suggestion.confidence)}
          </span>
        </div>
      </div>

      {/* Title and description */}
      <div>
        <h4 className="text-sm font-medium text-primary">{suggestion.title}</h4>
        <p className="text-xs text-secondary mt-1">{suggestion.description}</p>
      </div>

      {/* Reason if provided */}
      {suggestion.reason && (
        <div className="text-xs text-tertiary italic">
          Reason: {suggestion.reason}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex items-center space-x-2 pt-1">
        <button
          type="button"
          aria-label="Accept suggestion"
          onClick={handleAccept}
          className="flex items-center space-x-1 px-2 py-1 bg-green-600 hover:bg-green-700 text-primary text-xs rounded transition-colors"
        >
          <CheckIcon />
          <span>Accept</span>
        </button>
        <button
          type="button"
          aria-label="Reject suggestion"
          onClick={handleReject}
          className="flex items-center space-x-1 px-2 py-1 bg-red-600 hover:bg-red-700 text-primary text-xs rounded transition-colors"
        >
          <XIcon />
          <span>Reject</span>
        </button>
        {onExplainWhy && (
          <button
            type="button"
            aria-label="Why this suggestion"
            onClick={handleExplainWhy}
            className="flex items-center space-x-1 px-2 py-1 bg-tertiary hover:bg-hover text-primary text-xs rounded transition-colors"
          >
            <QuestionIcon />
            <span>Why?</span>
          </button>
        )}
      </div>
    </li>
  );
};

/** Stats display component */
interface StatsDisplayProps {
  totalSuggestions: number;
  acceptedCount: number;
  rejectedCount: number;
  acceptanceRate: number;
}

const StatsDisplay = ({
  totalSuggestions,
  acceptedCount,
  rejectedCount,
  acceptanceRate,
}: StatsDisplayProps) => (
  <div className="grid grid-cols-4 gap-2 p-2 bg-tertiary/30 rounded-lg text-center">
    <div>
      <div className="text-sm font-semibold text-primary">{totalSuggestions}</div>
      <div className="text-[10px] text-tertiary">Total</div>
    </div>
    <div>
      <div className="text-sm font-semibold text-green-400">{acceptedCount}</div>
      <div className="text-[10px] text-tertiary">Accepted</div>
    </div>
    <div>
      <div className="text-sm font-semibold text-red-400">{rejectedCount}</div>
      <div className="text-[10px] text-tertiary">Rejected</div>
    </div>
    <div>
      <div className="text-sm font-semibold text-cyan-400">{acceptanceRate}%</div>
      <div className="text-[10px] text-tertiary">Rate</div>
    </div>
  </div>
);

export function AipAssistWidget({
  suggestions,
  stats,
  isExpanded,
  isEnabled,
  onAccept,
  onReject,
  onToggleExpand,
  onToggleEnabled,
  onExplainWhy,
}: AipAssistWidgetProps) {
  const pendingSuggestions = suggestions.filter((s) => s.status === "pending");

  return (
    <div
      data-testid="aip-assist-widget"
      aria-label="aIP Assist suggestions"
      className="bg-secondary border border-primary rounded-lg overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-primary">
        <div className="flex items-center space-x-2">
          <AipIcon />
          <h3 className="text-sm font-semibold text-primary">aIP Assist</h3>
          {!isExpanded && pendingSuggestions.length > 0 && (
            <span className="px-1.5 py-0.5 bg-cyan-600 text-primary text-xs rounded-full">
              {pendingSuggestions.length}
            </span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {/* Enable/Disable toggle */}
          <button
            type="button"
            role="switch"
            aria-label="Toggle aIP Assist"
            aria-checked={isEnabled}
            onClick={onToggleEnabled}
            className={`relative w-10 h-5 rounded-full transition-colors ${
              isEnabled ? "bg-cyan-600" : "bg-tertiary"
            }`}
          >
            <div
              className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${
                isEnabled ? "translate-x-5" : "translate-x-0.5"
              }`}
            />
          </button>
          {/* Expand/Collapse toggle */}
          <button
            type="button"
            aria-label={isExpanded ? "Collapse widget" : "Expand widget"}
            onClick={onToggleExpand}
            className="p-1 hover:bg-tertiary rounded transition-colors"
          >
            <ChevronIcon isExpanded={isExpanded} />
          </button>
        </div>
      </div>

      {/* Disabled state */}
      {!isEnabled && (
        <div className="p-4 text-center">
          <p className="text-sm text-tertiary">aIP Assist is disabled</p>
          <button
            type="button"
            onClick={onToggleEnabled}
            className="mt-2 text-xs text-cyan-400 hover:text-cyan-300"
          >
            Enable aIP Assist
          </button>
        </div>
      )}

      {/* Expanded content */}
      {isEnabled && isExpanded && (
        <div className="p-3 space-y-3">
          {/* Session Stats */}
          <StatsDisplay
            totalSuggestions={stats.totalSuggestions}
            acceptedCount={stats.acceptedCount}
            rejectedCount={stats.rejectedCount}
            acceptanceRate={stats.acceptanceRate}
          />

          {/* Suggestions list */}
          {pendingSuggestions.length > 0 ? (
            <ul role="list" className="space-y-2 max-h-[300px] overflow-y-auto">
              {pendingSuggestions.map((suggestion) => (
                <SuggestionItem
                  key={suggestion.id}
                  suggestion={suggestion}
                  onAccept={onAccept}
                  onReject={onReject}
                  onExplainWhy={onExplainWhy}
                />
              ))}
            </ul>
          ) : (
            <div className="py-4 text-center">
              <p className="text-sm text-tertiary">No suggestions at the moment</p>
              <p className="text-xs text-tertiary mt-1">
                aIP will provide suggestions based on your actions
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Backwards compatibility alias
export const CopilotWidget = AipAssistWidget;
