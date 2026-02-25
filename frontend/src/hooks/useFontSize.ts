/**
 * useFontSize Hook - AgentFlow Design System v2.0
 *
 * Manages font size state (step 0/1/2), reads/writes localStorage,
 * and modifies html { font-size }.
 *
 * REQ-003-001-001
 */
import { useState, useCallback } from 'react';
import {
  getFontSizeStep,
  cycleFontSize as cycleFontSizeUtil,
  FONT_SIZES,
} from '../utils/font-size';

const SIZE_LABELS = ['Normal', 'Medium', 'Large'] as const;

export interface UseFontSizeReturn {
  fontSizeStep: number;
  fontSizePx: number;
  sizeLabel: string;
  cycleFontSize: () => void;
}

export function useFontSize(): UseFontSizeReturn {
  const [fontSizeStep, setFontSizeStep] = useState<number>(() => {
    if (typeof window === 'undefined') return 0;
    return getFontSizeStep();
  });

  const cycleFontSize = useCallback(() => {
    const nextStep = cycleFontSizeUtil(fontSizeStep);
    setFontSizeStep(nextStep);
  }, [fontSizeStep]);

  return {
    fontSizeStep,
    fontSizePx: FONT_SIZES[fontSizeStep],
    sizeLabel: SIZE_LABELS[fontSizeStep],
    cycleFontSize,
  };
}
