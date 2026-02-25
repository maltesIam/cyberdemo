/**
 * Font Size Utility — AgentFlow Design System v2.0
 *
 * Manages the 3-step cyclic font size (16px -> 18px -> 20px -> 16px).
 * Persists step index in localStorage and applies to documentElement.
 *
 * REQ-003-003-001 through REQ-003-003-003
 */

const FONT_SIZE_KEY = 'font-size-step';
export const FONT_SIZES = [16, 18, 20] as const;
const VALID_STEPS = ['0', '1', '2'] as const;

/**
 * Gets the stored font size step from localStorage.
 * Returns 0 (16px) as default if no valid value is found.
 */
export function getFontSizeStep(): number {
  try {
    const stored = localStorage.getItem(FONT_SIZE_KEY);
    if (stored && VALID_STEPS.includes(stored as (typeof VALID_STEPS)[number])) {
      return parseInt(stored, 10);
    }
  } catch {
    // localStorage unavailable
  }
  return 0;
}

/**
 * Saves the font size step to localStorage.
 */
export function saveFontSizeStep(step: number): void {
  try {
    if (step >= 0 && step < FONT_SIZES.length) {
      localStorage.setItem(FONT_SIZE_KEY, String(step));
    }
  } catch {
    // localStorage unavailable
  }
}

/**
 * Applies the font size from localStorage to documentElement.
 * Called before first paint to maintain consistency.
 */
export function applyFontSizeFromStorage(): void {
  const step = getFontSizeStep();
  const size = FONT_SIZES[step];
  document.documentElement.style.fontSize = `${size}px`;
}

/**
 * Cycles to the next font size step and applies it.
 * Returns the new step index.
 */
export function cycleFontSize(currentStep: number): number {
  const nextStep = (currentStep + 1) % FONT_SIZES.length;
  const size = FONT_SIZES[nextStep];
  document.documentElement.style.fontSize = `${size}px`;
  saveFontSizeStep(nextStep);
  return nextStep;
}
