/**
 * AttackChainVisualization Component
 *
 * Displays a MITRE ATT&CK attack chain visualization showing
 * the progression of attack stages during a simulation.
 *
 * Requirement: REQ-002-003-004 - Attack chain visualization
 * Test ID: UT-071
 */

import { useMemo } from "react";

/**
 * Represents a single stage in the attack chain
 */
export interface AttackStage {
  stage: number;
  tactic_id: string;
  tactic_name: string;
  technique_id: string;
  technique_name: string;
  status: "pending" | "active" | "completed";
  events_count: number;
}

/**
 * Props for AttackChainVisualization component
 */
interface AttackChainVisualizationProps {
  /** List of attack stages to display */
  stages: AttackStage[];
  /** Currently active stage number */
  currentStage: number;
  /** Optional title for the visualization */
  title?: string;
  /** Whether to show technique details */
  showTechniques?: boolean;
  /** Layout direction */
  layout?: "horizontal" | "vertical";
  /** Custom empty state message */
  emptyMessage?: string;
  /** Callback when a stage is clicked */
  onStageClick?: (stageNumber: number, stage: AttackStage) => void;
}

/**
 * Displays a visual representation of a MITRE ATT&CK attack chain.
 * Shows progression through attack stages with status indicators.
 */
export function AttackChainVisualization({
  stages,
  currentStage,
  title,
  showTechniques = false,
  layout = "horizontal",
  emptyMessage = "No attack chain data available",
  onStageClick,
}: AttackChainVisualizationProps) {
  // Calculate progress percentage
  const progressPercentage = useMemo(() => {
    if (stages.length === 0) return 0;
    const completedCount = stages.filter((s) => s.status === "completed").length;
    return Math.round((completedCount / stages.length) * 100);
  }, [stages]);

  // Handle empty state
  if (stages.length === 0) {
    return (
      <div
        data-testid="attack-chain-visualization"
        className={`flex ${layout === "horizontal" ? "flex-row" : "flex-col"} items-center justify-center p-8 bg-secondary/50 rounded-lg border border-primary`}
      >
        <div className="text-center text-secondary">
          <svg
            className="w-12 h-12 mx-auto mb-4 text-tertiary"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
            />
          </svg>
          <p>{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Title */}
      {title && (
        <h3 className="text-lg font-semibold text-primary">{title}</h3>
      )}

      {/* Progress Bar */}
      <div className="flex items-center gap-3">
        <div
          role="progressbar"
          aria-valuenow={progressPercentage}
          aria-valuemin={0}
          aria-valuemax={100}
          className="flex-1 h-2 bg-tertiary rounded-full overflow-hidden"
        >
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-500"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
        <span
          data-testid="progress-indicator"
          className="text-sm text-secondary min-w-[3rem] text-right"
        >
          {progressPercentage}%
        </span>
      </div>

      {/* Attack Chain */}
      <div
        data-testid="attack-chain-visualization"
        className={`flex ${layout === "horizontal" ? "flex-row" : "flex-col"} items-center gap-2`}
        role="list"
        aria-label="Attack chain stages"
      >
        {stages.map((stage, index) => (
          <div key={stage.stage} className="contents">
            {/* Stage Node */}
            <div
              data-testid={`attack-stage-${stage.stage}`}
              role="listitem"
              className={`
                relative flex flex-col items-center p-3 rounded-lg border-2 transition-all duration-300
                ${stage.status === "active" ? "active bg-cyan-900/50 border-cyan-500" : ""}
                ${stage.status === "completed" ? "completed bg-green-900/30 border-green-500" : ""}
                ${stage.status === "pending" ? "pending bg-secondary/50 border-primary" : ""}
                ${onStageClick ? "cursor-pointer hover:scale-105" : ""}
              `}
              onClick={() => onStageClick?.(stage.stage, stage)}
            >
              {/* Active Indicator Pulse */}
              {stage.status === "active" && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-cyan-400 rounded-full animate-pulse" />
              )}

              {/* Stage Number */}
              <div
                className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mb-2
                  ${stage.status === "completed" ? "bg-green-500 text-primary" : ""}
                  ${stage.status === "active" ? "bg-cyan-500 text-primary" : ""}
                  ${stage.status === "pending" ? "bg-tertiary text-secondary" : ""}
                `}
              >
                {stage.status === "completed" ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  stage.stage
                )}
              </div>

              {/* Tactic Info */}
              <div className="text-center min-w-[100px]">
                <p
                  className={`
                    text-xs font-mono mb-1
                    ${stage.status === "completed" ? "text-green-400" : ""}
                    ${stage.status === "active" ? "text-cyan-400" : ""}
                    ${stage.status === "pending" ? "text-tertiary" : ""}
                  `}
                >
                  {stage.tactic_id}
                </p>
                <p
                  className={`
                    text-sm font-medium
                    ${stage.status === "completed" ? "text-green-300" : ""}
                    ${stage.status === "active" ? "text-cyan-300" : ""}
                    ${stage.status === "pending" ? "text-secondary" : ""}
                  `}
                >
                  {stage.tactic_name}
                </p>

                {/* Technique Details */}
                {showTechniques && (
                  <div className="mt-2 pt-2 border-t border-primary">
                    <p className="text-xs font-mono text-tertiary">{stage.technique_id}</p>
                    <p className="text-xs text-secondary truncate max-w-[120px]">
                      {stage.technique_name}
                    </p>
                  </div>
                )}

                {/* Events Count */}
                {stage.events_count > 0 && (
                  <p className="text-xs text-tertiary mt-2">
                    {stage.events_count} events
                  </p>
                )}
              </div>
            </div>

            {/* Connector Arrow */}
            {index < stages.length - 1 && (
              <div
                data-testid="stage-connector"
                className={`
                  ${layout === "horizontal" ? "w-8 h-0.5" : "w-0.5 h-8"}
                  ${stages[index].status === "completed" ? "completed bg-green-500" : "bg-tertiary"}
                  transition-colors duration-300
                `}
              >
                {layout === "horizontal" && (
                  <svg
                    className={`w-3 h-3 absolute -right-1.5 -top-1 ${
                      stages[index].status === "completed" ? "text-green-500" : "text-tertiary"
                    }`}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default AttackChainVisualization;
