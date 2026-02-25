/**
 * Theme Utility — AgentFlow Design System v2.0
 *
 * Manages theme preference (dark/light/system) via localStorage
 * and applies the correct data-theme attribute on <html>.
 *
 * REQ-002-003-001 through REQ-002-003-005
 */

const THEME_KEY = 'theme-preference';
const VALID_PREFERENCES = ['dark', 'light', 'system'] as const;
type ThemePreference = (typeof VALID_PREFERENCES)[number];
type EffectiveTheme = 'dark' | 'light';

/**
 * Gets the stored theme preference from localStorage.
 * Returns 'dark' as default if no valid value is found.
 */
export function getStoredThemePreference(): ThemePreference {
  try {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored && VALID_PREFERENCES.includes(stored as ThemePreference)) {
      return stored as ThemePreference;
    }
  } catch {
    // localStorage unavailable
  }
  return 'dark';
}

/**
 * Saves theme preference to localStorage.
 */
export function saveThemePreference(preference: ThemePreference): void {
  try {
    if (VALID_PREFERENCES.includes(preference)) {
      localStorage.setItem(THEME_KEY, preference);
    }
  } catch {
    // localStorage unavailable
  }
}

/**
 * Resolves the effective theme (dark or light) based on preference.
 * For 'system', reads prefers-color-scheme media query.
 */
export function getEffectiveTheme(): EffectiveTheme {
  const preference = getStoredThemePreference();

  if (preference === 'dark') return 'dark';
  if (preference === 'light') return 'light';

  // system — detect OS preference
  if (preference === 'system') {
    try {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      return prefersDark ? 'dark' : 'light';
    } catch {
      return 'dark';
    }
  }

  return 'dark';
}

/**
 * Applies the theme from localStorage to the document.
 * Called before first paint (via inline script in <head>) to prevent FOUC.
 */
export function applyThemeFromStorage(): void {
  const theme = getEffectiveTheme();
  document.documentElement.setAttribute('data-theme', theme);
}

/**
 * Sets the theme and persists the preference.
 */
export function setTheme(preference: ThemePreference): void {
  saveThemePreference(preference);

  let effectiveTheme: EffectiveTheme;
  if (preference === 'system') {
    try {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      effectiveTheme = prefersDark ? 'dark' : 'light';
    } catch {
      effectiveTheme = 'dark';
    }
  } else {
    effectiveTheme = preference;
  }

  document.documentElement.setAttribute('data-theme', effectiveTheme);
}
