/**
 * DemoContext Unit Tests - TDD
 *
 * Tests for:
 * - REQ-006-002-001: Context React para estado global del demo
 *
 * The DemoContext provides global state management for the demo control panel:
 * - playState: stopped | playing | paused
 * - speed: 0.5 | 1 | 2 | 4
 * - selectedScenario: AttackScenario | null
 * - currentStage: number
 * - stages: MitreStage[]
 * - sessionId: string | null
 * - startedAt: string | null
 */

import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import { render, screen, act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";

// Import types from demo components
import type {
  DemoState,
  PlayState,
  SpeedMultiplier,
  AttackScenario,
  MitreStage,
} from "../../../src/components/demo/types";

// Import the context to be implemented
import {
  DemoProvider,
  useDemoContext,
  useDemoState,
  useDemoActions,
} from "../../../src/context/DemoContext";

// ============================================================================
// Test Fixtures
// ============================================================================

const mockScenario: AttackScenario = {
  id: "apt29",
  name: "APT29 (Cozy Bear)",
  description: "Government espionage campaign",
  category: "APT",
  stages: 8,
};

const mockStages: MitreStage[] = [
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
    completed: false,
    active: true,
  },
  {
    index: 2,
    tacticId: "TA0003",
    tacticName: "Persistence",
    techniqueIds: ["T1053"],
    completed: false,
    active: false,
  },
];

// Wrapper component for testing
const TestWrapper = ({ children }: { children: ReactNode }) => (
  <DemoProvider>{children}</DemoProvider>
);

// ============================================================================
// Provider Tests
// ============================================================================

describe("DemoProvider", () => {
  it("should render children without crashing", () => {
    render(
      <DemoProvider>
        <div data-testid="child">Test Child</div>
      </DemoProvider>
    );

    expect(screen.getByTestId("child")).toBeInTheDocument();
  });

  it("should provide default state values", () => {
    const TestComponent = () => {
      const state = useDemoState();
      return (
        <div>
          <span data-testid="playState">{state.playState}</span>
          <span data-testid="speed">{state.speed}</span>
          <span data-testid="currentStage">{state.currentStage}</span>
          <span data-testid="hasScenario">{state.selectedScenario ? "yes" : "no"}</span>
        </div>
      );
    };

    render(
      <DemoProvider>
        <TestComponent />
      </DemoProvider>
    );

    expect(screen.getByTestId("playState")).toHaveTextContent("stopped");
    expect(screen.getByTestId("speed")).toHaveTextContent("1");
    expect(screen.getByTestId("currentStage")).toHaveTextContent("0");
    expect(screen.getByTestId("hasScenario")).toHaveTextContent("no");
  });

  it("should throw error when used outside provider", () => {
    const TestComponent = () => {
      useDemoContext();
      return null;
    };

    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    expect(() => render(<TestComponent />)).toThrow(
      "useDemoContext must be used within a DemoProvider"
    );

    consoleSpy.mockRestore();
  });
});

// ============================================================================
// useDemoState Hook Tests
// ============================================================================

describe("useDemoState", () => {
  it("should return current demo state", () => {
    const { result } = renderHook(() => useDemoState(), {
      wrapper: TestWrapper,
    });

    expect(result.current).toMatchObject({
      playState: "stopped",
      speed: 1,
      selectedScenario: null,
      currentStage: 0,
      stages: [],
      sessionId: null,
      startedAt: null,
    });
  });

  it("should have correct type for playState", () => {
    const { result } = renderHook(() => useDemoState(), {
      wrapper: TestWrapper,
    });

    const validStates: PlayState[] = ["stopped", "playing", "paused"];
    expect(validStates).toContain(result.current.playState);
  });

  it("should have correct type for speed", () => {
    const { result } = renderHook(() => useDemoState(), {
      wrapper: TestWrapper,
    });

    const validSpeeds: SpeedMultiplier[] = [0.5, 1, 2, 4];
    expect(validSpeeds).toContain(result.current.speed);
  });
});

// ============================================================================
// useDemoActions Hook Tests
// ============================================================================

describe("useDemoActions", () => {
  describe("play()", () => {
    it("should change playState to playing", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.play();
      });

      expect(result.current.state.playState).toBe("playing");
    });

    it("should generate sessionId when starting new session", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      expect(result.current.state.sessionId).toBeNull();

      act(() => {
        result.current.actions.play();
      });

      expect(result.current.state.sessionId).not.toBeNull();
      expect(typeof result.current.state.sessionId).toBe("string");
    });

    it("should set startedAt timestamp when starting", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      expect(result.current.state.startedAt).toBeNull();

      act(() => {
        result.current.actions.play();
      });

      expect(result.current.state.startedAt).not.toBeNull();
      // Should be a valid ISO timestamp
      expect(new Date(result.current.state.startedAt!).toISOString()).toBe(
        result.current.state.startedAt
      );
    });

    it("should resume from paused state without changing sessionId", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      // Start, then pause
      act(() => {
        result.current.actions.play();
      });
      const originalSessionId = result.current.state.sessionId;

      act(() => {
        result.current.actions.pause();
      });

      // Resume
      act(() => {
        result.current.actions.play();
      });

      expect(result.current.state.sessionId).toBe(originalSessionId);
      expect(result.current.state.playState).toBe("playing");
    });
  });

  describe("pause()", () => {
    it("should change playState to paused", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.play();
        result.current.actions.pause();
      });

      expect(result.current.state.playState).toBe("paused");
    });

    it("should preserve sessionId when pausing", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.play();
      });
      const sessionId = result.current.state.sessionId;

      act(() => {
        result.current.actions.pause();
      });

      expect(result.current.state.sessionId).toBe(sessionId);
    });
  });

  describe("stop()", () => {
    it("should change playState to stopped", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.play();
        result.current.actions.stop();
      });

      expect(result.current.state.playState).toBe("stopped");
    });

    it("should reset currentStage to 0", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
        result.current.actions.play();
        result.current.actions.advanceStage();
        result.current.actions.advanceStage();
      });

      expect(result.current.state.currentStage).toBeGreaterThan(0);

      act(() => {
        result.current.actions.stop();
      });

      expect(result.current.state.currentStage).toBe(0);
    });

    it("should clear sessionId and startedAt", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.play();
      });

      expect(result.current.state.sessionId).not.toBeNull();
      expect(result.current.state.startedAt).not.toBeNull();

      act(() => {
        result.current.actions.stop();
      });

      expect(result.current.state.sessionId).toBeNull();
      expect(result.current.state.startedAt).toBeNull();
    });

    it("should reset all stage statuses", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
        result.current.actions.play();
        result.current.actions.advanceStage();
      });

      act(() => {
        result.current.actions.stop();
      });

      // All stages should be reset (first active, rest pending)
      const stages = result.current.state.stages;
      if (stages.length > 0) {
        expect(stages[0].active).toBe(true);
        expect(stages[0].completed).toBe(false);
        stages.slice(1).forEach((stage) => {
          expect(stage.active).toBe(false);
          expect(stage.completed).toBe(false);
        });
      }
    });
  });

  describe("setSpeed()", () => {
    it("should update speed value", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.setSpeed(2);
      });

      expect(result.current.state.speed).toBe(2);
    });

    it("should accept all valid speed values", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      const speeds: SpeedMultiplier[] = [0.5, 1, 2, 4];

      speeds.forEach((speed) => {
        act(() => {
          result.current.actions.setSpeed(speed);
        });
        expect(result.current.state.speed).toBe(speed);
      });
    });
  });

  describe("selectScenario()", () => {
    it("should set selectedScenario", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
      });

      expect(result.current.state.selectedScenario).toEqual(mockScenario);
    });

    it("should generate stages based on scenario", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
      });

      expect(result.current.state.stages.length).toBe(mockScenario.stages);
    });

    it("should reset currentStage when selecting new scenario", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
        result.current.actions.play();
        result.current.actions.advanceStage();
      });

      const otherScenario = { ...mockScenario, id: "fin7", stages: 5 };

      act(() => {
        result.current.actions.selectScenario(otherScenario);
      });

      expect(result.current.state.currentStage).toBe(0);
    });

    it("should stop playback when selecting new scenario during play", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
        result.current.actions.play();
      });

      expect(result.current.state.playState).toBe("playing");

      const otherScenario = { ...mockScenario, id: "fin7", stages: 5 };

      act(() => {
        result.current.actions.selectScenario(otherScenario);
      });

      expect(result.current.state.playState).toBe("stopped");
    });
  });

  describe("advanceStage()", () => {
    it("should increment currentStage", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
      });

      expect(result.current.state.currentStage).toBe(0);

      act(() => {
        result.current.actions.advanceStage();
      });

      expect(result.current.state.currentStage).toBe(1);
    });

    it("should mark previous stage as completed", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
        result.current.actions.advanceStage();
      });

      expect(result.current.state.stages[0].completed).toBe(true);
      expect(result.current.state.stages[0].active).toBe(false);
    });

    it("should set new stage as active", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
        result.current.actions.advanceStage();
      });

      expect(result.current.state.stages[1].active).toBe(true);
    });

    it("should not exceed total stages", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      const smallScenario = { ...mockScenario, stages: 2 };

      act(() => {
        result.current.actions.selectScenario(smallScenario);
      });

      // Try to advance beyond limits
      act(() => {
        result.current.actions.advanceStage();
        result.current.actions.advanceStage();
        result.current.actions.advanceStage();
        result.current.actions.advanceStage();
      });

      expect(result.current.state.currentStage).toBe(1); // Max index for 2 stages
    });
  });

  describe("jumpToStage()", () => {
    it("should set currentStage to specified index", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
        result.current.actions.jumpToStage(3);
      });

      expect(result.current.state.currentStage).toBe(3);
    });

    it("should mark all previous stages as completed", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
        result.current.actions.jumpToStage(3);
      });

      expect(result.current.state.stages[0].completed).toBe(true);
      expect(result.current.state.stages[1].completed).toBe(true);
      expect(result.current.state.stages[2].completed).toBe(true);
      expect(result.current.state.stages[3].completed).toBe(false);
      expect(result.current.state.stages[3].active).toBe(true);
    });

    it("should clamp to valid range", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.selectScenario(mockScenario);
      });

      act(() => {
        result.current.actions.jumpToStage(-5);
      });
      expect(result.current.state.currentStage).toBe(0);

      act(() => {
        result.current.actions.jumpToStage(100);
      });
      expect(result.current.state.currentStage).toBe(mockScenario.stages - 1);
    });
  });

  describe("togglePlayPause()", () => {
    it("should toggle from stopped to playing", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.togglePlayPause();
      });

      expect(result.current.state.playState).toBe("playing");
    });

    it("should toggle from playing to paused", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.play();
        result.current.actions.togglePlayPause();
      });

      expect(result.current.state.playState).toBe("paused");
    });

    it("should toggle from paused to playing", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      act(() => {
        result.current.actions.play();
        result.current.actions.pause();
        result.current.actions.togglePlayPause();
      });

      expect(result.current.state.playState).toBe("playing");
    });
  });

  describe("resetDemo()", () => {
    it("should reset all state to initial values", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      // Set up some state
      act(() => {
        result.current.actions.selectScenario(mockScenario);
        result.current.actions.setSpeed(4);
        result.current.actions.play();
        result.current.actions.advanceStage();
      });

      // Reset
      act(() => {
        result.current.actions.resetDemo();
      });

      expect(result.current.state).toMatchObject({
        playState: "stopped",
        speed: 1,
        selectedScenario: null,
        currentStage: 0,
        stages: [],
        sessionId: null,
        startedAt: null,
      });
    });
  });
});

// ============================================================================
// Integration with Components Tests
// ============================================================================

describe("DemoContext Integration", () => {
  it("should allow multiple components to share state", () => {
    const DisplayComponent = () => {
      const state = useDemoState();
      return <span data-testid="display">{state.playState}</span>;
    };

    const ControlComponent = () => {
      const actions = useDemoActions();
      return (
        <button onClick={() => actions.play()} data-testid="play-btn">
          Play
        </button>
      );
    };

    render(
      <DemoProvider>
        <DisplayComponent />
        <ControlComponent />
      </DemoProvider>
    );

    expect(screen.getByTestId("display")).toHaveTextContent("stopped");

    act(() => {
      screen.getByTestId("play-btn").click();
    });

    expect(screen.getByTestId("display")).toHaveTextContent("playing");
  });

  it("should update all consumers when state changes", () => {
    const Consumer1 = () => {
      const state = useDemoState();
      return <span data-testid="consumer1">{state.speed}</span>;
    };

    const Consumer2 = () => {
      const state = useDemoState();
      return <span data-testid="consumer2">{state.speed}</span>;
    };

    const Controller = () => {
      const actions = useDemoActions();
      return (
        <button onClick={() => actions.setSpeed(4)} data-testid="speed-btn">
          Set Speed
        </button>
      );
    };

    render(
      <DemoProvider>
        <Consumer1 />
        <Consumer2 />
        <Controller />
      </DemoProvider>
    );

    expect(screen.getByTestId("consumer1")).toHaveTextContent("1");
    expect(screen.getByTestId("consumer2")).toHaveTextContent("1");

    act(() => {
      screen.getByTestId("speed-btn").click();
    });

    expect(screen.getByTestId("consumer1")).toHaveTextContent("4");
    expect(screen.getByTestId("consumer2")).toHaveTextContent("4");
  });
});
