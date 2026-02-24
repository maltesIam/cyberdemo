/**
 * Tests for NarrationFooter Component
 * UT-013: Renders in layout footer area
 * UT-014: Messages display with timestamps in terminal format
 * UT-015: Color coding: info=white, warning=yellow, error=red, success=green
 * UT-016: Expand/collapse toggle
 * UT-017: Auto-scroll triggers when new message added
 * UT-018: Filter dropdown filters messages by type (NTH)
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { NarrationFooter } from '../../../src/components/demo/NarrationFooter';
import type { DemoNarrationMessage } from '../../../src/types/demo';

const createMessage = (id: string, type: DemoNarrationMessage['type'] = 'info'): DemoNarrationMessage => ({
  id,
  timestamp: '2026-02-24T10:30:00.000Z',
  type,
  content: `Test message ${id}`,
});

describe('UT-013: NarrationFooter renders in layout footer', () => {
  it('should render footer element', () => {
    render(
      <NarrationFooter
        messages={[]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByTestId('narration-footer')).toBeInTheDocument();
  });

  it('should have narration panel aria-label', () => {
    render(
      <NarrationFooter
        messages={[]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Narration panel')).toBeInTheDocument();
  });

  it('should show message count', () => {
    render(
      <NarrationFooter
        messages={[createMessage('1'), createMessage('2')]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByText('2 messages')).toBeInTheDocument();
  });
});

describe('UT-014: Messages with timestamps in terminal format', () => {
  it('should display messages in terminal style', () => {
    render(
      <NarrationFooter
        messages={[createMessage('1', 'info')]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByText('Test message 1')).toBeInTheDocument();
    expect(screen.getByText('[INFO]')).toBeInTheDocument();
  });

  it('should display >_narration terminal prompt', () => {
    render(
      <NarrationFooter
        messages={[]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByText('>_narration')).toBeInTheDocument();
  });

  it('should show waiting message when empty', () => {
    render(
      <NarrationFooter
        messages={[]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByText('Waiting for narration events...')).toBeInTheDocument();
  });
});

describe('UT-015: Color coding by type', () => {
  it('should render info messages with correct test id', () => {
    render(
      <NarrationFooter
        messages={[createMessage('1', 'info')]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByTestId('narration-msg-info')).toBeInTheDocument();
  });

  it('should render warning messages with [WARN] prefix', () => {
    render(
      <NarrationFooter
        messages={[createMessage('1', 'warning')]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByTestId('narration-msg-warning')).toBeInTheDocument();
    expect(screen.getByText('[WARN]')).toBeInTheDocument();
  });

  it('should render error messages with [ERR] prefix', () => {
    render(
      <NarrationFooter
        messages={[createMessage('1', 'error')]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByTestId('narration-msg-error')).toBeInTheDocument();
    expect(screen.getByText('[ERR]')).toBeInTheDocument();
  });

  it('should render success messages with [OK] prefix', () => {
    render(
      <NarrationFooter
        messages={[createMessage('1', 'success')]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByTestId('narration-msg-success')).toBeInTheDocument();
    expect(screen.getByText('[OK]')).toBeInTheDocument();
  });
});

describe('UT-016: Expand/collapse toggle', () => {
  it('should render expand/collapse button', () => {
    render(
      <NarrationFooter
        messages={[]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Collapse narration')).toBeInTheDocument();
  });

  it('should show expand label when collapsed', () => {
    render(
      <NarrationFooter
        messages={[]}
        isExpanded={false}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByLabelText('Expand narration')).toBeInTheDocument();
  });

  it('should call onToggleExpand when clicked', () => {
    const onToggle = vi.fn();
    render(
      <NarrationFooter
        messages={[]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={onToggle}
      />
    );
    fireEvent.click(screen.getByLabelText('Collapse narration'));
    expect(onToggle).toHaveBeenCalledTimes(1);
  });

  it('should not show messages when collapsed', () => {
    render(
      <NarrationFooter
        messages={[createMessage('1')]}
        isExpanded={false}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.queryByTestId('narration-messages')).not.toBeInTheDocument();
  });
});

describe('UT-017: Auto-scroll on new message', () => {
  it('should render messages container for auto-scroll', () => {
    render(
      <NarrationFooter
        messages={[createMessage('1'), createMessage('2'), createMessage('3')]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByTestId('narration-messages')).toBeInTheDocument();
  });
});

describe('UT-018: Filter by message type (NTH)', () => {
  it('should render filter dropdown when onFilterChange provided', () => {
    render(
      <NarrationFooter
        messages={[]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
        onFilterChange={vi.fn()}
      />
    );
    expect(screen.getByTestId('narration-filter')).toBeInTheDocument();
  });

  it('should filter messages by type', () => {
    const messages = [
      createMessage('1', 'info'),
      createMessage('2', 'warning'),
      createMessage('3', 'error'),
    ];
    render(
      <NarrationFooter
        messages={messages}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
        filterType="warning"
      />
    );
    expect(screen.getByText('Test message 2')).toBeInTheDocument();
    expect(screen.queryByText('Test message 1')).not.toBeInTheDocument();
    expect(screen.queryByText('Test message 3')).not.toBeInTheDocument();
  });
});
