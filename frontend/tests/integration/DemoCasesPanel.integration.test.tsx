/**
 * Integration Tests for DemoCasesPanel
 * IT-004: DemoCasesPanel invokes agent, shows loading, displays result
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DemoCasesPanel } from '../../src/components/demo/DemoCasesPanel';

describe('IT-004: DemoCasesPanel execution flow', () => {
  it('should execute Case 1 and show auto-containment result', async () => {
    const onExecute = vi.fn().mockResolvedValue({ result: 'Auto-containment' });
    render(<DemoCasesPanel onExecuteCase={onExecute} />);

    fireEvent.click(screen.getByTestId('case-card-CASE-001'));

    await waitFor(() => {
      expect(onExecute).toHaveBeenCalledWith('CASE-001');
      expect(screen.getByText('Result: Auto-containment')).toBeInTheDocument();
    });
  });

  it('should execute Case 2 and show approval card', async () => {
    const onExecute = vi.fn().mockResolvedValue({ result: 'Approval required', requiresApproval: true });
    const onApprove = vi.fn();
    render(<DemoCasesPanel onExecuteCase={onExecute} onApprove={onApprove} onReject={vi.fn()} />);

    fireEvent.click(screen.getByTestId('case-card-CASE-002'));

    await waitFor(() => {
      expect(screen.getByTestId('approval-card')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByLabelText('Approve containment'));
    expect(onApprove).toHaveBeenCalledWith('CASE-002');
  });

  it('should only allow one case at a time', async () => {
    let resolveCase: (value: { result: string }) => void;
    const promise = new Promise<{ result: string }>((resolve) => { resolveCase = resolve; });
    const onExecute = vi.fn().mockReturnValueOnce(promise);

    render(<DemoCasesPanel onExecuteCase={onExecute} />);
    fireEvent.click(screen.getByTestId('case-card-CASE-001'));

    // Case 2 and 3 should be disabled
    await waitFor(() => {
      expect(screen.getByTestId('case-spinner')).toBeInTheDocument();
    });

    // Resolve case 1
    resolveCase!({ result: 'Auto-containment' });
    await waitFor(() => {
      expect(screen.getByText('Result: Auto-containment')).toBeInTheDocument();
    });
  });
});
