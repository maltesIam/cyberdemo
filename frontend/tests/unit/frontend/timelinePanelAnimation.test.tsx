/**
 * UT-017: Timeline panel animation tests
 * REQ-001-004-003: Timeline panel slides in from right with staggered
 * entry animation for each timeline item.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TimelinePanel } from '../../../src/components/mcp/TimelinePanel';
import type { McpTimeline } from '../../../src/types/mcpState';

describe('TimelinePanel Animation', () => {
  const sampleTimeline: McpTimeline = {
    title: 'Attack Timeline',
    entries: [
      {
        id: 'entry-1',
        timestamp: '2026-02-24T10:00:00Z',
        title: 'Step 1',
        description: 'First step',
        severity: 'high',
      },
      {
        id: 'entry-2',
        timestamp: '2026-02-24T10:05:00Z',
        title: 'Step 2',
        description: 'Second step',
        severity: 'critical',
      },
      {
        id: 'entry-3',
        timestamp: '2026-02-24T10:10:00Z',
        title: 'Step 3',
        description: 'Third step',
        severity: 'medium',
      },
    ],
  };

  it('should have slide-in transition classes on the panel', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    const panel = screen.getByTestId('timeline-panel');

    // Should have transition classes for the slide animation
    expect(panel.className).toContain('transition-transform');
    expect(panel.className).toContain('duration-300');
  });

  it('should use translate-x classes for slide-in effect', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    const panel = screen.getByTestId('timeline-panel');

    // Panel uses translate-x-0 (open) or translate-x-full (closed) for slide
    expect(panel.className).toMatch(/translate-x/);
  });

  it('should have staggered transition-delay on each entry', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);

    const entries = screen.getAllByTestId(/timeline-entry-/);
    expect(entries.length).toBe(3);

    // Each entry should have a different transition-delay
    // Entry 0: 0ms, Entry 1: 100ms, Entry 2: 200ms
    entries.forEach((entry, index) => {
      const style = entry.getAttribute('style') ?? '';
      expect(style).toContain(`${index * 100}ms`);
    });
  });

  it('each entry should have transition classes for opacity and translate', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);

    const entries = screen.getAllByTestId(/timeline-entry-/);
    entries.forEach((entry) => {
      expect(entry.className).toContain('transition-all');
      expect(entry.className).toContain('duration-300');
    });
  });

  it('should position the panel with right-0 for right-edge sliding', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    const panel = screen.getByTestId('timeline-panel');
    expect(panel.className).toContain('right-0');
  });

  it('should have full height for the sliding panel', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    const panel = screen.getByTestId('timeline-panel');
    expect(panel.className).toContain('h-full');
  });

  it('should be a fixed position panel', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    const panel = screen.getByTestId('timeline-panel');
    expect(panel.className).toContain('fixed');
  });
});
