/**
 * Demo Control Panel Integration Tests
 *
 * Tests for EPIC-006: Demo Control Panel
 *
 * These integration tests verify that:
 * - DemoContext integrates correctly with demo components
 * - State flows correctly between components
 * - Keyboard shortcuts work with context
 * - MCP sync integrates with UI actions
 * - localStorage persistence works end-to-end
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, fireEvent, act, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";

// Import context and components
import {
  DemoProvider,
  useDemoState,
  useDemoActions,
  useDemoMCPSync,
  DEMO_STORAGE_KEY,
} from "../../src/context/DemoContext";
import {
  ScenarioDropdown,
  MitreProgressBar,
  useKeyboardShortcuts,
  ATTACK_SCENARIOS,
  SPEED_OPTIONS,
  type AttackScenario,
} from "../../src/components/demo";

// ============================================================================
// Test Components
// ============================================================================

/** Simple playback controls using DemoContext */
function TestPlaybackControls() {
  const { playState } = useDemoState();
  const { play, pause, stop, togglePlayPause } = useDemoActions();

  return (
    <div>
      <span data-testid="playState">{playState}</span>
      <button data-testid="play-btn" onClick={play}>
        Play
      </button>
      <button data-testid="pause-btn" onClick={pause}>
        Pause
      </button>
      <button data-testid="stop-btn" onClick={stop}>
        Stop
      </button>
      <button data-testid="toggle-btn" onClick={togglePlayPause}>
        Toggle
      </button>
    </div>
  );
}

/** Speed controls using DemoContext */
function TestSpeedControls() {
  const { speed } = useDemoState();
  const { setSpeed } = useDemoActions();

  return (
    <div>
      <span data-testid="speed">{speed}x</span>
      {SPEED_OPTIONS.map((s) => (
        <button key={s} data-testid={`speed-${s}`} onClick={() => setSpeed(s)}>
          {s}x
        </button>
      ))}
    </div>
  );
}

/** Scenario controls using DemoContext */
function TestScenarioControls() {
  const { selectedScenario, stages } = useDemoState();
  const { selectScenario } = useDemoActions();

  return (
    <div>
      <span data-testid="scenario-name">{selectedScenario?.name || "None"}</span>
      <span data-testid="stage-count">{stages.length}</span>
      <ScenarioDropdown
        scenarios={ATTACK_SCENARIOS}
        selectedScenario={selectedScenario}
        onSelect={selectScenario}
      />
    </div>
  );
}

/** Progress bar connected to context */
function TestProgressBar() {
  const { stages, currentStage } = useDemoState();
  const { advanceStage, jumpToStage } = useDemoActions();

  return (
    <div>
      <MitreProgressBar stages={stages} currentStage={currentStage} />
      <span data-testid="currentStage">{currentStage}</span>
      <button data-testid="advance-btn" onClick={advanceStage}>
        Advance
      </button>
      <button data-testid="jump-btn" onClick={() => jumpToStage(3)}>
        Jump to 3
      </button>
    </div>
  );
}

/** Keyboard shortcut handler */
function TestKeyboardShortcuts() {
  const { playState, speed } = useDemoState();
  const { togglePlayPause, stop, setSpeed } = useDemoActions();

  const handleSpeedUp = () => {
    const currentIndex = SPEED_OPTIONS.indexOf(speed);
    if (currentIndex < SPEED_OPTIONS.length - 1) {
      setSpeed(SPEED_OPTIONS[currentIndex + 1]);
    }
  };

  const handleSpeedDown = () => {
    const currentIndex = SPEED_OPTIONS.indexOf(speed);
    if (currentIndex > 0) {
      setSpeed(SPEED_OPTIONS[currentIndex - 1]);
    }
  };

  useKeyboardShortcuts({
    onTogglePlayPause: togglePlayPause,
    onStop: stop,
    onSpeedUp: handleSpeedUp,
    onSpeedDown: handleSpeedDown,
    isEnabled: true,
  });

  return (
    <div>
      <span data-testid="playState">{playState}</span>
      <span data-testid="speed">{speed}</span>
    </div>
  );
}

/** MCP sync test component */
function TestMCPSync({ onStateChange }: { onStateChange: (state: unknown) => void }) {
  const state = useDemoState();
  const { registerSyncCallback, unregisterSyncCallback, syncFromMCP } = useDemoMCPSync();
  const { setSpeed, selectScenario } = useDemoActions();

  return (
    <div>
      <span data-testid="speed">{state.speed}</span>
      <button
        data-testid="register-btn"
        onClick={() => registerSyncCallback(onStateChange)}
      >
        Register
      </button>
      <button
        data-testid="unregister-btn"
        onClick={() => unregisterSyncCallback(onStateChange)}
      >
        Unregister
      </button>
      <button data-testid="sync-speed-btn" onClick={() => syncFromMCP({ speed: 4 })}>
        Sync Speed from MCP
      </button>
      <button data-testid="local-speed-btn" onClick={() => setSpeed(2)}>
        Set Speed Locally
      </button>
      <button
        data-testid="select-scenario-btn"
        onClick={() => selectScenario(ATTACK_SCENARIOS[0])}
      >
        Select Scenario
      </button>
    </div>
  );
}

// ============================================================================
// Integration Tests
// ============================================================================

describe("Demo Control Panel Integration", () => {
  // ==========================================================================
  // Playback Controls + Context Integration
  // ==========================================================================

  describe("Playback Controls Integration", () => {
    it("should sync playback state across multiple components", () => {
      render(
        <DemoProvider>
          <TestPlaybackControls />
          <div data-testid="second-component">
            <SecondPlayStateDisplay />
          </div>
        </DemoProvider>
      );

      // Both should show stopped initially
      expect(screen.getByTestId("playState")).toHaveTextContent("stopped");
      expect(screen.getByTestId("second-playState")).toHaveTextContent("stopped");

      // Click play in first component
      fireEvent.click(screen.getByTestId("play-btn"));

      // Both should update to playing
      expect(screen.getByTestId("playState")).toHaveTextContent("playing");
      expect(screen.getByTestId("second-playState")).toHaveTextContent("playing");
    });

    it("should cycle through play states correctly", () => {
      render(
        <DemoProvider>
          <TestPlaybackControls />
        </DemoProvider>
      );

      expect(screen.getByTestId("playState")).toHaveTextContent("stopped");

      fireEvent.click(screen.getByTestId("play-btn"));
      expect(screen.getByTestId("playState")).toHaveTextContent("playing");

      fireEvent.click(screen.getByTestId("pause-btn"));
      expect(screen.getByTestId("playState")).toHaveTextContent("paused");

      fireEvent.click(screen.getByTestId("toggle-btn"));
      expect(screen.getByTestId("playState")).toHaveTextContent("playing");

      fireEvent.click(screen.getByTestId("stop-btn"));
      expect(screen.getByTestId("playState")).toHaveTextContent("stopped");
    });
  });

  // ==========================================================================
  // Speed Controls + Context Integration
  // ==========================================================================

  describe("Speed Controls Integration", () => {
    it("should update speed across components", () => {
      render(
        <DemoProvider>
          <TestSpeedControls />
          <SecondSpeedDisplay />
        </DemoProvider>
      );

      expect(screen.getByTestId("speed")).toHaveTextContent("1x");
      expect(screen.getByTestId("second-speed")).toHaveTextContent("1");

      fireEvent.click(screen.getByTestId("speed-4"));

      expect(screen.getByTestId("speed")).toHaveTextContent("4x");
      expect(screen.getByTestId("second-speed")).toHaveTextContent("4");
    });

    it("should allow all speed values", () => {
      render(
        <DemoProvider>
          <TestSpeedControls />
        </DemoProvider>
      );

      SPEED_OPTIONS.forEach((speed) => {
        fireEvent.click(screen.getByTestId(`speed-${speed}`));
        expect(screen.getByTestId("speed")).toHaveTextContent(`${speed}x`);
      });
    });
  });

  // ==========================================================================
  // Scenario Selection + Context Integration
  // ==========================================================================

  describe("Scenario Selection Integration", () => {
    it("should update scenario and generate stages", async () => {
      render(
        <DemoProvider>
          <TestScenarioControls />
        </DemoProvider>
      );

      expect(screen.getByTestId("scenario-name")).toHaveTextContent("None");
      expect(screen.getByTestId("stage-count")).toHaveTextContent("0");

      // Open dropdown and select scenario
      const dropdown = screen.getByRole("combobox");
      fireEvent.click(dropdown);

      // Select APT29
      const apt29Option = screen.getByText("APT29 (Cozy Bear)");
      fireEvent.click(apt29Option);

      await waitFor(() => {
        expect(screen.getByTestId("scenario-name")).toHaveTextContent(
          "APT29 (Cozy Bear)"
        );
        expect(screen.getByTestId("stage-count")).toHaveTextContent("8");
      });
    });

    it("should stop playback when changing scenario", async () => {
      render(
        <DemoProvider>
          <TestScenarioControls />
          <TestPlaybackControls />
        </DemoProvider>
      );

      // Select a scenario first
      const dropdown = screen.getByRole("combobox");
      fireEvent.click(dropdown);
      fireEvent.click(screen.getByText("APT29 (Cozy Bear)"));

      // Start playing
      fireEvent.click(screen.getByTestId("play-btn"));
      expect(screen.getByTestId("playState")).toHaveTextContent("playing");

      // Select another scenario
      fireEvent.click(dropdown);
      fireEvent.click(screen.getByText("FIN7"));

      await waitFor(() => {
        expect(screen.getByTestId("playState")).toHaveTextContent("stopped");
      });
    });
  });

  // ==========================================================================
  // Progress Bar + Context Integration
  // ==========================================================================

  describe("Progress Bar Integration", () => {
    it("should advance stages correctly", async () => {
      render(
        <DemoProvider>
          <TestScenarioControls />
          <TestProgressBar />
        </DemoProvider>
      );

      // Select a scenario first
      const dropdown = screen.getByRole("combobox");
      fireEvent.click(dropdown);
      fireEvent.click(screen.getByText("APT29 (Cozy Bear)"));

      await waitFor(() => {
        expect(screen.getByTestId("currentStage")).toHaveTextContent("0");
      });

      // Advance stage
      fireEvent.click(screen.getByTestId("advance-btn"));
      expect(screen.getByTestId("currentStage")).toHaveTextContent("1");

      fireEvent.click(screen.getByTestId("advance-btn"));
      expect(screen.getByTestId("currentStage")).toHaveTextContent("2");
    });

    it("should jump to specific stage", async () => {
      render(
        <DemoProvider>
          <TestScenarioControls />
          <TestProgressBar />
        </DemoProvider>
      );

      // Select a scenario first
      const dropdown = screen.getByRole("combobox");
      fireEvent.click(dropdown);
      fireEvent.click(screen.getByText("APT29 (Cozy Bear)"));

      await waitFor(() => {
        expect(screen.getByTestId("currentStage")).toHaveTextContent("0");
      });

      // Jump to stage 3
      fireEvent.click(screen.getByTestId("jump-btn"));
      expect(screen.getByTestId("currentStage")).toHaveTextContent("3");
    });
  });

  // ==========================================================================
  // Keyboard Shortcuts Integration
  // ==========================================================================

  describe("Keyboard Shortcuts Integration", () => {
    it("should toggle play/pause with Space key", async () => {
      render(
        <DemoProvider>
          <TestKeyboardShortcuts />
        </DemoProvider>
      );

      expect(screen.getByTestId("playState")).toHaveTextContent("stopped");

      // Press Space to play
      fireEvent.keyDown(document, { key: " " });

      await waitFor(() => {
        expect(screen.getByTestId("playState")).toHaveTextContent("playing");
      });

      // Press Space to pause
      fireEvent.keyDown(document, { key: " " });

      await waitFor(() => {
        expect(screen.getByTestId("playState")).toHaveTextContent("paused");
      });
    });

    it("should stop with Escape key", async () => {
      render(
        <DemoProvider>
          <TestKeyboardShortcuts />
        </DemoProvider>
      );

      // Start playing first
      fireEvent.keyDown(document, { key: " " });
      await waitFor(() => {
        expect(screen.getByTestId("playState")).toHaveTextContent("playing");
      });

      // Press Escape to stop
      fireEvent.keyDown(document, { key: "Escape" });

      await waitFor(() => {
        expect(screen.getByTestId("playState")).toHaveTextContent("stopped");
      });
    });

    it("should adjust speed with +/- keys", async () => {
      render(
        <DemoProvider>
          <TestKeyboardShortcuts />
        </DemoProvider>
      );

      expect(screen.getByTestId("speed")).toHaveTextContent("1");

      // Press + to speed up
      fireEvent.keyDown(document, { key: "+" });

      await waitFor(() => {
        expect(screen.getByTestId("speed")).toHaveTextContent("2");
      });

      // Press - to slow down
      fireEvent.keyDown(document, { key: "-" });

      await waitFor(() => {
        expect(screen.getByTestId("speed")).toHaveTextContent("1");
      });
    });
  });

  // ==========================================================================
  // MCP Sync Integration
  // ==========================================================================

  describe("MCP Sync Integration", () => {
    it("should notify callback when local state changes", async () => {
      const onStateChange = vi.fn();

      render(
        <DemoProvider>
          <TestMCPSync onStateChange={onStateChange} />
        </DemoProvider>
      );

      // Register callback
      fireEvent.click(screen.getByTestId("register-btn"));

      // Make local change
      fireEvent.click(screen.getByTestId("local-speed-btn"));

      await waitFor(() => {
        expect(onStateChange).toHaveBeenCalled();
        expect(onStateChange.mock.calls[onStateChange.mock.calls.length - 1][0].speed).toBe(2);
      });
    });

    it("should NOT notify callback when state comes from MCP", async () => {
      const onStateChange = vi.fn();

      render(
        <DemoProvider>
          <TestMCPSync onStateChange={onStateChange} />
        </DemoProvider>
      );

      // Register callback
      fireEvent.click(screen.getByTestId("register-btn"));
      onStateChange.mockClear();

      // Sync from MCP
      fireEvent.click(screen.getByTestId("sync-speed-btn"));

      // Wait a bit
      await new Promise((r) => setTimeout(r, 100));

      // Should NOT have been called for MCP-originated changes
      expect(onStateChange).not.toHaveBeenCalled();
    });

    it("should update state when syncing from MCP", async () => {
      render(
        <DemoProvider>
          <TestMCPSync onStateChange={vi.fn()} />
        </DemoProvider>
      );

      expect(screen.getByTestId("speed")).toHaveTextContent("1");

      // Sync from MCP
      fireEvent.click(screen.getByTestId("sync-speed-btn"));

      await waitFor(() => {
        expect(screen.getByTestId("speed")).toHaveTextContent("4");
      });
    });

    it("should stop notifying after unregister", async () => {
      const onStateChange = vi.fn();

      render(
        <DemoProvider>
          <TestMCPSync onStateChange={onStateChange} />
        </DemoProvider>
      );

      // Register callback
      fireEvent.click(screen.getByTestId("register-btn"));

      // Make a change
      fireEvent.click(screen.getByTestId("local-speed-btn"));
      await waitFor(() => {
        expect(onStateChange).toHaveBeenCalled();
      });

      const callCount = onStateChange.mock.calls.length;

      // Unregister
      fireEvent.click(screen.getByTestId("unregister-btn"));

      // Make another change
      fireEvent.click(screen.getByTestId("select-scenario-btn"));

      // Wait and verify no new calls
      await new Promise((r) => setTimeout(r, 100));
      expect(onStateChange.mock.calls.length).toBe(callCount);
    });
  });

  // ==========================================================================
  // localStorage Persistence Integration
  // ==========================================================================

  describe("localStorage Persistence Integration", () => {
    const localStorageMock = (() => {
      let store: Record<string, string> = {};
      return {
        getItem: vi.fn((key: string) => store[key] ?? null),
        setItem: vi.fn((key: string, value: string) => {
          store[key] = value;
        }),
        removeItem: vi.fn((key: string) => {
          delete store[key];
        }),
        clear: vi.fn(() => {
          store = {};
        }),
        _setStore: (newStore: Record<string, string>) => {
          store = newStore;
        },
      };
    })();

    beforeEach(() => {
      localStorageMock._setStore({});
      Object.defineProperty(window, "localStorage", {
        value: localStorageMock,
        writable: true,
      });
    });

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it("should persist state changes to localStorage", async () => {
      render(
        <DemoProvider persistToStorage>
          <TestSpeedControls />
        </DemoProvider>
      );

      fireEvent.click(screen.getByTestId("speed-4"));

      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalled();
        const lastCall =
          localStorageMock.setItem.mock.calls[
            localStorageMock.setItem.mock.calls.length - 1
          ];
        const saved = JSON.parse(lastCall[1]);
        expect(saved.speed).toBe(4);
      });
    });

    it("should restore state from localStorage on mount", async () => {
      localStorageMock._setStore({
        [DEMO_STORAGE_KEY]: JSON.stringify({
          speed: 2,
          selectedScenario: ATTACK_SCENARIOS[0],
        }),
      });

      render(
        <DemoProvider persistToStorage>
          <TestSpeedControls />
          <TestScenarioControls />
        </DemoProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId("speed")).toHaveTextContent("2x");
      });
    });
  });
});

// ============================================================================
// Helper Components
// ============================================================================

function SecondPlayStateDisplay() {
  const { playState } = useDemoState();
  return <span data-testid="second-playState">{playState}</span>;
}

function SecondSpeedDisplay() {
  const { speed } = useDemoState();
  return <span data-testid="second-speed">{speed}</span>;
}
