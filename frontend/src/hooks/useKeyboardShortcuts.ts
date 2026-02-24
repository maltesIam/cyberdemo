/**
 * useKeyboardShortcuts - Keyboard shortcut handler for simulation controls
 *
 * TECH-006: Space=Play/Pause, Esc=Stop
 * Ignores events from input/textarea/select elements
 */

import { useEffect, useCallback } from 'react';

export interface KeyboardShortcutHandlers {
  onPlayPause?: () => void;
  onStop?: () => void;
  enabled?: boolean;
}

const IGNORED_TAG_NAMES = new Set(['INPUT', 'TEXTAREA', 'SELECT']);

export function useKeyboardShortcuts({
  onPlayPause,
  onStop,
  enabled = true,
}: KeyboardShortcutHandlers): void {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      const target = event.target as HTMLElement;
      if (IGNORED_TAG_NAMES.has(target.tagName)) return;

      switch (event.code) {
        case 'Space':
          event.preventDefault();
          onPlayPause?.();
          break;
        case 'Escape':
          onStop?.();
          break;
      }
    },
    [enabled, onPlayPause, onStop]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);
}
