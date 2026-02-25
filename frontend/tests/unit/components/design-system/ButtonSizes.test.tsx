/**
 * UT-016: Button Sizes
 * Requirement: REQ-004-001-002
 * Task: T-004-002
 *
 * AC-001: btn-sm: text-xs (0.75rem), 6px 12px padding, 32px height
 * AC-002: btn-md: text-sm (0.875rem), 8px 16px padding, 36px height
 * AC-003: btn-lg: text-base (1rem), 10px 20px padding, 44px height
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Button } from '../../../../src/components/ui/Button';

describe('UT-016: Button Sizes (REQ-004-001-002)', () => {
  // AC-001: btn-sm: text-xs, 6px 12px padding, 32px height
  describe('AC-001: Small button (sm)', () => {
    it('should have 32px height', () => {
      render(<Button size="sm">Small</Button>);
      const btn = screen.getByRole('button', { name: 'Small' });
      expect(btn.style.height).toBe('32px');
    });

    it('should have text-xs font size (0.75rem)', () => {
      render(<Button size="sm">Small</Button>);
      const btn = screen.getByRole('button', { name: 'Small' });
      expect(btn.style.fontSize).toBe('0.75rem');
    });

    it('should have 6px 12px padding', () => {
      render(<Button size="sm">Small</Button>);
      const btn = screen.getByRole('button', { name: 'Small' });
      expect(btn.style.padding).toBe('6px 12px');
    });
  });

  // AC-002: btn-md: text-sm, 8px 16px padding, 36px height
  describe('AC-002: Medium button (md)', () => {
    it('should have 36px height', () => {
      render(<Button size="md">Medium</Button>);
      const btn = screen.getByRole('button', { name: 'Medium' });
      expect(btn.style.height).toBe('36px');
    });

    it('should have text-sm font size (0.875rem)', () => {
      render(<Button size="md">Medium</Button>);
      const btn = screen.getByRole('button', { name: 'Medium' });
      expect(btn.style.fontSize).toBe('0.875rem');
    });

    it('should have 8px 16px padding', () => {
      render(<Button size="md">Medium</Button>);
      const btn = screen.getByRole('button', { name: 'Medium' });
      expect(btn.style.padding).toBe('8px 16px');
    });

    it('should default to md size when no size prop provided', () => {
      render(<Button>Default</Button>);
      const btn = screen.getByRole('button', { name: 'Default' });
      expect(btn.style.height).toBe('36px');
      expect(btn.style.fontSize).toBe('0.875rem');
      expect(btn.style.padding).toBe('8px 16px');
    });
  });

  // AC-003: btn-lg: text-base, 10px 20px padding, 44px height
  describe('AC-003: Large button (lg)', () => {
    it('should have 44px height', () => {
      render(<Button size="lg">Large</Button>);
      const btn = screen.getByRole('button', { name: 'Large' });
      expect(btn.style.height).toBe('44px');
    });

    it('should have text-base font size (1rem)', () => {
      render(<Button size="lg">Large</Button>);
      const btn = screen.getByRole('button', { name: 'Large' });
      expect(btn.style.fontSize).toBe('1rem');
    });

    it('should have 10px 20px padding', () => {
      render(<Button size="lg">Large</Button>);
      const btn = screen.getByRole('button', { name: 'Large' });
      expect(btn.style.padding).toBe('10px 20px');
    });
  });

  // Cross-variant size tests
  describe('Size works with all variants', () => {
    it('should apply sm size to destructive variant', () => {
      render(<Button variant="destructive" size="sm">Small Delete</Button>);
      const btn = screen.getByRole('button', { name: 'Small Delete' });
      expect(btn.style.height).toBe('32px');
    });

    it('should apply lg size to ghost variant', () => {
      render(<Button variant="ghost" size="lg">Large Ghost</Button>);
      const btn = screen.getByRole('button', { name: 'Large Ghost' });
      expect(btn.style.height).toBe('44px');
    });

    it('should apply sm size to accent variant', () => {
      render(<Button variant="accent" size="sm">Small Accent</Button>);
      const btn = screen.getByRole('button', { name: 'Small Accent' });
      expect(btn.style.height).toBe('32px');
    });
  });
});
