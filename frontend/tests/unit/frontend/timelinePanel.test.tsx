/**
 * UT-005: Timeline as sliding panel tests
 * REQ-001-001-005: When state includes `timeline`, render as a sliding panel
 * from the right edge.
 * TECH-006: Timeline panel component
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TimelinePanel } from '../../../src/components/mcp/TimelinePanel';
import type { McpTimeline } from '../../../src/types/mcpState';

describe('TimelinePanel', () => {
  const sampleTimeline: McpTimeline = {
    title: 'Attack Timeline',
    entries: [
      {
        id: 'entry-1',
        timestamp: '2026-02-24T10:00:00Z',
        title: 'Initial Access',
        description: 'Phishing email delivered to user@corp.com',
        severity: 'high',
      },
      {
        id: 'entry-2',
        timestamp: '2026-02-24T10:05:00Z',
        title: 'Execution',
        description: 'Macro executed in Word document',
        severity: 'critical',
      },
      {
        id: 'entry-3',
        timestamp: '2026-02-24T10:10:00Z',
        title: 'Persistence',
        description: 'Registry key added for startup persistence',
        severity: 'medium',
      },
    ],
  };

  it('should render timeline title', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    expect(screen.getByText('Attack Timeline')).toBeDefined();
  });

  it('should render all timeline entries', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    expect(screen.getByText('Initial Access')).toBeDefined();
    expect(screen.getByText('Execution')).toBeDefined();
    expect(screen.getByText('Persistence')).toBeDefined();
  });

  it('should render entry descriptions', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    expect(screen.getByText('Phishing email delivered to user@corp.com')).toBeDefined();
    expect(screen.getByText('Macro executed in Word document')).toBeDefined();
  });

  it('should call onClose when close button is clicked', () => {
    const onClose = vi.fn();
    render(<TimelinePanel timeline={sampleTimeline} onClose={onClose} />);

    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('should have a data-testid for the panel', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    const panel = screen.getByTestId('timeline-panel');
    expect(panel).toBeDefined();
  });

  it('should position panel on the right edge', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    const panel = screen.getByTestId('timeline-panel');
    expect(panel.className).toContain('right-0');
  });

  it('should render nothing when timeline is null', () => {
    const { container } = render(<TimelinePanel timeline={null} onClose={vi.fn()} />);
    expect(container.innerHTML).toBe('');
  });

  it('should render nothing when timeline is undefined', () => {
    const { container } = render(<TimelinePanel timeline={undefined} onClose={vi.fn()} />);
    expect(container.innerHTML).toBe('');
  });

  it('should show severity indicators for entries', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    // Each entry should have a severity-colored indicator
    const entries = screen.getAllByTestId(/timeline-entry-/);
    expect(entries.length).toBe(3);
  });

  it('should display timestamps', () => {
    render(<TimelinePanel timeline={sampleTimeline} onClose={vi.fn()} />);
    // Timestamps should be displayed in some format (locale-dependent)
    const panel = screen.getByTestId('timeline-panel');
    // Check that at least one colon-separated time is present (e.g. "10:00" or "11:00")
    expect(panel.textContent).toMatch(/\d{2}:\d{2}/);
  });
});
