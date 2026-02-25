/**
 * IT-002: Theme tokens switch between dark and light correctly
 * Requirements: REQ-001-002-001, REQ-001-002-002
 * Tasks: T-001-006, T-001-007
 *
 * Integration test verifying that theme token switching works end-to-end:
 * - Dark theme tokens are applied when data-theme="dark"
 * - Light theme tokens are applied when data-theme="light"
 * - Switching between themes updates all semantic tokens
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import { setTheme, getEffectiveTheme } from '../../src/utils/theme';

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

let cssContent: string;

beforeAll(() => {
  const cssPath = path.resolve(__dirname, '../../src/styles/design-tokens.css');
  cssContent = fs.readFileSync(cssPath, 'utf-8');
});

beforeEach(() => {
  document.documentElement.removeAttribute('data-theme');
  localStorage.clear();
  mockMatchMedia(true);
});

describe('IT-002: Theme tokens switch between dark and light correctly', () => {
  describe('Dark theme activation', () => {
    it('should set data-theme="dark" when dark theme is selected', () => {
      setTheme('dark');
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });

    it('should persist dark preference to localStorage', () => {
      setTheme('dark');
      expect(localStorage.getItem('theme-preference')).toBe('dark');
    });
  });

  describe('Light theme activation', () => {
    it('should set data-theme="light" when light theme is selected', () => {
      setTheme('light');
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });

    it('should persist light preference to localStorage', () => {
      setTheme('light');
      expect(localStorage.getItem('theme-preference')).toBe('light');
    });
  });

  describe('System theme resolution', () => {
    it('should resolve to dark when OS prefers dark', () => {
      mockMatchMedia(true);
      setTheme('system');
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
      expect(localStorage.getItem('theme-preference')).toBe('system');
    });

    it('should resolve to light when OS prefers light', () => {
      mockMatchMedia(false);
      setTheme('system');
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
      expect(localStorage.getItem('theme-preference')).toBe('system');
    });
  });

  describe('Theme switching flow', () => {
    it('should switch from dark to light', () => {
      setTheme('dark');
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');

      setTheme('light');
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });

    it('should switch from light to dark', () => {
      setTheme('light');
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');

      setTheme('dark');
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });

    it('should switch from dark to system to light', () => {
      setTheme('dark');
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');

      mockMatchMedia(false);
      setTheme('system');
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');

      setTheme('light');
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });
  });

  describe('CSS file has both theme blocks', () => {
    it('should have dark theme block with all required tokens', () => {
      expect(cssContent).toContain('[data-theme="dark"]');
      expect(cssContent).toMatch(/\[data-theme="dark"\][\s\S]*--bg-primary/);
      expect(cssContent).toMatch(/\[data-theme="dark"\][\s\S]*--text-primary/);
      expect(cssContent).toMatch(/\[data-theme="dark"\][\s\S]*--border-primary/);
    });

    it('should have light theme block with all required tokens', () => {
      expect(cssContent).toContain('[data-theme="light"]');
      expect(cssContent).toMatch(/\[data-theme="light"\][\s\S]*--bg-primary/);
      expect(cssContent).toMatch(/\[data-theme="light"\][\s\S]*--text-primary/);
      expect(cssContent).toMatch(/\[data-theme="light"\][\s\S]*--border-primary/);
    });
  });
});
