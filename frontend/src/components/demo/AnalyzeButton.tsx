/**
 * AnalyzeButton Component
 *
 * Button for each incident row in the Incidents table that triggers
 * AI analysis. Has 3 states: initial, processing, completed.
 *
 * Requirements:
 * - REQ-002-002-001: Button in Incidents table row
 * - REQ-002-002-002: 3-state button
 * - REQ-002-002-003: Auto-expand narration on click
 * - REQ-002-002-004: Async analysis queue
 * - REQ-002-002-005: Persist result to incident
 * - REQ-002-002-006: Parallel analysis support (NTH)
 */

import { useCallback } from 'react';
import type { AnalysisDecision } from '../../types/demo';

export type AnalyzeButtonStatus = 'idle' | 'processing' | 'completed';

export interface AnalyzeButtonProps {
  incidentId: string;
  status: AnalyzeButtonStatus;
  decision?: AnalysisDecision;
  onAnalyze: (incidentId: string) => void;
  onExpandNarration?: () => void;
}

/** Robot icon for initial state */
const RobotIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
    />
  </svg>
);

/** Decision icons */
const DECISION_ICONS: Record<AnalysisDecision, string> = {
  contain: '🛡️',
  escalate: '⬆️',
  dismiss: '❌',
  monitor: '👁️',
};

const DECISION_LABELS: Record<AnalysisDecision, string> = {
  contain: 'Contained',
  escalate: 'Escalated',
  dismiss: 'Dismissed',
  monitor: 'Monitoring',
};

export function AnalyzeButton({
  incidentId,
  status,
  decision,
  onAnalyze,
  onExpandNarration,
}: AnalyzeButtonProps) {
  const handleClick = useCallback(() => {
    if (status !== 'idle') return;
    onExpandNarration?.();
    onAnalyze(incidentId);
  }, [status, incidentId, onAnalyze, onExpandNarration]);

  // Completed state with decision icon
  if (status === 'completed' && decision) {
    return (
      <button
        type="button"
        data-testid="analyze-button"
        aria-label={`Analysis complete: ${DECISION_LABELS[decision]}`}
        disabled
        className="flex items-center gap-1.5 px-3 py-1.5 bg-tertiary text-secondary text-sm rounded-lg cursor-default"
      >
        <span>{DECISION_ICONS[decision]}</span>
        <span>{DECISION_LABELS[decision]}</span>
      </button>
    );
  }

  // Processing state
  if (status === 'processing') {
    return (
      <button
        type="button"
        data-testid="analyze-button"
        aria-label="Analysis in progress"
        disabled
        className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-900/30 text-cyan-400 text-sm rounded-lg cursor-not-allowed"
      >
        <div className="animate-spin w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full" />
        <span>Analyzing...</span>
      </button>
    );
  }

  // Initial state
  return (
    <button
      type="button"
      data-testid="analyze-button"
      aria-label="Analyze with AI"
      onClick={handleClick}
      className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-700 text-primary text-sm rounded-lg transition-colors"
    >
      <RobotIcon />
      <span>Analyze with AI</span>
    </button>
  );
}
