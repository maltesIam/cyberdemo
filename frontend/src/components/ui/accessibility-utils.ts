/**
 * Accessibility Utilities - AgentFlow Design System
 *
 * T-119: Focus ring CSS
 * T-120: Theme toggle ARIA attributes
 * T-121: Font size button ARIA attributes
 * T-122: Modal focus trap utility
 * T-123: Toast ARIA attributes
 */

/**
 * T-119: Returns CSS for visible focus indicators.
 * Focus ring: 2px outline using primary-500.
 */
export function getFocusRingCSS(): string {
  return `
[data-focus-ring="true"]:focus-visible {
  outline: 2px solid var(--color-primary-500, #3b82f6);
  outline-offset: 2px;
}
`;
}

/**
 * T-120: Returns ARIA attributes for the theme toggle group.
 */
export function getThemeToggleARIA(): Record<string, string> {
  return {
    role: 'group',
    'aria-label': 'Theme selector',
  };
}

/**
 * T-120: Returns ARIA attributes for individual theme toggle buttons.
 */
export function getThemeToggleButtonARIA(
  buttonTheme: 'dark' | 'light' | 'system',
  activeTheme: 'dark' | 'light' | 'system'
): Record<string, boolean | string> {
  return {
    'aria-pressed': buttonTheme === activeTheme,
    'aria-label': `${buttonTheme.charAt(0).toUpperCase() + buttonTheme.slice(1)} theme`,
  };
}

/**
 * T-121: Returns ARIA attributes for font size button.
 */
export function getFontSizeButtonARIA(step: number): Record<string, string> {
  const labels = ['Normal', 'Medium', 'Large'];
  return {
    'aria-label': 'Adjust font size',
    'aria-description': `Current size: ${labels[step] ?? 'Normal'}`,
  };
}

/**
 * T-121: Returns announcement text for font size changes.
 */
export function getFontSizeAnnouncement(step: number): string {
  const labels = ['Normal', 'Medium', 'Large'];
  return `Font size: ${labels[step] ?? 'Normal'}`;
}

/**
 * T-122: Creates a focus trap for modal dialogs.
 */
export function createFocusTrap(container: HTMLElement) {
  const focusableSelectors =
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
  const focusableElements = Array.from(
    container.querySelectorAll<HTMLElement>(focusableSelectors)
  );

  return {
    focusableElements,
    firstElement: focusableElements[0] ?? null,
    lastElement: focusableElements[focusableElements.length - 1] ?? null,
    activate() {
      if (focusableElements.length > 0) {
        focusableElements[0].focus();
      }
    },
  };
}

/**
 * T-123: Returns ARIA attributes for toast notifications.
 */
export function getToastARIA(): Record<string, string> {
  return {
    role: 'status',
    'aria-live': 'polite',
  };
}
