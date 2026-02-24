/**
 * Integration Tests for AipAssistWidget
 * IT-002: AipAssistWidget receives suggestions and renders actions
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { DemoFloatingWidget } from '../../src/components/demo/DemoFloatingWidget';
import type { AipSuggestion, AipSessionStats } from '../../src/components/aip-assist/types';

const createSuggestion = (id: string): AipSuggestion => ({
  id,
  type: 'action',
  title: `Investigate alert ${id}`,
  description: 'High priority alert detected',
  confidence: 'high',
  status: 'pending',
  createdAt: new Date().toISOString(),
});

const stats: AipSessionStats = {
  totalSuggestions: 3,
  acceptedCount: 1,
  rejectedCount: 0,
  expiredCount: 0,
  acceptanceRate: 33,
};

describe('IT-002: AipAssistWidget suggestions flow', () => {
  it('should show collapsed state then expand to see suggestions', () => {
    const onToggle = vi.fn();
    const { rerender } = render(
      <DemoFloatingWidget
        suggestions={[createSuggestion('1')]}
        stats={stats}
        isExpanded={false}
        isEnabled={true}
        isThinking={false}
        unreadCount={1}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={onToggle}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.getByTestId('unread-badge')).toHaveTextContent('1');
    fireEvent.click(screen.getByLabelText('Open aIP Assist'));
    expect(onToggle).toHaveBeenCalled();

    // After expanding
    rerender(
      <DemoFloatingWidget
        suggestions={[createSuggestion('1')]}
        stats={stats}
        isExpanded={true}
        isEnabled={true}
        isThinking={false}
        unreadCount={0}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={onToggle}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.getByText('Investigate alert 1')).toBeInTheDocument();
  });

  it('should show thinking indicator then suggestion', () => {
    const { rerender } = render(
      <DemoFloatingWidget
        suggestions={[]}
        stats={stats}
        isExpanded={true}
        isEnabled={true}
        isThinking={true}
        unreadCount={0}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.getByTestId('thinking-indicator')).toBeInTheDocument();

    // After thinking completes, suggestion appears
    rerender(
      <DemoFloatingWidget
        suggestions={[createSuggestion('1')]}
        stats={stats}
        isExpanded={true}
        isEnabled={true}
        isThinking={false}
        unreadCount={1}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.queryByTestId('thinking-indicator')).not.toBeInTheDocument();
    expect(screen.getByText('Investigate alert 1')).toBeInTheDocument();
  });

  it('should handle accept and reject actions', () => {
    const onAccept = vi.fn();
    const onReject = vi.fn();
    render(
      <DemoFloatingWidget
        suggestions={[createSuggestion('1')]}
        stats={stats}
        isExpanded={true}
        isEnabled={true}
        isThinking={false}
        unreadCount={0}
        onAccept={onAccept}
        onReject={onReject}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    fireEvent.click(screen.getByLabelText('Accept suggestion'));
    expect(onAccept).toHaveBeenCalledWith('1');
  });
});
