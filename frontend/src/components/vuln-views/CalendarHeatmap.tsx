/**
 * CalendarHeatmap Component
 *
 * GitHub-style calendar showing CVE discoveries per day
 * with pulse animation on days with critical CVEs
 */

import { useState, useMemo } from "react";
import type { CalendarHeatmapData, VulnViewCommonProps } from "../../types/vulnerabilityViews";

// Intensity levels (0-4)
const INTENSITY_COLORS = [
  "bg-gray-800", // 0 - no CVEs
  "bg-green-900", // 1 - low
  "bg-green-700", // 2 - medium-low
  "bg-green-500", // 3 - medium-high
  "bg-green-300", // 4 - high
];

const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

interface CalendarHeatmapProps extends VulnViewCommonProps {
  data: CalendarHeatmapData;
  onDayClick?: (date: string) => void;
}

interface TooltipData {
  date: string;
  count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
}

export function CalendarHeatmap({
  data,
  className = "",
  onDayClick,
  isLoading = false,
  error = null,
}: CalendarHeatmapProps) {
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  // Process days into weeks/grid format
  const calendarGrid = useMemo(() => {
    if (data.days.length === 0) return [];

    // Create a map for quick lookup
    const dayMap = new Map(data.days.map((d) => [d.date, d]));

    // Build weeks grid
    const weeks: Array<Array<typeof data.days[0] | null>> = [];
    let currentWeek: Array<typeof data.days[0] | null> = [];

    // Start from the start_date
    const startDate = new Date(data.start_date || data.days[0]?.date || new Date());
    const endDate = new Date(data.end_date || data.days[data.days.length - 1]?.date || new Date());

    // Pad to start on Sunday
    const startDayOfWeek = startDate.getDay();
    for (let i = 0; i < startDayOfWeek; i++) {
      currentWeek.push(null);
    }

    // Iterate through each day
    const current = new Date(startDate);
    while (current <= endDate) {
      const dateStr = current.toISOString().split("T")[0];
      const dayData = dayMap.get(dateStr) || {
        date: dateStr,
        count: 0,
        critical_count: 0,
        high_count: 0,
        medium_count: 0,
        low_count: 0,
      };

      currentWeek.push(dayData);

      if (currentWeek.length === 7) {
        weeks.push(currentWeek);
        currentWeek = [];
      }

      current.setDate(current.getDate() + 1);
    }

    // Pad final week
    if (currentWeek.length > 0) {
      while (currentWeek.length < 7) {
        currentWeek.push(null);
      }
      weeks.push(currentWeek);
    }

    return weeks;
  }, [data]);

  // Calculate intensity level (0-4)
  const getIntensity = (count: number): number => {
    if (count === 0) return 0;
    if (data.max_count === 0) return 1;

    const ratio = count / data.max_count;
    if (ratio <= 0.25) return 1;
    if (ratio <= 0.5) return 2;
    if (ratio <= 0.75) return 3;
    return 4;
  };

  // Get unique months for labels
  const monthLabels = useMemo(() => {
    const months: Array<{ label: string; weekIndex: number }> = [];
    let lastMonth = -1;

    calendarGrid.forEach((week, weekIndex) => {
      const firstDay = week.find((d) => d !== null);
      if (firstDay) {
        const date = new Date(firstDay.date);
        const month = date.getMonth();
        if (month !== lastMonth) {
          months.push({ label: MONTH_LABELS[month], weekIndex });
          lastMonth = month;
        }
      }
    });

    return months;
  }, [calendarGrid]);

  // Handle day click
  const handleDayClick = (date: string) => {
    onDayClick?.(date);
  };

  // Handle mouse enter for tooltip
  const handleMouseEnter = (day: typeof data.days[0], event: React.MouseEvent) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltipPosition({
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
    });
    setTooltip({
      date: day.date,
      count: day.count,
      critical_count: day.critical_count,
      high_count: day.high_count,
      medium_count: day.medium_count,
      low_count: day.low_count,
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div
        data-testid="calendar-loading"
        className={`flex items-center justify-center h-64 bg-gray-900 rounded-lg ${className}`}
      >
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`flex items-center justify-center h-64 bg-gray-900 rounded-lg ${className}`}>
        <div className="text-center">
          <svg className="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (data.days.length === 0) {
    return (
      <div
        data-testid="calendar-heatmap"
        className={`flex items-center justify-center h-64 bg-gray-900 rounded-lg ${className}`}
        aria-label="Calendar heatmap - no data"
      >
        <div className="text-center text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p>No calendar data available</p>
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="calendar-heatmap"
      className={`bg-gray-900 rounded-lg p-4 ${className}`}
      aria-label="calendar heatmap showing CVE discoveries by date"
    >
      {/* Month labels */}
      <div className="flex pl-8 mb-2 text-xs text-gray-400">
        {monthLabels.map((month, idx) => (
          <div
            key={idx}
            className="flex-shrink-0"
            style={{
              marginLeft: idx === 0 ? `${month.weekIndex * 14}px` : undefined,
              width: "56px",
            }}
          >
            {month.label}
          </div>
        ))}
      </div>

      <div className="flex">
        {/* Day of week labels */}
        <div className="flex flex-col gap-0.5 mr-2 text-xs text-gray-400">
          {DAY_LABELS.map((day, idx) => (
            <div
              key={day}
              className="h-3 flex items-center"
              style={{ visibility: idx % 2 === 1 ? "visible" : "hidden" }}
            >
              {day}
            </div>
          ))}
        </div>

        {/* Calendar grid */}
        <div className="flex gap-0.5 overflow-x-auto">
          {calendarGrid.map((week, weekIdx) => (
            <div key={weekIdx} className="flex flex-col gap-0.5">
              {week.map((day, dayIdx) => {
                if (!day) {
                  return <div key={dayIdx} className="w-3 h-3" />;
                }

                const intensity = getIntensity(day.count);
                const hasCritical = day.critical_count > 0;

                return (
                  <div
                    key={day.date}
                    data-testid={`calendar-day-${day.date}`}
                    data-intensity={intensity}
                    data-has-critical={hasCritical.toString()}
                    className={`
                      w-3 h-3 rounded-sm cursor-pointer transition-all duration-200
                      ${INTENSITY_COLORS[intensity]}
                      ${hasCritical ? "animate-pulse ring-1 ring-red-500/50" : ""}
                      hover:ring-2 hover:ring-cyan-500/50 focus:ring-2 focus:ring-cyan-500/50 focus:outline-none
                    `}
                    tabIndex={0}
                    role="button"
                    aria-label={`${day.date}: ${day.count} CVEs${hasCritical ? `, ${day.critical_count} critical` : ""}`}
                    onClick={() => handleDayClick(day.date)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        handleDayClick(day.date);
                      }
                    }}
                    onMouseEnter={(e) => handleMouseEnter(day, e)}
                    onMouseLeave={() => setTooltip(null)}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div data-testid="calendar-legend" className="flex items-center justify-end gap-2 mt-4 text-xs text-gray-400">
        <span>Less</span>
        {INTENSITY_COLORS.map((color, idx) => (
          <div key={idx} className={`w-3 h-3 rounded-sm ${color}`} />
        ))}
        <span>More</span>
      </div>

      {/* Stats */}
      <div className="flex items-center gap-6 mt-4 pt-4 border-t border-gray-700">
        <div>
          <div className="text-2xl font-bold text-white">{data.total_cves}</div>
          <div className="text-xs text-gray-400">Total CVEs</div>
        </div>
        <div>
          <div className="text-xl font-bold text-red-400">
            {data.days.reduce((sum, d) => sum + d.critical_count, 0)}
          </div>
          <div className="text-xs text-gray-400">Critical</div>
        </div>
        <div>
          <div className="text-xl font-bold text-orange-400">
            {data.days.reduce((sum, d) => sum + d.high_count, 0)}
          </div>
          <div className="text-xs text-gray-400">High</div>
        </div>
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div
          role="tooltip"
          className="fixed z-50 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl text-sm pointer-events-none"
          style={{
            left: `${tooltipPosition.x}px`,
            top: `${tooltipPosition.y}px`,
            transform: "translate(-50%, -100%)",
          }}
        >
          <div className="font-medium text-white">{tooltip.date}</div>
          <div className="text-cyan-400">{tooltip.count} CVEs</div>
          {tooltip.critical_count > 0 && (
            <div className="text-red-400">{tooltip.critical_count} Critical</div>
          )}
          {tooltip.high_count > 0 && (
            <div className="text-orange-400">{tooltip.high_count} High</div>
          )}
          {tooltip.medium_count > 0 && (
            <div className="text-yellow-400">{tooltip.medium_count} Medium</div>
          )}
          {tooltip.low_count > 0 && (
            <div className="text-green-400">{tooltip.low_count} Low</div>
          )}
        </div>
      )}
    </div>
  );
}
