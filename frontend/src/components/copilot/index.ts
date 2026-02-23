/**
 * Copilot Components Exports - DEPRECATED
 *
 * This module is deprecated. Use components/aip-assist instead.
 * All exports are re-exported from aip-assist for backwards compatibility.
 *
 * aIP = Artificial Intelligence Person
 */

// Re-export everything from aip-assist for backwards compatibility
export { AipAssistWidget, CopilotWidget } from "../aip-assist";

export type {
  // Primary types
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
} from "../aip-assist";

export {
  getSuggestionTypeColor,
  getConfidenceColor,
  getSuggestionTypeLabel,
} from "../aip-assist";
