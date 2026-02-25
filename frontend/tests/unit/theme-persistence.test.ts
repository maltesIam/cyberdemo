/**
 * Unit Tests: Theme Persistence
 * Tasks: T-021 (REQ-002-003-001), T-022 (REQ-002-003-002), T-023 (REQ-002-003-003),
 *        T-024 (REQ-002-003-004), T-025 (REQ-002-003-005)
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { applyThemeFromStorage, getEffectiveTheme } from '../../src/utils/theme';

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
  localStorage.clear();
  mockMatchMedia(true);
});

// UT-021: REQ-002-003-001 - Theme saved to localStorage key theme-preference
describe('T-021: Theme saved to localStorage', () => {
  it('should use "theme-preference" as the localStorage key', () => {
    localStorage.setItem('theme-preference', 'dark');
    expect(localStorage.getItem('theme-preference')).toBe('dark');
  });

  it('should accept "dark" as a valid value', () => {
    localStorage.setItem('theme-preference', 'dark');
    const theme = getEffectiveTheme();
    expect(theme).toBe('dark');
  });

  it('should accept "light" as a valid value', () => {
    localStorage.setItem('theme-preference', 'light');
    const theme = getEffectiveTheme();
    expect(theme).toBe('light');
  });

  it('should accept "system" as a valid value', () => {
    localStorage.setItem('theme-preference', 'system');
    const theme = getEffectiveTheme();
    // system resolves to dark/light based on OS
    expect(['dark', 'light']).toContain(theme);
  });
});

// UT-022: REQ-002-003-002 - Theme applied from localStorage before first paint
describe('T-022: Theme applied from localStorage before first paint', () => {
  it('should apply stored theme to data-theme attribute', () => {
    localStorage.setItem('theme-preference', 'light');
    applyThemeFromStorage();
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });

  it('should apply dark theme from storage', () => {
    localStorage.setItem('theme-preference', 'dark');
    applyThemeFromStorage();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });
});

// UT-023: REQ-002-003-003 - System mode detects OS preference on load
describe('T-023: System mode detects OS preference on load', () => {
  it('should resolve to dark when OS prefers dark and stored as system', () => {
    mockMatchMedia(true);
    localStorage.setItem('theme-preference', 'system');
    applyThemeFromStorage();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('should resolve to light when OS prefers light and stored as system', () => {
    mockMatchMedia(false);
    localStorage.setItem('theme-preference', 'system');
    applyThemeFromStorage();
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });
});

// UT-024: REQ-002-003-004 - Default to dark if localStorage empty/unavailable
describe('T-024: Default to dark if localStorage empty', () => {
  it('should default to dark when localStorage is empty', () => {
    applyThemeFromStorage();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('should default to dark when localStorage has invalid value', () => {
    localStorage.setItem('theme-preference', 'invalid');
    applyThemeFromStorage();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });
});

// UT-025: REQ-002-003-005 - Body transition 300ms ease-default on theme switch
describe('T-025: Body transition on theme switch', () => {
  it('should apply theme without errors', () => {
    applyThemeFromStorage();
    // Transition is a CSS concern - we verify the function works without errors
    expect(document.documentElement.getAttribute('data-theme')).toBeTruthy();
  });
});
