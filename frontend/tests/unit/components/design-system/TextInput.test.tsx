/**
 * UT-017: Text Input Styling
 * Requirement: REQ-004-002-001
 * Task: T-004-003
 *
 * AC-001: Background uses bg-input token
 * AC-002: Border uses border-primary, 1px
 * AC-003: Focus state shows border-focus + blue ring (3px) - CSS verified via data attribute
 * AC-004: Error state shows red border + red ring
 * AC-005: Placeholder uses text-tertiary color
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Input } from '../../../../src/components/ui/Input';

describe('UT-017: Text Input Styling (REQ-004-002-001)', () => {
  // AC-001: Background uses bg-input token
  describe('AC-001: bg-input background', () => {
    it('should have bg-input background color', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.backgroundColor).toBe('var(--bg-input)');
    });
  });

  // AC-002: Border uses border-primary, 1px
  describe('AC-002: border-primary border', () => {
    it('should have border-primary border color', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.borderColor).toBe('var(--border-primary)');
    });

    it('should have 1px border width', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.borderWidth).toBe('1px');
    });

    it('should have solid border style', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.borderStyle).toBe('solid');
    });

    it('should have radius-lg border radius', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.borderRadius).toBe('var(--radius-lg)');
    });
  });

  // AC-003: Focus state shows border-focus + blue ring (3px)
  describe('AC-003: Focus state', () => {
    it('should have data-focus-ring attribute for CSS-based focus ring', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.getAttribute('data-focus-ring')).toBe('true');
    });

    it('should have transition for smooth focus animation', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.transition).toBeTruthy();
    });
  });

  // AC-004: Error state shows red border + red ring
  describe('AC-004: Error state', () => {
    it('should have error border color when error prop is true', () => {
      render(<Input aria-label="test input" error />);
      const input = screen.getByRole('textbox');
      expect(input.style.borderColor).toBe('var(--color-error)');
    });

    it('should have input-error class when error', () => {
      render(<Input aria-label="test input" error />);
      const input = screen.getByRole('textbox');
      expect(input.className).toContain('input-error');
    });

    it('should have aria-invalid when error', () => {
      render(<Input aria-label="test input" error />);
      const input = screen.getByRole('textbox');
      expect(input.getAttribute('aria-invalid')).toBe('true');
    });

    it('should NOT have aria-invalid when no error', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.getAttribute('aria-invalid')).toBeNull();
    });

    it('should have input-base class when no error', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.className).toContain('input-base');
    });
  });

  // AC-005: Placeholder uses text-tertiary color
  describe('AC-005: Placeholder text-tertiary', () => {
    it('should render with placeholder text', () => {
      render(<Input aria-label="test input" placeholder="Enter text..." />);
      const input = screen.getByRole('textbox');
      expect(input.getAttribute('placeholder')).toBe('Enter text...');
    });

    it('should have data-placeholder-color for text-tertiary styling', () => {
      render(<Input aria-label="test input" placeholder="Enter text..." />);
      const input = screen.getByRole('textbox');
      expect(input.getAttribute('data-placeholder-color')).toBe('text-tertiary');
    });
  });

  // Additional: Base dimensions and colors
  describe('Base input properties', () => {
    it('should have 36px height', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.height).toBe('36px');
    });

    it('should have text-primary text color', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.color).toBe('var(--text-primary)');
    });

    it('should have 100% width', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.width).toBe('100%');
    });

    it('should use font-sans family', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.fontFamily).toBe('var(--font-sans)');
    });
  });
});
