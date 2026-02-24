/**
 * NarrationFooter Component
 *
 * Footer panel displaying narration messages in terminal style on all pages.
 * Supports streaming messages with timestamps, color coding, expand/collapse,
 * and auto-scroll.
 *
 * Requirements:
 * - REQ-001-003-001: Footer panel on all pages
 * - REQ-001-003-002: Streaming messages with timestamps
 * - REQ-001-003-003: Color coding by type
 * - REQ-001-003-004: Expand/collapse toggle
 * - REQ-001-003-005: Auto-scroll to latest
 * - REQ-001-003-006: Message type filter (NTH)
 */

import { useEffect, useRef, useState } from 'react';
import type { DemoNarrationMessage } from '../../types/demo';

export type NarrationMessageType = 'info' | 'warning' | 'error' | 'success';

/** Color mapping for message types: info=white, warning=yellow, error=red, success=green */
const MESSAGE_COLORS: Record<NarrationMessageType, string> = {
  info: 'text-gray-200',
  warning: 'text-yellow-400',
  error: 'text-red-400',
  success: 'text-green-400',
};

const MESSAGE_PREFIX: Record<NarrationMessageType, string> = {
  info: '[INFO]',
  warning: '[WARN]',
  error: '[ERR]',
  success: '[OK]',
};

export interface NarrationFooterProps {
  messages: DemoNarrationMessage[];
  isExpanded: boolean;
  isEnabled: boolean;
  onToggleExpand: () => void;
  onToggleEnabled?: () => void;
  filterType?: NarrationMessageType | 'all';
  onFilterChange?: (type: NarrationMessageType | 'all') => void;
  alwaysVisible?: boolean;
}

/** Format timestamp for terminal display */
const formatTimestamp = (iso: string): string => {
  const date = new Date(iso);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
};

export function NarrationFooter({
  messages,
  isExpanded,
  isEnabled,
  onToggleExpand,
  onToggleEnabled,
  filterType = 'all',
  onFilterChange,
  alwaysVisible = false,
}: NarrationFooterProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const prevCountRef = useRef(messages.length);

  // Auto-scroll when new messages arrive
  useEffect(() => {
    if (messages.length > prevCountRef.current && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
    prevCountRef.current = messages.length;
  }, [messages.length]);

  // Filter messages
  const filteredMessages = filterType === 'all'
    ? messages
    : messages.filter((m) => m.type === filterType);

  return (
    <footer
      data-testid="narration-footer"
      aria-label="Narration panel"
      className={`bg-gray-900 border-t border-gray-700 transition-all ${
        isExpanded ? 'h-48' : 'h-10'
      } ${alwaysVisible ? '' : ''}`}
    >
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 h-10 border-b border-gray-700/50">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-cyan-400">{'>'}_narration</span>
          <span className="text-xs text-gray-500">
            {filteredMessages.length} message{filteredMessages.length !== 1 ? 's' : ''}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {/* Filter dropdown (NTH - T-054) */}
          {onFilterChange && (
            <select
              data-testid="narration-filter"
              value={filterType}
              onChange={(e) => onFilterChange(e.target.value as NarrationMessageType | 'all')}
              className="text-xs bg-gray-800 text-gray-300 border border-gray-700 rounded px-1 py-0.5"
            >
              <option value="all">All</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
              <option value="success">Success</option>
            </select>
          )}
          {/* Enable toggle */}
          {onToggleEnabled && (
            <button
              type="button"
              aria-label={isEnabled ? 'Disable narration' : 'Enable narration'}
              onClick={onToggleEnabled}
              className={`text-xs px-2 py-0.5 rounded ${
                isEnabled ? 'bg-cyan-600/30 text-cyan-400' : 'bg-gray-700 text-gray-500'
              }`}
            >
              {isEnabled ? 'ON' : 'OFF'}
            </button>
          )}
          {/* Expand/collapse toggle */}
          {!alwaysVisible && (
            <button
              type="button"
              aria-label={isExpanded ? 'Collapse narration' : 'Expand narration'}
              onClick={onToggleExpand}
              className="p-1 text-gray-400 hover:text-white rounded transition-colors"
            >
              <svg
                className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Messages area */}
      {isExpanded && (
        <div
          ref={scrollRef}
          data-testid="narration-messages"
          className="h-[calc(100%-2.5rem)] overflow-y-auto font-mono text-xs px-4 py-1"
        >
          {filteredMessages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-600">
              Waiting for narration events...
            </div>
          ) : (
            filteredMessages.map((msg) => (
              <div
                key={msg.id}
                data-testid={`narration-msg-${msg.type}`}
                className={`py-0.5 ${MESSAGE_COLORS[msg.type]}`}
              >
                <span className="text-gray-500">[{formatTimestamp(msg.timestamp)}]</span>{' '}
                <span className="text-gray-400">{MESSAGE_PREFIX[msg.type]}</span>{' '}
                {msg.content}
              </div>
            ))
          )}
        </div>
      )}
    </footer>
  );
}
