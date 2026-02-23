/**
 * DemoContext localStorage Persistence Tests - TDD
 *
 * Tests for:
 * - REQ-006-002-002: Persistencia de estado entre recargas (localStorage)
 *
 * The DemoContext should:
 * - Save state to localStorage when state changes
 * - Restore state from localStorage on mount
 * - Handle corrupted/invalid localStorage data gracefully
 * - Clear localStorage when demo is reset
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";

// Import types
import type { AttackScenario } from "../../../src/components/demo/types";

// Import context with localStorage support
import {
  DemoProvider,
  useDemoState,
  useDemoActions,
  DEMO_STORAGE_KEY,
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

// Storage mock
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
    get length() {
      return Object.keys(store).length;
    },
    key: vi.fn((index: number) => Object.keys(store)[index] ?? null),
    // Helper for tests
    _getStore: () => store,
    _setStore: (newStore: Record<string, string>) => {
      store = newStore;
    },
  };
})();

// Wrapper component for testing
const TestWrapper = ({ children }: { children: ReactNode }) => (
  <DemoProvider persistToStorage>{children}</DemoProvider>
);

// ============================================================================
// Setup / Teardown
// ============================================================================

describe("DemoContext localStorage Persistence", () => {
  beforeEach(() => {
    // Reset localStorage mock
    localStorageMock._setStore({});
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
    localStorageMock.clear.mockClear();

    // Replace window.localStorage
    Object.defineProperty(window, "localStorage", {
      value: localStorageMock,
      writable: true,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ==========================================================================
  // Storage Key Export
  // ==========================================================================

  describe("Storage Key", () => {
    it("should export DEMO_STORAGE_KEY constant", () => {
      expect(DEMO_STORAGE_KEY).toBeDefined();
      expect(typeof DEMO_STORAGE_KEY).toBe("string");
    });

    it("should have a meaningful storage key name", () => {
      expect(DEMO_STORAGE_KEY).toMatch(/demo/i);
    });
  });

  // ==========================================================================
  // State Persistence
  // ==========================================================================

  describe("State Persistence", () => {
    it("should save state to localStorage when speed changes", () => {
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

      expect(localStorageMock.setItem).toHaveBeenCalled();
      const savedData = JSON.parse(
        localStorageMock.setItem.mock.calls[localStorageMock.setItem.mock.calls.length - 1][1]
      );
      expect(savedData.speed).toBe(2);
    });

    it("should save state to localStorage when scenario is selected", () => {
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

      expect(localStorageMock.setItem).toHaveBeenCalled();
      const savedData = JSON.parse(
        localStorageMock.setItem.mock.calls[localStorageMock.setItem.mock.calls.length - 1][1]
      );
      expect(savedData.selectedScenario?.id).toBe(mockScenario.id);
    });

    it("should not save playState=playing to localStorage", () => {
      // Playing state should not be persisted (user should explicitly restart)
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

      const lastCall =
        localStorageMock.setItem.mock.calls[
          localStorageMock.setItem.mock.calls.length - 1
        ];
      const savedData = JSON.parse(lastCall[1]);

      // Should save as stopped or paused, not playing
      expect(savedData.playState).not.toBe("playing");
    });

    it("should save currentStage to localStorage", () => {
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
        result.current.actions.advanceStage();
      });

      const lastCall =
        localStorageMock.setItem.mock.calls[
          localStorageMock.setItem.mock.calls.length - 1
        ];
      const savedData = JSON.parse(lastCall[1]);
      expect(savedData.currentStage).toBe(2);
    });
  });

  // ==========================================================================
  // State Restoration
  // ==========================================================================

  describe("State Restoration", () => {
    it("should restore speed from localStorage on mount", () => {
      // Pre-populate localStorage
      const savedState = {
        playState: "stopped",
        speed: 4,
        selectedScenario: null,
        currentStage: 0,
        stages: [],
      };
      localStorageMock._setStore({
        [DEMO_STORAGE_KEY]: JSON.stringify(savedState),
      });

      const { result } = renderHook(() => useDemoState(), {
        wrapper: TestWrapper,
      });

      expect(result.current.speed).toBe(4);
    });

    it("should restore selectedScenario from localStorage on mount", () => {
      const savedState = {
        playState: "stopped",
        speed: 1,
        selectedScenario: mockScenario,
        currentStage: 0,
        stages: [],
      };
      localStorageMock._setStore({
        [DEMO_STORAGE_KEY]: JSON.stringify(savedState),
      });

      const { result } = renderHook(() => useDemoState(), {
        wrapper: TestWrapper,
      });

      expect(result.current.selectedScenario?.id).toBe(mockScenario.id);
    });

    it("should restore currentStage from localStorage on mount", () => {
      const savedState = {
        playState: "stopped",
        speed: 1,
        selectedScenario: mockScenario,
        currentStage: 3,
        stages: [],
      };
      localStorageMock._setStore({
        [DEMO_STORAGE_KEY]: JSON.stringify(savedState),
      });

      const { result } = renderHook(() => useDemoState(), {
        wrapper: TestWrapper,
      });

      expect(result.current.currentStage).toBe(3);
    });

    it("should NOT restore playState=playing (always starts stopped)", () => {
      const savedState = {
        playState: "playing", // This should be ignored
        speed: 1,
        selectedScenario: null,
        currentStage: 0,
        stages: [],
        sessionId: "old-session",
        startedAt: "2024-01-01T00:00:00Z",
      };
      localStorageMock._setStore({
        [DEMO_STORAGE_KEY]: JSON.stringify(savedState),
      });

      const { result } = renderHook(() => useDemoState(), {
        wrapper: TestWrapper,
      });

      // Should not restore playing state
      expect(result.current.playState).toBe("stopped");
      // Session should be cleared
      expect(result.current.sessionId).toBeNull();
    });
  });

  // ==========================================================================
  // Error Handling
  // ==========================================================================

  describe("Error Handling", () => {
    it("should use default state if localStorage is empty", () => {
      const { result } = renderHook(() => useDemoState(), {
        wrapper: TestWrapper,
      });

      expect(result.current.playState).toBe("stopped");
      expect(result.current.speed).toBe(1);
      expect(result.current.selectedScenario).toBeNull();
    });

    it("should use default state if localStorage contains invalid JSON", () => {
      localStorageMock._setStore({
        [DEMO_STORAGE_KEY]: "not valid json {{{",
      });

      const { result } = renderHook(() => useDemoState(), {
        wrapper: TestWrapper,
      });

      expect(result.current.playState).toBe("stopped");
      expect(result.current.speed).toBe(1);
    });

    it("should use default state if localStorage contains wrong schema", () => {
      localStorageMock._setStore({
        [DEMO_STORAGE_KEY]: JSON.stringify({
          wrongKey: "wrongValue",
          anotherWrong: 123,
        }),
      });

      const { result } = renderHook(() => useDemoState(), {
        wrapper: TestWrapper,
      });

      expect(result.current.playState).toBe("stopped");
      expect(result.current.speed).toBe(1);
    });

    it("should handle localStorage access errors gracefully", () => {
      localStorageMock.getItem.mockImplementationOnce(() => {
        throw new Error("localStorage access denied");
      });

      // Should not throw, just use defaults
      const { result } = renderHook(() => useDemoState(), {
        wrapper: TestWrapper,
      });

      expect(result.current.playState).toBe("stopped");
    });

    it("should handle localStorage write errors gracefully", () => {
      localStorageMock.setItem.mockImplementationOnce(() => {
        throw new Error("QuotaExceeded");
      });

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      // Should not throw, state should still update
      expect(() => {
        act(() => {
          result.current.actions.setSpeed(2);
        });
      }).not.toThrow();

      expect(result.current.state.speed).toBe(2);
    });
  });

  // ==========================================================================
  // Clear on Reset
  // ==========================================================================

  describe("Clear on Reset", () => {
    it("should clear localStorage when resetDemo is called", () => {
      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: TestWrapper }
      );

      // Set some state
      act(() => {
        result.current.actions.selectScenario(mockScenario);
        result.current.actions.setSpeed(4);
      });

      // Reset
      act(() => {
        result.current.actions.resetDemo();
      });

      expect(localStorageMock.removeItem).toHaveBeenCalledWith(DEMO_STORAGE_KEY);
    });
  });

  // ==========================================================================
  // persistToStorage Prop
  // ==========================================================================

  describe("persistToStorage Prop", () => {
    it("should NOT persist to localStorage when persistToStorage is false", () => {
      const NonPersistingWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider persistToStorage={false}>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: NonPersistingWrapper }
      );

      act(() => {
        result.current.actions.setSpeed(4);
      });

      // Should not call setItem
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
    });

    it("should default persistToStorage to false", () => {
      const DefaultWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
        }),
        { wrapper: DefaultWrapper }
      );

      act(() => {
        result.current.actions.setSpeed(4);
      });

      // Should not call setItem by default
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
    });
  });
});
