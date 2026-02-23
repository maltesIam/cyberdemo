/**
 * DemoContext MCP Sync Tests - TDD
 *
 * Tests for:
 * - REQ-006-002-003: Sync de estado con MCP Frontend Server
 *
 * The DemoContext should sync with MCP Frontend Server:
 * - Send state changes to MCP via callback/hook
 * - Receive state updates from MCP commands
 * - Handle sync errors gracefully
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";

// Import types
import type { AttackScenario, DemoState } from "../../../src/components/demo/types";

// Import context with MCP sync support
import {
  DemoProvider,
  useDemoState,
  useDemoActions,
  useDemoMCPSync,
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

// Mock MCP sync callback
const mockMCPSyncCallback = vi.fn();

// ============================================================================
// Tests
// ============================================================================

describe("DemoContext MCP Sync", () => {
  beforeEach(() => {
    mockMCPSyncCallback.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ==========================================================================
  // useDemoMCPSync Hook
  // ==========================================================================

  describe("useDemoMCPSync Hook", () => {
    it("should export useDemoMCPSync hook", () => {
      expect(useDemoMCPSync).toBeDefined();
      expect(typeof useDemoMCPSync).toBe("function");
    });

    it("should return sync functions", () => {
      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(() => useDemoMCPSync(), {
        wrapper: SyncTestWrapper,
      });

      expect(result.current.registerSyncCallback).toBeDefined();
      expect(result.current.unregisterSyncCallback).toBeDefined();
      expect(result.current.syncFromMCP).toBeDefined();
    });
  });

  // ==========================================================================
  // Outbound Sync (DemoContext -> MCP)
  // ==========================================================================

  describe("Outbound Sync (DemoContext -> MCP)", () => {
    it("should call registered sync callback when speed changes", async () => {
      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      // Register callback
      act(() => {
        result.current.sync.registerSyncCallback(mockMCPSyncCallback);
      });

      // Change speed
      act(() => {
        result.current.actions.setSpeed(2);
      });

      await waitFor(() => {
        expect(mockMCPSyncCallback).toHaveBeenCalled();
      });

      const lastCall = mockMCPSyncCallback.mock.calls[mockMCPSyncCallback.mock.calls.length - 1];
      expect(lastCall[0].speed).toBe(2);
    });

    it("should call registered sync callback when scenario is selected", async () => {
      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      act(() => {
        result.current.sync.registerSyncCallback(mockMCPSyncCallback);
      });

      act(() => {
        result.current.actions.selectScenario(mockScenario);
      });

      await waitFor(() => {
        expect(mockMCPSyncCallback).toHaveBeenCalled();
      });

      const lastCall = mockMCPSyncCallback.mock.calls[mockMCPSyncCallback.mock.calls.length - 1];
      expect(lastCall[0].selectedScenario?.id).toBe(mockScenario.id);
    });

    it("should call registered sync callback when playState changes", async () => {
      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      act(() => {
        result.current.sync.registerSyncCallback(mockMCPSyncCallback);
      });

      act(() => {
        result.current.actions.play();
      });

      await waitFor(() => {
        expect(mockMCPSyncCallback).toHaveBeenCalled();
      });

      const lastCall = mockMCPSyncCallback.mock.calls[mockMCPSyncCallback.mock.calls.length - 1];
      expect(lastCall[0].playState).toBe("playing");
    });

    it("should not call callback after unregistering", async () => {
      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      act(() => {
        result.current.sync.registerSyncCallback(mockMCPSyncCallback);
      });

      act(() => {
        result.current.actions.setSpeed(2);
      });

      await waitFor(() => {
        expect(mockMCPSyncCallback).toHaveBeenCalled();
      });

      const callCount = mockMCPSyncCallback.mock.calls.length;

      // Unregister
      act(() => {
        result.current.sync.unregisterSyncCallback(mockMCPSyncCallback);
      });

      // Make another change
      act(() => {
        result.current.actions.setSpeed(4);
      });

      // Wait a bit and verify no new calls
      await new Promise((r) => setTimeout(r, 50));
      expect(mockMCPSyncCallback.mock.calls.length).toBe(callCount);
    });

    it("should support multiple sync callbacks", async () => {
      const callback1 = vi.fn();
      const callback2 = vi.fn();

      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      act(() => {
        result.current.sync.registerSyncCallback(callback1);
        result.current.sync.registerSyncCallback(callback2);
      });

      act(() => {
        result.current.actions.setSpeed(2);
      });

      await waitFor(() => {
        expect(callback1).toHaveBeenCalled();
        expect(callback2).toHaveBeenCalled();
      });
    });
  });

  // ==========================================================================
  // Inbound Sync (MCP -> DemoContext)
  // ==========================================================================

  describe("Inbound Sync (MCP -> DemoContext)", () => {
    it("should update state when syncFromMCP is called with valid data", () => {
      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      expect(result.current.state.speed).toBe(1);

      act(() => {
        result.current.sync.syncFromMCP({
          speed: 4,
        });
      });

      expect(result.current.state.speed).toBe(4);
    });

    it("should update scenario when syncFromMCP is called", () => {
      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      act(() => {
        result.current.sync.syncFromMCP({
          selectedScenario: mockScenario,
        });
      });

      expect(result.current.state.selectedScenario?.id).toBe(mockScenario.id);
    });

    it("should update playState when syncFromMCP is called", () => {
      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      act(() => {
        result.current.sync.syncFromMCP({
          playState: "playing",
        });
      });

      expect(result.current.state.playState).toBe("playing");
    });

    it("should update currentStage when syncFromMCP is called", () => {
      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      // First set up scenario
      act(() => {
        result.current.actions.selectScenario(mockScenario);
      });

      act(() => {
        result.current.sync.syncFromMCP({
          currentStage: 5,
        });
      });

      expect(result.current.state.currentStage).toBe(5);
    });

    it("should NOT trigger outbound sync when updating from MCP", async () => {
      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      act(() => {
        result.current.sync.registerSyncCallback(mockMCPSyncCallback);
      });

      // Clear any initial calls
      mockMCPSyncCallback.mockClear();

      // Sync from MCP
      act(() => {
        result.current.sync.syncFromMCP({
          speed: 4,
        });
      });

      // Wait a bit
      await new Promise((r) => setTimeout(r, 50));

      // Callback should NOT be called for MCP-originated updates
      // (to prevent infinite loops)
      expect(mockMCPSyncCallback).not.toHaveBeenCalled();
    });

    it("should ignore invalid/unknown properties in syncFromMCP", () => {
      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      const initialState = { ...result.current.state };

      act(() => {
        result.current.sync.syncFromMCP({
          unknownProperty: "should be ignored",
          anotherUnknown: 123,
        } as Partial<DemoState>);
      });

      // State should remain unchanged for invalid properties
      expect(result.current.state.speed).toBe(initialState.speed);
      expect(result.current.state.playState).toBe(initialState.playState);
    });
  });

  // ==========================================================================
  // Error Handling
  // ==========================================================================

  describe("Error Handling", () => {
    it("should handle sync callback errors gracefully", async () => {
      const errorCallback = vi.fn().mockImplementation(() => {
        throw new Error("Sync error");
      });

      const SyncTestWrapper = ({ children }: { children: ReactNode }) => (
        <DemoProvider>{children}</DemoProvider>
      );

      const { result } = renderHook(
        () => ({
          state: useDemoState(),
          actions: useDemoActions(),
          sync: useDemoMCPSync(),
        }),
        { wrapper: SyncTestWrapper }
      );

      act(() => {
        result.current.sync.registerSyncCallback(errorCallback);
      });

      // Should not throw
      expect(() => {
        act(() => {
          result.current.actions.setSpeed(2);
        });
      }).not.toThrow();

      // State should still update
      expect(result.current.state.speed).toBe(2);
    });
  });
});
