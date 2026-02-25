/**
 * ThemeContext — AgentFlow Design System v2.0
 *
 * React context provider for theme state management.
 * Provides useTheme hook to all children.
 *
 * TECH-003, REQ-002-001-001
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
  type ReactNode,
} from 'react';
import {
  getStoredThemePreference,
  setTheme as applyTheme,
  getEffectiveTheme,
} from '../utils/theme';

type ThemePreference = 'dark' | 'light' | 'system';
type EffectiveTheme = 'dark' | 'light';

interface ThemeContextValue {
  /** The user's theme preference (dark, light, or system) */
  theme: ThemePreference;
  /** The actual applied theme after resolving system preference */
  effectiveTheme: EffectiveTheme;
  /** Set the theme preference */
  setTheme: (preference: ThemePreference) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<ThemePreference>(() => {
    if (typeof window === 'undefined') return 'dark';
    return getStoredThemePreference();
  });

  const [effectiveTheme, setEffectiveTheme] = useState<EffectiveTheme>(() => {
    if (typeof window === 'undefined') return 'dark';
    return getEffectiveTheme();
  });

  const setTheme = useCallback((preference: ThemePreference) => {
    setThemeState(preference);
    applyTheme(preference);

    // Resolve effective theme
    if (preference === 'system') {
      try {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setEffectiveTheme(prefersDark ? 'dark' : 'light');
      } catch {
        setEffectiveTheme('dark');
      }
    } else {
      setEffectiveTheme(preference);
    }
  }, []);

  // Listen for OS preference changes when in system mode
  useEffect(() => {
    if (theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      const newEffective = e.matches ? 'dark' : 'light';
      setEffectiveTheme(newEffective);
      applyTheme('system');
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  const value = useMemo<ThemeContextValue>(
    () => ({ theme, effectiveTheme, setTheme }),
    [theme, effectiveTheme, setTheme]
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook to access theme context.
 * Must be used within a ThemeProvider.
 */
export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
