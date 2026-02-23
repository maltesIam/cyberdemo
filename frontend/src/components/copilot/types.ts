/**
 * Types for Copilot Widget Components - DEPRECATED
 *
 * This module is deprecated. Use components/aip-assist/types instead.
 * All exports are re-exported from aip-assist for backwards compatibility.
 *
 * aIP = Artificial Intelligence Person
 */

// Re-export everything from aip-assist for backwards compatibility
export type {
  // Primary types
  AipSuggestion,
  AipSessionStats,
  AipAssistWidgetProps,
  // Backwards compatibility aliases
  CopilotSuggestion,
  CopilotSessionStats,
  CopilotWidgetProps,
  // Shared types
  SuggestionType,
  SuggestionConfidence,
  SuggestionStatus,
} from "../aip-assist/types";

export {
  getSuggestionTypeColor,
  getConfidenceColor,
  getSuggestionTypeLabel,
} from "../aip-assist/types";
