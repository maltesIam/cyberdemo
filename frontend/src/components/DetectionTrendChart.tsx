/**
 * DetectionTrendChart Component
 *
 * A simple SVG-based bar/line chart showing detection trend over the last 7 days.
 */

import { useMemo } from "react";
import { format, subDays } from "date-fns";

export interface DayCount {
  day: string;
  count: number;
}

interface DetectionTrendChartProps {
  data: DayCount[];
}

// Generate default 7-day data if none provided
function generateDefaultData(): DayCount[] {
  const today = new Date();
  return Array.from({ length: 7 }, (_, i) => {
    const date = subDays(today, 6 - i);
    return {
      day: format(date, "EEE"),
      count: 0,
    };
  });
}

export function DetectionTrendChart({ data }: DetectionTrendChartProps) {
  const chartData = data.length > 0 ? data : generateDefaultData();

  // Calculate chart dimensions and scale
  const chartConfig = useMemo(() => {
    const maxCount = Math.max(...chartData.map((d) => d.count), 1);
    const chartWidth = 600;
    const chartHeight = 200;
    const padding = { top: 20, right: 20, bottom: 40, left: 40 };
    const plotWidth = chartWidth - padding.left - padding.right;
    const plotHeight = chartHeight - padding.top - padding.bottom;
    const barWidth = (plotWidth / chartData.length) * 0.6;
    const barGap = (plotWidth / chartData.length) * 0.4;

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
  }, [chartData]);

  if (chartData.every((d) => d.count === 0)) {
    return (
      <div className="bg-secondary rounded-lg p-6 border border-primary">
        <h3 className="text-lg font-semibold text-primary mb-4">Detection Trend (Last 7 Days)</h3>
        <div className="h-48 flex items-center justify-center text-tertiary">
          No detection data available for the last 7 days
        </div>
      </div>
    );
  }

  const { maxCount, chartWidth, chartHeight, padding, plotWidth: _plotWidth, plotHeight, barWidth, barGap } =
    chartConfig;

  // Calculate bar positions and heights
  const bars = chartData.map((item, index) => {
    const x = padding.left + index * (barWidth + barGap) + barGap / 2;
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
  const yTicks = [0, Math.round(maxCount / 2), maxCount];

  // Line path for trend line
  const linePoints = bars.map((bar) => ({
    x: bar.x + bar.width / 2,
    y: bar.y,
  }));
  const linePath = `M ${linePoints.map((p) => `${p.x},${p.y}`).join(" L ")}`;

  return (
    <div className="bg-secondary rounded-lg p-6 border border-primary">
      <h3 className="text-lg font-semibold text-primary mb-4">Detection Trend (Last 7 Days)</h3>
      <div className="w-full" data-testid="detection-trend-chart">
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
                height={Math.max(bar.height, 2)}
                fill="#22c55e"
                rx="3"
                className="hover:fill-green-400 transition-colors"
              >
                <title>
                  {bar.day}: {bar.count} detections
                </title>
              </rect>
            </g>
          ))}

          {/* Trend line */}
          <path
            d={linePath}
            fill="none"
            stroke="#86efac"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data points on line */}
          {linePoints.map((point, i) => (
            <circle
              key={`point-${i}`}
              cx={point.x}
              cy={point.y}
              r="4"
              fill="#22c55e"
              stroke="#1f2937"
              strokeWidth="2"
            />
          ))}

          {/* X-axis labels (day names) */}
          {bars.map((bar, i) => (
            <text
              key={`label-${i}`}
              x={bar.x + bar.width / 2}
              y={chartHeight - 10}
              textAnchor="middle"
              fill="#9ca3af"
              fontSize="11"
            >
              {bar.day}
            </text>
          ))}

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
