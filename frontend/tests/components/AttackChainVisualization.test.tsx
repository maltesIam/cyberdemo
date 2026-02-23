/**
 * AttackChainVisualization Component Unit Tests
 *
 * Test ID: UT-071 (REQ-002-003-004)
 *
 * Tests for:
 * 1. Component renders MITRE ATT&CK chain
 * 2. Displays active stage correctly
 * 3. Shows stage progress
 * 4. Handles click events on stages
 * 5. Displays tactic/technique information
 * 6. Handles empty state
 * 7. Updates when simulation progresses
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, cleanup, waitFor } from "@testing-library/react";
import { AttackChainVisualization, type AttackStage } from "../../src/components/AttackChainVisualization";

// Mock attack chain data
const mockAttackChain: AttackStage[] = [
  {
    stage: 1,
    tactic_id: "TA0001",
    tactic_name: "Initial Access",
    technique_id: "T1566",
    technique_name: "Phishing",
    status: "completed",
    events_count: 5,
  },
  {
    stage: 2,
    tactic_id: "TA0002",
    tactic_name: "Execution",
    technique_id: "T1059",
    technique_name: "Command and Scripting Interpreter",
    status: "active",
    events_count: 3,
  },
  {
    stage: 3,
    tactic_id: "TA0003",
    tactic_name: "Persistence",
    technique_id: "T1547",
    technique_name: "Boot or Logon Autostart Execution",
    status: "pending",
    events_count: 0,
  },
  {
    stage: 4,
    tactic_id: "TA0005",
    tactic_name: "Defense Evasion",
    technique_id: "T1027",
    technique_name: "Obfuscated Files or Information",
    status: "pending",
    events_count: 0,
  },
];

describe("AttackChainVisualization Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    cleanup();
  });

  // ============================================================================
  // TEST 1: Component renders MITRE ATT&CK chain
  // ============================================================================
  describe("Basic Rendering", () => {
    it("should render the attack chain container", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      expect(screen.getByTestId("attack-chain-visualization")).toBeInTheDocument();
    });

    it("should render all stages", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      // Should have all 4 stages
      const stages = screen.getAllByTestId(/^attack-stage-/);
      expect(stages).toHaveLength(4);
    });

    it("should display tactic names for each stage", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      expect(screen.getByText("Initial Access")).toBeInTheDocument();
      expect(screen.getByText("Execution")).toBeInTheDocument();
      expect(screen.getByText("Persistence")).toBeInTheDocument();
      expect(screen.getByText("Defense Evasion")).toBeInTheDocument();
    });

    it("should display stage numbers for non-completed stages", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      // Stage 1 is completed so shows checkmark instead of number
      // Stages 2, 3, 4 should show numbers
      expect(screen.getByText("2")).toBeInTheDocument();
      expect(screen.getByText("3")).toBeInTheDocument();
      expect(screen.getByText("4")).toBeInTheDocument();
    });

    it("should render title when provided", () => {
      render(
        <AttackChainVisualization
          stages={mockAttackChain}
          currentStage={2}
          title="APT29 Attack Chain"
        />
      );

      expect(screen.getByText("APT29 Attack Chain")).toBeInTheDocument();
    });
  });

  // ============================================================================
  // TEST 2: Displays active stage correctly
  // ============================================================================
  describe("Active Stage Display", () => {
    it("should highlight the active stage", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      const activeStage = screen.getByTestId("attack-stage-2");
      expect(activeStage).toHaveClass("active");
    });

    it("should mark completed stages with completed style", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      const completedStage = screen.getByTestId("attack-stage-1");
      expect(completedStage).toHaveClass("completed");
    });

    it("should mark pending stages with pending style", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      const pendingStage = screen.getByTestId("attack-stage-3");
      expect(pendingStage).toHaveClass("pending");
    });

    it("should show active indicator animation on current stage", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      const activeStage = screen.getByTestId("attack-stage-2");
      // Active stage should have pulse/animation class
      expect(activeStage.querySelector(".animate-pulse")).toBeInTheDocument();
    });
  });

  // ============================================================================
  // TEST 3: Shows stage progress
  // ============================================================================
  describe("Progress Display", () => {
    it("should show overall progress percentage", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      // With 2 of 4 stages (1 completed, 1 active), progress should be ~25-50%
      expect(screen.getByTestId("progress-indicator")).toBeInTheDocument();
    });

    it("should display progress bar", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      expect(screen.getByRole("progressbar")).toBeInTheDocument();
    });

    it("should update progress bar width based on completion", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      const progressBar = screen.getByRole("progressbar");
      // 1 of 4 completed = 25%
      expect(progressBar).toHaveAttribute("aria-valuenow", "25");
    });

    it("should show events count for stages with events", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      // Stage 1 has 5 events
      expect(screen.getByText("5 events")).toBeInTheDocument();
      // Stage 2 has 3 events
      expect(screen.getByText("3 events")).toBeInTheDocument();
    });
  });

  // ============================================================================
  // TEST 4: Handles click events on stages
  // ============================================================================
  describe("Click Events", () => {
    it("should call onStageClick when a stage is clicked", () => {
      const onStageClick = vi.fn();
      render(
        <AttackChainVisualization
          stages={mockAttackChain}
          currentStage={2}
          onStageClick={onStageClick}
        />
      );

      const stage1 = screen.getByTestId("attack-stage-1");
      fireEvent.click(stage1);

      expect(onStageClick).toHaveBeenCalledWith(1, mockAttackChain[0]);
    });

    it("should not call onStageClick if not provided", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      const stage1 = screen.getByTestId("attack-stage-1");
      // Should not throw
      fireEvent.click(stage1);
    });

    it("should show cursor pointer on clickable stages", () => {
      const onStageClick = vi.fn();
      render(
        <AttackChainVisualization
          stages={mockAttackChain}
          currentStage={2}
          onStageClick={onStageClick}
        />
      );

      const stage1 = screen.getByTestId("attack-stage-1");
      expect(stage1).toHaveClass("cursor-pointer");
    });
  });

  // ============================================================================
  // TEST 5: Displays tactic/technique information
  // ============================================================================
  describe("Tactic/Technique Information", () => {
    it("should display MITRE tactic IDs", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      expect(screen.getByText("TA0001")).toBeInTheDocument();
      expect(screen.getByText("TA0002")).toBeInTheDocument();
    });

    it("should display technique name on hover or expand", async () => {
      render(
        <AttackChainVisualization
          stages={mockAttackChain}
          currentStage={2}
          showTechniques={true}
        />
      );

      expect(screen.getByText("Phishing")).toBeInTheDocument();
      expect(screen.getByText("Command and Scripting Interpreter")).toBeInTheDocument();
    });

    it("should display technique IDs when showTechniques is true", () => {
      render(
        <AttackChainVisualization
          stages={mockAttackChain}
          currentStage={2}
          showTechniques={true}
        />
      );

      expect(screen.getByText("T1566")).toBeInTheDocument();
      expect(screen.getByText("T1059")).toBeInTheDocument();
    });

    it("should not display technique details when showTechniques is false", () => {
      render(
        <AttackChainVisualization
          stages={mockAttackChain}
          currentStage={2}
          showTechniques={false}
        />
      );

      expect(screen.queryByText("T1566")).not.toBeInTheDocument();
    });
  });

  // ============================================================================
  // TEST 6: Handles empty state
  // ============================================================================
  describe("Empty State", () => {
    it("should render empty state when no stages provided", () => {
      render(<AttackChainVisualization stages={[]} currentStage={0} />);

      expect(screen.getByText(/no attack chain/i)).toBeInTheDocument();
    });

    it("should show message when simulation not started", () => {
      render(
        <AttackChainVisualization
          stages={[]}
          currentStage={0}
          emptyMessage="Start a simulation to see the attack chain"
        />
      );

      expect(screen.getByText("Start a simulation to see the attack chain")).toBeInTheDocument();
    });
  });

  // ============================================================================
  // TEST 7: Updates when simulation progresses
  // ============================================================================
  describe("Simulation Progress Updates", () => {
    it("should update active stage when currentStage changes", () => {
      // Create initial chain where stage 1 is active
      const initialChain: AttackStage[] = [
        { ...mockAttackChain[0], status: "active" },
        { ...mockAttackChain[1], status: "pending" },
        { ...mockAttackChain[2], status: "pending" },
        { ...mockAttackChain[3], status: "pending" },
      ];

      const { rerender } = render(
        <AttackChainVisualization stages={initialChain} currentStage={1} />
      );

      // Initially stage 1 is active
      expect(screen.getByTestId("attack-stage-1")).toHaveClass("active");
      expect(screen.getByTestId("attack-stage-2")).not.toHaveClass("active");

      // Update to stage 2
      const updatedChain: AttackStage[] = [
        { ...mockAttackChain[0], status: "completed" },
        { ...mockAttackChain[1], status: "active" },
        { ...mockAttackChain[2], status: "pending" },
        { ...mockAttackChain[3], status: "pending" },
      ];

      rerender(<AttackChainVisualization stages={updatedChain} currentStage={2} />);

      // Now stage 2 is active
      expect(screen.getByTestId("attack-stage-1")).toHaveClass("completed");
      expect(screen.getByTestId("attack-stage-2")).toHaveClass("active");
    });

    it("should update events count when events are generated", () => {
      const initialChain: AttackStage[] = [
        { ...mockAttackChain[0], events_count: 0 },
        { ...mockAttackChain[1], events_count: 0 },
        { ...mockAttackChain[2] },
        { ...mockAttackChain[3] },
      ];

      const { rerender } = render(
        <AttackChainVisualization stages={initialChain} currentStage={1} />
      );

      // Update with new events
      const updatedChain: AttackStage[] = [
        { ...mockAttackChain[0], events_count: 10 },
        { ...mockAttackChain[1], events_count: 5 },
        { ...mockAttackChain[2] },
        { ...mockAttackChain[3] },
      ];

      rerender(<AttackChainVisualization stages={updatedChain} currentStage={2} />);

      expect(screen.getByText("10 events")).toBeInTheDocument();
      expect(screen.getByText("5 events")).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Additional Tests: Layout and Accessibility
  // ============================================================================
  describe("Layout and Accessibility", () => {
    it("should have accessible labels for screen readers", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      const stages = screen.getAllByRole("listitem");
      expect(stages.length).toBeGreaterThan(0);
    });

    it("should use semantic list structure", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      expect(screen.getByRole("list")).toBeInTheDocument();
    });

    it("should support horizontal layout by default", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      const container = screen.getByTestId("attack-chain-visualization");
      expect(container).toHaveClass("flex-row");
    });

    it("should support vertical layout when specified", () => {
      render(
        <AttackChainVisualization
          stages={mockAttackChain}
          currentStage={2}
          layout="vertical"
        />
      );

      const container = screen.getByTestId("attack-chain-visualization");
      expect(container).toHaveClass("flex-col");
    });
  });

  // ============================================================================
  // Tests: Connectors between stages
  // ============================================================================
  describe("Stage Connectors", () => {
    it("should render connectors between stages", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      // Should have 3 connectors for 4 stages
      const connectors = screen.getAllByTestId("stage-connector");
      expect(connectors).toHaveLength(3);
    });

    it("should style completed connectors differently", () => {
      render(<AttackChainVisualization stages={mockAttackChain} currentStage={2} />);

      // First connector (between completed and active) should be completed style
      const connectors = screen.getAllByTestId("stage-connector");
      expect(connectors[0]).toHaveClass("completed");
    });
  });
});
