/**
 * MitreProgressBar Component
 *
 * A visual progress bar showing MITRE ATT&CK stages with
 * completion status, tooltips, and compact mode.
 *
 * Requirements:
 * - REQ-006-001-004: Progress bar showing MITRE stages
 */

import { useState } from "react";
import type { MitreProgressBarProps, MitreStage } from "./types";

/** Calculate progress percentage */
const calculateProgress = (stages: MitreStage[]): number => {
  if (stages.length === 0) return 0;
  const completedCount = stages.filter(s => s.completed).length;
  return Math.round((completedCount / stages.length) * 100);
};

/** Get status for a stage */
const getStageStatus = (stage: MitreStage): "completed" | "active" | "pending" => {
  if (stage.completed) return "completed";
  if (stage.active) return "active";
  return "pending";
};

/** Tooltip component */
const StageTooltip = ({ stage }: { stage: MitreStage }) => (
  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 pointer-events-none">
    <div className="bg-primary border border-primary rounded-lg p-2 shadow-lg min-w-[150px]">
      <div className="text-xs font-semibold text-primary">{stage.tacticName}</div>
      <div className="text-xs text-cyan-400">{stage.tacticId}</div>
      {stage.techniqueIds.length > 0 && (
        <div className="text-xs text-secondary mt-1">
          {stage.techniqueIds.join(", ")}
        </div>
      )}
    </div>
    <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900" />
  </div>
);

/** Stage marker component */
const StageMarker = ({
  stage,
  isCompact,
  showTooltip,
  onMouseEnter,
  onMouseLeave,
}: {
  stage: MitreStage;
  isCompact: boolean;
  showTooltip: boolean;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}) => {
  const status = getStageStatus(stage);

  const statusClasses = {
    completed: "bg-green-500",
    active: "bg-cyan-500 animate-pulse",
    pending: "bg-tertiary",
  };

  const markerSize = isCompact ? "w-2 h-2" : "w-3 h-3";

  return (
    <div
      className="relative flex flex-col items-center"
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {showTooltip && <StageTooltip stage={stage} />}
      <div
        data-testid={`stage-marker-${status}`}
        className={`${markerSize} rounded-full ${statusClasses[status]} transition-all cursor-pointer hover:ring-2 hover:ring-white/30`}
      />
      {!isCompact && (
        <span className="text-[10px] text-secondary mt-1 whitespace-nowrap">
          {stage.tacticName}
        </span>
      )}
    </div>
  );
};

export function MitreProgressBar({
  stages,
  currentStage: _currentStage,
  compact = false,
}: MitreProgressBarProps) {
  // Note: _currentStage prop is kept for API compatibility;
  // actual stage tracking uses the active property on stages
  void _currentStage;
  const [hoveredStage, setHoveredStage] = useState<number | null>(null);

  const progress = calculateProgress(stages);
  const completedCount = stages.filter(s => s.completed).length;

  // Calculate fill width - up to the middle of current stage
  const calculateFillWidth = (): string => {
    if (stages.length === 0) return "0%";
    if (stages.length === 1) {
      return stages[0].completed ? "100%" : "10%";
    }

    // All completed
    if (stages.every(s => s.completed)) return "100%";

    // Calculate based on completed stages
    const segmentWidth = 100 / (stages.length - 1);
    const fillPercentage = completedCount * segmentWidth;

    return `${Math.min(fillPercentage, 100)}%`;
  };

  // Get current stage info for compact view
  const activeStage = stages.find(s => s.active);

  return (
    <div className="w-full">
      {/* Header with progress info */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-secondary">MITRE ATT&CK Progress</span>
        <span className="text-xs text-secondary">
          {completedCount}/{stages.length} ({progress}%)
        </span>
      </div>

      {/* Progress bar */}
      <div
        role="progressbar"
        aria-label="Attack stage progress"
        aria-valuemin={0}
        aria-valuemax={stages.length}
        aria-valuenow={completedCount}
        className={`relative w-full bg-tertiary rounded-full ${compact ? "h-2" : "h-3"}`}
      >
        {/* Progress fill */}
        <div
          data-testid="progress-fill"
          className={`absolute left-0 top-0 bg-gradient-to-r from-green-500 to-cyan-500 rounded-full transition-all duration-500 ${
            compact ? "h-2" : "h-3"
          }`}
          style={{ width: calculateFillWidth() }}
        />

        {/* Stage markers (not in compact mode) */}
        {!compact && stages.length > 0 && (
          <div className="absolute inset-0 flex items-center justify-between px-1">
            {stages.map((stage, index) => (
              <StageMarker
                key={stage.tacticId}
                stage={stage}
                isCompact={compact}
                showTooltip={hoveredStage === index}
                onMouseEnter={() => setHoveredStage(index)}
                onMouseLeave={() => setHoveredStage(null)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Stage labels (full mode) */}
      {!compact && stages.length > 0 && (
        <div className="flex justify-between mt-1">
          {stages.map((stage) => (
            <div
              key={stage.tacticId}
              className="flex-1 text-center"
            >
              <span className={`text-[10px] ${stage.active ? "text-cyan-400 font-medium" : "text-tertiary"}`}>
                {stage.tacticName}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Compact mode: Show current stage name */}
      {compact && activeStage && (
        <div className="mt-1 text-xs text-cyan-400">
          Stage {activeStage.index + 1}: {activeStage.tacticName}
        </div>
      )}
    </div>
  );
}
