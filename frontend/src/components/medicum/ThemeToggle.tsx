/**
 * ThemeToggle - Three-mode theme toggle component (Dark/Light/System)
 * REQ-002-001-001: Pill shape with 3 buttons
 * REQ-002-001-002: Active button primary-600 bg, inactive text-secondary
 * REQ-002-001-003: Dark=Moon, Light=Sun, System=Monitor icons
 * REQ-002-001-004: Click sets data-theme on html element
 * REQ-002-001-005: System reads prefers-color-scheme media query
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Moon, Sun, Monitor } from 'lucide-react';

export type ThemeMode = 'dark' | 'light' | 'system';

interface ThemeToggleProps {
  className?: string;
}

function getSystemTheme(): 'dark' | 'light' {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return 'dark';
}

function applyTheme(mode: ThemeMode): void {
  const resolved = mode === 'system' ? getSystemTheme() : mode;
  document.documentElement.setAttribute('data-theme', resolved);
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ className = '' }) => {
  const [mode, setMode] = useState<ThemeMode>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('theme-preference');
      if (stored === 'dark' || stored === 'light' || stored === 'system') {
        return stored;
      }
    }
    return 'dark';
  });

  useEffect(() => {
    applyTheme(mode);
    localStorage.setItem('theme-preference', mode);
  }, [mode]);

  useEffect(() => {
    if (mode !== 'system') return;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = () => applyTheme('system');
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [mode]);

  const handleClick = useCallback((newMode: ThemeMode) => {
    setMode(newMode);
  }, []);

  const modes: { mode: ThemeMode; icon: React.ReactNode; label: string }[] = [
    { mode: 'dark', icon: <Moon size={14} />, label: 'Dark' },
    { mode: 'light', icon: <Sun size={14} />, label: 'Light' },
    { mode: 'system', icon: <Monitor size={14} />, label: 'System' },
  ];

  return (
    <div
      className={`inline-flex items-center rounded-full border p-0.5 ${className}`}
      style={{
        backgroundColor: 'var(--bg-tertiary)',
        borderColor: 'var(--border-primary)',
        transition: `all var(--duration-normal) var(--ease-default)`,
      }}
      role="group"
      aria-label="Theme selector"
    >
      {modes.map(({ mode: m, icon, label }) => (
        <button
          key={m}
          onClick={() => handleClick(m)}
          aria-pressed={mode === m}
          aria-label={`${label} theme`}
          className="flex items-center justify-center rounded-full px-2 py-1 text-xs font-medium"
          style={{
            backgroundColor: mode === m ? 'var(--color-primary-600)' : 'transparent',
            color: mode === m ? '#ffffff' : 'var(--text-secondary)',
            transition: `all var(--duration-normal) var(--ease-default)`,
            minWidth: '28px',
            height: '24px',
          }}
        >
          {icon}
        </button>
      ))}
    </div>
  );
};

export default ThemeToggle;
