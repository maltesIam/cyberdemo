/**
 * MitreProgressBar Component Tests
 *
 * Tests for the MITRE ATT&CK stage progress bar including:
 * - Visual progress display
 * - Stage labels and tooltips
 * - Current stage indication
 * - Compact mode
 *
 * Requirements: REQ-006-001-004
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MitreProgressBar } from "../../../src/components/demo/MitreProgressBar";
import type { MitreStage } from "../../../src/components/demo/types";

// Sample MITRE stages for testing
const SAMPLE_STAGES: MitreStage[] = [
  {
    index: 0,
    tacticId: "TA0001",
    tacticName: "Initial Access",
    techniqueIds: ["T1566"],
    completed: true,
    active: false,
  },
  {
    index: 1,
    tacticId: "TA0002",
    tacticName: "Execution",
    techniqueIds: ["T1059"],
    completed: true,
    active: false,
  },
  {
    index: 2,
    tacticId: "TA0003",
    tacticName: "Persistence",
    techniqueIds: ["T1547"],
    completed: false,
    active: true,
  },
  {
    index: 3,
    tacticId: "TA0004",
    tacticName: "Privilege Escalation",
    techniqueIds: ["T1548"],
    completed: false,
    active: false,
  },
  {
    index: 4,
    tacticId: "TA0005",
    tacticName: "Defense Evasion",
    techniqueIds: ["T1070"],
    completed: false,
    active: false,
  },
];

describe("MitreProgressBar", () => {
  describe("Rendering (REQ-006-001-004)", () => {
    it("should render the progress bar", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      expect(screen.getByRole("progressbar")).toBeInTheDocument();
    });

    it("should render all stages", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      // Each stage should have a marker
      const stageMarkers = screen.getAllByTestId(/stage-marker/);
      expect(stageMarkers).toHaveLength(5);
    });

    it("should display stage labels", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      // Multiple instances of stage names may exist (markers + labels)
      expect(screen.getAllByText("Initial Access").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Execution").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Persistence").length).toBeGreaterThan(0);
    });

    it("should show progress percentage", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      // 2 out of 5 completed = 40%
      expect(screen.getByText(/40%|2\/5/)).toBeInTheDocument();
    });
  });

  describe("Stage Indicators", () => {
    it("should mark completed stages with green color", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      const completedStages = screen.getAllByTestId("stage-marker-completed");
      expect(completedStages).toHaveLength(2);
      completedStages.forEach(stage => {
        expect(stage).toHaveClass("bg-green-500");
      });
    });

    it("should mark current stage with cyan/blue color", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      const activeStage = screen.getByTestId("stage-marker-active");
      expect(activeStage).toHaveClass("bg-cyan-500");
    });

    it("should mark pending stages with gray color", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      const pendingStages = screen.getAllByTestId("stage-marker-pending");
      expect(pendingStages).toHaveLength(2);
      pendingStages.forEach(stage => {
        expect(stage).toHaveClass("bg-tertiary");
      });
    });

    it("should show pulsing animation on active stage", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      const activeStage = screen.getByTestId("stage-marker-active");
      expect(activeStage).toHaveClass("animate-pulse");
    });
  });

  describe("Progress Fill", () => {
    it("should show filled progress up to current stage", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      const progressFill = screen.getByTestId("progress-fill");
      // Should be approximately 50% (2.5 out of 5 stages including current)
      const style = progressFill.getAttribute("style");
      expect(style).toMatch(/width:\s*(40|45|50)%/);
    });

    it("should show 0% when at first stage", () => {
      const stagesAtStart = SAMPLE_STAGES.map((s, i) => ({
        ...s,
        completed: false,
        active: i === 0,
      }));
      render(<MitreProgressBar stages={stagesAtStart} currentStage={0} />);

      const progressFill = screen.getByTestId("progress-fill");
      const style = progressFill.getAttribute("style");
      expect(style).toMatch(/width:\s*(0|10)%/);
    });

    it("should show 100% when all stages complete", () => {
      const completedStages = SAMPLE_STAGES.map(s => ({
        ...s,
        completed: true,
        active: false,
      }));
      render(<MitreProgressBar stages={completedStages} currentStage={4} />);

      const progressFill = screen.getByTestId("progress-fill");
      const style = progressFill.getAttribute("style");
      expect(style).toMatch(/width:\s*100%/);
    });
  });

  describe("Tooltips", () => {
    it("should show tooltip on stage hover", async () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      const firstStageMarker = screen.getAllByTestId(/stage-marker/)[0];
      fireEvent.mouseEnter(firstStageMarker);

      expect(screen.getByText("TA0001")).toBeInTheDocument();
      expect(screen.getByText("T1566")).toBeInTheDocument();
    });

    it("should hide tooltip on mouse leave", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      const firstStageMarker = screen.getAllByTestId(/stage-marker/)[0];
      fireEvent.mouseEnter(firstStageMarker);
      expect(screen.getByText("TA0001")).toBeInTheDocument();

      fireEvent.mouseLeave(firstStageMarker);
      expect(screen.queryByText("TA0001")).not.toBeInTheDocument();
    });
  });

  describe("Compact Mode", () => {
    it("should render compact view when compact prop is true", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} compact={true} />);

      const progressBar = screen.getByRole("progressbar");
      expect(progressBar).toHaveClass("h-2");
    });

    it("should not show stage labels in compact mode", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} compact={true} />);

      expect(screen.queryByText("Initial Access")).not.toBeInTheDocument();
      expect(screen.queryByText("Execution")).not.toBeInTheDocument();
    });

    it("should show current stage name in compact mode", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} compact={true} />);

      expect(screen.getByText(/Persistence/)).toBeInTheDocument();
    });
  });

  describe("Edge Cases", () => {
    it("should handle empty stages array", () => {
      render(<MitreProgressBar stages={[]} currentStage={0} />);

      const progressBar = screen.getByRole("progressbar");
      expect(progressBar).toBeInTheDocument();
      expect(screen.getByText(/0%|0\/0/)).toBeInTheDocument();
    });

    it("should handle single stage", () => {
      const singleStage = [SAMPLE_STAGES[0]];
      render(<MitreProgressBar stages={singleStage} currentStage={0} />);

      const stageMarkers = screen.getAllByTestId(/stage-marker/);
      expect(stageMarkers).toHaveLength(1);
    });

    it("should handle out of bounds currentStage", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={10} />);

      // Should not crash, treat as last stage
      const progressBar = screen.getByRole("progressbar");
      expect(progressBar).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("should have proper ARIA attributes", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      const progressBar = screen.getByRole("progressbar");
      expect(progressBar).toHaveAttribute("aria-valuemin", "0");
      expect(progressBar).toHaveAttribute("aria-valuemax", "5");
      expect(progressBar).toHaveAttribute("aria-valuenow", "2");
    });

    it("should have accessible label", () => {
      render(<MitreProgressBar stages={SAMPLE_STAGES} currentStage={2} />);

      const progressBar = screen.getByRole("progressbar");
      expect(progressBar).toHaveAttribute("aria-label", expect.stringMatching(/progress|stage/i));
    });
  });
});
