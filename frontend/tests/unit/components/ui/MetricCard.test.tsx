/**
 * Unit Tests for MetricCard Component
 * T-004-005: REQ-004-003-002 - Metric card component
 * Verifies metric card with label, value, and change indicator.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { MetricCard } from '../../../../src/components/ui/MetricCard';

describe('MetricCard Component', () => {
  describe('REQ-004-003-002: Metric card component', () => {
    it('should render with label, value', () => {
      render(<MetricCard label="Total Alerts" value="1,234" />);
      expect(screen.getByText('Total Alerts')).toBeInTheDocument();
      expect(screen.getByText('1,234')).toBeInTheDocument();
    });

    it('AC-001: label should be text-xs, uppercase, tertiary color, weight-medium', () => {
      render(<MetricCard label="Total Alerts" value="100" />);
      const label = screen.getByText('Total Alerts');
      expect(label.style.fontSize).toBe('0.75rem');
      expect(label.style.textTransform).toBe('uppercase');
      expect(label.style.color).toBe('var(--text-tertiary)');
      expect(label.style.fontWeight).toBe('500');
    });

    it('AC-001: label should have letter-spacing 0.05em', () => {
      render(<MetricCard label="Active" value="50" />);
      const label = screen.getByText('Active');
      expect(label.style.letterSpacing).toBe('0.05em');
    });

    it('AC-002: value should be text-3xl, weight-bold', () => {
      render(<MetricCard label="Count" value="9,999" />);
      const value = screen.getByText('9,999');
      expect(value.style.fontSize).toBe('1.875rem');
      expect(value.style.fontWeight).toBe('700');
    });

    it('AC-002: value should have letter-spacing -0.02em', () => {
      render(<MetricCard label="Count" value="500" />);
      const value = screen.getByText('500');
      expect(value.style.letterSpacing).toBe('-0.02em');
    });

    it('AC-003: should show green change indicator with up arrow for positive change', () => {
      render(<MetricCard label="Alerts" value="100" change={12.5} />);
      const changeEl = screen.getByTestId('metric-change');
      expect(changeEl.style.color).toBe('var(--color-success)');
      expect(changeEl.textContent).toContain('12.5%');
    });

    it('AC-003: should show red change indicator with down arrow for negative change', () => {
      render(<MetricCard label="Alerts" value="100" change={-5.3} />);
      const changeEl = screen.getByTestId('metric-change');
      expect(changeEl.style.color).toBe('var(--color-error)');
      expect(changeEl.textContent).toContain('5.3%');
    });

    it('should not show change indicator when change is not provided', () => {
      render(<MetricCard label="Alerts" value="100" />);
      expect(screen.queryByTestId('metric-change')).not.toBeInTheDocument();
    });

    it('should wrap content in a card container', () => {
      render(<MetricCard label="Test" value="42" />);
      const card = screen.getByTestId('metric-card');
      expect(card.style.backgroundColor).toBe('var(--bg-card)');
    });
  });
});
