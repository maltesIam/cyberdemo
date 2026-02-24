/**
 * AnimatedKpiValue - KPI number counting animation component
 *
 * REQ-001-004-004: KPI numbers animate from 0 to their target value
 * with a counting effect.
 * TECH-007: KPI animation component
 */

import { useEffect, useRef, useState } from 'react';

interface AnimatedKpiValueProps {
  /** Target numeric value */
  value: number;
  /** Whether to animate from 0 to value. Default: false (show immediately) */
  animate?: boolean;
  /** Duration of the counting animation in ms. Default: 1000 */
  durationMs?: number;
  /** Number of decimal places to display. Default: 0 */
  decimals?: number;
  /** Prefix string (e.g. "$") */
  prefix?: string;
  /** Suffix string (e.g. "h", "%") */
  suffix?: string;
  /** Additional CSS class */
  className?: string;
}

/**
 * Easing function for smooth counting (ease-out cubic)
 */
function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3);
}

export function AnimatedKpiValue({
  value,
  animate = false,
  durationMs = 1000,
  decimals = 0,
  prefix = '',
  suffix = '',
  className = '',
}: AnimatedKpiValueProps) {
  const [displayValue, setDisplayValue] = useState(animate ? 0 : value);
  const animationRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const startValueRef = useRef(0);

  useEffect(() => {
    // Cleanup any existing animation
    if (animationRef.current) {
      clearInterval(animationRef.current);
      animationRef.current = null;
    }

    if (!animate) {
      setDisplayValue(value);
      return;
    }

    // Start animation from current display value to target
    startValueRef.current = displayValue;
    startTimeRef.current = Date.now();

    const fps = 60;
    const intervalMs = Math.max(1000 / fps, 16);

    animationRef.current = setInterval(() => {
      const elapsed = Date.now() - (startTimeRef.current ?? Date.now());
      const progress = Math.min(elapsed / durationMs, 1);
      const easedProgress = easeOutCubic(progress);

      const current = startValueRef.current + (value - startValueRef.current) * easedProgress;
      setDisplayValue(current);

      if (progress >= 1) {
        setDisplayValue(value);
        if (animationRef.current) {
          clearInterval(animationRef.current);
          animationRef.current = null;
        }
      }
    }, intervalMs);

    return () => {
      if (animationRef.current) {
        clearInterval(animationRef.current);
        animationRef.current = null;
      }
    };
  }, [value, animate, durationMs]);

  const formattedValue = decimals > 0
    ? displayValue.toFixed(decimals)
    : Math.round(displayValue).toString();

  return (
    <span data-testid="animated-kpi" className={className}>
      {prefix}{formattedValue}{suffix}
    </span>
  );
}
