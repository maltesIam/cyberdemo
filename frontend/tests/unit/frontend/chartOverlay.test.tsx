/**
 * UT-004: Charts as floating overlay tests
 * REQ-001-001-004: When state includes `charts` array, render each entry
 * as a floating overlay component on the current page.
 * TECH-004: Chart overlay component
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChartOverlay } from '../../../src/components/mcp/ChartOverlay';
import type { McpChart } from '../../../src/types/mcpState';

describe('ChartOverlay', () => {
  const sampleChart: McpChart = {
    id: 'chart-1',
    title: 'Incidents by Severity',
    type: 'bar',
    data: [
      { label: 'Critical', value: 5, color: '#ef4444' },
      { label: 'High', value: 12, color: '#f97316' },
      { label: 'Medium', value: 24, color: '#eab308' },
      { label: 'Low', value: 8, color: '#22c55e' },
    ],
  };

  it('should render chart title', () => {
    render(<ChartOverlay chart={sampleChart} onDismiss={vi.fn()} />);
    expect(screen.getByText('Incidents by Severity')).toBeDefined();
  });

  it('should render data labels', () => {
    render(<ChartOverlay chart={sampleChart} onDismiss={vi.fn()} />);
    expect(screen.getByText('Critical')).toBeDefined();
    expect(screen.getByText('High')).toBeDefined();
    expect(screen.getByText('Medium')).toBeDefined();
    expect(screen.getByText('Low')).toBeDefined();
  });

  it('should render data values', () => {
    render(<ChartOverlay chart={sampleChart} onDismiss={vi.fn()} />);
    expect(screen.getByText('5')).toBeDefined();
    expect(screen.getByText('12')).toBeDefined();
    expect(screen.getByText('24')).toBeDefined();
    expect(screen.getByText('8')).toBeDefined();
  });

  it('should call onDismiss when close button is clicked', () => {
    const onDismiss = vi.fn();
    render(<ChartOverlay chart={sampleChart} onDismiss={onDismiss} />);

    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);

    expect(onDismiss).toHaveBeenCalledWith('chart-1');
  });

  it('should have a data-testid attribute for the chart container', () => {
    render(<ChartOverlay chart={sampleChart} onDismiss={vi.fn()} />);
    const container = screen.getByTestId('chart-overlay-chart-1');
    expect(container).toBeDefined();
  });

  it('should render as a floating positioned element', () => {
    render(<ChartOverlay chart={sampleChart} onDismiss={vi.fn()} />);
    const container = screen.getByTestId('chart-overlay-chart-1');
    const style = window.getComputedStyle(container);
    // The component should have position:fixed or be inside a fixed container
    expect(container.className).toContain('fixed');
  });

  it('should display chart type indicator', () => {
    render(<ChartOverlay chart={sampleChart} onDismiss={vi.fn()} />);
    // The chart type should be indicated somewhere
    expect(screen.getByTestId('chart-overlay-chart-1').textContent).toContain('bar');
  });
});

describe('ChartOverlayList', () => {
  it('should render multiple chart overlays', async () => {
    const { ChartOverlayList } = await import('../../../src/components/mcp/ChartOverlay');

    const charts: McpChart[] = [
      {
        id: 'chart-1',
        title: 'Chart A',
        type: 'bar',
        data: [{ label: 'X', value: 10 }],
      },
      {
        id: 'chart-2',
        title: 'Chart B',
        type: 'line',
        data: [{ label: 'Y', value: 20 }],
      },
    ];

    render(<ChartOverlayList charts={charts} onDismiss={vi.fn()} />);

    expect(screen.getByText('Chart A')).toBeDefined();
    expect(screen.getByText('Chart B')).toBeDefined();
  });

  it('should render nothing when charts array is empty', async () => {
    const { ChartOverlayList } = await import('../../../src/components/mcp/ChartOverlay');

    const { container } = render(<ChartOverlayList charts={[]} onDismiss={vi.fn()} />);
    expect(container.innerHTML).toBe('');
  });

  it('should render nothing when charts is undefined', async () => {
    const { ChartOverlayList } = await import('../../../src/components/mcp/ChartOverlay');

    const { container } = render(<ChartOverlayList charts={undefined} onDismiss={vi.fn()} />);
    expect(container.innerHTML).toBe('');
  });
});
