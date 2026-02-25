/**
 * IT-003: ThemeProvider + useTheme + localStorage integration
 * Requirements: TECH-003, REQ-002-001-001, DATA-001
 * Tasks: T-TECH-003, T-002-001, T-DATA-001
 *
 * Integration test verifying the complete theme system works together:
 * - ThemeProvider provides context
 * - useTheme hook reads/writes localStorage
 * - data-theme attribute is updated on changes
 * - System preference detection works
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { ThemeProvider, useTheme } from '../../src/context/ThemeContext';
import { FontSizeProvider, useFontSize } from '../../src/context/FontSizeContext';
import { DesignSystemProvider } from '../../src/context/DesignSystemProvider';

const mockMatchMedia = (prefersDark: boolean) => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: query.includes('dark') ? prefersDark : !prefersDark,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
};

beforeEach(() => {
  document.documentElement.removeAttribute('data-theme');
  document.documentElement.style.fontSize = '';
  localStorage.clear();
  mockMatchMedia(true);
});

describe('IT-003: ThemeProvider + useTheme + localStorage integration', () => {
  describe('Full theme flow: context -> localStorage -> DOM', () => {
    function wrapper({ children }: { children: React.ReactNode }) {
      return React.createElement(ThemeProvider, null, children);
    }

    it('should persist theme to localStorage and update DOM', () => {
      const { result } = renderHook(() => useTheme(), { wrapper });

      // Initial state
      expect(result.current.theme).toBe('dark');

      // Change theme
      act(() => {
        result.current.setTheme('light');
      });

      // Verify all three targets
      expect(result.current.theme).toBe('light');
      expect(localStorage.getItem('theme-preference')).toBe('light');
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });

    it('should restore theme from localStorage on mount', () => {
      localStorage.setItem('theme-preference', 'light');

      const { result } = renderHook(() => useTheme(), { wrapper });

      expect(result.current.theme).toBe('light');
    });

    it('should cycle through dark -> light -> system -> dark', () => {
      const { result } = renderHook(() => useTheme(), { wrapper });

      expect(result.current.theme).toBe('dark');

      act(() => result.current.setTheme('light'));
      expect(result.current.theme).toBe('light');
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');

      act(() => result.current.setTheme('system'));
      expect(result.current.theme).toBe('system');
      expect(localStorage.getItem('theme-preference')).toBe('system');

      act(() => result.current.setTheme('dark'));
      expect(result.current.theme).toBe('dark');
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });
  });

  describe('System preference integration', () => {
    function wrapper({ children }: { children: React.ReactNode }) {
      return React.createElement(ThemeProvider, null, children);
    }

    it('should resolve system to dark when OS prefers dark', () => {
      mockMatchMedia(true);
      const { result } = renderHook(() => useTheme(), { wrapper });

      act(() => result.current.setTheme('system'));

      expect(result.current.theme).toBe('system');
      expect(result.current.effectiveTheme).toBe('dark');
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });

    it('should resolve system to light when OS prefers light', () => {
      mockMatchMedia(false);
      const { result } = renderHook(() => useTheme(), { wrapper });

      act(() => result.current.setTheme('system'));

      expect(result.current.theme).toBe('system');
      expect(result.current.effectiveTheme).toBe('light');
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });
  });

  describe('Combined DesignSystemProvider integration', () => {
    it('should provide both theme and font size to child components', () => {
      function TestComponent() {
        const { theme, setTheme } = useTheme();
        const { fontSizeStep, cycleFontSize } = useFontSize();

        return React.createElement('div', null,
          React.createElement('span', { 'data-testid': 'theme' }, theme),
          React.createElement('span', { 'data-testid': 'font-step' }, String(fontSizeStep)),
          React.createElement('button', {
            'data-testid': 'toggle-theme',
            onClick: () => setTheme(theme === 'dark' ? 'light' : 'dark'),
          }, 'Toggle Theme'),
          React.createElement('button', {
            'data-testid': 'cycle-font',
            onClick: cycleFontSize,
          }, 'Cycle Font'),
        );
      }

      render(
        React.createElement(DesignSystemProvider, null,
          React.createElement(TestComponent)
        )
      );

      // Initial state
      expect(screen.getByTestId('theme').textContent).toBe('dark');
      expect(screen.getByTestId('font-step').textContent).toBe('0');

      // Toggle theme
      fireEvent.click(screen.getByTestId('toggle-theme'));
      expect(screen.getByTestId('theme').textContent).toBe('light');
      expect(localStorage.getItem('theme-preference')).toBe('light');

      // Cycle font size
      fireEvent.click(screen.getByTestId('cycle-font'));
      expect(screen.getByTestId('font-step').textContent).toBe('1');
      expect(document.documentElement.style.fontSize).toBe('18px');
    });
  });
});
