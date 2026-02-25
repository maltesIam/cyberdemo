/**
 * Unit Tests for Toast Component (T-113)
 * Verifies toast: bg-elevated, border-primary, shadow-lg, 380px.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Toast } from '../../../../src/components/ui/Toast';

describe('Toast Component', () => {
  // T-113: REQ-007-005-002 - Toasts: bg-elevated, border-primary, shadow-lg, 380px
  describe('T-113: Toast styles', () => {
    it('should render toast with message', () => {
      render(<Toast message="Operation complete" />);
      expect(screen.getByText('Operation complete')).toBeInTheDocument();
    });

    it('should have bg-elevated background', () => {
      render(<Toast message="Toast" />);
      const toast = screen.getByRole('status');
      expect(toast.style.backgroundColor).toBe('var(--bg-elevated)');
    });

    it('should have border-primary border', () => {
      render(<Toast message="Toast" />);
      const toast = screen.getByRole('status');
      expect(toast.style.borderColor).toBe('var(--border-primary)');
    });

    it('should have shadow-lg box shadow', () => {
      render(<Toast message="Toast" />);
      const toast = screen.getByRole('status');
      expect(toast.style.boxShadow).toBe('var(--shadow-lg)');
    });

    it('should have max-width 380px', () => {
      render(<Toast message="Toast" />);
      const toast = screen.getByRole('status');
      expect(toast.style.maxWidth).toBe('380px');
    });

    it('should have role="status" for accessibility (T-123)', () => {
      render(<Toast message="Toast" />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });
  });
});
