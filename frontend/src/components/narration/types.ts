/**
 * Types for Narration Panel
 *
 * Requirements:
 * - REQ-003-001-002: Message types (thinking/finding/decision/action)
 * - REQ-003-001-003: Confidence indicator (high/medium/low)
 * - REQ-003-002-002: Message format {type, content, confidence, timestamp}
 */

/** Message types with corresponding icons */
export type MessageType = "thinking" | "finding" | "decision" | "action";

/** Confidence levels with corresponding colors */
export type ConfidenceLevel = "high" | "medium" | "low";

/** A narration message from the agent */
export interface NarrationMessage {
  /** Unique identifier for the message */
  id: string;
  /** Type of message determines the icon displayed */
  type: MessageType;
  /** The narration content */
  content: string;
  /** Confidence level of the statement */
  confidence: ConfidenceLevel;
  /** ISO timestamp of when the message was created */
  timestamp: string;
}

/** Props for the NarrationPanel component */
export interface NarrationPanelProps {
  /** List of narration messages to display */
  messages: NarrationMessage[];
  /** Whether the panel is collapsed (defaults to false) */
  isCollapsed?: boolean;
  /** Callback when panel is toggled */
  onToggle?: () => void;
  /** Whether narration is enabled (defaults to true) */
  isNarrationEnabled?: boolean;
  /** Callback when narration is toggled */
  onNarrationToggle?: (enabled: boolean) => void;
  /** Whether to auto-scroll to new messages (defaults to true) */
  autoScroll?: boolean;
}

/** Props for individual narration message component */
export interface NarrationMessageProps {
  message: NarrationMessage;
}

/** Icon map for message types */
export const MESSAGE_TYPE_ICONS: Record<MessageType, string> = {
  thinking: "thinking", // Brain/thought bubble
  finding: "finding", // Magnifying glass
  decision: "decision", // Checkmark
  action: "action", // Lightning bolt
};

/** Color map for confidence levels */
export const CONFIDENCE_COLORS: Record<ConfidenceLevel, string> = {
  high: "bg-green-500",
  medium: "bg-yellow-500",
  low: "bg-red-500",
};
