/**
 * IncidentsByHourChart Component
 *
 * A simple SVG-based bar chart showing incidents per hour over the last 24 hours.
 */

import { useMemo } from "react";

export interface HourCount {
  hour: string;
  count: number;
}

interface IncidentsByHourChartProps {
  data: HourCount[];
}

export function IncidentsByHourChart({ data }: IncidentsByHourChartProps) {
  // Calculate chart dimensions and scale
  const chartConfig = useMemo(() => {
    const maxCount = Math.max(...data.map((d) => d.count), 1);
    const chartWidth = 600;
    const chartHeight = 200;
    const padding = { top: 20, right: 20, bottom: 40, left: 40 };
    const plotWidth = chartWidth - padding.left - padding.right;
    const plotHeight = chartHeight - padding.top - padding.bottom;
    const barWidth = (plotWidth / data.length) * 0.8;
    const barGap = (plotWidth / data.length) * 0.2;

    return {
      maxCount,
      chartWidth,
      chartHeight,
      padding,
      plotWidth,
      plotHeight,
      barWidth,
      barGap,
    };
  }, [data]);

  if (data.length === 0) {
    return (
      <div className="bg-secondary rounded-lg p-6 border border-primary">
        <h3 className="text-lg font-semibold text-primary mb-4">Incidents by Hour (Last 24h)</h3>
        <div className="h-48 flex items-center justify-center text-tertiary">
          No incident data available
        </div>
      </div>
    );
  }

  const { maxCount, chartWidth, chartHeight, padding, plotWidth: _plotWidth, plotHeight, barWidth, barGap } =
    chartConfig;

  // Calculate bar positions and heights
  const bars = data.map((item, index) => {
    const x = padding.left + index * (barWidth + barGap);
    const height = (item.count / maxCount) * plotHeight;
    const y = padding.top + plotHeight - height;
    return {
      ...item,
      x,
      y,
      height,
      width: barWidth,
    };
  });

  // Y-axis ticks
  const yTicks = [
    0,
    Math.round(maxCount / 4),
    Math.round(maxCount / 2),
    Math.round((maxCount * 3) / 4),
    maxCount,
  ];

  // X-axis labels (show every 4 hours)
  const xLabels = data.filter((_, i) => i % 4 === 0);

  return (
    <div className="bg-secondary rounded-lg p-6 border border-primary">
      <h3 className="text-lg font-semibold text-primary mb-4">Incidents by Hour (Last 24h)</h3>
      <div className="w-full" data-testid="incidents-by-hour-chart">
        <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-auto">
          {/* Grid lines */}
          {yTicks.map((tick, i) => {
            const y = padding.top + plotHeight - (tick / maxCount) * plotHeight;
            return (
              <g key={`grid-${i}`}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={chartWidth - padding.right}
                  y2={y}
                  stroke="#374151"
                  strokeDasharray="2,2"
                />
                <text x={padding.left - 8} y={y + 4} textAnchor="end" fill="#9ca3af" fontSize="10">
                  {tick}
                </text>
              </g>
            );
          })}

          {/* Bars */}
          {bars.map((bar, index) => (
            <g key={`bar-${index}`}>
              <rect
                x={bar.x}
                y={bar.y}
                width={bar.width}
                height={bar.height}
                fill="#06b6d4"
                rx="2"
                className="hover:fill-cyan-400 transition-colors"
              >
                <title>
                  {bar.hour}: {bar.count} incidents
                </title>
              </rect>
            </g>
          ))}

          {/* X-axis labels */}
          {xLabels.map((item, i) => {
            const index = data.findIndex((d) => d.hour === item.hour);
            const x = padding.left + index * (barWidth + barGap) + barWidth / 2;
            return (
              <text
                key={`label-${i}`}
                x={x}
                y={chartHeight - 10}
                textAnchor="middle"
                fill="#9ca3af"
                fontSize="10"
              >
                {item.hour}
              </text>
            );
          })}

          {/* Axes */}
          <line
            x1={padding.left}
            y1={padding.top + plotHeight}
            x2={chartWidth - padding.right}
            y2={padding.top + plotHeight}
            stroke="#4b5563"
            strokeWidth="1"
          />
          <line
            x1={padding.left}
            y1={padding.top}
            x2={padding.left}
            y2={padding.top + plotHeight}
            stroke="#4b5563"
            strokeWidth="1"
          />
        </svg>
      </div>
    </div>
  );
}
