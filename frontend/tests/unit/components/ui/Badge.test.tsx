/**
 * Unit Tests for Badge Component
 * T-004-009: REQ-004-006-001 - Badge variants
 * Verifies badge pill shape, text-xs, weight-medium, and all variant styles.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Badge } from '../../../../src/components/ui/Badge';

describe('Badge Component', () => {
  describe('REQ-004-006-001: Badge variants', () => {
    it('should render badge with text', () => {
      render(<Badge>Active</Badge>);
      expect(screen.getByText('Active')).toBeInTheDocument();
    });

    it('AC-001: should have pill shape with radius-full', () => {
      render(<Badge>Active</Badge>);
      const badge = screen.getByText('Active');
      expect(badge.style.borderRadius).toBe('var(--radius-full)');
    });

    it('AC-002: should have text-xs font size (0.75rem)', () => {
      render(<Badge>Active</Badge>);
      const badge = screen.getByText('Active');
      expect(badge.style.fontSize).toBe('0.75rem');
    });

    it('AC-002: should have weight-medium font weight (500)', () => {
      render(<Badge>Active</Badge>);
      const badge = screen.getByText('Active');
      expect(badge.style.fontWeight).toBe('500');
    });

    it('AC-002: should have 2px 8px padding', () => {
      render(<Badge>Active</Badge>);
      const badge = screen.getByText('Active');
      expect(badge.style.padding).toBe('2px 8px');
    });

    it('AC-003: default variant should have tertiary background', () => {
      render(<Badge variant="default">Default</Badge>);
      const badge = screen.getByText('Default');
      expect(badge.style.backgroundColor).toBe('var(--bg-tertiary)');
      expect(badge.className).toContain('badge-default');
    });

    it('AC-003: primary variant should have blue semi-transparent background', () => {
      render(<Badge variant="primary">Primary</Badge>);
      const badge = screen.getByText('Primary');
      expect(badge.style.backgroundColor).toBe('rgba(59, 130, 246, 0.15)');
      expect(badge.className).toContain('badge-primary');
    });

    it('AC-003: secondary variant should have cyan semi-transparent background', () => {
      render(<Badge variant="secondary">Secondary</Badge>);
      const badge = screen.getByText('Secondary');
      expect(badge.style.backgroundColor).toBe('rgba(6, 182, 212, 0.15)');
      expect(badge.className).toContain('badge-secondary');
    });

    it('AC-003: success variant should have green semi-transparent background', () => {
      render(<Badge variant="success">Success</Badge>);
      const badge = screen.getByText('Success');
      expect(badge.style.backgroundColor).toBe('rgba(34, 197, 94, 0.15)');
      expect(badge.className).toContain('badge-success');
    });

    it('AC-003: warning variant should have amber semi-transparent background', () => {
      render(<Badge variant="warning">Warning</Badge>);
      const badge = screen.getByText('Warning');
      expect(badge.style.backgroundColor).toBe('rgba(245, 158, 11, 0.15)');
      expect(badge.className).toContain('badge-warning');
    });

    it('AC-003: error variant should have red semi-transparent background', () => {
      render(<Badge variant="error">Error</Badge>);
      const badge = screen.getByText('Error');
      expect(badge.style.backgroundColor).toBe('rgba(239, 68, 68, 0.15)');
      expect(badge.className).toContain('badge-error');
    });

    it('should display as inline-flex for proper alignment', () => {
      render(<Badge>Tag</Badge>);
      const badge = screen.getByText('Tag');
      expect(badge.style.display).toBe('inline-flex');
    });

    it('should accept custom className', () => {
      render(<Badge className="custom">Custom</Badge>);
      const badge = screen.getByText('Custom');
      expect(badge.className).toContain('custom');
    });
  });
});
