/**
 * Unit tests for Copilot Action Capture Hooks.
 *
 * REQ-004-001-001: Hook en componentes React para capturar acciones
 * REQ-004-001-002: Throttling de eventos (max 10/segundo)
 *
 * Tests follow TDD methodology - written BEFORE implementation.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";

describe("useCopilotActions Hook", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe("Import Tests", () => {
    it("should export useCopilotActions hook", async () => {
      const module = await import("../../../src/hooks/useCopilotActions");
      expect(module.useCopilotActions).toBeDefined();
      expect(typeof module.useCopilotActions).toBe("function");
    });

    it("should export CopilotActionType enum", async () => {
      const module = await import("../../../src/hooks/useCopilotActions");
      expect(module.CopilotActionType).toBeDefined();
    });

    it("should export CopilotActionContext type", async () => {
      // Types are compile-time only, so we test the interface via usage
      const module = await import("../../../src/hooks/useCopilotActions");
      expect(module.useCopilotActions).toBeDefined();
    });
  });

  describe("CopilotActionType Enum", () => {
    it("should have CLICK action type", async () => {
      const { CopilotActionType } = await import(
        "../../../src/hooks/useCopilotActions"
      );
      expect(CopilotActionType.CLICK).toBe("click");
    });

    it("should have VIEW action type", async () => {
      const { CopilotActionType } = await import(
        "../../../src/hooks/useCopilotActions"
      );
      expect(CopilotActionType.VIEW).toBe("view");
    });

    it("should have SELECT action type", async () => {
      const { CopilotActionType } = await import(
        "../../../src/hooks/useCopilotActions"
      );
      expect(CopilotActionType.SELECT).toBe("select");
    });

    it("should have NAVIGATE action type", async () => {
      const { CopilotActionType } = await import(
        "../../../src/hooks/useCopilotActions"
      );
      expect(CopilotActionType.NAVIGATE).toBe("navigate");
    });

    it("should have SEARCH action type", async () => {
      const { CopilotActionType } = await import(
        "../../../src/hooks/useCopilotActions"
      );
      expect(CopilotActionType.SEARCH).toBe("search");
    });
  });

  describe("Hook Initialization", () => {
    it("should return trackAction function", async () => {
      const { useCopilotActions } = await import(
        "../../../src/hooks/useCopilotActions"
      );
      const { result } = renderHook(() =>
        useCopilotActions({ sessionId: "test-session" })
      );

      expect(result.current.trackAction).toBeDefined();
      expect(typeof result.current.trackAction).toBe("function");
    });

    it("should return isConnected state", async () => {
      const { useCopilotActions } = await import(
        "../../../src/hooks/useCopilotActions"
      );
      const { result } = renderHook(() =>
        useCopilotActions({ sessionId: "test-session" })
      );

      expect(typeof result.current.isConnected).toBe("boolean");
    });

    it("should return actionCount state", async () => {
      const { useCopilotActions } = await import(
        "../../../src/hooks/useCopilotActions"
      );
      const { result } = renderHook(() =>
        useCopilotActions({ sessionId: "test-session" })
      );

      expect(typeof result.current.actionCount).toBe("number");
      expect(result.current.actionCount).toBe(0);
    });
  });

  describe("Action Tracking", () => {
    it("should track a click action", async () => {
      const { useCopilotActions, CopilotActionType } = await import(
        "../../../src/hooks/useCopilotActions"
      );
      const { result } = renderHook(() =>
        useCopilotActions({ sessionId: "test-session" })
      );

      act(() => {
        result.current.trackAction({
          action: CopilotActionType.CLICK,
          element: "button",
        });
      });

      expect(result.current.actionCount).toBe(1);
    });

    it("should track multiple actions", async () => {
      const { useCopilotActions, CopilotActionType } = await import(
        "../../../src/hooks/useCopilotActions"
      );
      const { result } = renderHook(() =>
        useCopilotActions({ sessionId: "test-session" })
      );

      act(() => {
        result.current.trackAction({
          action: CopilotActionType.CLICK,
          element: "button1",
        });
        result.current.trackAction({
          action: CopilotActionType.VIEW,
          element: "panel",
        });
        result.current.trackAction({
          action: CopilotActionType.SELECT,
          element: "row",
        });
      });

      expect(result.current.actionCount).toBe(3);
    });

    it("should include visible data in action context", async () => {
      const { useCopilotActions, CopilotActionType } = await import(
        "../../../src/hooks/useCopilotActions"
      );

      const onAction = vi.fn();
      const { result } = renderHook(() =>
        useCopilotActions({
          sessionId: "test-session",
          onAction,
        })
      );

      const visibleData = { alertId: "ALT-001", severity: "critical" };

      act(() => {
        result.current.trackAction({
          action: CopilotActionType.SELECT,
          element: "alert-row",
          visibleData,
        });
      });

      expect(onAction).toHaveBeenCalledWith(
        expect.objectContaining({
          visibleData,
        })
      );
    });
  });
});

describe("useThrottle Hook", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe("Import Tests", () => {
    it("should export useThrottle hook", async () => {
      const module = await import("../../../src/hooks/useThrottle");
      expect(module.useThrottle).toBeDefined();
      expect(typeof module.useThrottle).toBe("function");
    });
  });

  describe("Throttle Behavior", () => {
    it("should allow first call immediately", async () => {
      const { useThrottle } = await import("../../../src/hooks/useThrottle");
      const callback = vi.fn();

      const { result } = renderHook(() => useThrottle(callback, 100));

      act(() => {
        result.current();
      });

      expect(callback).toHaveBeenCalledTimes(1);
    });

    it("should throttle rapid calls", async () => {
      const { useThrottle } = await import("../../../src/hooks/useThrottle");
      const callback = vi.fn();

      const { result } = renderHook(() => useThrottle(callback, 100));

      act(() => {
        result.current();
        result.current();
        result.current();
        result.current();
      });

      // Only first call should execute immediately
      expect(callback).toHaveBeenCalledTimes(1);
    });

    it("should allow calls after throttle period", async () => {
      const { useThrottle } = await import("../../../src/hooks/useThrottle");
      const callback = vi.fn();

      const { result } = renderHook(() => useThrottle(callback, 100));

      act(() => {
        result.current();
      });

      expect(callback).toHaveBeenCalledTimes(1);

      // Advance time past throttle period
      act(() => {
        vi.advanceTimersByTime(150);
      });

      act(() => {
        result.current();
      });

      expect(callback).toHaveBeenCalledTimes(2);
    });
  });
});

describe("Rate Limiting (REQ-004-001-002: max 10/sec)", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("should limit actions to 10 per second", async () => {
    const { useCopilotActions, CopilotActionType } = await import(
      "../../../src/hooks/useCopilotActions"
    );

    const onAction = vi.fn();
    const { result } = renderHook(() =>
      useCopilotActions({
        sessionId: "test-session",
        maxActionsPerSecond: 10,
        onAction,
      })
    );

    // Try to fire 20 actions rapidly
    act(() => {
      for (let i = 0; i < 20; i++) {
        result.current.trackAction({
          action: CopilotActionType.CLICK,
          element: `button-${i}`,
        });
      }
    });

    // Only 10 should have been processed
    expect(onAction.mock.calls.length).toBeLessThanOrEqual(10);
  });

  it("should reset rate limit after 1 second", async () => {
    const { useCopilotActions, CopilotActionType } = await import(
      "../../../src/hooks/useCopilotActions"
    );

    const onAction = vi.fn();
    const { result } = renderHook(() =>
      useCopilotActions({
        sessionId: "test-session",
        maxActionsPerSecond: 10,
        onAction,
      })
    );

    // Fire 10 actions (should all pass)
    act(() => {
      for (let i = 0; i < 10; i++) {
        result.current.trackAction({
          action: CopilotActionType.CLICK,
          element: `button-${i}`,
        });
      }
    });

    const firstBatchCount = onAction.mock.calls.length;

    // Advance time by 1 second
    act(() => {
      vi.advanceTimersByTime(1000);
    });

    // Fire 10 more actions
    act(() => {
      for (let i = 0; i < 10; i++) {
        result.current.trackAction({
          action: CopilotActionType.CLICK,
          element: `button-${i + 10}`,
        });
      }
    });

    // Should have processed both batches
    expect(onAction.mock.calls.length).toBeGreaterThan(firstBatchCount);
  });

  it("should provide rate limit status", async () => {
    const { useCopilotActions, CopilotActionType } = await import(
      "../../../src/hooks/useCopilotActions"
    );

    const { result } = renderHook(() =>
      useCopilotActions({
        sessionId: "test-session",
        maxActionsPerSecond: 10,
      })
    );

    expect(result.current.isRateLimited).toBe(false);

    // Fire 10 actions to hit the limit
    act(() => {
      for (let i = 0; i < 10; i++) {
        result.current.trackAction({
          action: CopilotActionType.CLICK,
          element: `button-${i}`,
        });
      }
    });

    expect(result.current.isRateLimited).toBe(true);
  });
});
