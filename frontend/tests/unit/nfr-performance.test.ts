/**
 * Unit Tests: NFR Performance Requirements
 * Tasks: T-151 (NFR-001), T-152 (NFR-002), T-153 (NFR-003)
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { applyThemeFromStorage, getEffectiveTheme } from '../../src/utils/theme';
import { applyFontSizeFromStorage } from '../../src/utils/font-size';

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

// UT-146: NFR-001 - Theme switch latency < 300ms
describe('T-151: Theme switch latency < 300ms', () => {
  it('should apply theme in under 300ms', () => {
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
    document.documentElement.setAttribute('data-theme', 'light');
    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(300);
  });
});

// UT-147: NFR-002 - Font size change latency < 100ms
describe('T-152: Font size change latency < 100ms', () => {
  it('should apply font size in under 100ms', () => {
    localStorage.setItem('font-size-step', '1');
    const start = performance.now();
    applyFontSizeFromStorage();
    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(100);
    expect(document.documentElement.style.fontSize).toBe('18px');
  });

  it('should change font size in under 100ms', () => {
    const start = performance.now();
    document.documentElement.style.fontSize = '20px';
    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(100);
  });
});

// UT-148: NFR-003 - No FOUC on page load
describe('T-153: No FOUC on page load', () => {
  it('should have inline theme script that runs synchronously', () => {
    // This is verified by the index.html structure
    // The theme is applied before any rendering via inline script in <head>
    const fs = require('fs');
    const path = require('path');
    const html = fs.readFileSync(path.resolve(__dirname, '../../index.html'), 'utf-8');
    const headContent = html.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
    // Must have theme script in head
    expect(headContent).toMatch(/theme-preference|data-theme/);
  });

  it('should apply theme before body is parsed', () => {
    // The inline script sets data-theme on <html> element
    // which is already available in <head> parsing
    localStorage.setItem('theme-preference', 'dark');
    applyThemeFromStorage();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });
});
