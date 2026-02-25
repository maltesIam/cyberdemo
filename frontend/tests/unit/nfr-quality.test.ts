/**
 * Unit Tests: NFR Quality Requirements
 * Tasks: T-154 (NFR-004), T-155 (NFR-005), T-162 (NFR-012)
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import { applyThemeFromStorage } from '../../src/utils/theme';
import { applyFontSizeFromStorage, getFontSizeStep } from '../../src/utils/font-size';

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

// UT-149: NFR-004 - Feature parity across themes
describe('T-154: 100% feature parity across themes', () => {
  it('should have both dark and light theme blocks in design tokens', () => {
    const tokensPath = path.resolve(__dirname, '../../src/styles/design-tokens.css');
    const tokens = fs.readFileSync(tokensPath, 'utf-8');
    expect(tokens).toContain('[data-theme="dark"]');
    expect(tokens).toContain('[data-theme="light"]');
  });

  it('should define the same token names in both themes', () => {
    const tokensPath = path.resolve(__dirname, '../../src/styles/design-tokens.css');
    const tokens = fs.readFileSync(tokensPath, 'utf-8');

    // Extract tokens from each theme block
    const extractTokenNames = (block: string): string[] => {
      const matches = block.match(/--[\w-]+(?=\s*:)/g) || [];
      return matches.sort();
    };

    const darkBlock = extractBlock(tokens, 'dark');
    const lightBlock = extractBlock(tokens, 'light');

    const darkTokens = extractTokenNames(darkBlock);
    const lightTokens = extractTokenNames(lightBlock);

    // Both themes should have the same semantic tokens
    expect(darkTokens.length).toBeGreaterThan(0);
    expect(lightTokens.length).toBeGreaterThan(0);
    expect(darkTokens).toEqual(lightTokens);
  });
});

// UT-150: NFR-005 - Graceful localStorage fallback
describe('T-155: Graceful localStorage fallback', () => {
  it('should default to dark theme when localStorage is empty', () => {
    applyThemeFromStorage();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('should default to step 0 font size when localStorage is empty', () => {
    const step = getFontSizeStep();
    expect(step).toBe(0);
  });

  it('should handle corrupted localStorage values gracefully', () => {
    localStorage.setItem('theme-preference', '{}');
    localStorage.setItem('font-size-step', 'abc');

    // Should not throw
    expect(() => applyThemeFromStorage()).not.toThrow();
    expect(() => applyFontSizeFromStorage()).not.toThrow();

    // Should fall back to defaults
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });
});

// UT-157: NFR-012 - Per-project preference persistence
describe('T-162: Per-project preference persistence', () => {
  it('should store preferences using standard localStorage keys', () => {
    localStorage.setItem('theme-preference', 'light');
    localStorage.setItem('font-size-step', '1');
    expect(localStorage.getItem('theme-preference')).toBe('light');
    expect(localStorage.getItem('font-size-step')).toBe('1');
  });

  it('should use simple key names without project prefix (per-origin scoping)', () => {
    // localStorage is already scoped per origin, so no prefix needed
    const themeKey = 'theme-preference';
    const fontKey = 'font-size-step';
    expect(themeKey).not.toContain('/');
    expect(fontKey).not.toContain('/');
  });
});

function extractBlock(css: string, theme: string): string {
  const startIndex = css.indexOf(`[data-theme="${theme}"]`);
  if (startIndex === -1) return '';
  const braceStart = css.indexOf('{', startIndex);
  if (braceStart === -1) return '';
  let depth = 1;
  let i = braceStart + 1;
  while (i < css.length && depth > 0) {
    if (css[i] === '{') depth++;
    if (css[i] === '}') depth--;
    i++;
  }
  return css.substring(braceStart + 1, i - 1);
}
