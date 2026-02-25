/**
 * FontSizeButton - Cyclic font size accessibility control
 * REQ-003-001-001: Lucide icon button
 * REQ-003-001-002: Click cycles 16px -> 18px -> 20px -> 16px
 * REQ-003-001-003: Modifies document.documentElement.style.fontSize
 * REQ-003-001-004: Visually indicates current size state
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Type } from 'lucide-react';

const FONT_SIZES = [16, 18, 20];
const FONT_LABELS = ['Normal', 'Medium', 'Large'];

interface FontSizeButtonProps {
  className?: string;
}

export const FontSizeButton: React.FC<FontSizeButtonProps> = ({ className = '' }) => {
  const [step, setStep] = useState<number>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('font-size-step');
      const parsed = stored !== null ? parseInt(stored, 10) : 0;
      return [0, 1, 2].includes(parsed) ? parsed : 0;
    }
    return 0;
  });

  useEffect(() => {
    document.documentElement.style.fontSize = `${FONT_SIZES[step]}px`;
    localStorage.setItem('font-size-step', String(step));
  }, [step]);

  const handleClick = useCallback(() => {
    setStep((prev) => (prev + 1) % 3);
  }, []);

  return (
    <button
      onClick={handleClick}
      aria-label={`Adjust font size - current: ${FONT_LABELS[step]}`}
      title={`Font size: ${FONT_LABELS[step]}`}
      className={`flex items-center justify-center rounded-full ${className}`}
      style={{
        backgroundColor: 'var(--bg-tertiary)',
        borderColor: 'var(--border-primary)',
        color: 'var(--text-secondary)',
        border: '1px solid var(--border-primary)',
        width: '32px',
        height: '32px',
        transition: `all var(--duration-normal) var(--ease-default)`,
        position: 'relative',
      }}
      data-font-step={step}
    >
      <Type size={14} />
      {step > 0 && (
        <span
          className="absolute -top-0.5 -right-0.5 flex items-center justify-center rounded-full text-primary"
          style={{
            backgroundColor: 'var(--color-primary-600)',
            width: '12px',
            height: '12px',
            fontSize: '8px',
            fontWeight: 'var(--weight-bold)' as any,
          }}
        >
          {step}
        </span>
      )}
    </button>
  );
};

export default FontSizeButton;
