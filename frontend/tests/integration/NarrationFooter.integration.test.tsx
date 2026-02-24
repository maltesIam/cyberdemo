/**
 * Integration Tests for NarrationFooter
 * IT-003: NarrationFooter receives messages via WebSocket and renders stream
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { NarrationFooter } from '../../src/components/demo/NarrationFooter';
import type { DemoNarrationMessage } from '../../src/types/demo';

const createMsg = (id: string, type: DemoNarrationMessage['type'] = 'info'): DemoNarrationMessage => ({
  id,
  timestamp: new Date().toISOString(),
  type,
  content: `Narration message ${id}`,
});

describe('IT-003: NarrationFooter streaming integration', () => {
  it('should display messages as they arrive', () => {
    const { rerender } = render(
      <NarrationFooter messages={[]} isExpanded={true} isEnabled={true} onToggleExpand={vi.fn()} />
    );
    expect(screen.getByText('Waiting for narration events...')).toBeInTheDocument();

    // First message arrives
    rerender(
      <NarrationFooter
        messages={[createMsg('1', 'info')]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByText('Narration message 1')).toBeInTheDocument();
    expect(screen.getByText('1 message')).toBeInTheDocument();

    // More messages arrive
    rerender(
      <NarrationFooter
        messages={[createMsg('1', 'info'), createMsg('2', 'warning'), createMsg('3', 'error')]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={vi.fn()}
      />
    );
    expect(screen.getByText('3 messages')).toBeInTheDocument();
    expect(screen.getByText('[WARN]')).toBeInTheDocument();
    expect(screen.getByText('[ERR]')).toBeInTheDocument();
  });

  it('should toggle expand/collapse', () => {
    const onToggle = vi.fn();
    const { rerender } = render(
      <NarrationFooter
        messages={[createMsg('1')]}
        isExpanded={true}
        isEnabled={true}
        onToggleExpand={onToggle}
      />
    );
    expect(screen.getByTestId('narration-messages')).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText('Collapse narration'));
    expect(onToggle).toHaveBeenCalled();

    rerender(
      <NarrationFooter
        messages={[createMsg('1')]}
        isExpanded={false}
        isEnabled={true}
        onToggleExpand={onToggle}
      />
    );
    expect(screen.queryByTestId('narration-messages')).not.toBeInTheDocument();
  });
});
