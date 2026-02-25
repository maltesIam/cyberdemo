/**
 * TimeSlider Component
 *
 * Time-based slider for viewing attack surface evolution over time.
 * Allows scrubbing through historical data to see changes.
 */

import { useState, useCallback, useMemo, useRef, useEffect } from "react";
import clsx from "clsx";
import { format, subHours, differenceInMinutes } from "date-fns";
import type { TimeRange } from "./types";

interface TimeSliderProps {
  timeRange: TimeRange;
  onChange: (range: TimeRange) => void;
  // Optional: Event markers on the timeline
  events?: TimelineEvent[];
  // Whether to show playback controls
  showPlayback?: boolean;
  className?: string;
}

interface TimelineEvent {
  timestamp: Date;
  type: "incident" | "detection" | "containment";
  label: string;
  severity?: "critical" | "high" | "medium" | "low";
}

// Preset time ranges
const TIME_PRESETS = [
  { label: "1H", hours: 1 },
  { label: "6H", hours: 6 },
  { label: "12H", hours: 12 },
  { label: "24H", hours: 24 },
  { label: "7D", hours: 168 },
] as const;

// Event type colors
const EVENT_COLORS: Record<TimelineEvent["type"], string> = {
  incident: "#f97316", // orange
  detection: "#ef4444", // red
  containment: "#3b82f6", // blue
};

export function TimeSlider({
  timeRange,
  onChange,
  events = [],
  showPlayback = true,
  className,
}: TimeSliderProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<1 | 2 | 4>(1);
  const playIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const sliderRef = useRef<HTMLDivElement>(null);

  // Calculate timeline duration in minutes
  const durationMinutes = useMemo(
    () => differenceInMinutes(timeRange.end, timeRange.start),
    [timeRange],
  );

  // Current position as percentage (0-100)
  const [position, setPosition] = useState(100);

  // Calculate visible time based on position
  const currentTime = useMemo(() => {
    const minutes = (position / 100) * durationMinutes;
    return new Date(timeRange.start.getTime() + minutes * 60 * 1000);
  }, [position, durationMinutes, timeRange.start]);

  // Handle slider drag
  const handleSliderChange = useCallback(
    (newPosition: number) => {
      const clampedPosition = Math.max(0, Math.min(100, newPosition));
      setPosition(clampedPosition);

      // Calculate new end time based on position
      const minutes = (clampedPosition / 100) * durationMinutes;
      const newEnd = new Date(timeRange.start.getTime() + minutes * 60 * 1000);

      onChange({
        start: timeRange.start,
        end: newEnd,
      });
    },
    [durationMinutes, onChange, timeRange.start],
  );

  // Handle mouse/touch events on slider track
  const handleTrackClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!sliderRef.current) return;
      const rect = sliderRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percentage = (x / rect.width) * 100;
      handleSliderChange(percentage);
    },
    [handleSliderChange],
  );

  // Playback controls
  const startPlayback = useCallback(() => {
    setIsPlaying(true);
    setPosition(0);
  }, []);

  const stopPlayback = useCallback(() => {
    setIsPlaying(false);
    if (playIntervalRef.current) {
      clearInterval(playIntervalRef.current);
      playIntervalRef.current = null;
    }
  }, []);

  const togglePlayback = useCallback(() => {
    if (isPlaying) {
      stopPlayback();
    } else {
      startPlayback();
    }
  }, [isPlaying, startPlayback, stopPlayback]);

  // Playback animation
  useEffect(() => {
    if (isPlaying) {
      playIntervalRef.current = setInterval(() => {
        setPosition((prev) => {
          const next = prev + 0.5 * playbackSpeed;
          if (next >= 100) {
            stopPlayback();
            return 100;
          }
          return next;
        });
      }, 50);
    }

    return () => {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current);
      }
    };
  }, [isPlaying, playbackSpeed, stopPlayback]);

  // Handle preset selection
  const handlePresetSelect = useCallback(
    (hours: number) => {
      const now = new Date();
      onChange({
        start: subHours(now, hours),
        end: now,
      });
      setPosition(100);
    },
    [onChange],
  );

  // Calculate event positions on timeline
  const eventPositions = useMemo(() => {
    return events
      .map((event) => {
        const eventTime = event.timestamp.getTime();
        const startTime = timeRange.start.getTime();
        const endTime = timeRange.end.getTime();
        const totalDuration = endTime - startTime;
        const eventOffset = eventTime - startTime;
        const percentage = (eventOffset / totalDuration) * 100;
        return {
          ...event,
          position: Math.max(0, Math.min(100, percentage)),
        };
      })
      .filter((e) => e.position >= 0 && e.position <= 100);
  }, [events, timeRange]);

  return (
    <div className={clsx("flex flex-col gap-3", className)}>
      {/* Header with time display */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <svg
            className="w-4 h-4 text-secondary"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span className="text-sm font-medium text-secondary">Timeline</span>
        </div>
        <div className="text-sm font-mono text-cyan-400">{format(currentTime, "MMM d, HH:mm")}</div>
      </div>

      {/* Time presets */}
      <div className="flex items-center gap-1.5">
        {TIME_PRESETS.map((preset) => (
          <button
            key={preset.label}
            onClick={() => handlePresetSelect(preset.hours)}
            className={clsx(
              "px-2 py-1 rounded text-xs font-medium transition-colors",
              durationMinutes === preset.hours * 60
                ? "bg-cyan-600 text-primary"
                : "bg-tertiary text-secondary hover:bg-tertiary hover:text-secondary",
            )}
          >
            {preset.label}
          </button>
        ))}
      </div>

      {/* Slider track */}
      <div className="relative">
        <div
          ref={sliderRef}
          onClick={handleTrackClick}
          className="relative h-8 bg-secondary rounded-lg cursor-pointer overflow-hidden"
        >
          {/* Progress fill */}
          <div
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-cyan-600/30 to-cyan-500/50 rounded-l-lg"
            style={{ width: `${position}%` }}
          />

          {/* Event markers */}
          {eventPositions.map((event, index) => (
            <div
              key={index}
              className="absolute top-1 bottom-1 w-1 rounded-full cursor-pointer group"
              style={{
                left: `${event.position}%`,
                backgroundColor: EVENT_COLORS[event.type],
              }}
              title={`${event.label} - ${format(event.timestamp, "HH:mm")}`}
            >
              {/* Tooltip */}
              <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 hidden group-hover:block z-10">
                <div className="bg-primary border border-primary rounded px-2 py-1 text-xs whitespace-nowrap shadow-lg">
                  <div className="font-medium text-primary">{event.label}</div>
                  <div className="text-secondary">{format(event.timestamp, "HH:mm:ss")}</div>
                </div>
              </div>
            </div>
          ))}

          {/* Slider handle */}
          <div
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-4 h-4 bg-cyan-500 rounded-full shadow-lg border-2 border-white cursor-grab active:cursor-grabbing"
            style={{ left: `${position}%` }}
          />

          {/* Time labels */}
          <div className="absolute bottom-0 left-2 text-[10px] text-tertiary">
            {format(timeRange.start, "HH:mm")}
          </div>
          <div className="absolute bottom-0 right-2 text-[10px] text-tertiary">
            {format(timeRange.end, "HH:mm")}
          </div>
        </div>
      </div>

      {/* Playback controls */}
      {showPlayback && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* Play/Pause button */}
            <button
              onClick={togglePlayback}
              className="w-8 h-8 flex items-center justify-center rounded-lg bg-tertiary text-primary hover:bg-tertiary transition-colors"
            >
              {isPlaying ? (
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z" />
                </svg>
              )}
            </button>

            {/* Reset button */}
            <button
              onClick={() => setPosition(100)}
              className="w-8 h-8 flex items-center justify-center rounded-lg bg-tertiary text-secondary hover:bg-tertiary hover:text-primary transition-colors"
              title="Reset to current"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>

            {/* Speed control */}
            <div className="flex items-center gap-1 ml-2">
              <span className="text-xs text-tertiary">Speed:</span>
              {([1, 2, 4] as const).map((speed) => (
                <button
                  key={speed}
                  onClick={() => setPlaybackSpeed(speed)}
                  className={clsx(
                    "px-1.5 py-0.5 rounded text-xs font-medium transition-colors",
                    playbackSpeed === speed
                      ? "bg-cyan-600 text-primary"
                      : "bg-tertiary text-secondary hover:bg-tertiary",
                  )}
                >
                  {speed}x
                </button>
              ))}
            </div>
          </div>

          {/* Event legend */}
          <div className="flex items-center gap-3">
            {Object.entries(EVENT_COLORS).map(([type, color]) => (
              <div key={type} className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-xs text-tertiary capitalize">{type}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Compact version for embedding in toolbars
export function TimeSliderCompact({
  timeRange,
  onChange,
  className,
}: Pick<TimeSliderProps, "timeRange" | "onChange" | "className">) {
  const [position, setPosition] = useState(100);
  const sliderRef = useRef<HTMLDivElement>(null);

  const durationMinutes = useMemo(
    () => differenceInMinutes(timeRange.end, timeRange.start),
    [timeRange],
  );

  const currentTime = useMemo(() => {
    const minutes = (position / 100) * durationMinutes;
    return new Date(timeRange.start.getTime() + minutes * 60 * 1000);
  }, [position, durationMinutes, timeRange.start]);

  const handleTrackClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!sliderRef.current) return;
      const rect = sliderRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
      setPosition(percentage);

      const minutes = (percentage / 100) * durationMinutes;
      const newEnd = new Date(timeRange.start.getTime() + minutes * 60 * 1000);
      onChange({ start: timeRange.start, end: newEnd });
    },
    [durationMinutes, onChange, timeRange.start],
  );

  return (
    <div className={clsx("flex items-center gap-2", className)}>
      <svg
        className="w-4 h-4 text-secondary flex-shrink-0"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <div
        ref={sliderRef}
        onClick={handleTrackClick}
        className="relative flex-1 h-2 bg-tertiary rounded-full cursor-pointer"
      >
        <div
          className="absolute inset-y-0 left-0 bg-cyan-500/50 rounded-full"
          style={{ width: `${position}%` }}
        />
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3 h-3 bg-cyan-500 rounded-full shadow"
          style={{ left: `${position}%` }}
        />
      </div>
      <span className="text-xs font-mono text-secondary flex-shrink-0 w-14">
        {format(currentTime, "HH:mm")}
      </span>
    </div>
  );
}
