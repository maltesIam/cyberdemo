/**
 * Unit Tests for Button Component (T-099 to T-103)
 * Verifies button variants, sizes, focus ring, and disabled state.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Button } from '../../../../src/components/ui/Button';

describe('Button Component', () => {
  // T-099: REQ-007-001-001 - Primary buttons: primary-600 bg, hover primary-700 + translateY
  describe('T-099: Primary button', () => {
    it('should render with primary variant by default', () => {
      render(<Button>Click me</Button>);
      const btn = screen.getByRole('button', { name: 'Click me' });
      expect(btn).toBeInTheDocument();
      expect(btn.className).toContain('btn-primary');
    });

    it('should have primary-600 background color style', () => {
      render(<Button variant="primary">Primary</Button>);
      const btn = screen.getByRole('button', { name: 'Primary' });
      expect(btn.style.backgroundColor).toBe('var(--color-primary-600)');
    });

    it('should have white text color', () => {
      render(<Button variant="primary">Primary</Button>);
      const btn = screen.getByRole('button', { name: 'Primary' });
      expect(btn.style.color).toBe('white');
    });
  });

  // T-100: REQ-007-001-002 - Destructive buttons: color-error bg, hover error-dark
  describe('T-100: Destructive button', () => {
    it('should render with destructive variant', () => {
      render(<Button variant="destructive">Delete</Button>);
      const btn = screen.getByRole('button', { name: 'Delete' });
      expect(btn.className).toContain('btn-destructive');
    });

    it('should have color-error background', () => {
      render(<Button variant="destructive">Delete</Button>);
      const btn = screen.getByRole('button', { name: 'Delete' });
      expect(btn.style.backgroundColor).toBe('var(--color-error)');
    });
  });

  // T-101: REQ-007-001-003 - Button sizes: sm 32px, md 36px, lg 44px
  describe('T-101: Button sizes', () => {
    it('should render sm size with 32px height', () => {
      render(<Button size="sm">Small</Button>);
      const btn = screen.getByRole('button', { name: 'Small' });
      expect(btn.style.height).toBe('32px');
    });

    it('should render md size with 36px height (default)', () => {
      render(<Button size="md">Medium</Button>);
      const btn = screen.getByRole('button', { name: 'Medium' });
      expect(btn.style.height).toBe('36px');
    });

    it('should render lg size with 44px height', () => {
      render(<Button size="lg">Large</Button>);
      const btn = screen.getByRole('button', { name: 'Large' });
      expect(btn.style.height).toBe('44px');
    });

    it('should default to md size', () => {
      render(<Button>Default</Button>);
      const btn = screen.getByRole('button', { name: 'Default' });
      expect(btn.style.height).toBe('36px');
    });
  });

  // T-102: REQ-007-001-004 - Focus ring: 2px outline primary-500
  describe('T-102: Focus ring', () => {
    it('should have focus outline style defined', () => {
      render(<Button>Focus</Button>);
      const btn = screen.getByRole('button', { name: 'Focus' });
      // The button class should include focus ring styles
      expect(btn.className).toContain('btn-');
      // Focus ring is defined via CSS, check the data attribute
      expect(btn.getAttribute('data-focus-ring')).toBe('true');
    });
  });

  // T-103: REQ-007-001-005 - Disabled: opacity 0.5, cursor-not-allowed
  describe('T-103: Disabled state', () => {
    it('should render as disabled', () => {
      render(<Button disabled>Disabled</Button>);
      const btn = screen.getByRole('button', { name: 'Disabled' });
      expect(btn).toBeDisabled();
    });

    it('should have opacity 0.5 when disabled', () => {
      render(<Button disabled>Disabled</Button>);
      const btn = screen.getByRole('button', { name: 'Disabled' });
      expect(btn.style.opacity).toBe('0.5');
    });

    it('should have cursor not-allowed when disabled', () => {
      render(<Button disabled>Disabled</Button>);
      const btn = screen.getByRole('button', { name: 'Disabled' });
      expect(btn.style.cursor).toBe('not-allowed');
    });
  });
});
