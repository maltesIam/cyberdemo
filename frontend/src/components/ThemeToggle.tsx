/**
 * ThemeToggle Component — AgentFlow Design System v2.0
 *
 * Pill-shaped toggle with Dark (Moon), Light (Sun), System (Monitor) buttons.
 * Uses Lucide React icons. Manages data-theme attribute and localStorage.
 *
 * REQ-002-001-001 through REQ-002-001-006
 */

import { useState, useEffect, useCallback } from 'react';
import { Moon, Sun, Monitor, type LucideIcon } from 'lucide-react';
import { setTheme, getStoredThemePreference } from '../utils/theme';

type ThemeMode = 'dark' | 'light' | 'system';

interface ThemeModeOption {
  value: ThemeMode;
  label: string;
  Icon: LucideIcon;
}

const MODES: ThemeModeOption[] = [
  { value: 'dark', label: 'Dark theme', Icon: Moon },
  { value: 'light', label: 'Light theme', Icon: Sun },
  { value: 'system', label: 'System theme', Icon: Monitor },
];

export function ThemeToggle() {
  const [mode, setMode] = useState<ThemeMode>(() => {
    if (typeof window === 'undefined') return 'dark';
    const stored = getStoredThemePreference();
    return stored;
  });

  // Listen for OS preference changes when in system mode
  useEffect(() => {
    if (mode !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      setTheme('system');
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [mode]);

  const handleModeChange = useCallback((newMode: ThemeMode) => {
    setMode(newMode);
    setTheme(newMode);
  }, []);

  return (
    <div
      data-testid="theme-toggle"
      className="inline-flex items-center rounded-full p-0.5 gap-0.5"
      style={{
        backgroundColor: 'var(--bg-tertiary)',
        transition: `all var(--transition-default) var(--ease-default)`,
      }}
      role="radiogroup"
      aria-label="Theme selection"
    >
      {MODES.map(({ value, label, Icon }) => {
        const isActive = mode === value;
        return (
          <button
            key={value}
            type="button"
            aria-label={label}
            aria-pressed={isActive}
            onClick={() => handleModeChange(value)}
            className="flex items-center justify-center rounded-full p-1.5"
            style={{
              backgroundColor: isActive ? 'var(--primary-600)' : 'transparent',
              color: isActive ? 'white' : 'var(--text-secondary)',
              transition: `all var(--transition-default) var(--ease-default)`,
              minWidth: '28px',
              minHeight: '28px',
            }}
          >
            <Icon size={14} />
          </button>
        );
      })}
    </div>
  );
}
