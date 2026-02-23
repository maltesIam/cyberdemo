/**
 * useThrottle Hook - Throttle function calls.
 *
 * REQ-004-001-002: Throttling de eventos (max 10/segundo)
 *
 * A hook that returns a throttled version of the callback function.
 * The throttled function will only be called once per specified delay.
 */
import { useCallback, useRef } from "react";

/**
 * Hook to throttle function calls.
 *
 * @param callback - The function to throttle
 * @param delay - Minimum time between calls in milliseconds
 * @returns A throttled version of the callback
 */
export function useThrottle<T extends (...args: unknown[]) => void>(
  callback: T,
  delay: number
): (...args: Parameters<T>) => void {
  const lastCallTime = useRef<number>(0);
  const callbackRef = useRef(callback);

  // Update callback ref when callback changes
  callbackRef.current = callback;

  return useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();

      if (now - lastCallTime.current >= delay) {
        lastCallTime.current = now;
        callbackRef.current(...args);
      }
    },
    [delay]
  );
}
