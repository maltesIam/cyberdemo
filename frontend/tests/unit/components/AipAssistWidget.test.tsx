/**
 * Tests for AipAssistWidget (Floating wrapper)
 * UT-007: Fixed position bottom-right
 * UT-008: Collapsed state with badge
 * UT-009: Expanded panel with suggestions
 * UT-010: Action buttons per suggestion
 * UT-011: Thinking indicator
 * UT-012: Badge count for unread
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { DemoFloatingWidget } from '../../../src/components/demo/DemoFloatingWidget';
import type { AipSuggestion, AipSessionStats } from '../../../src/components/aip-assist/types';

const defaultStats: AipSessionStats = {
  totalSuggestions: 5,
  acceptedCount: 2,
  rejectedCount: 1,
  expiredCount: 0,
  acceptanceRate: 40,
};

const createSuggestion = (id: string, status: AipSuggestion['status'] = 'pending'): AipSuggestion => ({
  id,
  type: 'action',
  title: `Suggestion ${id}`,
  description: 'Test description',
  confidence: 'high',
  status,
  createdAt: new Date().toISOString(),
});

describe('UT-007: Floating widget bottom-right', () => {
  it('should render floating widget', () => {
    render(
      <DemoFloatingWidget
        suggestions={[]}
        stats={defaultStats}
        isExpanded={false}
        isEnabled={true}
        isThinking={false}
        unreadCount={0}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.getByTestId('aip-floating-widget')).toBeInTheDocument();
  });
});

describe('UT-008: Collapsed state with circular button and badge', () => {
  it('should render circular button when collapsed', () => {
    render(
      <DemoFloatingWidget
        suggestions={[]}
        stats={defaultStats}
        isExpanded={false}
        isEnabled={true}
        isThinking={false}
        unreadCount={0}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Open aIP Assist')).toBeInTheDocument();
  });

  it('should show badge with unread count when collapsed', () => {
    render(
      <DemoFloatingWidget
        suggestions={[]}
        stats={defaultStats}
        isExpanded={false}
        isEnabled={true}
        isThinking={false}
        unreadCount={3}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.getByTestId('unread-badge')).toHaveTextContent('3');
  });

  it('should call onToggleExpand when button clicked', () => {
    const onToggle = vi.fn();
    render(
      <DemoFloatingWidget
        suggestions={[]}
        stats={defaultStats}
        isExpanded={false}
        isEnabled={true}
        isThinking={false}
        unreadCount={0}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={onToggle}
        onToggleEnabled={vi.fn()}
      />
    );
    fireEvent.click(screen.getByLabelText('Open aIP Assist'));
    expect(onToggle).toHaveBeenCalledTimes(1);
  });
});

describe('UT-009: Expanded panel with suggestions', () => {
  it('should render full panel when expanded', () => {
    render(
      <DemoFloatingWidget
        suggestions={[createSuggestion('1')]}
        stats={defaultStats}
        isExpanded={true}
        isEnabled={true}
        isThinking={false}
        unreadCount={0}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.getByText('aIP Assist')).toBeInTheDocument();
  });

  it('should show suggestion items when expanded', () => {
    render(
      <DemoFloatingWidget
        suggestions={[createSuggestion('1'), createSuggestion('2')]}
        stats={defaultStats}
        isExpanded={true}
        isEnabled={true}
        isThinking={false}
        unreadCount={0}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.getByText('Suggestion 1')).toBeInTheDocument();
    expect(screen.getByText('Suggestion 2')).toBeInTheDocument();
  });
});

describe('UT-010: Action buttons per suggestion', () => {
  it('should render Accept and Reject buttons for each suggestion', () => {
    render(
      <DemoFloatingWidget
        suggestions={[createSuggestion('1')]}
        stats={defaultStats}
        isExpanded={true}
        isEnabled={true}
        isThinking={false}
        unreadCount={0}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Accept suggestion')).toBeInTheDocument();
    expect(screen.getByLabelText('Reject suggestion')).toBeInTheDocument();
  });
});

describe('UT-011: Thinking indicator', () => {
  it('should show thinking indicator when isThinking is true and expanded', () => {
    render(
      <DemoFloatingWidget
        suggestions={[]}
        stats={defaultStats}
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
    expect(screen.getByText('AI is thinking')).toBeInTheDocument();
  });

  it('should not show thinking indicator when isThinking is false', () => {
    render(
      <DemoFloatingWidget
        suggestions={[]}
        stats={defaultStats}
        isExpanded={true}
        isEnabled={true}
        isThinking={false}
        unreadCount={0}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.queryByTestId('thinking-indicator')).not.toBeInTheDocument();
  });
});

describe('UT-012: Badge count for unread', () => {
  it('should hide badge when unreadCount is 0', () => {
    render(
      <DemoFloatingWidget
        suggestions={[]}
        stats={defaultStats}
        isExpanded={false}
        isEnabled={true}
        isThinking={false}
        unreadCount={0}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.queryByTestId('unread-badge')).not.toBeInTheDocument();
  });

  it('should show 9+ for unreadCount > 9', () => {
    render(
      <DemoFloatingWidget
        suggestions={[]}
        stats={defaultStats}
        isExpanded={false}
        isEnabled={true}
        isThinking={false}
        unreadCount={15}
        onAccept={vi.fn()}
        onReject={vi.fn()}
        onToggleExpand={vi.fn()}
        onToggleEnabled={vi.fn()}
      />
    );
    expect(screen.getByTestId('unread-badge')).toHaveTextContent('9+');
  });
});
