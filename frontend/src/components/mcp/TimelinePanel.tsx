/**
 * TimelinePanel - Sliding panel from right edge for timeline display
 *
 * REQ-001-001-005: When state includes `timeline`, render as a sliding panel
 * TECH-006: Timeline panel component
 * REQ-001-004-003: Slide-in animation with staggered entry for items
 */

import { useEffect, useState } from 'react';
import type { McpTimeline, McpTimelineEntry } from '../../types/mcpState';

/** Severity color map for timeline entries */
const SEVERITY_COLORS: Record<string, string> = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-yellow-500',
  low: 'bg-green-500',
  info: 'bg-blue-500',
};

/** Format timestamp for display */
function formatTimestamp(iso: string): string {
  try {
    const date = new Date(iso);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  } catch {
    return iso;
  }
}

interface TimelineEntryItemProps {
  entry: McpTimelineEntry;
  index: number;
  isVisible: boolean;
}

function TimelineEntryItem({ entry, index, isVisible }: TimelineEntryItemProps) {
  const severityColor = SEVERITY_COLORS[entry.severity ?? 'info'] ?? SEVERITY_COLORS.info;

  return (
    <div
      data-testid={`timeline-entry-${entry.id}`}
      className={`
        relative pl-6 pb-4 border-l-2 border-gray-700 last:border-l-0
        transition-all duration-300 ease-out
        ${isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4'}
      `}
      style={{ transitionDelay: `${index * 100}ms` }}
    >
      {/* Severity dot on the timeline line */}
      <div
        className={`absolute -left-[5px] top-1 w-2.5 h-2.5 rounded-full ${severityColor} ring-2 ring-gray-800`}
      />

      {/* Timestamp */}
      <span className="text-xs text-gray-500 font-mono">
        {formatTimestamp(entry.timestamp)}
      </span>

      {/* Title */}
      <h4 className="text-sm font-semibold text-white mt-0.5">{entry.title}</h4>

      {/* Description */}
      <p className="text-xs text-gray-400 mt-0.5">{entry.description}</p>
    </div>
  );
}

interface TimelinePanelProps {
  timeline: McpTimeline | null | undefined;
  onClose: () => void;
}

export function TimelinePanel({ timeline, onClose }: TimelinePanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [entriesVisible, setEntriesVisible] = useState(false);

  useEffect(() => {
    if (timeline) {
      // Slide panel in
      requestAnimationFrame(() => setIsOpen(true));
      // Then stagger entries
      const timer = setTimeout(() => setEntriesVisible(true), 200);
      return () => clearTimeout(timer);
    } else {
      setIsOpen(false);
      setEntriesVisible(false);
    }
  }, [timeline]);

  if (!timeline) return null;

  const handleClose = () => {
    setIsOpen(false);
    setEntriesVisible(false);
    onClose();
  };

  return (
    <div
      data-testid="timeline-panel"
      className={`
        fixed top-0 right-0 h-full w-80 z-50
        bg-gray-800/95 backdrop-blur-sm border-l border-gray-600 shadow-2xl
        transition-transform duration-300 ease-out overflow-y-auto
        ${isOpen ? 'translate-x-0' : 'translate-x-full'}
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700 sticky top-0 bg-gray-800/95">
        <h3 className="text-sm font-semibold text-white">{timeline.title}</h3>
        <button
          onClick={handleClose}
          aria-label="Close timeline"
          className="text-gray-400 hover:text-white transition-colors p-1"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Timeline entries */}
      <div className="p-4">
        {timeline.entries.map((entry, index) => (
          <TimelineEntryItem
            key={entry.id}
            entry={entry}
            index={index}
            isVisible={entriesVisible}
          />
        ))}
      </div>
    </div>
  );
}
