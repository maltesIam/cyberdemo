/**
 * Unit Tests for Card Component
 * T-004-004: REQ-004-003-001 - Base card styling
 * Verifies card base and interactive variants per AgentFlow Design System spec.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Card } from '../../../../src/components/ui/Card';

describe('Card Component', () => {
  // T-004-004: REQ-004-003-001 - Base Card Styling
  describe('REQ-004-003-001: Base card styling', () => {
    it('AC-001: should render card with content', () => {
      render(<Card>Card content</Card>);
      expect(screen.getByText('Card content')).toBeInTheDocument();
    });

    it('AC-001: should have bg-card background', () => {
      render(<Card>Card</Card>);
      const card = screen.getByText('Card').closest('[data-component="card"]');
      expect(card?.style.backgroundColor).toBe('var(--bg-card)');
    });

    it('AC-002: should have border-secondary border color with 1px width', () => {
      render(<Card>Card</Card>);
      const card = screen.getByText('Card').closest('[data-component="card"]');
      expect(card?.style.borderColor).toBe('var(--border-secondary)');
      expect(card?.style.borderWidth).toBe('1px');
    });

    it('AC-003: should have radius-xl border radius', () => {
      render(<Card>Card</Card>);
      const card = screen.getByText('Card').closest('[data-component="card"]');
      expect(card?.style.borderRadius).toBe('var(--radius-xl)');
    });

    it('AC-003: should have space-6 padding', () => {
      render(<Card>Card</Card>);
      const card = screen.getByText('Card').closest('[data-component="card"]');
      expect(card?.style.padding).toBe('var(--spacing-6)');
    });

    it('AC-004: interactive card should have card-interactive class', () => {
      render(<Card interactive>Interactive</Card>);
      const card = screen.getByText('Interactive').closest('[data-component="card"]');
      expect(card?.className).toContain('card-interactive');
    });

    it('AC-004: interactive card should have cursor pointer', () => {
      render(<Card interactive>Interactive</Card>);
      const card = screen.getByText('Interactive').closest('[data-component="card"]');
      expect(card?.style.cursor).toBe('pointer');
    });

    it('should have transition for smooth hover effects', () => {
      render(<Card>Card</Card>);
      const card = screen.getByText('Card').closest('[data-component="card"]');
      expect(card?.style.transition).toContain('var(--duration-normal)');
    });

    it('should accept custom className', () => {
      render(<Card className="custom-class">Card</Card>);
      const card = screen.getByText('Card').closest('[data-component="card"]');
      expect(card?.className).toContain('custom-class');
    });

    it('should accept custom style prop', () => {
      render(<Card style={{ maxWidth: '300px' }}>Card</Card>);
      const card = screen.getByText('Card').closest('[data-component="card"]');
      expect(card?.style.maxWidth).toBe('300px');
    });

    it('should accept onClick handler for interactive cards', () => {
      let clicked = false;
      render(<Card interactive onClick={() => { clicked = true; }}>Click me</Card>);
      const card = screen.getByText('Click me').closest('[data-component="card"]');
      card?.click();
      expect(clicked).toBe(true);
    });
  });
});
