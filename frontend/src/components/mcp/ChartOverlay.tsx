/**
 * ChartOverlay - Floating chart overlay component
 *
 * REQ-001-001-004: Render charts as floating overlays on the current page
 * TECH-004: Chart overlay component
 * REQ-001-004-001: Smooth entrance animation + auto-dismiss timer
 */

import { useEffect, useState } from 'react';
import type { McpChart, ChartDataPoint } from '../../types/mcpState';

interface ChartOverlayProps {
  chart: McpChart;
  onDismiss: (chartId: string) => void;
}

/** Renders a horizontal bar representation of a data point */
function ChartBar({ point, maxValue }: { point: ChartDataPoint; maxValue: number }) {
  const widthPercent = maxValue > 0 ? (point.value / maxValue) * 100 : 0;
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="w-20 text-secondary truncate">{point.label}</span>
      <div className="flex-1 bg-tertiary rounded-full h-3">
        <div
          className="h-3 rounded-full transition-all duration-700 ease-out mcp-chart-bar-enter"
          style={{
            width: `${widthPercent}%`,
            backgroundColor: point.color ?? '#3b82f6',
          }}
        />
      </div>
      <span className="w-8 text-right text-secondary">{point.value}</span>
    </div>
  );
}

export function ChartOverlay({ chart, onDismiss }: ChartOverlayProps) {
  const [isVisible, setIsVisible] = useState(false);
  const maxValue = Math.max(...chart.data.map((d) => d.value), 1);

  // Entrance animation
  useEffect(() => {
    const timer = requestAnimationFrame(() => setIsVisible(true));
    return () => cancelAnimationFrame(timer);
  }, []);

  // Auto-dismiss timer
  useEffect(() => {
    const dismissMs = chart.autoDismissMs ?? 10000;
    if (dismissMs <= 0) return;

    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => onDismiss(chart.id), 300);
    }, dismissMs);

    return () => clearTimeout(timer);
  }, [chart.id, chart.autoDismissMs, onDismiss]);

  const handleClose = () => {
    setIsVisible(false);
    onDismiss(chart.id);
  };

  return (
    <div
      data-testid={`chart-overlay-${chart.id}`}
      className={`
        fixed z-40 bg-secondary/95 backdrop-blur-sm border border-primary rounded-lg shadow-2xl
        p-4 min-w-[280px] max-w-[400px]
        transition-all duration-300 ease-out
        ${isVisible ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-4 scale-95'}
      `}
      style={{
        bottom: `${80 + (chart.position?.y ?? 0)}px`,
        left: `${20 + (chart.position?.x ?? 0)}px`,
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-primary">{chart.title}</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-tertiary bg-tertiary px-1.5 py-0.5 rounded">
            {chart.type}
          </span>
          <button
            onClick={handleClose}
            aria-label="Close chart"
            className="text-secondary hover:text-primary transition-colors p-0.5"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Chart Body */}
      <div className="space-y-2">
        {chart.data.map((point) => (
          <ChartBar key={point.label} point={point} maxValue={maxValue} />
        ))}
      </div>
    </div>
  );
}

/** Props for ChartOverlayList */
interface ChartOverlayListProps {
  charts: McpChart[] | undefined;
  onDismiss: (chartId: string) => void;
}

/**
 * Renders a list of chart overlays, stacked vertically.
 */
export function ChartOverlayList({ charts, onDismiss }: ChartOverlayListProps) {
  if (!charts || charts.length === 0) return null;

  return (
    <>
      {charts.map((chart, index) => (
        <ChartOverlay
          key={chart.id}
          chart={{
            ...chart,
            position: chart.position ?? { x: 0, y: index * 220 },
          }}
          onDismiss={onDismiss}
        />
      ))}
    </>
  );
}
