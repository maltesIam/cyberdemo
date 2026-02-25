/**
 * Unit Tests for Input Component (T-106 to T-109)
 * Verifies input base, focus, error, and placeholder states.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Input } from '../../../../src/components/ui/Input';

describe('Input Component', () => {
  // T-106: REQ-007-003-001 - Inputs: bg-input, border-primary, radius-lg, 36px
  describe('T-106: Base input', () => {
    it('should render an input element', () => {
      render(<Input aria-label="test input" />);
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('should have bg-input background', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.backgroundColor).toBe('var(--bg-input)');
    });

    it('should have border-primary border', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.borderColor).toBe('var(--border-primary)');
    });

    it('should have radius-lg border radius', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.borderRadius).toBe('var(--radius-lg)');
    });

    it('should have 36px height', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.style.height).toBe('36px');
    });
  });

  // T-107: REQ-007-003-002 - Input focus: border-focus + blue ring
  describe('T-107: Input focus state', () => {
    it('should have data-focus-ring attribute', () => {
      render(<Input aria-label="test input" />);
      const input = screen.getByRole('textbox');
      expect(input.getAttribute('data-focus-ring')).toBe('true');
    });
  });

  // T-108: REQ-007-003-003 - Input error: red border + red ring
  describe('T-108: Input error state', () => {
    it('should have error class when error prop is true', () => {
      render(<Input aria-label="test input" error />);
      const input = screen.getByRole('textbox');
      expect(input.className).toContain('input-error');
    });

    it('should have error border color', () => {
      render(<Input aria-label="test input" error />);
      const input = screen.getByRole('textbox');
      expect(input.style.borderColor).toBe('var(--color-error)');
    });

    it('should have aria-invalid when error', () => {
      render(<Input aria-label="test input" error />);
      const input = screen.getByRole('textbox');
      expect(input.getAttribute('aria-invalid')).toBe('true');
    });
  });

  // T-109: REQ-007-003-004 - Placeholder: text-tertiary
  describe('T-109: Placeholder color', () => {
    it('should render with placeholder text', () => {
      render(<Input aria-label="test input" placeholder="Enter text..." />);
      const input = screen.getByRole('textbox');
      expect(input.getAttribute('placeholder')).toBe('Enter text...');
    });

    it('should have data-placeholder-color attribute for text-tertiary', () => {
      render(<Input aria-label="test input" placeholder="Enter text..." />);
      const input = screen.getByRole('textbox');
      expect(input.getAttribute('data-placeholder-color')).toBe('text-tertiary');
    });
  });
});
