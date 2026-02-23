/**
 * useCopilotActions Hook - DEPRECATED
 *
 * This module is deprecated. Use hooks/useAipAssist instead.
 * All exports are re-exported from useAipAssist for backwards compatibility.
 *
 * aIP = Artificial Intelligence Person
 */

// Re-export everything from useAipAssist for backwards compatibility
export {
  // Primary exports
  useAipAssist,
  AipActionType,
  // Backwards compatibility aliases
  useCopilotActions,
  CopilotActionType,
} from "./useAipAssist";

export type {
  // Primary types
  AipActionContext,
  UseAipAssistOptions,
  UseAipAssistReturn,
  // Backwards compatibility aliases
  CopilotActionContext,
  UseCopilotActionsOptions,
  UseCopilotActionsReturn,
} from "./useAipAssist";
