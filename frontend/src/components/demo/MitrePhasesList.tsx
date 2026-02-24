/**
 * MitrePhasesList Component
 *
 * Vertical list of MITRE ATT&CK phases with status indicators.
 * Used in the left column of the Simulation page.
 *
 * Requirements:
 * - REQ-003-001-003: MITRE phases left column with status indicators
 */

import type { MitreStage } from './types';

export interface MitrePhasesListProps {
  stages: MitreStage[];
  currentStage: number;
}

/** Status indicator for each phase */
const PhaseStatus = ({ stage }: { stage: MitreStage }) => {
  if (stage.completed) {
    return (
      <div data-testid={`phase-status-completed`} className="w-3 h-3 bg-green-500 rounded-full" />
    );
  }
  if (stage.active) {
    return (
      <div data-testid={`phase-status-active`} className="w-3 h-3 bg-cyan-500 rounded-full animate-pulse" />
    );
  }
  return (
    <div data-testid={`phase-status-pending`} className="w-3 h-3 bg-gray-600 rounded-full" />
  );
};

export function MitrePhasesList({ stages, currentStage }: MitrePhasesListProps) {
  return (
    <div data-testid="mitre-phases-list" className="space-y-1">
      <h3 className="text-sm font-semibold text-gray-200 mb-3">MITRE ATT&CK Phases</h3>
      {stages.length === 0 ? (
        <p className="text-xs text-gray-500">Select a scenario to view phases</p>
      ) : (
        <ul className="space-y-1">
          {stages.map((stage, index) => (
            <li
              key={stage.tacticId}
              data-testid={`phase-item-${index}`}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                stage.active
                  ? 'bg-cyan-900/20 border border-cyan-700'
                  : stage.completed
                  ? 'bg-green-900/10 border border-transparent'
                  : 'border border-transparent'
              }`}
            >
              {/* Step number */}
              <span className="text-xs text-gray-500 w-4 text-right">{index + 1}</span>

              {/* Status indicator */}
              <PhaseStatus stage={stage} />

              {/* Phase info */}
              <div className="flex-1 min-w-0">
                <div className={`text-sm font-medium truncate ${
                  stage.active ? 'text-cyan-300' : stage.completed ? 'text-gray-300' : 'text-gray-500'
                }`}>
                  {stage.tacticName}
                </div>
                <div className="text-xs text-gray-500 truncate">{stage.tacticId}</div>
              </div>

              {/* Technique count */}
              {stage.techniqueIds.length > 0 && (
                <span className="text-xs text-gray-600">
                  {stage.techniqueIds.length} tech
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
