/**
 * IncidentTimelineChart Component
 *
 * A simple SVG-based timeline chart showing incident progression phases:
 * Alert -> Investigation -> Containment -> Resolution
 */

import { useMemo } from "react";
import { format, differenceInMinutes } from "date-fns";

export interface TimelinePhase {
  name: string;
  timestamp: string;
  color: string;
}

interface IncidentTimelineChartProps {
  phases: TimelinePhase[];
  showDurations?: boolean;
}

// Default colors for incident phases
export const PHASE_COLORS = {
  alert: "#ef4444", // red-500
  investigation: "#f59e0b", // amber-500
  containment: "#3b82f6", // blue-500
  resolution: "#22c55e", // green-500
};

export function IncidentTimelineChart({
  phases,
  showDurations = false,
}: IncidentTimelineChartProps) {
  // Calculate durations between phases
  const phasesWithDuration = useMemo(() => {
    return phases.map((phase, index) => {
      let durationMinutes = 0;
      if (index > 0) {
        const prevPhase = phases[index - 1];
        durationMinutes = differenceInMinutes(
          new Date(phase.timestamp),
          new Date(prevPhase.timestamp),
        );
      }
      return {
        ...phase,
        durationMinutes,
      };
    });
  }, [phases]);

  // Format duration for display
  const formatDuration = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes}m`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  if (phases.length === 0) {
    return <div className="text-center py-8 text-gray-500">No timeline data available</div>;
  }

  const chartWidth = 600;
  const chartHeight = 120;
  const nodeRadius = 16;
  const padding = 40;
  const lineY = chartHeight / 2;

  // Calculate spacing between nodes
  const availableWidth = chartWidth - padding * 2;
  const spacing = phases.length > 1 ? availableWidth / (phases.length - 1) : 0;

  return (
    <div data-testid="incident-timeline-chart" className="w-full">
      <svg
        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
        className="w-full h-auto"
        style={{ maxHeight: "150px" }}
      >
        {/* Connection lines */}
        {phases.length > 1 &&
          phases.slice(0, -1).map((_, index) => {
            const x1 = padding + index * spacing + nodeRadius;
            const x2 = padding + (index + 1) * spacing - nodeRadius;
            return (
              <line
                key={`line-${index}`}
                x1={x1}
                y1={lineY}
                x2={x2}
                y2={lineY}
                stroke="#4b5563"
                strokeWidth="2"
                strokeDasharray="4 2"
              />
            );
          })}

        {/* Phase nodes */}
        {phasesWithDuration.map((phase, index) => {
          const cx = padding + index * spacing;
          return (
            <g key={`node-${index}`}>
              {/* Outer ring with color */}
              <circle cx={cx} cy={lineY} r={nodeRadius} fill={phase.color} opacity={0.2} />
              {/* Inner circle */}
              <circle cx={cx} cy={lineY} r={nodeRadius - 4} fill={phase.color} />
              {/* Phase number */}
              <text
                x={cx}
                y={lineY + 4}
                textAnchor="middle"
                fill="white"
                fontSize="12"
                fontWeight="bold"
              >
                {index + 1}
              </text>
            </g>
          );
        })}

        {/* Duration labels between phases */}
        {showDurations &&
          phasesWithDuration.slice(1).map((phase, index) => {
            const x = padding + (index + 0.5) * spacing;
            return (
              <text
                key={`duration-${index}`}
                data-testid="timeline-duration"
                x={x}
                y={lineY - 25}
                textAnchor="middle"
                fill="#9ca3af"
                fontSize="10"
              >
                {formatDuration(phase.durationMinutes)}
              </text>
            );
          })}
      </svg>

      {/* Phase labels below the chart */}
      <div className="flex justify-between px-4 mt-2">
        {phasesWithDuration.map((phase, index) => (
          <div
            key={`label-${index}`}
            className="flex flex-col items-center text-center"
            style={{ width: `${100 / phases.length}%` }}
          >
            <span className="text-sm font-medium text-white">{phase.name}</span>
            <span className="text-xs text-gray-400">
              {format(new Date(phase.timestamp), "HH:mm")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Helper function to convert postmortem timeline to chart phases
 */
export function convertTimelineToPhases(
  timeline: Array<{ timestamp: string; description: string }>,
): TimelinePhase[] {
  // Map descriptions to phase types
  const phaseMapping: Record<string, { name: string; color: string }> = {
    alert: { name: "Alert", color: PHASE_COLORS.alert },
    detected: { name: "Alert", color: PHASE_COLORS.alert },
    investigation: { name: "Investigation", color: PHASE_COLORS.investigation },
    started: { name: "Investigation", color: PHASE_COLORS.investigation },
    containment: { name: "Containment", color: PHASE_COLORS.containment },
    contained: { name: "Containment", color: PHASE_COLORS.containment },
    isolated: { name: "Containment", color: PHASE_COLORS.containment },
    resolution: { name: "Resolution", color: PHASE_COLORS.resolution },
    resolved: { name: "Resolution", color: PHASE_COLORS.resolution },
    closed: { name: "Resolution", color: PHASE_COLORS.resolution },
  };

  return timeline.map((entry) => {
    const descLower = entry.description.toLowerCase();

    // Find matching phase
    for (const [keyword, phase] of Object.entries(phaseMapping)) {
      if (descLower.includes(keyword)) {
        return {
          name: phase.name,
          timestamp: entry.timestamp,
          color: phase.color,
        };
      }
    }

    // Default phase
    return {
      name: "Event",
      timestamp: entry.timestamp,
      color: "#6b7280", // gray-500
    };
  });
}
