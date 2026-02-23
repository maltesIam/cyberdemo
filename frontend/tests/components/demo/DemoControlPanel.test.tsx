/**
 * DemoControlPanel Component Tests
 *
 * Tests for the main demo control panel container component.
 *
 * Requirements:
 * - TECH-011: DemoControlPanel React component
 * - REQ-006-001-001: Play/Pause/Stop buttons
 * - REQ-006-001-002: Speed slider (0.5x-4x)
 * - REQ-006-001-003: Scenario selection dropdown
 * - REQ-006-001-004: MITRE stage progress bar
 * - REQ-006-001-005: Keyboard shortcuts
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DemoControlPanel } from "../../../src/components/demo/DemoControlPanel";
import type { DemoState, AttackScenario } from "../../../src/components/demo/types";

// Mock scenarios for testing
const mockScenarios: AttackScenario[] = [
  {
    id: "apt29",
    name: "APT29 (Cozy Bear)",
    description: "Government espionage campaign",
    category: "APT",
    stages: 8,
  },
  {
    id: "fin7",
    name: "FIN7",
    description: "Financial attack campaign",
    category: "Financial",
    stages: 7,
  },
];

// Default initial state for testing
const defaultState: DemoState = {
  playState: "stopped",
  speed: 1,
  selectedScenario: null,
  currentStage: 0,
  stages: [],
  sessionId: null,
  startedAt: null,
};

// Helper to render the component with default props
const renderDemoControlPanel = (overrides: Partial<{
  state: Partial<DemoState>;
  scenarios: AttackScenario[];
  onPlay: () => void;
  onPause: () => void;
  onStop: () => void;
  onSpeedChange: (speed: number) => void;
  onScenarioSelect: (scenario: AttackScenario) => void;
}> = {}) => {
  const defaultProps = {
    state: { ...defaultState, ...overrides.state },
    scenarios: overrides.scenarios ?? mockScenarios,
    onPlay: overrides.onPlay ?? vi.fn(),
    onPause: overrides.onPause ?? vi.fn(),
    onStop: overrides.onStop ?? vi.fn(),
    onSpeedChange: overrides.onSpeedChange ?? vi.fn(),
    onScenarioSelect: overrides.onScenarioSelect ?? vi.fn(),
  };

  return {
    ...render(<DemoControlPanel {...defaultProps} />),
    ...defaultProps,
  };
};

describe("DemoControlPanel", () => {
  describe("Component Structure", () => {
    it("should render the control panel container", () => {
      renderDemoControlPanel();
      expect(screen.getByTestId("demo-control-panel")).toBeInTheDocument();
    });

    it("should render with proper styling classes", () => {
      renderDemoControlPanel();
      const panel = screen.getByTestId("demo-control-panel");
      expect(panel).toHaveClass("bg-gray-800");
    });

    it("should render the Demo Controls header", () => {
      renderDemoControlPanel();
      expect(screen.getByText("Demo Controls")).toBeInTheDocument();
    });
  });

  describe("Play/Pause/Stop Buttons (REQ-006-001-001)", () => {
    it("should render play button when state is stopped", () => {
      renderDemoControlPanel({ state: { playState: "stopped" } });
      expect(screen.getByRole("button", { name: /play/i })).toBeInTheDocument();
    });

    it("should render pause button when state is playing", () => {
      renderDemoControlPanel({ state: { playState: "playing" } });
      expect(screen.getByRole("button", { name: /pause/i })).toBeInTheDocument();
    });

    it("should render play button when state is paused", () => {
      renderDemoControlPanel({ state: { playState: "paused" } });
      expect(screen.getByRole("button", { name: /play/i })).toBeInTheDocument();
    });

    it("should render stop button", () => {
      renderDemoControlPanel();
      expect(screen.getByRole("button", { name: /stop/i })).toBeInTheDocument();
    });

    it("should call onPlay when play button is clicked", async () => {
      const onPlay = vi.fn();
      renderDemoControlPanel({
        state: { playState: "stopped", selectedScenario: mockScenarios[0] },
        onPlay
      });

      fireEvent.click(screen.getByRole("button", { name: /play/i }));
      expect(onPlay).toHaveBeenCalledTimes(1);
    });

    it("should call onPause when pause button is clicked", async () => {
      const onPause = vi.fn();
      renderDemoControlPanel({
        state: { playState: "playing" },
        onPause
      });

      fireEvent.click(screen.getByRole("button", { name: /pause/i }));
      expect(onPause).toHaveBeenCalledTimes(1);
    });

    it("should call onStop when stop button is clicked", async () => {
      const onStop = vi.fn();
      renderDemoControlPanel({
        state: { playState: "playing" },
        onStop
      });

      fireEvent.click(screen.getByRole("button", { name: /stop/i }));
      expect(onStop).toHaveBeenCalledTimes(1);
    });

    it("should disable play button when no scenario is selected", () => {
      renderDemoControlPanel({ state: { selectedScenario: null } });
      expect(screen.getByRole("button", { name: /play/i })).toBeDisabled();
    });

    it("should enable play button when a scenario is selected", () => {
      renderDemoControlPanel({
        state: { selectedScenario: mockScenarios[0], playState: "stopped" }
      });
      expect(screen.getByRole("button", { name: /play/i })).not.toBeDisabled();
    });

    it("should disable stop button when state is stopped", () => {
      renderDemoControlPanel({ state: { playState: "stopped" } });
      expect(screen.getByRole("button", { name: /stop/i })).toBeDisabled();
    });
  });

  describe("Speed Slider (REQ-006-001-002)", () => {
    it("should render speed slider", () => {
      renderDemoControlPanel();
      expect(screen.getByRole("slider", { name: /speed/i })).toBeInTheDocument();
    });

    it("should display current speed value", () => {
      renderDemoControlPanel({ state: { speed: 2 } });
      // Speed is shown in multiple places, verify the slider value
      const slider = screen.getByRole("slider", { name: /speed/i });
      expect(slider).toHaveValue("2");
    });

    it("should have min value of 0.5", () => {
      renderDemoControlPanel();
      const slider = screen.getByRole("slider", { name: /speed/i });
      expect(slider).toHaveAttribute("min", "0.5");
    });

    it("should have max value of 4", () => {
      renderDemoControlPanel();
      const slider = screen.getByRole("slider", { name: /speed/i });
      expect(slider).toHaveAttribute("max", "4");
    });

    it("should call onSpeedChange when slider is moved", async () => {
      const onSpeedChange = vi.fn();
      renderDemoControlPanel({ onSpeedChange });

      const slider = screen.getByRole("slider", { name: /speed/i });
      fireEvent.change(slider, { target: { value: "2" } });

      expect(onSpeedChange).toHaveBeenCalledWith(2);
    });

    it("should display 0.5x as minimum speed", () => {
      renderDemoControlPanel({ state: { speed: 0.5 } });
      const slider = screen.getByRole("slider", { name: /speed/i });
      expect(slider).toHaveValue("0.5");
    });

    it("should display 4x as maximum speed", () => {
      renderDemoControlPanel({ state: { speed: 4 } });
      const slider = screen.getByRole("slider", { name: /speed/i });
      expect(slider).toHaveValue("4");
    });
  });

  describe("Scenario Selection (REQ-006-001-003)", () => {
    it("should render scenario dropdown", () => {
      renderDemoControlPanel();
      expect(screen.getByText("Scenario")).toBeInTheDocument();
    });

    it("should pass scenarios to dropdown", () => {
      renderDemoControlPanel({ scenarios: mockScenarios });
      // Click to open dropdown
      const dropdown = screen.getByRole("combobox");
      fireEvent.click(dropdown);

      expect(screen.getByText("APT29 (Cozy Bear)")).toBeInTheDocument();
      expect(screen.getByText("FIN7")).toBeInTheDocument();
    });

    it("should call onScenarioSelect when scenario is selected", async () => {
      const onScenarioSelect = vi.fn();
      renderDemoControlPanel({ onScenarioSelect });

      const dropdown = screen.getByRole("combobox");
      fireEvent.click(dropdown);

      const option = screen.getByText("APT29 (Cozy Bear)");
      fireEvent.click(option);

      expect(onScenarioSelect).toHaveBeenCalledWith(mockScenarios[0]);
    });

    it("should disable dropdown while simulation is playing", () => {
      renderDemoControlPanel({ state: { playState: "playing" } });
      expect(screen.getByRole("combobox")).toBeDisabled();
    });
  });

  describe("Progress Bar (REQ-006-001-004)", () => {
    it("should render MITRE progress bar", () => {
      renderDemoControlPanel();
      expect(screen.getByRole("progressbar")).toBeInTheDocument();
    });

    it("should show progress bar when scenario has stages", () => {
      const stages = [
        { index: 0, tacticId: "TA0001", tacticName: "Initial Access", techniqueIds: [], completed: true, active: false },
        { index: 1, tacticId: "TA0002", tacticName: "Execution", techniqueIds: [], completed: false, active: true },
      ];
      renderDemoControlPanel({ state: { stages } });

      expect(screen.getByText("MITRE ATT&CK Progress")).toBeInTheDocument();
    });
  });

  describe("Status Display", () => {
    it("should show stopped status when not running", () => {
      renderDemoControlPanel({ state: { playState: "stopped" } });
      expect(screen.getByText(/stopped/i)).toBeInTheDocument();
    });

    it("should show playing status when simulation is running", () => {
      renderDemoControlPanel({ state: { playState: "playing" } });
      expect(screen.getByText(/playing/i)).toBeInTheDocument();
    });

    it("should show paused status when simulation is paused", () => {
      renderDemoControlPanel({ state: { playState: "paused" } });
      expect(screen.getByText(/paused/i)).toBeInTheDocument();
    });

    it("should show selected scenario name", () => {
      renderDemoControlPanel({ state: { selectedScenario: mockScenarios[0] } });
      expect(screen.getByText("APT29 (Cozy Bear)")).toBeInTheDocument();
    });
  });

  describe("Keyboard Shortcut Hints", () => {
    it("should display keyboard shortcut hints", () => {
      renderDemoControlPanel();
      expect(screen.getByText(/space/i)).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("should have accessible labels for all controls", () => {
      renderDemoControlPanel();

      expect(screen.getByRole("button", { name: /play/i })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /stop/i })).toBeInTheDocument();
      expect(screen.getByRole("slider", { name: /speed/i })).toBeInTheDocument();
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    it("should have proper aria-label on control panel", () => {
      renderDemoControlPanel();
      const panel = screen.getByTestId("demo-control-panel");
      expect(panel).toHaveAttribute("aria-label", "Demo simulation controls");
    });
  });

  describe("Visual Feedback", () => {
    it("should show pulse animation when playing", () => {
      renderDemoControlPanel({ state: { playState: "playing" } });
      const indicator = screen.getByTestId("status-indicator");
      expect(indicator).toHaveClass("animate-pulse");
    });

    it("should show green indicator when playing", () => {
      renderDemoControlPanel({ state: { playState: "playing" } });
      const indicator = screen.getByTestId("status-indicator");
      expect(indicator).toHaveClass("bg-green-500");
    });

    it("should show yellow indicator when paused", () => {
      renderDemoControlPanel({ state: { playState: "paused" } });
      const indicator = screen.getByTestId("status-indicator");
      expect(indicator).toHaveClass("bg-yellow-500");
    });

    it("should show gray indicator when stopped", () => {
      renderDemoControlPanel({ state: { playState: "stopped" } });
      const indicator = screen.getByTestId("status-indicator");
      expect(indicator).toHaveClass("bg-gray-500");
    });
  });
});

describe("DemoControlPanel Integration", () => {
  it("should work as a complete control flow", async () => {
    const onPlay = vi.fn();
    const onPause = vi.fn();
    const onStop = vi.fn();
    const onScenarioSelect = vi.fn();

    const { rerender } = render(
      <DemoControlPanel
        state={{ ...defaultState, selectedScenario: mockScenarios[0] }}
        scenarios={mockScenarios}
        onPlay={onPlay}
        onPause={onPause}
        onStop={onStop}
        onSpeedChange={vi.fn()}
        onScenarioSelect={onScenarioSelect}
      />
    );

    // Start simulation
    fireEvent.click(screen.getByRole("button", { name: /play/i }));
    expect(onPlay).toHaveBeenCalled();

    // Rerender with playing state
    rerender(
      <DemoControlPanel
        state={{ ...defaultState, playState: "playing", selectedScenario: mockScenarios[0] }}
        scenarios={mockScenarios}
        onPlay={onPlay}
        onPause={onPause}
        onStop={onStop}
        onSpeedChange={vi.fn()}
        onScenarioSelect={onScenarioSelect}
      />
    );

    // Pause simulation
    fireEvent.click(screen.getByRole("button", { name: /pause/i }));
    expect(onPause).toHaveBeenCalled();

    // Rerender with paused state
    rerender(
      <DemoControlPanel
        state={{ ...defaultState, playState: "paused", selectedScenario: mockScenarios[0] }}
        scenarios={mockScenarios}
        onPlay={onPlay}
        onPause={onPause}
        onStop={onStop}
        onSpeedChange={vi.fn()}
        onScenarioSelect={onScenarioSelect}
      />
    );

    // Stop simulation
    fireEvent.click(screen.getByRole("button", { name: /stop/i }));
    expect(onStop).toHaveBeenCalled();
  });
});
