/**
 * DesignSystemProvider — AgentFlow Design System v2.0
 *
 * Combined provider that wraps both ThemeProvider and FontSizeProvider.
 * Use this as a single wrapper at the top of the app.
 *
 * TECH-003
 */

import { type ReactNode } from 'react';
import { ThemeProvider } from './ThemeContext';
import { FontSizeProvider } from './FontSizeContext';

interface DesignSystemProviderProps {
  children: ReactNode;
}

export function DesignSystemProvider({ children }: DesignSystemProviderProps) {
  return (
    <ThemeProvider>
      <FontSizeProvider>
        {children}
      </FontSizeProvider>
    </ThemeProvider>
  );
}
