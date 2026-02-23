/**
 * DemoControlPanel Component
 *
 * Main container for demo simulation controls including
 * play/pause/stop, speed control, scenario selection, and progress display.
 *
 * Requirements:
 * - TECH-011: DemoControlPanel React component
 * - REQ-006-001-001: Play/Pause/Stop buttons
 * - REQ-006-001-002: Speed slider (0.5x-4x)
 * - REQ-006-001-003: Scenario selection dropdown
 * - REQ-006-001-004: MITRE stage progress bar
 * - REQ-006-001-005: Keyboard shortcuts
 */

import { useCallback } from "react";
import type {
  DemoState,
  AttackScenario,
  SpeedMultiplier,
  PlayState,
} from "./types";
import { ScenarioDropdown } from "./ScenarioDropdown";
import { MitreProgressBar } from "./MitreProgressBar";
import { SPEED_OPTIONS } from "./types";

/** Props for PlaybackButton component */
interface PlaybackButtonProps {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: "primary" | "danger" | "default";
}

/** Playback button component */
const PlaybackButton = ({
  icon,
  label,
  onClick,
  disabled = false,
  variant = "default",
}: PlaybackButtonProps) => {
  const variantClasses = {
    primary: "bg-cyan-600 hover:bg-cyan-700 text-white",
    danger: "bg-red-600 hover:bg-red-700 text-white",
    default: "bg-gray-700 hover:bg-gray-600 text-gray-200",
  };

  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center justify-center w-10 h-10 rounded-lg transition-colors ${
        variantClasses[variant]
      } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
    >
      {icon}
    </button>
  );
};

/** Play icon */
const PlayIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
    <path d="M8 5v14l11-7z" />
  </svg>
);

/** Pause icon */
const PauseIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
  </svg>
);

/** Stop icon */
const StopIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
    <path d="M6 6h12v12H6z" />
  </svg>
);

/** Get status indicator color class */
const getStatusColor = (playState: PlayState): string => {
  switch (playState) {
    case "playing":
      return "bg-green-500";
    case "paused":
      return "bg-yellow-500";
    default:
      return "bg-gray-500";
  }
};

/** Get status text */
const getStatusText = (playState: PlayState): string => {
  switch (playState) {
    case "playing":
      return "Playing";
    case "paused":
      return "Paused";
    default:
      return "Stopped";
  }
};

export interface DemoControlPanelProps {
  /** Current demo state */
  state: DemoState;
  /** Available attack scenarios */
  scenarios: AttackScenario[];
  /** Callback when play is clicked */
  onPlay: () => void;
  /** Callback when pause is clicked */
  onPause: () => void;
  /** Callback when stop is clicked */
  onStop: () => void;
  /** Callback when speed changes */
  onSpeedChange: (speed: SpeedMultiplier) => void;
  /** Callback when a scenario is selected */
  onScenarioSelect: (scenario: AttackScenario) => void;
}

export function DemoControlPanel({
  state,
  scenarios,
  onPlay,
  onPause,
  onStop,
  onSpeedChange,
  onScenarioSelect,
}: DemoControlPanelProps) {
  const { playState, speed, selectedScenario, stages, currentStage } = state;

  const isPlaying = playState === "playing";
  const isPaused = playState === "paused";
  const isStopped = playState === "stopped";
  const canPlay = selectedScenario !== null && (isStopped || isPaused);
  const canStop = !isStopped;

  const handleSpeedChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = parseFloat(e.target.value) as SpeedMultiplier;
      onSpeedChange(value);
    },
    [onSpeedChange]
  );

  const handlePlayPauseClick = useCallback(() => {
    if (isPlaying) {
      onPause();
    } else {
      onPlay();
    }
  }, [isPlaying, onPlay, onPause]);

  return (
    <div
      data-testid="demo-control-panel"
      aria-label="Demo simulation controls"
      className="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-4"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-200">Demo Controls</h3>
        <div className="flex items-center space-x-2">
          <div
            data-testid="status-indicator"
            className={`w-2 h-2 rounded-full ${getStatusColor(playState)} ${
              isPlaying ? "animate-pulse" : ""
            }`}
          />
          <span className="text-xs text-gray-400">{getStatusText(playState)}</span>
        </div>
      </div>

      {/* Scenario Selection */}
      <div className="space-y-2">
        <ScenarioDropdown
          scenarios={scenarios}
          selectedScenario={selectedScenario}
          onSelect={onScenarioSelect}
          isDisabled={isPlaying}
        />
      </div>

      {/* Playback Controls */}
      <div className="flex items-center space-x-2">
        {isPlaying ? (
          <PlaybackButton
            icon={<PauseIcon />}
            label="Pause"
            onClick={onPause}
            variant="primary"
          />
        ) : (
          <PlaybackButton
            icon={<PlayIcon />}
            label="Play"
            onClick={onPlay}
            disabled={!canPlay}
            variant="primary"
          />
        )}
        <PlaybackButton
          icon={<StopIcon />}
          label="Stop"
          onClick={onStop}
          disabled={!canStop}
          variant="danger"
        />
      </div>

      {/* Speed Slider */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label htmlFor="speed-slider" className="text-xs text-gray-400">
            Speed
          </label>
          <span className="text-xs font-medium text-gray-200">{speed}x</span>
        </div>
        <input
          id="speed-slider"
          type="range"
          role="slider"
          aria-label="Speed"
          min="0.5"
          max="4"
          step="0.5"
          value={speed}
          onChange={handleSpeedChange}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
        />
        <div className="flex justify-between text-[10px] text-gray-500">
          <span>0.5x</span>
          <span>1x</span>
          <span>2x</span>
          <span>4x</span>
        </div>
      </div>

      {/* Progress Bar */}
      <MitreProgressBar
        stages={stages}
        currentStage={currentStage}
        compact={false}
      />

      {/* Keyboard Shortcuts Help */}
      <div className="border-t border-gray-700 pt-3">
        <div className="text-[10px] text-gray-500 space-y-1">
          <div className="flex justify-between">
            <span>Play/Pause</span>
            <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-gray-400">Space</kbd>
          </div>
          <div className="flex justify-between">
            <span>Stop</span>
            <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-gray-400">Esc</kbd>
          </div>
          <div className="flex justify-between">
            <span>Speed +/-</span>
            <span>
              <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-gray-400">+</kbd>
              {" / "}
              <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-gray-400">-</kbd>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
