/**
 * Unit Tests for Tabs Component
 * T-004-007: REQ-004-004-002 - Tabs component styling
 * Verifies horizontal tabs with design token styling.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Tabs } from '../../../../src/components/ui/Tabs';

describe('Tabs Component', () => {
  describe('REQ-004-004-002: Tabs component styling', () => {
    const tabs = [
      { id: 'overview', label: 'Overview' },
      { id: 'details', label: 'Details' },
      { id: 'history', label: 'History' },
    ];

    it('should render all tab labels', () => {
      render(<Tabs tabs={tabs} activeTab="overview" onTabChange={() => {}} />);
      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Details')).toBeInTheDocument();
      expect(screen.getByText('History')).toBeInTheDocument();
    });

    it('AC-001: tab text should be text-sm, weight-medium', () => {
      render(<Tabs tabs={tabs} activeTab="overview" onTabChange={() => {}} />);
      const tab = screen.getByText('Overview');
      expect(tab.style.fontSize).toBe('0.875rem');
      expect(tab.style.fontWeight).toBe('500');
    });

    it('AC-002: active tab should have primary-400 text color', () => {
      render(<Tabs tabs={tabs} activeTab="overview" onTabChange={() => {}} />);
      const activeTab = screen.getByText('Overview');
      expect(activeTab.style.color).toBe('var(--color-primary-400)');
    });

    it('AC-002: active tab should have colored bottom border', () => {
      render(<Tabs tabs={tabs} activeTab="overview" onTabChange={() => {}} />);
      const activeTab = screen.getByText('Overview');
      expect(activeTab.style.borderBottomWidth).toBe('2px');
      expect(activeTab.style.borderBottomColor).toBe('var(--color-primary-400)');
    });

    it('AC-003: inactive tabs should show text-secondary', () => {
      render(<Tabs tabs={tabs} activeTab="overview" onTabChange={() => {}} />);
      const inactiveTab = screen.getByText('Details');
      expect(inactiveTab.style.color).toBe('var(--text-secondary)');
    });

    it('inactive tabs should have transparent bottom border', () => {
      render(<Tabs tabs={tabs} activeTab="overview" onTabChange={() => {}} />);
      const inactiveTab = screen.getByText('Details');
      expect(inactiveTab.style.borderBottomColor).toBe('transparent');
    });

    it('should call onTabChange when a tab is clicked', () => {
      const onTabChange = vi.fn();
      render(<Tabs tabs={tabs} activeTab="overview" onTabChange={onTabChange} />);
      screen.getByText('Details').click();
      expect(onTabChange).toHaveBeenCalledWith('details');
    });

    it('should render tab buttons with cursor pointer', () => {
      render(<Tabs tabs={tabs} activeTab="overview" onTabChange={() => {}} />);
      const tab = screen.getByText('Overview');
      expect(tab.style.cursor).toBe('pointer');
    });

    it('should have a container with bottom border', () => {
      render(<Tabs tabs={tabs} activeTab="overview" onTabChange={() => {}} />);
      const container = screen.getByRole('tablist');
      expect(container.style.borderBottomWidth).toBe('1px');
      expect(container.style.borderBottomColor).toBe('var(--border-secondary)');
    });
  });
});
