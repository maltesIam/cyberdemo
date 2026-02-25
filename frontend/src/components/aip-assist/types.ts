/**
 * Types for aIP Assist Widget Components
 *
 * aIP = Artificial Intelligence Person
 *
 * Requirements:
 * - REQ-004-002-004: UI widget for showing suggestions
 * - REQ-004-002-005: Tracking of acceptance/rejection by session
 */

/** Suggestion type from aIP Assist */
export type SuggestionType = "action" | "investigation" | "correlation" | "alert";

/** Suggestion confidence level */
export type SuggestionConfidence = "high" | "medium" | "low";

/** Suggestion status */
export type SuggestionStatus = "pending" | "accepted" | "rejected" | "expired";

/** A single aIP Assist suggestion */
export interface AipSuggestion {
  /** Unique identifier */
  id: string;
  /** Type of suggestion */
  type: SuggestionType;
  /** Title of the suggestion */
  title: string;
  /** Detailed description */
  description: string;
  /** Confidence level */
  confidence: SuggestionConfidence;
  /** Current status */
  status: SuggestionStatus;
  /** When the suggestion was created */
  createdAt: string;
  /** Related context (alert ID, incident ID, etc.) */
  relatedContext?: string;
  /** Reason for the suggestion */
  reason?: string;
}

/** Session statistics for suggestion tracking */
export interface AipSessionStats {
  /** Total suggestions shown */
  totalSuggestions: number;
  /** Number of accepted suggestions */
  acceptedCount: number;
  /** Number of rejected suggestions */
  rejectedCount: number;
  /** Number of expired suggestions */
  expiredCount: number;
  /** Acceptance rate (0-100) */
  acceptanceRate: number;
}

/** Props for the AipAssistWidget component */
export interface AipAssistWidgetProps {
  /** List of active suggestions */
  suggestions: AipSuggestion[];
  /** Session statistics */
  stats: AipSessionStats;
  /** Whether the widget is expanded */
  isExpanded: boolean;
  /** Whether aIP Assist is enabled */
  isEnabled: boolean;
  /** Callback when a suggestion is accepted */
  onAccept: (suggestionId: string) => void;
  /** Callback when a suggestion is rejected */
  onReject: (suggestionId: string) => void;
  /** Callback when widget is toggled */
  onToggleExpand: () => void;
  /** Callback when aIP Assist is toggled on/off */
  onToggleEnabled: () => void;
  /** Callback to explain why a suggestion was made */
  onExplainWhy?: (suggestionId: string) => void;
}

/** Get color classes for suggestion type */
export const getSuggestionTypeColor = (type: SuggestionType): string => {
  switch (type) {
    case "action":
      return "bg-blue-500";
    case "investigation":
      return "bg-purple-500";
    case "correlation":
      return "bg-green-500";
    case "alert":
      return "bg-red-500";
    default:
      return "bg-gray-500";
  }
};

/** Get color classes for confidence level */
export const getConfidenceColor = (confidence: SuggestionConfidence): string => {
  switch (confidence) {
    case "high":
      return "text-green-400";
    case "medium":
      return "text-yellow-400";
    case "low":
      return "text-red-400";
    default:
      return "text-secondary";
  }
};

/** Get label for suggestion type */
export const getSuggestionTypeLabel = (type: SuggestionType): string => {
  switch (type) {
    case "action":
      return "Action";
    case "investigation":
      return "Investigation";
    case "correlation":
      return "Correlation";
    case "alert":
      return "Alert";
    default:
      return "Unknown";
  }
};

// =============================================================================
// Backwards Compatibility Aliases
// =============================================================================

/** @deprecated Use AipSuggestion instead */
export type CopilotSuggestion = AipSuggestion;

/** @deprecated Use AipSessionStats instead */
export type CopilotSessionStats = AipSessionStats;

/** @deprecated Use AipAssistWidgetProps instead */
export type CopilotWidgetProps = AipAssistWidgetProps;
