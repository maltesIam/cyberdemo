/**
 * FontSizeContext — AgentFlow Design System v2.0
 *
 * React context provider for font size state management.
 * Provides useFontSize hook to all children.
 *
 * TECH-003, REQ-003-001-001
 */

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useMemo,
  type ReactNode,
} from 'react';
import {
  getFontSizeStep,
  cycleFontSize as applyNextFontSize,
  FONT_SIZES,
} from '../utils/font-size';

interface FontSizeContextValue {
  /** Current font size step (0, 1, or 2) */
  fontSizeStep: number;
  /** Current font size in pixels */
  fontSize: number;
  /** Cycle to the next font size step */
  cycleFontSize: () => void;
}

const FontSizeContext = createContext<FontSizeContextValue | undefined>(undefined);

interface FontSizeProviderProps {
  children: ReactNode;
}

export function FontSizeProvider({ children }: FontSizeProviderProps) {
  const [fontSizeStep, setFontSizeStep] = useState<number>(() => {
    if (typeof window === 'undefined') return 0;
    return getFontSizeStep();
  });

  const cycleFontSize = useCallback(() => {
    setFontSizeStep(current => {
      const nextStep = applyNextFontSize(current);
      return nextStep;
    });
  }, []);

  const fontSize = FONT_SIZES[fontSizeStep] ?? 16;

  const value = useMemo<FontSizeContextValue>(
    () => ({ fontSizeStep, fontSize, cycleFontSize }),
    [fontSizeStep, fontSize, cycleFontSize]
  );

  return (
    <FontSizeContext.Provider value={value}>
      {children}
    </FontSizeContext.Provider>
  );
}

/**
 * Hook to access font size context.
 * Must be used within a FontSizeProvider.
 */
export function useFontSize(): FontSizeContextValue {
  const context = useContext(FontSizeContext);
  if (context === undefined) {
    throw new Error('useFontSize must be used within a FontSizeProvider');
  }
  return context;
}
