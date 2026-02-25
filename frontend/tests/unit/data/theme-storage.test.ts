/**
 * UT-059: LocalStorage theme persistence
 * Requirement: DATA-001
 * Task: T-DATA-001
 *
 * Validates localStorage theme preference storage.
 * Acceptance Criteria:
 * - AC-001: Key `theme-preference` stores selected theme
 * - AC-002: Valid values: "dark", "light", "system"
 * - AC-003: Default if no stored value: "dark"
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  getStoredThemePreference,
  saveThemePreference,
  setTheme,
  getEffectiveTheme,
} from '../../../src/utils/theme';

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
  localStorage.clear();
  document.documentElement.removeAttribute('data-theme');
  mockMatchMedia(true);
});

describe('UT-059: DATA-001 - LocalStorage theme preference', () => {
  // AC-001: Key `theme-preference` stores selected theme
  describe('AC-001: Uses theme-preference key in localStorage', () => {
    it('should store theme under key "theme-preference"', () => {
      saveThemePreference('light');
      expect(localStorage.getItem('theme-preference')).toBe('light');
    });

    it('should read from key "theme-preference"', () => {
      localStorage.setItem('theme-preference', 'dark');
      const pref = getStoredThemePreference();
      expect(pref).toBe('dark');
    });

    it('should update localStorage when setTheme is called', () => {
      setTheme('light');
      expect(localStorage.getItem('theme-preference')).toBe('light');
    });
  });

  // AC-002: Valid values: "dark", "light", "system"
  describe('AC-002: Valid values are dark, light, system', () => {
    it('should store and retrieve "dark"', () => {
      saveThemePreference('dark');
      expect(getStoredThemePreference()).toBe('dark');
    });

    it('should store and retrieve "light"', () => {
      saveThemePreference('light');
      expect(getStoredThemePreference()).toBe('light');
    });

    it('should store and retrieve "system"', () => {
      saveThemePreference('system');
      expect(getStoredThemePreference()).toBe('system');
    });

    it('should reject invalid values and return default', () => {
      localStorage.setItem('theme-preference', 'invalid');
      expect(getStoredThemePreference()).toBe('dark');
    });

    it('should handle empty string and return default', () => {
      localStorage.setItem('theme-preference', '');
      expect(getStoredThemePreference()).toBe('dark');
    });
  });

  // AC-003: Default if no stored value: "dark"
  describe('AC-003: Default to dark when no stored value', () => {
    it('should default to "dark" when localStorage is empty', () => {
      expect(getStoredThemePreference()).toBe('dark');
    });

    it('should default to "dark" effective theme when no preference stored', () => {
      expect(getEffectiveTheme()).toBe('dark');
    });

    it('should resolve system preference to dark when OS prefers dark', () => {
      mockMatchMedia(true);
      saveThemePreference('system');
      expect(getEffectiveTheme()).toBe('dark');
    });

    it('should resolve system preference to light when OS prefers light', () => {
      mockMatchMedia(false);
      saveThemePreference('system');
      expect(getEffectiveTheme()).toBe('light');
    });
  });
});
