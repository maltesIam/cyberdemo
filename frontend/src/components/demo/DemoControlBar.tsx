/**
 * DemoControlBar Component
 *
 * Horizontal header bar wrapping demo controls for display on all pages.
 * Renders scenario dropdown, play/pause/stop, speed slider, and MITRE progress.
 *
 * Requirements:
 * - REQ-001-001-001: Render in header on all pages
 * - REQ-001-001-002: Scenario dropdown with 6 options
 * - REQ-001-001-003: Play/Pause/Stop buttons
 * - REQ-001-001-004: Speed slider 0.5x-4x
 * - REQ-001-001-005: MITRE phase progress circles
 * - REQ-001-001-006: Collapse/expand toggle (NTH)
 */

import { useState, useCallback } from 'react';
import type { DemoState, AttackScenario, SpeedMultiplier, PlayState, MitreStage } from './types';
import { ATTACK_SCENARIOS, SPEED_OPTIONS } from './types';
import { ScenarioDropdown } from './ScenarioDropdown';

/** Props for DemoControlBar */
export interface DemoControlBarProps {
  state: DemoState;
  onPlay: () => void;
  onPause: () => void;
  onStop: () => void;
  onSpeedChange: (speed: SpeedMultiplier) => void;
  onScenarioSelect: (scenario: AttackScenario) => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

/** Play icon */
const PlayIcon = () => (
  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
    <path d="M8 5v14l11-7z" />
  </svg>
);

/** Pause icon */
const PauseIcon = () => (
  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
  </svg>
);

/** Stop icon */
const StopIcon = () => (
  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
    <path d="M6 6h12v12H6z" />
  </svg>
);

/** Get color for MITRE phase circle */
const getPhaseColor = (stage: MitreStage): string => {
  if (stage.completed) return 'bg-green-500';
  if (stage.active) return 'bg-cyan-500 animate-pulse';
  return 'bg-tertiary';
};

export function DemoControlBar({
  state,
  onPlay,
  onPause,
  onStop,
  onSpeedChange,
  onScenarioSelect,
  isCollapsed = false,
  onToggleCollapse,
}: DemoControlBarProps) {
  const { playState, speed, selectedScenario, stages } = state;

  const isPlaying = playState === 'playing';
  const isStopped = playState === 'stopped';
  const canPlay = selectedScenario !== null && !isPlaying;
  const canStop = !isStopped;

  const handleSpeedChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onSpeedChange(parseFloat(e.target.value) as SpeedMultiplier);
    },
    [onSpeedChange]
  );

  if (isCollapsed) {
    return (
      <div
        data-testid="demo-control-bar"
        className="flex items-center justify-between px-4 py-1 bg-secondary/50 border-b border-primary"
      >
        <span className="text-xs text-secondary">Demo Controls</span>
        {onToggleCollapse && (
          <button
            type="button"
            aria-label="Expand control bar"
            onClick={onToggleCollapse}
            className="text-xs text-cyan-400 hover:text-cyan-300"
          >
            Expand
          </button>
        )}
      </div>
    );
  }

  return (
    <div
      data-testid="demo-control-bar"
      aria-label="Demo simulation controls"
      className="flex items-center gap-4 px-4 py-2 bg-secondary/50 border-b border-primary"
    >
      {/* Scenario Dropdown */}
      <div className="w-48 flex-shrink-0">
        <ScenarioDropdown
          scenarios={ATTACK_SCENARIOS}
          selectedScenario={selectedScenario}
          onSelect={onScenarioSelect}
          isDisabled={isPlaying}
        />
      </div>

      {/* Playback Controls */}
      <div className="flex items-center gap-1" role="group" aria-label="Playback controls">
        {isPlaying ? (
          <button
            type="button"
            aria-label="Pause"
            onClick={onPause}
            className="p-2 bg-cyan-600 hover:bg-cyan-700 text-primary rounded-lg transition-colors"
          >
            <PauseIcon />
          </button>
        ) : (
          <button
            type="button"
            aria-label="Play"
            onClick={onPlay}
            disabled={!canPlay}
            className="p-2 bg-cyan-600 hover:bg-cyan-700 text-primary rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PlayIcon />
          </button>
        )}
        <button
          type="button"
          aria-label="Stop"
          onClick={onStop}
          disabled={!canStop}
          className="p-2 bg-red-600 hover:bg-red-700 text-primary rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <StopIcon />
        </button>
      </div>

      {/* Speed Slider */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <label htmlFor="header-speed-slider" className="text-xs text-secondary">
          Speed
        </label>
        <input
          id="header-speed-slider"
          type="range"
          role="slider"
          aria-label="Speed"
          min="0.5"
          max="4"
          step="0.5"
          value={speed}
          onChange={handleSpeedChange}
          className="w-20 h-1.5 bg-tertiary rounded-lg appearance-none cursor-pointer accent-cyan-500"
        />
        <span className="text-xs font-medium text-primary w-8">{speed}x</span>
      </div>

      {/* MITRE Phase Progress Circles */}
      <div className="flex items-center gap-1 flex-1 justify-center" role="group" aria-label="MITRE phase progress">
        {stages.map((stage) => (
          <div
            key={stage.tacticId}
            data-testid={`phase-circle-${stage.tacticId}`}
            title={stage.tacticName}
            className={`w-3 h-3 rounded-full ${getPhaseColor(stage)} transition-all`}
          />
        ))}
        {stages.length === 0 && (
          <span className="text-xs text-tertiary">No scenario selected</span>
        )}
      </div>

      {/* Collapse toggle */}
      {onToggleCollapse && (
        <button
          type="button"
          aria-label="Collapse control bar"
          onClick={onToggleCollapse}
          className="p-1 text-secondary hover:text-primary rounded transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
          </svg>
        </button>
      )}
    </div>
  );
}
