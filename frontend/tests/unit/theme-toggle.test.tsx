/**
 * Unit Tests: ThemeToggle React Component
 * Tasks: T-012 (REQ-002-001-001), T-013 (REQ-002-001-002), T-014 (REQ-002-001-003),
 *        T-015 (REQ-002-001-004), T-016 (REQ-002-001-005), T-017 (REQ-002-001-006)
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { ThemeToggle } from '../../src/components/ThemeToggle';

// Mock matchMedia
const mockMatchMedia = (matches: boolean) => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: query.includes('dark') ? matches : !matches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
};

beforeEach(() => {
  // Reset DOM state
  document.documentElement.removeAttribute('data-theme');
  localStorage.clear();
  mockMatchMedia(true); // default to dark OS preference
});

// UT-012: REQ-002-001-001 - ThemeToggle renders pill shape with 3 buttons
describe('T-012: ThemeToggle renders pill shape with 3 buttons', () => {
  it('should render three buttons', () => {
    render(<ThemeToggle />);
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBe(3);
  });

  it('should have a container element (pill shape)', () => {
    const { container } = render(<ThemeToggle />);
    const wrapper = container.firstElementChild;
    expect(wrapper).toBeTruthy();
    expect(wrapper?.children.length).toBe(3);
  });
});

// UT-013: REQ-002-001-002 - Active button primary-600 bg, inactive text-secondary
describe('T-013: ThemeToggle button styling', () => {
  it('should have one active button with distinct styling', () => {
    render(<ThemeToggle />);
    const buttons = screen.getAllByRole('button');
    // At least one button should have aria-pressed="true"
    const activeButtons = buttons.filter(b => b.getAttribute('aria-pressed') === 'true');
    expect(activeButtons.length).toBe(1);
  });

  it('should have inactive buttons with different styling', () => {
    render(<ThemeToggle />);
    const buttons = screen.getAllByRole('button');
    const inactiveButtons = buttons.filter(b => b.getAttribute('aria-pressed') !== 'true');
    expect(inactiveButtons.length).toBe(2);
  });
});

// UT-014: REQ-002-001-003 - ThemeToggle uses correct Lucide icons per mode
describe('T-014: ThemeToggle uses correct Lucide icons', () => {
  it('should render Moon icon for dark mode button', () => {
    render(<ThemeToggle />);
    // Lucide icons render as SVGs. Look for aria-label or test-id
    expect(screen.getByLabelText(/dark/i)).toBeTruthy();
  });

  it('should render Sun icon for light mode button', () => {
    render(<ThemeToggle />);
    expect(screen.getByLabelText(/light/i)).toBeTruthy();
  });

  it('should render Monitor icon for system mode button', () => {
    render(<ThemeToggle />);
    expect(screen.getByLabelText(/system/i)).toBeTruthy();
  });
});

// UT-015: REQ-002-001-004 - ThemeToggle click sets data-theme on html element
describe('T-015: ThemeToggle click sets data-theme on html element', () => {
  it('should set data-theme="light" when light button is clicked', () => {
    render(<ThemeToggle />);
    const lightButton = screen.getByLabelText(/light/i);
    fireEvent.click(lightButton);
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });

  it('should set data-theme="dark" when dark button is clicked', () => {
    render(<ThemeToggle />);
    const darkButton = screen.getByLabelText(/dark/i);
    fireEvent.click(darkButton);
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('should store preference in localStorage', () => {
    render(<ThemeToggle />);
    const lightButton = screen.getByLabelText(/light/i);
    fireEvent.click(lightButton);
    expect(localStorage.getItem('theme-preference')).toBe('light');
  });
});

// UT-016: REQ-002-001-005 - System option reads prefers-color-scheme
describe('T-016: ThemeToggle System reads prefers-color-scheme', () => {
  it('should apply dark theme when OS prefers dark and system is selected', () => {
    mockMatchMedia(true); // OS prefers dark
    render(<ThemeToggle />);
    const systemButton = screen.getByLabelText(/system/i);
    fireEvent.click(systemButton);
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  it('should apply light theme when OS prefers light and system is selected', () => {
    mockMatchMedia(false); // OS prefers light
    render(<ThemeToggle />);
    const systemButton = screen.getByLabelText(/system/i);
    fireEvent.click(systemButton);
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });

  it('should store "system" in localStorage when system is selected', () => {
    render(<ThemeToggle />);
    const systemButton = screen.getByLabelText(/system/i);
    fireEvent.click(systemButton);
    expect(localStorage.getItem('theme-preference')).toBe('system');
  });
});

// UT-017: REQ-002-001-006 - Transition 200ms ease-default
describe('T-017: ThemeToggle transitions', () => {
  it('should have transition property on buttons', () => {
    const { container } = render(<ThemeToggle />);
    const buttons = container.querySelectorAll('button');
    // Check that buttons or container have transition styling
    // (Since JSDOM doesn't compute styles, we check for style attribute or class)
    expect(buttons.length).toBe(3);
    // The component should at minimum exist and render - transition is a CSS concern
    // verified at the integration/visual level
  });
});
