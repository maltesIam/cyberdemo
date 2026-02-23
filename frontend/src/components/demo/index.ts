/**
 * Demo Control Panel Components Exports
 *
 * Requirements covered:
 * - REQ-006-001-001: Play/Pause/Stop buttons
 * - REQ-006-001-002: Speed slider (0.5x-4x)
 * - REQ-006-001-003: Scenario selection dropdown
 * - REQ-006-001-004: MITRE stage progress bar
 * - REQ-006-001-005: Keyboard shortcuts
 */

export { ScenarioDropdown } from "./ScenarioDropdown";
export { MitreProgressBar } from "./MitreProgressBar";
export { DemoControlPanel } from "./DemoControlPanel";
export { useKeyboardShortcuts, getShortcutLabel } from "./useKeyboardShortcuts";

export type {
  AttackScenario,
  MitreStage,
  PlayState,
  SpeedMultiplier,
  DemoState,
  ScenarioDropdownProps,
  MitreProgressBarProps,
  SpeedSliderProps,
  PlaybackControlsProps,
} from "./types";

export {
  ATTACK_SCENARIOS,
  KEYBOARD_SHORTCUTS,
  SPEED_OPTIONS,
} from "./types";
