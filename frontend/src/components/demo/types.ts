/**
 * Types for Demo Control Panel Components
 *
 * Requirements:
 * - REQ-006-001-001: Play/Pause/Stop buttons
 * - REQ-006-001-002: Speed slider (0.5x-4x)
 * - REQ-006-001-003: Scenario selection dropdown
 * - REQ-006-001-004: MITRE stage progress bar
 * - REQ-006-001-005: Keyboard shortcuts
 * - REQ-006-002-001: DemoContext for global state
 */

/** Simulation play state */
export type PlayState = "stopped" | "playing" | "paused";

/** Speed multiplier values */
export type SpeedMultiplier = 0.5 | 1 | 2 | 4;

/** Attack scenario definition */
export interface AttackScenario {
  /** Unique identifier for the scenario */
  id: string;
  /** Display name of the scenario */
  name: string;
  /** Short description of the attack */
  description: string;
  /** Category for grouping (APT, Ransomware, etc.) */
  category: string;
  /** Number of MITRE stages in this scenario */
  stages: number;
}

/** MITRE ATT&CK Stage */
export interface MitreStage {
  /** Stage index (0-based) */
  index: number;
  /** Tactic ID (e.g., TA0001) */
  tacticId: string;
  /** Tactic name (e.g., "Initial Access") */
  tacticName: string;
  /** Technique IDs used in this stage */
  techniqueIds: string[];
  /** Whether this stage has been completed */
  completed: boolean;
  /** Whether this stage is currently active */
  active: boolean;
}

/** Demo simulation state */
export interface DemoState {
  /** Current play state */
  playState: PlayState;
  /** Current speed multiplier */
  speed: SpeedMultiplier;
  /** Currently selected scenario */
  selectedScenario: AttackScenario | null;
  /** Current stage index in the scenario */
  currentStage: number;
  /** All stages in the current scenario */
  stages: MitreStage[];
  /** Session ID for the current simulation */
  sessionId: string | null;
  /** When the simulation started */
  startedAt: string | null;
}

/** Props for ScenarioDropdown component */
export interface ScenarioDropdownProps {
  /** Available scenarios */
  scenarios: AttackScenario[];
  /** Currently selected scenario */
  selectedScenario: AttackScenario | null;
  /** Callback when a scenario is selected */
  onSelect: (scenario: AttackScenario) => void;
  /** Whether the dropdown is disabled */
  isDisabled?: boolean;
}

/** Props for MitreProgressBar component */
export interface MitreProgressBarProps {
  /** All stages in the scenario */
  stages: MitreStage[];
  /** Current active stage index */
  currentStage: number;
  /** Whether to show compact view */
  compact?: boolean;
}

/** Props for SpeedSlider component */
export interface SpeedSliderProps {
  /** Current speed value */
  value: SpeedMultiplier;
  /** Callback when speed changes */
  onChange: (speed: SpeedMultiplier) => void;
  /** Whether the slider is disabled */
  isDisabled?: boolean;
}

/** Props for PlaybackControls component */
export interface PlaybackControlsProps {
  /** Current play state */
  playState: PlayState;
  /** Callback when play is clicked */
  onPlay: () => void;
  /** Callback when pause is clicked */
  onPause: () => void;
  /** Callback when stop is clicked */
  onStop: () => void;
  /** Whether controls are disabled */
  isDisabled?: boolean;
}

/** All available scenarios */
export const ATTACK_SCENARIOS: AttackScenario[] = [
  {
    id: "apt29",
    name: "APT29 (Cozy Bear)",
    description: "Government espionage campaign",
    category: "APT",
    stages: 8,
  },
  {
    id: "fin7",
    name: "FIN7",
    description: "Financial attack campaign",
    category: "Financial",
    stages: 7,
  },
  {
    id: "lazarus",
    name: "Lazarus Group",
    description: "Destructive attack campaign",
    category: "APT",
    stages: 9,
  },
  {
    id: "revil",
    name: "REvil Ransomware",
    description: "Ransomware attack",
    category: "Ransomware",
    stages: 6,
  },
  {
    id: "solarwinds",
    name: "SolarWinds-style",
    description: "Supply chain attack",
    category: "Supply Chain",
    stages: 10,
  },
  {
    id: "insider",
    name: "Insider Threat",
    description: "Internal threat actor",
    category: "Insider",
    stages: 5,
  },
];

/** Keyboard shortcuts for demo control */
export const KEYBOARD_SHORTCUTS = {
  togglePlayPause: " ", // Space
  stop: "Escape",
  speedUp: "+",
  speedDown: "-",
} as const;

/** Available speed options */
export const SPEED_OPTIONS: SpeedMultiplier[] = [0.5, 1, 2, 4];
