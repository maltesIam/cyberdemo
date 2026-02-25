/**
 * Integration Tests: Specialized Components with Design Token Integration
 * Test ID: IT-008
 * Requirements: REQ-006-001-001
 *
 * Tests that specialized domain components integrate correctly
 * with the design token system.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import {
  AgentStatusBadge,
  type AgentStatus,
} from '../../src/components/ui/AgentStatusBadge';

beforeEach(() => {
  document.documentElement.removeAttribute('data-theme');
  localStorage.clear();
});

describe('IT-008: Specialized Components Integration', () => {
  describe('Agent Status Badge with Design Tokens', () => {
    it('should render all six statuses in a list context', () => {
      const statuses: AgentStatus[] = ['idle', 'running', 'success', 'error', 'waiting', 'queued'];

      render(
        <div data-testid="status-list">
          {statuses.map((status) => (
            <AgentStatusBadge key={status} status={status} label={`Agent-${status}`} />
          ))}
        </div>
      );

      const list = screen.getByTestId('status-list');
      expect(list.children.length).toBe(6);

      statuses.forEach((status) => {
        expect(screen.getByTestId(`agent-status-${status}`)).toBeTruthy();
        expect(screen.getByText(`Agent-${status}`)).toBeTruthy();
      });
    });

    it('should render badge dot elements for all statuses', () => {
      const statuses: AgentStatus[] = ['idle', 'running', 'success', 'error', 'waiting', 'queued'];

      statuses.forEach((status) => {
        const { unmount } = render(<AgentStatusBadge status={status} />);
        const dot = screen.getByTestId(`agent-status-${status}-dot`);
        expect(dot).toBeTruthy();
        unmount();
      });
    });

    it('should accept custom className for integration with parent layouts', () => {
      render(<AgentStatusBadge status="running" className="ml-2" />);
      const badge = screen.getByTestId('agent-status-running');
      expect(badge.className).toContain('ml-2');
    });
  });
});
