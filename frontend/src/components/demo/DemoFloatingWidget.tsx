/**
 * DemoFloatingWidget Component
 *
 * Floating aIP Assist widget positioned bottom-right on all pages.
 * Wraps AipAssistWidget with floating positioning, collapsed circular button,
 * notification badge, and thinking indicator.
 *
 * Requirements:
 * - REQ-001-002-001: Floating widget bottom-right
 * - REQ-001-002-002: Collapsed state with badge
 * - REQ-001-002-003: Expanded panel with suggestions
 * - REQ-001-002-004: Action buttons per suggestion
 * - REQ-001-002-005: Thinking indicator
 * - REQ-001-002-006: Badge count for unread
 */

import { AipAssistWidget } from '../aip-assist/AipAssistWidget';
import type { AipSuggestion } from '../aip-assist/types';
import type { AipSessionStats } from '../aip-assist/types';

export interface DemoFloatingWidgetProps {
  suggestions: AipSuggestion[];
  stats: AipSessionStats;
  isExpanded: boolean;
  isEnabled: boolean;
  isThinking: boolean;
  unreadCount: number;
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
  onToggleExpand: () => void;
  onToggleEnabled: () => void;
  onExplainWhy?: (id: string) => void;
}

/** Robot/AI icon for collapsed button */
const AipIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
    />
  </svg>
);

/** Thinking indicator dots animation */
const ThinkingIndicator = () => (
  <div data-testid="thinking-indicator" className="flex items-center gap-1 px-3 py-2 border-b border-gray-700">
    <span className="text-xs text-cyan-400">AI is thinking</span>
    <div className="flex gap-0.5">
      <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
      <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
      <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
  </div>
);

export function DemoFloatingWidget({
  suggestions,
  stats,
  isExpanded,
  isEnabled,
  isThinking,
  unreadCount,
  onAccept,
  onReject,
  onToggleExpand,
  onToggleEnabled,
  onExplainWhy,
}: DemoFloatingWidgetProps) {
  // Collapsed state: circular button with badge
  if (!isExpanded) {
    return (
      <div
        data-testid="aip-floating-widget"
        className="fixed bottom-6 right-6 z-50"
      >
        <button
          type="button"
          aria-label="Open aIP Assist"
          onClick={onToggleExpand}
          className="relative w-14 h-14 bg-cyan-600 hover:bg-cyan-700 text-white rounded-full shadow-lg transition-all hover:scale-105 flex items-center justify-center"
        >
          <AipIcon />
          {/* Notification badge */}
          {unreadCount > 0 && (
            <span
              data-testid="unread-badge"
              className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center"
            >
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
          {/* Thinking pulse */}
          {isThinking && (
            <span className="absolute inset-0 rounded-full bg-cyan-400 animate-ping opacity-20" />
          )}
        </button>
      </div>
    );
  }

  // Expanded state: full panel
  return (
    <div
      data-testid="aip-floating-widget"
      className="fixed bottom-6 right-6 z-50 w-80 max-h-[500px] flex flex-col rounded-lg shadow-2xl overflow-hidden"
    >
      {isThinking && <ThinkingIndicator />}
      <AipAssistWidget
        suggestions={suggestions}
        stats={stats}
        isExpanded={true}
        isEnabled={isEnabled}
        onAccept={onAccept}
        onReject={onReject}
        onToggleExpand={onToggleExpand}
        onToggleEnabled={onToggleEnabled}
        onExplainWhy={onExplainWhy}
      />
    </div>
  );
}
