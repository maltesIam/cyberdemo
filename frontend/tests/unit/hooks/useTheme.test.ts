/**
 * UT-009: useTheme hook returns theme and toggleTheme
 * Requirement: REQ-002-001-001
 * Task: T-002-001
 *
 * Validates the useTheme React hook.
 * Acceptance Criteria:
 * - AC-001: Hook provides `theme` state (dark, light, system)
 * - AC-002: Hook provides `setTheme()` function
 * - AC-003: On mount, reads from localStorage key `theme-preference`
 * - AC-004: On theme change, writes to localStorage and updates <html> data-theme attribute
 * - AC-005: System mode detects OS preference via prefers-color-scheme media query
 * - AC-006: System mode responds to OS preference changes in real-time
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import React from 'react';
import { ThemeProvider, useTheme } from '../../../src/context/ThemeContext';

// Mock matchMedia
const mockMatchMedia = (prefersDark: boolean) => {
  const listeners: Array<(e: { matches: boolean }) => void> = [];
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: query.includes('dark') ? prefersDark : !prefersDark,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn((_event: string, handler: (e: { matches: boolean }) => void) => {
        listeners.push(handler);
      }),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
  return listeners;
};

function wrapper({ children }: { children: React.ReactNode }) {
  return React.createElement(ThemeProvider, null, children);
}

beforeEach(() => {
  document.documentElement.removeAttribute('data-theme');
  localStorage.clear();
  mockMatchMedia(true);
});

describe('UT-009: REQ-002-001-001 - useTheme hook', () => {
  // AC-001: Hook provides `theme` state
  describe('AC-001: Hook provides theme state', () => {
    it('should return current theme state', () => {
      const { result } = renderHook(() => useTheme(), { wrapper });
      expect(['dark', 'light', 'system']).toContain(result.current.theme);
    });

    it('should default to "dark" when no localStorage value exists', () => {
      const { result } = renderHook(() => useTheme(), { wrapper });
      expect(result.current.theme).toBe('dark');
    });

    it('should read "light" from localStorage', () => {
      localStorage.setItem('theme-preference', 'light');
      const { result } = renderHook(() => useTheme(), { wrapper });
      expect(result.current.theme).toBe('light');
    });

    it('should read "system" from localStorage', () => {
      localStorage.setItem('theme-preference', 'system');
      const { result } = renderHook(() => useTheme(), { wrapper });
      expect(result.current.theme).toBe('system');
    });
  });

  // AC-002: Hook provides setTheme() function
  describe('AC-002: Hook provides setTheme function', () => {
    it('should expose a setTheme function', () => {
      const { result } = renderHook(() => useTheme(), { wrapper });
      expect(typeof result.current.setTheme).toBe('function');
    });

    it('should change theme when setTheme is called', () => {
      const { result } = renderHook(() => useTheme(), { wrapper });
      act(() => {
        result.current.setTheme('light');
      });
      expect(result.current.theme).toBe('light');
    });
  });

  // AC-003: On mount, reads from localStorage key `theme-preference`
  describe('AC-003: Reads from localStorage on mount', () => {
    it('should read stored preference on mount', () => {
      localStorage.setItem('theme-preference', 'light');
      const { result } = renderHook(() => useTheme(), { wrapper });
      expect(result.current.theme).toBe('light');
    });

    it('should default to dark if localStorage value is invalid', () => {
      localStorage.setItem('theme-preference', 'invalid-value');
      const { result } = renderHook(() => useTheme(), { wrapper });
      expect(result.current.theme).toBe('dark');
    });
  });

  // AC-004: On theme change, writes to localStorage and updates <html> data-theme
  describe('AC-004: Writes to localStorage and updates data-theme', () => {
    it('should write to localStorage when theme changes', () => {
      const { result } = renderHook(() => useTheme(), { wrapper });
      act(() => {
        result.current.setTheme('light');
      });
      expect(localStorage.getItem('theme-preference')).toBe('light');
    });

    it('should update data-theme attribute on <html>', () => {
      const { result } = renderHook(() => useTheme(), { wrapper });
      act(() => {
        result.current.setTheme('light');
      });
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });

    it('should update data-theme to dark when setTheme("dark") is called', () => {
      const { result } = renderHook(() => useTheme(), { wrapper });
      act(() => {
        result.current.setTheme('light');
      });
      act(() => {
        result.current.setTheme('dark');
      });
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });
  });

  // AC-005: System mode detects OS preference
  describe('AC-005: System mode detects OS preference', () => {
    it('should resolve to dark when OS prefers dark and theme is system', () => {
      mockMatchMedia(true);
      const { result } = renderHook(() => useTheme(), { wrapper });
      act(() => {
        result.current.setTheme('system');
      });
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });

    it('should resolve to light when OS prefers light and theme is system', () => {
      mockMatchMedia(false);
      const { result } = renderHook(() => useTheme(), { wrapper });
      act(() => {
        result.current.setTheme('system');
      });
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });
  });

  // AC-006: System mode responds to OS preference changes in real-time
  describe('AC-006: System mode responds to OS preference changes', () => {
    it('should provide effectiveTheme derived from system preference', () => {
      mockMatchMedia(true);
      const { result } = renderHook(() => useTheme(), { wrapper });
      act(() => {
        result.current.setTheme('system');
      });
      expect(result.current.effectiveTheme).toBe('dark');
    });
  });
});
