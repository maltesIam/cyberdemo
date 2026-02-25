/**
 * UT-015: Button Variants
 * Requirement: REQ-004-001-001
 * Task: T-004-001
 *
 * AC-001: Primary button uses primary-600 background, white text
 * AC-002: Secondary button uses transparent background
 * AC-003: Ghost button uses transparent background, text-secondary
 * AC-004: Destructive button uses error color background
 * AC-005: Accent button uses secondary-600 background
 * AC-006: All buttons show translateY(-1px) on hover (CSS concern, verified structurally)
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Button } from '../../../../src/components/ui/Button';

describe('UT-015: Button Variants (REQ-004-001-001)', () => {
  // AC-001: Primary button uses primary-600 background, white text
  describe('AC-001: Primary variant', () => {
    it('should render primary variant by default', () => {
      render(<Button>Primary</Button>);
      const btn = screen.getByRole('button', { name: 'Primary' });
      expect(btn.className).toContain('btn-primary');
    });

    it('should have primary-600 background color', () => {
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

  // AC-002: Secondary button uses transparent background
  describe('AC-002: Secondary variant', () => {
    it('should render secondary variant', () => {
      render(<Button variant="secondary">Secondary</Button>);
      const btn = screen.getByRole('button', { name: 'Secondary' });
      expect(btn.className).toContain('btn-secondary');
    });

    it('should have transparent background', () => {
      render(<Button variant="secondary">Secondary</Button>);
      const btn = screen.getByRole('button', { name: 'Secondary' });
      expect(btn.style.backgroundColor).toBe('transparent');
    });

    it('should have text-primary color', () => {
      render(<Button variant="secondary">Secondary</Button>);
      const btn = screen.getByRole('button', { name: 'Secondary' });
      expect(btn.style.color).toBe('var(--text-primary)');
    });
  });

  // AC-003: Ghost button uses transparent background, text-secondary
  describe('AC-003: Ghost variant', () => {
    it('should render ghost variant', () => {
      render(<Button variant="ghost">Ghost</Button>);
      const btn = screen.getByRole('button', { name: 'Ghost' });
      expect(btn.className).toContain('btn-ghost');
    });

    it('should have transparent background', () => {
      render(<Button variant="ghost">Ghost</Button>);
      const btn = screen.getByRole('button', { name: 'Ghost' });
      expect(btn.style.backgroundColor).toBe('transparent');
    });

    it('should have text-secondary color', () => {
      render(<Button variant="ghost">Ghost</Button>);
      const btn = screen.getByRole('button', { name: 'Ghost' });
      expect(btn.style.color).toBe('var(--text-secondary)');
    });
  });

  // AC-004: Destructive button uses error color background
  describe('AC-004: Destructive variant', () => {
    it('should render destructive variant', () => {
      render(<Button variant="destructive">Delete</Button>);
      const btn = screen.getByRole('button', { name: 'Delete' });
      expect(btn.className).toContain('btn-destructive');
    });

    it('should have error color background', () => {
      render(<Button variant="destructive">Delete</Button>);
      const btn = screen.getByRole('button', { name: 'Delete' });
      expect(btn.style.backgroundColor).toBe('var(--color-error)');
    });

    it('should have white text', () => {
      render(<Button variant="destructive">Delete</Button>);
      const btn = screen.getByRole('button', { name: 'Delete' });
      expect(btn.style.color).toBe('white');
    });
  });

  // AC-005: Accent button uses secondary-600 background
  describe('AC-005: Accent variant', () => {
    it('should render accent variant', () => {
      render(<Button variant="accent">Accent</Button>);
      const btn = screen.getByRole('button', { name: 'Accent' });
      expect(btn.className).toContain('btn-accent');
    });

    it('should have secondary-600 background', () => {
      render(<Button variant="accent">Accent</Button>);
      const btn = screen.getByRole('button', { name: 'Accent' });
      expect(btn.style.backgroundColor).toBe('var(--color-secondary-600)');
    });

    it('should have white text', () => {
      render(<Button variant="accent">Accent</Button>);
      const btn = screen.getByRole('button', { name: 'Accent' });
      expect(btn.style.color).toBe('white');
    });
  });

  // AC-006: All buttons use transition for hover effects (translateY)
  describe('AC-006: Hover transition support', () => {
    it('should have transition property on primary button', () => {
      render(<Button variant="primary">Primary</Button>);
      const btn = screen.getByRole('button', { name: 'Primary' });
      expect(btn.style.transition).toBeTruthy();
    });

    it('should have transition property on secondary button', () => {
      render(<Button variant="secondary">Secondary</Button>);
      const btn = screen.getByRole('button', { name: 'Secondary' });
      expect(btn.style.transition).toBeTruthy();
    });

    it('should have transition property on ghost button', () => {
      render(<Button variant="ghost">Ghost</Button>);
      const btn = screen.getByRole('button', { name: 'Ghost' });
      expect(btn.style.transition).toBeTruthy();
    });

    it('should have transition property on destructive button', () => {
      render(<Button variant="destructive">Destructive</Button>);
      const btn = screen.getByRole('button', { name: 'Destructive' });
      expect(btn.style.transition).toBeTruthy();
    });

    it('should have transition property on accent button', () => {
      render(<Button variant="accent">Accent</Button>);
      const btn = screen.getByRole('button', { name: 'Accent' });
      expect(btn.style.transition).toBeTruthy();
    });
  });

  // Disabled state for all variants
  describe('Disabled state', () => {
    it('should be disabled when disabled prop is true', () => {
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
