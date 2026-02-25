/**
 * NarrationPanel Component
 *
 * A collapsable panel that displays agent narration messages with
 * different message types, confidence indicators, and auto-scroll.
 *
 * Requirements:
 * - REQ-003-001-001: Collapsable panel on right side
 * - REQ-003-001-002: Message types with icons (thinking/finding/decision/action)
 * - REQ-003-001-003: Confidence indicator with colors (high/medium/low)
 * - REQ-003-001-004: Auto-scroll for new messages
 * - REQ-003-001-005: Toggle to enable/disable narration
 */

import { useEffect, useRef, useState } from "react";
import type { NarrationPanelProps, NarrationMessage, MessageType, ConfidenceLevel } from "./types";
import { CONFIDENCE_COLORS } from "./types";

/** Icon component for thinking type */
const ThinkingIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    data-testid="icon-thinking"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
    />
  </svg>
);

/** Icon component for finding type */
const FindingIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    data-testid="icon-finding"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
    />
  </svg>
);

/** Icon component for decision type */
const DecisionIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    data-testid="icon-decision"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
    />
  </svg>
);

/** Icon component for action type */
const ActionIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    data-testid="icon-action"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M13 10V3L4 14h7v7l9-11h-7z"
    />
  </svg>
);

/** Map message types to their icons */
const MessageTypeIcons: Record<MessageType, React.FC> = {
  thinking: ThinkingIcon,
  finding: FindingIcon,
  decision: DecisionIcon,
  action: ActionIcon,
};

/** Format timestamp for display */
const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
};

/** Confidence indicator component */
const ConfidenceIndicator = ({ level }: { level: ConfidenceLevel }) => {
  const colorClass = CONFIDENCE_COLORS[level];

  return (
    <div className="flex items-center space-x-1">
      <div
        data-testid="confidence-indicator"
        className={`w-2 h-2 rounded-full ${colorClass}`}
      />
      <span className="text-xs text-secondary capitalize">{level}</span>
    </div>
  );
};

/** Individual narration message component */
const NarrationMessageItem = ({ message }: { message: NarrationMessage }) => {
  const Icon = MessageTypeIcons[message.type];

  return (
    <div className="p-3 border-b border-primary last:border-b-0 hover:bg-tertiary/50 transition-colors">
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 text-cyan-400">
          <Icon />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-tertiary">
              {formatTimestamp(message.timestamp)}
            </span>
            <ConfidenceIndicator level={message.confidence} />
          </div>
          <p className="text-sm text-primary break-words">{message.content}</p>
        </div>
      </div>
    </div>
  );
};

/** Toggle switch component */
const ToggleSwitch = ({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
}) => (
  <label className="flex items-center cursor-pointer">
    <div className="relative">
      <input
        type="checkbox"
        role="switch"
        aria-label={label}
        className="sr-only"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <div
        className={`w-10 h-5 rounded-full transition-colors ${
          checked ? "bg-cyan-600" : "bg-tertiary"
        }`}
      />
      <div
        className={`absolute left-0.5 top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
          checked ? "translate-x-5" : "translate-x-0"
        }`}
      />
    </div>
    <span className="ml-2 text-xs text-secondary">
      {checked ? "Enabled" : "Disabled"}
    </span>
  </label>
);

/** Collapse/Expand toggle button */
const CollapseToggle = ({
  isCollapsed,
  onClick,
}: {
  isCollapsed: boolean;
  onClick: () => void;
}) => (
  <button
    role="button"
    aria-label="Toggle panel"
    onClick={onClick}
    onKeyDown={(e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        onClick();
      }
    }}
    className="p-1 rounded hover:bg-tertiary transition-colors"
  >
    <svg
      className={`w-5 h-5 text-secondary transition-transform ${
        isCollapsed ? "rotate-180" : ""
      }`}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d={isCollapsed ? "M9 5l7 7-7 7" : "M15 19l-7-7 7-7"}
      />
    </svg>
  </button>
);

/** Main NarrationPanel component */
export function NarrationPanel({
  messages,
  isCollapsed: isCollapsedProp = false,
  onToggle,
  isNarrationEnabled: isNarrationEnabledProp = true,
  onNarrationToggle,
  autoScroll = true,
}: NarrationPanelProps) {
  // Internal state for uncontrolled mode
  const [isCollapsedInternal, setIsCollapsedInternal] = useState(isCollapsedProp);
  const [isNarrationEnabledInternal, setIsNarrationEnabledInternal] = useState(isNarrationEnabledProp);

  // Determine if controlled or uncontrolled
  const isCollapsed = onToggle ? isCollapsedProp : isCollapsedInternal;
  const isNarrationEnabled = onNarrationToggle ? isNarrationEnabledProp : isNarrationEnabledInternal;

  // Ref for auto-scroll
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const previousMessageCount = useRef(messages.length);

  // Auto-scroll effect
  useEffect(() => {
    if (autoScroll && messages.length > previousMessageCount.current && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
    previousMessageCount.current = messages.length;
  }, [messages.length, autoScroll]);

  // Handle toggle
  const handleToggle = () => {
    if (onToggle) {
      onToggle();
    } else {
      setIsCollapsedInternal(!isCollapsedInternal);
    }
  };

  // Handle narration toggle
  const handleNarrationToggle = (enabled: boolean) => {
    if (onNarrationToggle) {
      onNarrationToggle(enabled);
    } else {
      setIsNarrationEnabledInternal(enabled);
    }
  };

  return (
    <aside
      role="region"
      aria-label="Agent Narration Panel"
      className={`bg-secondary border-l border-primary flex flex-col transition-all duration-300 ${
        isCollapsed ? "w-12" : "w-80"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-primary">
        {!isCollapsed && (
          <div className="flex items-center space-x-2">
            <svg
              className="w-5 h-5 text-cyan-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
            <h2 className="text-sm font-semibold text-primary">Agent Narration</h2>
          </div>
        )}

        <div className="flex items-center space-x-2">
          {isCollapsed && messages.length > 0 && (
            <span className="flex items-center justify-center w-5 h-5 text-xs font-bold text-primary bg-cyan-600 rounded-full">
              {messages.length}
            </span>
          )}
          <CollapseToggle isCollapsed={isCollapsed} onClick={handleToggle} />
        </div>
      </div>

      {/* Content (only when expanded) */}
      {!isCollapsed && (
        <>
          {/* Controls */}
          <div className="flex items-center justify-between p-3 border-b border-primary bg-secondary/50">
            <span className="text-xs text-secondary">Narration</span>
            <ToggleSwitch
              checked={isNarrationEnabled}
              onChange={handleNarrationToggle}
              label="Toggle narration"
            />
          </div>

          {/* Messages */}
          <div
            data-testid="narration-messages"
            className="flex-1 overflow-y-auto"
          >
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-32 text-tertiary text-sm">
                No messages yet
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <NarrationMessageItem key={message.id} message={message} />
                ))}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </>
      )}
    </aside>
  );
}
