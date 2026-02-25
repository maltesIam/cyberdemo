/**
 * UT-051: ThemeProvider and FontSizeProvider context works
 * Requirement: TECH-003
 * Task: T-TECH-003
 *
 * Validates the React context providers for theme and font size.
 * Acceptance Criteria:
 * - AC-001: ThemeProvider wraps entire App component
 * - AC-002: Provides useTheme and useFontSize hooks to all children
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { ThemeProvider, useTheme } from '../../../src/context/ThemeContext';
import { FontSizeProvider, useFontSize } from '../../../src/context/FontSizeContext';
import { DesignSystemProvider } from '../../../src/context/DesignSystemProvider';

// Mock matchMedia
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

describe('UT-051: TECH-003 - React context providers', () => {
  // AC-001: ThemeProvider wraps entire App component
  describe('AC-001: ThemeProvider provides theme context', () => {
    it('should provide theme value to children via useTheme', () => {
      function themeWrapper({ children }: { children: React.ReactNode }) {
        return React.createElement(ThemeProvider, null, children);
      }
      const { result } = renderHook(() => useTheme(), { wrapper: themeWrapper });
      expect(result.current.theme).toBeDefined();
      expect(typeof result.current.setTheme).toBe('function');
    });

    it('should allow children to read and change theme', () => {
      function themeWrapper({ children }: { children: React.ReactNode }) {
        return React.createElement(ThemeProvider, null, children);
      }
      const { result } = renderHook(() => useTheme(), { wrapper: themeWrapper });

      act(() => {
        result.current.setTheme('light');
      });
      expect(result.current.theme).toBe('light');

      act(() => {
        result.current.setTheme('dark');
      });
      expect(result.current.theme).toBe('dark');
    });
  });

  // AC-002: FontSizeProvider provides font size context
  describe('AC-002: FontSizeProvider provides font size context', () => {
    it('should provide fontSizeStep to children via useFontSize', () => {
      function fontSizeWrapper({ children }: { children: React.ReactNode }) {
        return React.createElement(FontSizeProvider, null, children);
      }
      const { result } = renderHook(() => useFontSize(), { wrapper: fontSizeWrapper });
      expect(result.current.fontSizeStep).toBeDefined();
      expect(typeof result.current.cycleFontSize).toBe('function');
    });

    it('should cycle through font sizes: 0 -> 1 -> 2 -> 0', () => {
      function fontSizeWrapper({ children }: { children: React.ReactNode }) {
        return React.createElement(FontSizeProvider, null, children);
      }
      const { result } = renderHook(() => useFontSize(), { wrapper: fontSizeWrapper });

      expect(result.current.fontSizeStep).toBe(0);

      act(() => {
        result.current.cycleFontSize();
      });
      expect(result.current.fontSizeStep).toBe(1);

      act(() => {
        result.current.cycleFontSize();
      });
      expect(result.current.fontSizeStep).toBe(2);

      act(() => {
        result.current.cycleFontSize();
      });
      expect(result.current.fontSizeStep).toBe(0);
    });
  });

  // Combined DesignSystemProvider
  describe('DesignSystemProvider wraps both ThemeProvider and FontSizeProvider', () => {
    it('should provide both useTheme and useFontSize to children', () => {
      function TestComponent() {
        const themeCtx = useTheme();
        const fontSizeCtx = useFontSize();
        return React.createElement('div', {
          'data-testid': 'test',
          'data-theme-value': themeCtx.theme,
          'data-font-step': fontSizeCtx.fontSizeStep,
        });
      }

      render(
        React.createElement(DesignSystemProvider, null,
          React.createElement(TestComponent)
        )
      );

      const el = screen.getByTestId('test');
      expect(el.getAttribute('data-theme-value')).toBe('dark');
      expect(el.getAttribute('data-font-step')).toBe('0');
    });
  });
});
