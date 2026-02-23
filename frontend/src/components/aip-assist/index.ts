/**
 * aIP Assist Components Exports
 *
 * aIP = Artificial Intelligence Person
 *
 * Requirements covered:
 * - REQ-004-002-004: UI widget for showing suggestions
 * - REQ-004-002-005: Tracking of acceptance/rejection by session
 * - TECH-012: New component AipAssistWidget.tsx
 */

export { AipAssistWidget, CopilotWidget } from "./AipAssistWidget";

export type {
  AipSuggestion,
  AipSessionStats,
  AipAssistWidgetProps,
  // Backwards compatibility aliases
  CopilotSuggestion,
  CopilotSessionStats,
  CopilotWidgetProps,
  SuggestionType,
  SuggestionConfidence,
  SuggestionStatus,
} from "./types";

export {
  getSuggestionTypeColor,
  getConfidenceColor,
  getSuggestionTypeLabel,
} from "./types";
