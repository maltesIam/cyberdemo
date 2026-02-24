/**
 * DemoCasesPanel Component
 *
 * Panel displaying 3 predefined demo case cards on the Dashboard.
 * Each card shows case name, host, type, expected result, and invokes
 * an agent on click.
 *
 * Requirements:
 * - REQ-002-001-001: Panel on Dashboard
 * - REQ-002-001-002: 3 case cards with metadata
 * - REQ-002-001-003: Invoke agent on click
 * - REQ-002-001-004: Loading state during execution
 * - REQ-002-001-005: Deterministic result display
 * - REQ-002-001-006: Approval card for Case 2
 */

import { useState, useCallback } from 'react';

/** Demo case definition */
export interface DemoCase {
  id: string;
  name: string;
  host: string;
  type: string;
  expectedResult: string;
  icon: string;
  requiresApproval?: boolean;
}

/** Demo case execution state */
export type CaseExecutionStatus = 'idle' | 'loading' | 'completed' | 'approval_required';

export interface CaseExecutionState {
  status: CaseExecutionStatus;
  result?: string;
  error?: string;
}

/** Predefined demo cases */
export const DEMO_CASES: DemoCase[] = [
  {
    id: 'CASE-001',
    name: 'Malware Auto-Containment',
    host: 'WS-FIN-042',
    type: 'Malware on standard workstation',
    expectedResult: 'Auto-containment',
    icon: '🛡️',
  },
  {
    id: 'CASE-002',
    name: 'VIP Threat Response',
    host: 'LAPTOP-CFO-01',
    type: 'Malware on VIP laptop',
    expectedResult: 'Approval required',
    icon: '👤',
    requiresApproval: true,
  },
  {
    id: 'CASE-003',
    name: 'False Positive Detection',
    host: 'SRV-DEV-03',
    type: 'Suspicious activity on dev server',
    expectedResult: 'False positive',
    icon: '🔍',
  },
];

export interface DemoCasesPanelProps {
  onExecuteCase: (caseId: string) => Promise<{ result: string; requiresApproval?: boolean }>;
  onApprove?: (caseId: string) => void;
  onReject?: (caseId: string) => void;
}

/** Loading spinner */
const Spinner = () => (
  <div data-testid="case-spinner" className="animate-spin w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full" />
);

/** Result icon based on outcome */
const ResultIcon = ({ result }: { result: string }) => {
  const icons: Record<string, string> = {
    'Auto-containment': '✅',
    'Approval required': '⚠️',
    'False positive': '🟢',
  };
  return <span className="text-lg">{icons[result] ?? '📋'}</span>;
};

/** Approval Card for Case 2 */
const ApprovalCard = ({
  caseId,
  onApprove,
  onReject,
}: {
  caseId: string;
  onApprove: () => void;
  onReject: () => void;
}) => (
  <div data-testid="approval-card" className="mt-3 p-3 bg-yellow-900/30 border border-yellow-700 rounded-lg">
    <p className="text-sm text-yellow-200 mb-2">VIP asset requires human approval</p>
    <div className="flex gap-2">
      <button
        type="button"
        aria-label="Approve containment"
        onClick={onApprove}
        className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
      >
        Approve
      </button>
      <button
        type="button"
        aria-label="Reject containment"
        onClick={onReject}
        className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
      >
        Reject
      </button>
    </div>
  </div>
);

export function DemoCasesPanel({ onExecuteCase, onApprove, onReject }: DemoCasesPanelProps) {
  const [execStates, setExecStates] = useState<Record<string, CaseExecutionState>>({});
  const [activeCase, setActiveCase] = useState<string | null>(null);

  const handleExecute = useCallback(
    async (demoCase: DemoCase) => {
      if (activeCase) return; // Only one case at a time (BR-004-01)

      setActiveCase(demoCase.id);
      setExecStates((prev) => ({
        ...prev,
        [demoCase.id]: { status: 'loading' },
      }));

      try {
        const { result, requiresApproval } = await onExecuteCase(demoCase.id);
        setExecStates((prev) => ({
          ...prev,
          [demoCase.id]: {
            status: requiresApproval ? 'approval_required' : 'completed',
            result,
          },
        }));
        if (!requiresApproval) {
          setActiveCase(null);
        }
      } catch (err) {
        setExecStates((prev) => ({
          ...prev,
          [demoCase.id]: {
            status: 'completed',
            error: err instanceof Error ? err.message : 'Execution failed',
          },
        }));
        setActiveCase(null);
      }
    },
    [activeCase, onExecuteCase]
  );

  const handleApprove = useCallback(
    (caseId: string) => {
      onApprove?.(caseId);
      setExecStates((prev) => ({
        ...prev,
        [caseId]: { ...prev[caseId], status: 'completed' },
      }));
      setActiveCase(null);
    },
    [onApprove]
  );

  const handleReject = useCallback(
    (caseId: string) => {
      onReject?.(caseId);
      setExecStates((prev) => ({
        ...prev,
        [caseId]: { ...prev[caseId], status: 'completed', result: 'Rejected' },
      }));
      setActiveCase(null);
    },
    [onReject]
  );

  return (
    <div data-testid="demo-cases-panel" className="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-200 mb-3">Demo Cases</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {DEMO_CASES.map((demoCase) => {
          const execState = execStates[demoCase.id] ?? { status: 'idle' };
          const isLoading = execState.status === 'loading';
          const isCompleted = execState.status === 'completed';
          const needsApproval = execState.status === 'approval_required';
          const isDisabled = activeCase !== null && activeCase !== demoCase.id;

          return (
            <div
              key={demoCase.id}
              data-testid={`case-card-${demoCase.id}`}
              className={`p-3 rounded-lg border transition-all ${
                isLoading
                  ? 'border-cyan-500 bg-cyan-900/10'
                  : isCompleted
                  ? 'border-green-500/50 bg-green-900/10'
                  : needsApproval
                  ? 'border-yellow-500 bg-yellow-900/10'
                  : 'border-gray-600 hover:border-gray-500 cursor-pointer'
              } ${isDisabled ? 'opacity-50 pointer-events-none' : ''}`}
              onClick={() => execState.status === 'idle' && !isDisabled && handleExecute(demoCase)}
              role="button"
              tabIndex={0}
              aria-label={`Execute ${demoCase.name}`}
              onKeyDown={(e) => {
                if ((e.key === 'Enter' || e.key === ' ') && execState.status === 'idle' && !isDisabled) {
                  e.preventDefault();
                  handleExecute(demoCase);
                }
              }}
            >
              {/* Card header */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-lg">{demoCase.icon}</span>
                {isLoading && <Spinner />}
                {isCompleted && <ResultIcon result={execState.result ?? ''} />}
              </div>

              {/* Card metadata */}
              <h4 className="text-sm font-medium text-gray-200">{demoCase.name}</h4>
              <div className="mt-1 space-y-0.5">
                <p className="text-xs text-gray-400">
                  <span className="text-gray-500">Host:</span> {demoCase.host}
                </p>
                <p className="text-xs text-gray-400">
                  <span className="text-gray-500">Type:</span> {demoCase.type}
                </p>
                <p className="text-xs text-gray-400">
                  <span className="text-gray-500">Expected:</span>{' '}
                  <span className="text-cyan-400">{demoCase.expectedResult}</span>
                </p>
              </div>

              {/* Result display */}
              {isCompleted && execState.result && (
                <div className="mt-2 px-2 py-1 bg-gray-700/50 rounded text-xs text-gray-200">
                  Result: {execState.result}
                </div>
              )}

              {/* Error display */}
              {execState.error && (
                <div className="mt-2 px-2 py-1 bg-red-900/30 rounded text-xs text-red-400">
                  {execState.error}
                </div>
              )}

              {/* Approval card for Case 2 */}
              {needsApproval && (
                <ApprovalCard
                  caseId={demoCase.id}
                  onApprove={() => handleApprove(demoCase.id)}
                  onReject={() => handleReject(demoCase.id)}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
