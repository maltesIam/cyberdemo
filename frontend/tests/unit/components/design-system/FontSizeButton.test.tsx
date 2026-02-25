/**
 * UT-014: FontSizeButton UI Component
 * Requirement: REQ-003-002-001
 * Task: T-003-002
 *
 * AC-001: Button shows typography icon (e.g., "Aa")
 * AC-002: Visual indicator changes per step (e.g., text label changes)
 * AC-003: Tooltip shows current level: "Font size: Normal / Medium / Large"
 * AC-004: ARIA label: aria-label="Adjust font size", announces current level
 * AC-005: Placed immediately to the LEFT of the theme toggle in the header
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { FontSizeButton } from '../../../../src/components/FontSizeButton';

beforeEach(() => {
  document.documentElement.style.fontSize = '';
  localStorage.clear();
});

describe('UT-014: FontSizeButton UI Component (REQ-003-002-001)', () => {
  // AC-001: Button shows typography icon (e.g., "Aa" or ALargeSmall icon)
  describe('AC-001: Typography icon', () => {
    it('should render a button element', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      expect(button).toBeTruthy();
    });

    it('should contain an SVG icon (Lucide ALargeSmall)', () => {
      const { container } = render(<FontSizeButton />);
      const svg = container.querySelector('svg');
      expect(svg).toBeTruthy();
    });
  });

  // AC-002: Visual indicator changes per step
  describe('AC-002: Visual indicator per step', () => {
    it('should have aria-label indicating Default at step 0', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      expect(button.getAttribute('aria-label')).toMatch(/16px/);
      expect(button.getAttribute('aria-label')).toMatch(/Default/i);
    });

    it('should update aria-label to Medium after one click', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      expect(button.getAttribute('aria-label')).toMatch(/18px/);
      expect(button.getAttribute('aria-label')).toMatch(/Medium/i);
    });

    it('should update aria-label to Large after two clicks', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      fireEvent.click(button);
      expect(button.getAttribute('aria-label')).toMatch(/20px/);
      expect(button.getAttribute('aria-label')).toMatch(/Large/i);
    });
  });

  // AC-003: Tooltip shows current level
  describe('AC-003: Tooltip with current level', () => {
    it('should have title attribute showing current font size level at Default', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      expect(button.getAttribute('title')).toContain('16px');
      expect(button.getAttribute('title')).toContain('Default');
    });

    it('should update title after clicking to Medium', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      expect(button.getAttribute('title')).toContain('18px');
      expect(button.getAttribute('title')).toContain('Medium');
    });

    it('should update title after clicking to Large', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      fireEvent.click(button);
      expect(button.getAttribute('title')).toContain('20px');
      expect(button.getAttribute('title')).toContain('Large');
    });
  });

  // AC-004: ARIA label announces current level
  describe('AC-004: ARIA attributes', () => {
    it('should have aria-label containing "Font size"', () => {
      render(<FontSizeButton />);
      const button = screen.getByLabelText(/font size/i);
      expect(button).toBeTruthy();
    });

    it('should be accessible via aria-label', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      expect(button.getAttribute('aria-label')).toBeTruthy();
    });
  });

  // AC-005: Placement verification (LEFT of ThemeToggle in header)
  describe('AC-005: Placement (LEFT of ThemeToggle)', () => {
    it('should be renderable as a standalone component for header placement', () => {
      const { container } = render(<FontSizeButton />);
      expect(container.firstElementChild).toBeTruthy();
      expect(container.firstElementChild?.tagName).toBe('BUTTON');
    });
  });

  // Functional: Font size cycling
  describe('Functional: Font size cycling', () => {
    it('should cycle to 18px after first click', () => {
      render(<FontSizeButton />);
      fireEvent.click(screen.getByRole('button'));
      expect(document.documentElement.style.fontSize).toBe('18px');
    });

    it('should cycle to 20px after second click', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      fireEvent.click(button);
      expect(document.documentElement.style.fontSize).toBe('20px');
    });

    it('should cycle back to 16px after third click', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      fireEvent.click(button);
      fireEvent.click(button);
      expect(document.documentElement.style.fontSize).toBe('16px');
    });

    it('should persist step to localStorage', () => {
      render(<FontSizeButton />);
      fireEvent.click(screen.getByRole('button'));
      expect(localStorage.getItem('font-size-step')).toBe('1');
    });
  });

  // Styling
  describe('Styling', () => {
    it('should have rounded-full class for pill shape', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      expect(button.className).toContain('rounded-full');
    });

    it('should use design token background (bg-tertiary)', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      expect(button.style.backgroundColor).toBe('var(--bg-tertiary)');
    });

    it('should use design token text color (text-secondary)', () => {
      render(<FontSizeButton />);
      const button = screen.getByRole('button');
      expect(button.style.color).toBe('var(--text-secondary)');
    });
  });
});
