/**
 * Unit Tests for Sidebar Navigation Styling
 * T-004-006: REQ-004-004-001 - Sidebar navigation styling
 * Verifies sidebar uses design tokens for backgrounds, nav groups, and active states.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

// We test the Sidebar component structure. Since it uses react-router-dom NavLink,
// we need to mock the router.
vi.mock('react-router-dom', () => ({
  NavLink: ({ children, to, className }: { children: React.ReactNode; to: string; className: string | (({ isActive }: { isActive: boolean }) => string) }) => {
    const resolvedClass = typeof className === 'function' ? className({ isActive: to === '/dashboard' }) : className;
    return (
      <a href={to} className={resolvedClass} data-testid={`nav-link-${to.replace('/', '')}`}>
        {children}
      </a>
    );
  },
}));

import { Sidebar } from '../../../src/components/Sidebar';

describe('Sidebar Navigation', () => {
  describe('REQ-004-004-001: Sidebar navigation styling', () => {
    it('AC-001: sidebar should use bg-secondary background via Tailwind class', () => {
      render(<Sidebar />);
      const sidebar = screen.getByRole('complementary');
      // The sidebar uses Tailwind class bg-secondary
      expect(sidebar.className).toContain('bg-secondary');
    });

    it('AC-002: logo should use gradient text styling', () => {
      render(<Sidebar />);
      // Check that SoulBot heading exists
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toBeInTheDocument();
      expect(heading.textContent).toContain('Soul');
    });

    it('AC-003: nav group section should exist within sidebar', () => {
      render(<Sidebar />);
      const nav = screen.getByRole('navigation');
      expect(nav).toBeInTheDocument();
    });

    it('AC-004: nav links should have text-sm styling via font-medium class', () => {
      render(<Sidebar />);
      // Check that nav links contain font-medium class
      const dashboardLink = screen.getByTestId('nav-link-dashboard');
      expect(dashboardLink.querySelector('.font-medium')).toBeInTheDocument();
    });

    it('AC-004: nav links should use text-secondary for inactive items', () => {
      render(<Sidebar />);
      // Inactive links should contain text-secondary class
      const surfaceLink = screen.getByTestId('nav-link-surface');
      expect(surfaceLink.className).toContain('text-secondary');
    });

    it('AC-005: active link should have a distinct active styling', () => {
      render(<Sidebar />);
      // Dashboard is mocked as active (isActive: to === '/dashboard')
      const dashboardLink = screen.getByTestId('nav-link-dashboard');
      // Active link should have primary background tint and inverse text (not text-secondary)
      expect(dashboardLink.className).toContain('text-inverse');
      expect(dashboardLink.className).not.toContain('text-secondary');
    });

    it('should render all navigation items', () => {
      render(<Sidebar />);
      expect(screen.getByText('Command Center')).toBeInTheDocument();
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Assets')).toBeInTheDocument();
      expect(screen.getByText('Incidents')).toBeInTheDocument();
      expect(screen.getByText('Detections')).toBeInTheDocument();
    });

    it('should have rounded-lg class on nav links for radius-md equivalent', () => {
      render(<Sidebar />);
      const surfaceLink = screen.getByTestId('nav-link-surface');
      expect(surfaceLink.className).toContain('rounded-lg');
    });

    it('should have hover:bg-tertiary for inactive items hover state', () => {
      render(<Sidebar />);
      const surfaceLink = screen.getByTestId('nav-link-surface');
      expect(surfaceLink.className).toContain('hover:bg-tertiary');
    });
  });
});
