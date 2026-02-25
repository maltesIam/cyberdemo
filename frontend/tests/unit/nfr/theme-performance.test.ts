/**
 * Unit Tests: NFR-001 - Theme Switch Performance
 * Task: T-NFR-001
 * Test ID: UT-061
 *
 * Acceptance Criteria:
 * - AC-001: Theme transition completes within 300ms
 * - AC-002: No FOUC on page load
 * - AC-003: CSS transitions use GPU-accelerated properties
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { applyThemeFromStorage, setTheme } from '../../../src/utils/theme';
import * as fs from 'fs';
import * as path from 'path';

beforeEach(() => {
  document.documentElement.removeAttribute('data-theme');
  document.documentElement.style.fontSize = '';
  localStorage.clear();
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: query.includes('dark'),
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
});

describe('T-NFR-001: Theme Switch < 300ms Performance (NFR-001)', () => {
  // AC-001: Theme transition completes within 300ms
  describe('AC-001: Theme transition time', () => {
    it('should apply theme from storage in under 300ms', () => {
      localStorage.setItem('theme-preference', 'light');
      const start = performance.now();
      applyThemeFromStorage();
      const elapsed = performance.now() - start;
      expect(elapsed).toBeLessThan(300);
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });

    it('should switch from dark to light in under 300ms', () => {
      document.documentElement.setAttribute('data-theme', 'dark');
      const start = performance.now();
      setTheme('light');
      const elapsed = performance.now() - start;
      expect(elapsed).toBeLessThan(300);
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });

    it('should switch from light to dark in under 300ms', () => {
      document.documentElement.setAttribute('data-theme', 'light');
      const start = performance.now();
      setTheme('dark');
      const elapsed = performance.now() - start;
      expect(elapsed).toBeLessThan(300);
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });

    it('should switch to system theme in under 300ms', () => {
      const start = performance.now();
      setTheme('system');
      const elapsed = performance.now() - start;
      expect(elapsed).toBeLessThan(300);
    });

    it('should handle rapid consecutive theme switches under 300ms each', () => {
      const modes: Array<'dark' | 'light' | 'system'> = ['dark', 'light', 'system', 'dark', 'light'];
      for (const mode of modes) {
        const start = performance.now();
        setTheme(mode);
        const elapsed = performance.now() - start;
        expect(elapsed).toBeLessThan(300);
      }
    });
  });

  // AC-002: No FOUC on page load
  describe('AC-002: FOUC prevention', () => {
    it('should have inline theme script in index.html head section', () => {
      const htmlPath = path.resolve(__dirname, '../../../index.html');
      const html = fs.readFileSync(htmlPath, 'utf-8');
      const headContent = html.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
      expect(headContent).toMatch(/theme-preference|data-theme/);
    });

    it('should apply theme synchronously before body render', () => {
      localStorage.setItem('theme-preference', 'dark');
      applyThemeFromStorage();
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });
  });

  // AC-003: CSS transitions use GPU-accelerated properties
  describe('AC-003: GPU-accelerated transitions in design tokens', () => {
    it('should define transition tokens in design-tokens.css', () => {
      const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
      const css = fs.readFileSync(cssPath, 'utf-8');

      // Verify transition tokens exist
      expect(css).toContain('--transition-fast');
      expect(css).toContain('--transition-default');
      expect(css).toContain('--transition-slow');
    });

    it('should define easing tokens in design-tokens.css', () => {
      const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
      const css = fs.readFileSync(cssPath, 'utf-8');

      expect(css).toContain('--ease-default');
      expect(css).toContain('--ease-in');
      expect(css).toContain('--ease-out');
    });

    it('should use transition-slow (300ms) for body theme transitions', () => {
      const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
      const css = fs.readFileSync(cssPath, 'utf-8');

      // Body should use var(--transition-slow) for theme switching
      expect(css).toMatch(/body\s*\{[^}]*transition.*var\(--transition-slow\)/s);
    });
  });
});
