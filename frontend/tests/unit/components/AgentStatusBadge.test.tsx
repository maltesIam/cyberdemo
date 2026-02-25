/**
 * Unit Tests: Agent Status Badge Component
 * Task: T-006-001
 * Requirement: REQ-006-001-001
 * Test ID: UT-046
 *
 * Acceptance Criteria:
 * - AC-001: Six status variants: idle (slate), running (blue), success (green), error (red), waiting (amber), queued (cyan)
 * - AC-002: Running and error dots have pulse animation (2s infinite)
 * - AC-003: Badge uses correct agent status color tokens
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import {
  AgentStatusBadge,
  type AgentStatus,
  AGENT_STATUS_CONFIG,
} from '../../../src/components/ui/AgentStatusBadge';

describe('T-006-001: Agent Status Badges (REQ-006-001-001)', () => {
  // AC-001: Six status variants with correct colors
  describe('AC-001: Status variants render correctly', () => {
    const statuses: AgentStatus[] = ['idle', 'running', 'success', 'error', 'waiting', 'queued'];

    it('should render all six status variants', () => {
      statuses.forEach((status) => {
        const { unmount } = render(<AgentStatusBadge status={status} />);
        const badge = screen.getByTestId(`agent-status-${status}`);
        expect(badge).toBeTruthy();
        unmount();
      });
    });

    it('should display idle status with slate color token', () => {
      render(<AgentStatusBadge status="idle" />);
      const badge = screen.getByTestId('agent-status-idle');
      expect(badge).toBeTruthy();
      expect(AGENT_STATUS_CONFIG.idle.color).toBe('var(--color-agent-idle)');
    });

    it('should display running status with blue color token', () => {
      render(<AgentStatusBadge status="running" />);
      const badge = screen.getByTestId('agent-status-running');
      expect(badge).toBeTruthy();
      expect(AGENT_STATUS_CONFIG.running.color).toBe('var(--color-agent-running)');
    });

    it('should display success status with green color token', () => {
      render(<AgentStatusBadge status="success" />);
      const badge = screen.getByTestId('agent-status-success');
      expect(badge).toBeTruthy();
      expect(AGENT_STATUS_CONFIG.success.color).toBe('var(--color-agent-success)');
    });

    it('should display error status with red color token', () => {
      render(<AgentStatusBadge status="error" />);
      const badge = screen.getByTestId('agent-status-error');
      expect(badge).toBeTruthy();
      expect(AGENT_STATUS_CONFIG.error.color).toBe('var(--color-agent-error)');
    });

    it('should display waiting status with amber color token', () => {
      render(<AgentStatusBadge status="waiting" />);
      const badge = screen.getByTestId('agent-status-waiting');
      expect(badge).toBeTruthy();
      expect(AGENT_STATUS_CONFIG.waiting.color).toBe('var(--color-agent-waiting)');
    });

    it('should display queued status with cyan color token', () => {
      render(<AgentStatusBadge status="queued" />);
      const badge = screen.getByTestId('agent-status-queued');
      expect(badge).toBeTruthy();
      expect(AGENT_STATUS_CONFIG.queued.color).toBe('var(--color-agent-queued)');
    });
  });

  // AC-002: Running and error dots have pulse animation
  describe('AC-002: Pulse animation on running and error statuses', () => {
    it('should have pulse animation on running status dot', () => {
      render(<AgentStatusBadge status="running" />);
      const dot = screen.getByTestId('agent-status-running-dot');
      expect(dot).toBeTruthy();
      expect(AGENT_STATUS_CONFIG.running.pulse).toBe(true);
    });

    it('should have pulse animation on error status dot', () => {
      render(<AgentStatusBadge status="error" />);
      const dot = screen.getByTestId('agent-status-error-dot');
      expect(dot).toBeTruthy();
      expect(AGENT_STATUS_CONFIG.error.pulse).toBe(true);
    });

    it('should NOT have pulse animation on idle status', () => {
      render(<AgentStatusBadge status="idle" />);
      expect(AGENT_STATUS_CONFIG.idle.pulse).toBe(false);
    });

    it('should NOT have pulse animation on success status', () => {
      render(<AgentStatusBadge status="success" />);
      expect(AGENT_STATUS_CONFIG.success.pulse).toBe(false);
    });

    it('should NOT have pulse animation on waiting status', () => {
      render(<AgentStatusBadge status="waiting" />);
      expect(AGENT_STATUS_CONFIG.waiting.pulse).toBe(false);
    });

    it('should NOT have pulse animation on queued status', () => {
      render(<AgentStatusBadge status="queued" />);
      expect(AGENT_STATUS_CONFIG.queued.pulse).toBe(false);
    });
  });

  // AC-003: Badge uses correct agent status color tokens
  describe('AC-003: Color tokens are used correctly', () => {
    it('should map all status colors to CSS variable tokens', () => {
      const expectedTokens: Record<AgentStatus, string> = {
        idle: 'var(--color-agent-idle)',
        running: 'var(--color-agent-running)',
        success: 'var(--color-agent-success)',
        error: 'var(--color-agent-error)',
        waiting: 'var(--color-agent-waiting)',
        queued: 'var(--color-agent-queued)',
      };

      for (const [status, expectedColor] of Object.entries(expectedTokens)) {
        expect(AGENT_STATUS_CONFIG[status as AgentStatus].color).toBe(expectedColor);
      }
    });

    it('should render status label text', () => {
      render(<AgentStatusBadge status="running" label="Agent-1" />);
      expect(screen.getByText('Agent-1')).toBeTruthy();
    });

    it('should render default label when no label prop given', () => {
      render(<AgentStatusBadge status="success" />);
      const badge = screen.getByTestId('agent-status-success');
      // Badge should show the status name if no label given
      expect(badge.textContent).toContain('success');
    });
  });

  // Additional: Accessibility
  describe('Accessibility', () => {
    it('should have an aria-label indicating the status', () => {
      render(<AgentStatusBadge status="running" label="Agent-1" />);
      const badge = screen.getByTestId('agent-status-running');
      expect(badge.getAttribute('aria-label')).toContain('running');
    });
  });
});
