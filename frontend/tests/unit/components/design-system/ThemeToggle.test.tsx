/**
 * UT-011: ThemeToggle UI Component
 * Requirement: REQ-002-002-001
 * Task: T-002-003
 *
 * AC-001: Three-button pill-shaped container with radius-full
 * AC-002: Active button has primary-600 background, white text
 * AC-003: Inactive buttons have transparent background, text-secondary
 * AC-004: Transition between states uses duration-normal (200ms)
 * AC-005: ARIA labels present: aria-label="Theme selector", each button aria-pressed
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { ThemeToggle } from '../../../../src/components/ThemeToggle';

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
  document.documentElement.removeAttribute('data-theme');
  localStorage.clear();
  mockMatchMedia(true);
});

describe('UT-011: ThemeToggle UI Component (REQ-002-002-001)', () => {
  // AC-001: Three-button pill-shaped container with radius-full
  describe('AC-001: Pill-shaped container with three buttons', () => {
    it('should render exactly three mode buttons (Dark, Light, System)', () => {
      render(<ThemeToggle />);
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBe(3);
    });

    it('should have a container wrapper with rounded-full styling', () => {
      const { container } = render(<ThemeToggle />);
      const wrapper = container.firstElementChild as HTMLElement;
      expect(wrapper).toBeTruthy();
      expect(wrapper.className).toContain('rounded-full');
    });

    it('should render Moon icon for dark mode', () => {
      render(<ThemeToggle />);
      expect(screen.getByLabelText('Dark theme')).toBeTruthy();
    });

    it('should render Sun icon for light mode', () => {
      render(<ThemeToggle />);
      expect(screen.getByLabelText('Light theme')).toBeTruthy();
    });

    it('should render Monitor icon for system mode', () => {
      render(<ThemeToggle />);
      expect(screen.getByLabelText('System theme')).toBeTruthy();
    });
  });

  // AC-002: Active button has primary-600 background, white text
  describe('AC-002: Active button styling', () => {
    it('should show primary-600 background on the active button', () => {
      render(<ThemeToggle />);
      // Default is dark, so dark button is active
      const darkButton = screen.getByLabelText('Dark theme');
      expect(darkButton.style.backgroundColor).toBe('var(--primary-600)');
    });

    it('should show white text color on the active button', () => {
      render(<ThemeToggle />);
      const darkButton = screen.getByLabelText('Dark theme');
      // JSDOM color normalization varies; accept white, #ffffff, or rgb(255, 255, 255)
      const whiteValues = ['white', '#ffffff', 'rgb(255, 255, 255)'];
      expect(whiteValues).toContain(darkButton.style.color);
    });

    it('should update active button when clicking light', () => {
      render(<ThemeToggle />);
      const lightButton = screen.getByLabelText('Light theme');
      fireEvent.click(lightButton);
      expect(lightButton.style.backgroundColor).toBe('var(--primary-600)');
      // JSDOM color normalization varies; accept white, #ffffff, or rgb(255, 255, 255)
      const whiteValues = ['white', '#ffffff', 'rgb(255, 255, 255)'];
      expect(whiteValues).toContain(lightButton.style.color);
    });
  });

  // AC-003: Inactive buttons have transparent background, text-secondary
  describe('AC-003: Inactive button styling', () => {
    it('should show transparent background on inactive buttons', () => {
      render(<ThemeToggle />);
      const lightButton = screen.getByLabelText('Light theme');
      expect(lightButton.style.backgroundColor).toBe('transparent');
    });

    it('should show text-secondary color on inactive buttons', () => {
      render(<ThemeToggle />);
      const lightButton = screen.getByLabelText('Light theme');
      expect(lightButton.style.color).toBe('var(--text-secondary)');
    });
  });

  // AC-004: Transition between states uses duration-normal (200ms)
  describe('AC-004: Transition duration', () => {
    it('should have transition style referencing --transition-default on buttons', () => {
      render(<ThemeToggle />);
      const darkButton = screen.getByLabelText('Dark theme');
      const transitionStyle = darkButton.style.transition;
      expect(transitionStyle).toContain('var(--transition-default)');
    });

    it('should have transition style on container', () => {
      const { container } = render(<ThemeToggle />);
      const wrapper = container.firstElementChild as HTMLElement;
      expect(wrapper.style.transition).toContain('var(--transition-default)');
    });
  });

  // AC-005: ARIA labels present: aria-label="Theme selector", each button aria-pressed
  describe('AC-005: ARIA attributes', () => {
    it('should have aria-label="Theme selection" on the container', () => {
      render(<ThemeToggle />);
      const group = screen.getByRole('radiogroup');
      expect(group).toBeTruthy();
      expect(group.getAttribute('aria-label')).toBe('Theme selection');
    });

    it('should have aria-pressed on each button', () => {
      render(<ThemeToggle />);
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        const pressed = button.getAttribute('aria-pressed');
        expect(pressed === 'true' || pressed === 'false').toBe(true);
      });
    });

    it('should have exactly one button with aria-pressed=true (the active one)', () => {
      render(<ThemeToggle />);
      const buttons = screen.getAllByRole('button');
      const activeButtons = buttons.filter(b => b.getAttribute('aria-pressed') === 'true');
      expect(activeButtons.length).toBe(1);
    });

    it('should update aria-pressed when clicking a different mode', () => {
      render(<ThemeToggle />);
      const lightButton = screen.getByLabelText('Light theme');
      fireEvent.click(lightButton);
      expect(lightButton.getAttribute('aria-pressed')).toBe('true');

      const darkButton = screen.getByLabelText('Dark theme');
      expect(darkButton.getAttribute('aria-pressed')).toBe('false');
    });
  });

  // Functional: Theme change applies correctly
  describe('Functional: Theme mode switching', () => {
    it('should set data-theme to light when light button is clicked', () => {
      render(<ThemeToggle />);
      fireEvent.click(screen.getByLabelText('Light theme'));
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });

    it('should set data-theme to dark when dark button is clicked', () => {
      render(<ThemeToggle />);
      fireEvent.click(screen.getByLabelText('Dark theme'));
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });

    it('should store theme preference in localStorage', () => {
      render(<ThemeToggle />);
      fireEvent.click(screen.getByLabelText('Light theme'));
      expect(localStorage.getItem('theme-preference')).toBe('light');
    });

    it('should apply system theme based on OS preference (dark)', () => {
      mockMatchMedia(true);
      render(<ThemeToggle />);
      fireEvent.click(screen.getByLabelText('System theme'));
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });

    it('should apply system theme based on OS preference (light)', () => {
      mockMatchMedia(false);
      render(<ThemeToggle />);
      fireEvent.click(screen.getByLabelText('System theme'));
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });
  });
});
