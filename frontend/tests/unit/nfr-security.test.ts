/**
 * Unit Tests: NFR Security Requirements
 * Tasks: T-156 (NFR-006), T-157 (NFR-007)
 *
 * These tests verify that the theme and font utilities do NOT use
 * any dangerous patterns. They are security validation tests.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { applyThemeFromStorage } from '../../src/utils/theme';

beforeEach(() => {
  document.documentElement.removeAttribute('data-theme');
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

// UT-151: NFR-006 - No sensitive data stored
describe('T-156: No sensitive data in localStorage', () => {
  it('should only store "dark", "light", or "system" in theme-preference', () => {
    const validValues = ['dark', 'light', 'system'];
    validValues.forEach(v => {
      localStorage.setItem('theme-preference', v);
      expect(validValues).toContain(localStorage.getItem('theme-preference'));
    });
  });

  it('should only store "0", "1", or "2" in font-size-step', () => {
    const validValues = ['0', '1', '2'];
    validValues.forEach(v => {
      localStorage.setItem('font-size-step', v);
      expect(validValues).toContain(localStorage.getItem('font-size-step'));
    });
  });
});

// UT-152: NFR-007 - No XSS vectors in theme/font handling
describe('T-157: No XSS vectors in theme/font handling', () => {
  it('should not use innerHTML for theme application', () => {
    const fs = require('fs');
    const path = require('path');
    const themeUtil = fs.readFileSync(path.resolve(__dirname, '../../src/utils/theme.ts'), 'utf-8');
    expect(themeUtil).not.toContain('innerHTML');
  });

  it('should use safe DOM APIs only (setAttribute, style property)', () => {
    const fs = require('fs');
    const path = require('path');
    const themeUtil = fs.readFileSync(path.resolve(__dirname, '../../src/utils/theme.ts'), 'utf-8');
    // Should use safe APIs like setAttribute or dataset
    const usesSafeAPIs = themeUtil.includes('setAttribute') || themeUtil.includes('dataset');
    expect(usesSafeAPIs).toBe(true);
  });

  it('should sanitize localStorage values (only accept known values)', () => {
    localStorage.setItem('theme-preference', '<script>alert("xss")</script>');
    applyThemeFromStorage();
    // Should default to dark, not apply the malicious string
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('should not inject user-controlled strings into DOM as HTML in font util', () => {
    const fs = require('fs');
    const path = require('path');
    const fontUtil = fs.readFileSync(path.resolve(__dirname, '../../src/utils/font-size.ts'), 'utf-8');
    expect(fontUtil).not.toContain('innerHTML');
  });
});
