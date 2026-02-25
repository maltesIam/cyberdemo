/**
 * FontSizeButton Component — AgentFlow Design System v2.0
 *
 * Cyclic font size button: 16px -> 18px -> 20px -> 16px.
 * Uses Lucide React icon (ALargeSmall). Modifies documentElement.style.fontSize.
 *
 * REQ-003-001-001 through REQ-003-001-006
 */

import { useState, useCallback } from 'react';
import { ALargeSmall } from 'lucide-react';
import { cycleFontSize, getFontSizeStep, FONT_SIZES } from '../utils/font-size';

const SIZE_LABELS = ['Default', 'Medium', 'Large'];

export function FontSizeButton() {
  const [step, setStep] = useState<number>(() => {
    if (typeof window === 'undefined') return 0;
    return getFontSizeStep();
  });

  const handleClick = useCallback(() => {
    const nextStep = cycleFontSize(step);
    setStep(nextStep);
  }, [step]);

  return (
    <button
      data-testid="font-size-button"
      type="button"
      onClick={handleClick}
      aria-label={`Font size: ${FONT_SIZES[step]}px (${SIZE_LABELS[step]}). Click to cycle.`}
      className="flex items-center justify-center rounded-full p-1.5"
      style={{
        backgroundColor: 'var(--bg-tertiary)',
        color: 'var(--text-secondary)',
        transition: `all var(--transition-default) var(--ease-default)`,
        minWidth: '28px',
        minHeight: '28px',
      }}
      title={`Font size: ${FONT_SIZES[step]}px (${SIZE_LABELS[step]})`}
    >
      <ALargeSmall size={14} />
    </button>
  );
}
