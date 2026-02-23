/**
 * useKeyboardShortcuts Hook
 *
 * Provides keyboard shortcuts for demo control panel.
 *
 * Requirements:
 * - REQ-006-001-005: Keyboard shortcuts (Space=pause, Esc=stop, +/-=speed)
 */

import { useEffect, useCallback } from "react";
import { KEYBOARD_SHORTCUTS } from "./types";

export interface UseKeyboardShortcutsProps {
  /** Callback for play/pause toggle (Space key) */
  onTogglePlayPause?: () => void;
  /** Callback for stop (Escape key) */
  onStop?: () => void;
  /** Callback for speed increase (+/= key) */
  onSpeedUp?: () => void;
  /** Callback for speed decrease (- key) */
  onSpeedDown?: () => void;
  /** Whether keyboard shortcuts are enabled */
  isEnabled: boolean;
}

/** Elements that should not trigger shortcuts when focused */
const INTERACTIVE_ELEMENTS = ["INPUT", "TEXTAREA", "SELECT"];

/**
 * Hook that listens for keyboard shortcuts and invokes callbacks
 */
export function useKeyboardShortcuts({
  onTogglePlayPause,
  onStop,
  onSpeedUp,
  onSpeedDown,
  isEnabled,
}: UseKeyboardShortcutsProps): void {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Don't handle shortcuts if disabled
      if (!isEnabled) return;

      // Don't handle shortcuts when typing in form elements
      const target = event.target as HTMLElement;
      if (target && INTERACTIVE_ELEMENTS.includes(target.tagName)) {
        return;
      }

      switch (event.key) {
        case " ": // Space - Toggle Play/Pause
          event.preventDefault();
          onTogglePlayPause?.();
          break;

        case "Escape": // Escape - Stop
          onStop?.();
          break;

        case "+": // Plus - Speed Up
        case "=": // Equals (unshifted plus on most keyboards)
          onSpeedUp?.();
          break;

        case "-": // Minus - Speed Down
          onSpeedDown?.();
          break;

        default:
          // No action for other keys
          break;
      }
    },
    [isEnabled, onTogglePlayPause, onStop, onSpeedUp, onSpeedDown]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyDown]);
}

/**
 * Helper to get a human-readable shortcut label
 */
export function getShortcutLabel(action: keyof typeof KEYBOARD_SHORTCUTS): string {
  const key = KEYBOARD_SHORTCUTS[action];

  switch (key) {
    case " ":
      return "Space";
    case "Escape":
      return "Esc";
    default:
      return key;
  }
}
