/**
 * Tests for DemoCasesPanel Component
 * UT-019: Renders on Dashboard
 * UT-020: 3 case cards with metadata
 * UT-021: Invoke agent on click
 * UT-022: Loading state with spinner
 * UT-023: Result display matches expected
 * UT-024: Approval card for Case 2
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DemoCasesPanel, DEMO_CASES } from '../../../src/components/demo/DemoCasesPanel';

describe('UT-019: DemoCasesPanel renders on Dashboard', () => {
  it('should render the panel', () => {
    render(<DemoCasesPanel onExecuteCase={vi.fn().mockResolvedValue({ result: 'ok' })} />);
    expect(screen.getByTestId('demo-cases-panel')).toBeInTheDocument();
  });

  it('should have Demo Cases title', () => {
    render(<DemoCasesPanel onExecuteCase={vi.fn().mockResolvedValue({ result: 'ok' })} />);
    expect(screen.getByText('Demo Cases')).toBeInTheDocument();
  });
});

describe('UT-020: 3 case cards with metadata', () => {
  it('should render 3 case cards', () => {
    render(<DemoCasesPanel onExecuteCase={vi.fn().mockResolvedValue({ result: 'ok' })} />);
    expect(screen.getByTestId('case-card-CASE-001')).toBeInTheDocument();
    expect(screen.getByTestId('case-card-CASE-002')).toBeInTheDocument();
    expect(screen.getByTestId('case-card-CASE-003')).toBeInTheDocument();
  });

  it('should display case names', () => {
    render(<DemoCasesPanel onExecuteCase={vi.fn().mockResolvedValue({ result: 'ok' })} />);
    expect(screen.getByText('Malware Auto-Containment')).toBeInTheDocument();
    expect(screen.getByText('VIP Threat Response')).toBeInTheDocument();
    expect(screen.getByText('False Positive Detection')).toBeInTheDocument();
  });

  it('should display host info', () => {
    render(<DemoCasesPanel onExecuteCase={vi.fn().mockResolvedValue({ result: 'ok' })} />);
    expect(screen.getByText('WS-FIN-042')).toBeInTheDocument();
    expect(screen.getByText('LAPTOP-CFO-01')).toBeInTheDocument();
    expect(screen.getByText('SRV-DEV-03')).toBeInTheDocument();
  });

  it('should display expected results', () => {
    render(<DemoCasesPanel onExecuteCase={vi.fn().mockResolvedValue({ result: 'ok' })} />);
    expect(screen.getByText('Auto-containment')).toBeInTheDocument();
    expect(screen.getByText('Approval required')).toBeInTheDocument();
    expect(screen.getByText('False positive')).toBeInTheDocument();
  });
});

describe('UT-021: Invoke agent on click', () => {
  it('should call onExecuteCase when card clicked', async () => {
    const onExecute = vi.fn().mockResolvedValue({ result: 'Auto-containment' });
    render(<DemoCasesPanel onExecuteCase={onExecute} />);
    fireEvent.click(screen.getByTestId('case-card-CASE-001'));
    await waitFor(() => expect(onExecute).toHaveBeenCalledWith('CASE-001'));
  });
});

describe('UT-022: Loading state with spinner', () => {
  it('should show spinner during execution', async () => {
    const promise = new Promise<{ result: string }>(() => {}); // Never resolves
    const onExecute = vi.fn().mockReturnValue(promise);
    render(<DemoCasesPanel onExecuteCase={onExecute} />);
    fireEvent.click(screen.getByTestId('case-card-CASE-001'));
    await waitFor(() => expect(screen.getByTestId('case-spinner')).toBeInTheDocument());
  });
});

describe('UT-023: Result display matches expected', () => {
  it('should display result after completion', async () => {
    const onExecute = vi.fn().mockResolvedValue({ result: 'Auto-containment' });
    render(<DemoCasesPanel onExecuteCase={onExecute} />);
    fireEvent.click(screen.getByTestId('case-card-CASE-001'));
    await waitFor(() => expect(screen.getByText('Result: Auto-containment')).toBeInTheDocument());
  });
});

describe('UT-024: Approval card for Case 2', () => {
  it('should show approval card when requiresApproval is true', async () => {
    const onExecute = vi.fn().mockResolvedValue({ result: 'Approval required', requiresApproval: true });
    const onApprove = vi.fn();
    const onReject = vi.fn();
    render(
      <DemoCasesPanel
        onExecuteCase={onExecute}
        onApprove={onApprove}
        onReject={onReject}
      />
    );
    fireEvent.click(screen.getByTestId('case-card-CASE-002'));
    await waitFor(() => expect(screen.getByTestId('approval-card')).toBeInTheDocument());
    expect(screen.getByLabelText('Approve containment')).toBeInTheDocument();
    expect(screen.getByLabelText('Reject containment')).toBeInTheDocument();
  });

  it('should call onApprove when approve clicked', async () => {
    const onExecute = vi.fn().mockResolvedValue({ result: 'Approval required', requiresApproval: true });
    const onApprove = vi.fn();
    render(
      <DemoCasesPanel
        onExecuteCase={onExecute}
        onApprove={onApprove}
      />
    );
    fireEvent.click(screen.getByTestId('case-card-CASE-002'));
    await waitFor(() => screen.getByLabelText('Approve containment'));
    fireEvent.click(screen.getByLabelText('Approve containment'));
    expect(onApprove).toHaveBeenCalledWith('CASE-002');
  });
});
