/**
 * Unit Tests for Agent UI Actions Trigger (UT-011)
 *
 * Requirement: REQ-001-003-002
 * Task: T-029
 *
 * After the agent produces analysis text for a phase, the corresponding
 * UI actions fire with a 1-2 second delay. Uses UIBridge for sending
 * UI commands and integrates with the rate limiter and action queue.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  createAgentUIActionDispatcher,
  type UIAction,
  type AgentUIActionDispatcher,
} from "../../../src/services/agentUIActions";

describe("agentUIActions", () => {
  let dispatcher: AgentUIActionDispatcher;
  let mockNavigate: ReturnType<typeof vi.fn>;
  let mockHighlight: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.useFakeTimers();
    mockNavigate = vi.fn();
    mockHighlight = vi.fn();

    dispatcher = createAgentUIActionDispatcher({
      onNavigate: mockNavigate,
      onHighlight: mockHighlight,
    });
  });

  afterEach(() => {
    dispatcher.destroy();
    vi.useRealTimers();
  });

  it("should not fire actions immediately after dispatch", () => {
    const actions: UIAction[] = [
      { type: "navigate", target: "incidents", description: "Go to incidents" },
    ];

    dispatcher.dispatch(actions);

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it("should fire navigate actions after the configured delay", () => {
    const actions: UIAction[] = [
      { type: "navigate", target: "incidents", description: "Go to incidents" },
    ];

    dispatcher.dispatch(actions);

    // Default delay is 1500ms (between 1-2 seconds)
    vi.advanceTimersByTime(1500);

    expect(mockNavigate).toHaveBeenCalledWith("incidents");
  });

  it("should fire highlight actions after the delay", () => {
    const actions: UIAction[] = [
      { type: "highlight", element: "source_ip", description: "Highlight IP" },
    ];

    dispatcher.dispatch(actions);

    vi.advanceTimersByTime(1500);

    expect(mockHighlight).toHaveBeenCalledWith("source_ip");
  });

  it("should fire both navigate and highlight for a phase", () => {
    const actions: UIAction[] = [
      { type: "navigate", target: "incidents", description: "Go to incidents" },
      { type: "highlight", element: "source_ip", description: "Highlight IP" },
    ];

    dispatcher.dispatch(actions);

    vi.advanceTimersByTime(1500);

    expect(mockNavigate).toHaveBeenCalledWith("incidents");
    expect(mockHighlight).toHaveBeenCalledWith("source_ip");
  });

  it("should use custom delay when configured", () => {
    dispatcher.destroy();
    dispatcher = createAgentUIActionDispatcher({
      onNavigate: mockNavigate,
      onHighlight: mockHighlight,
      delayMs: 2000,
    });

    const actions: UIAction[] = [
      { type: "navigate", target: "assets", description: "Go to assets" },
    ];

    dispatcher.dispatch(actions);

    vi.advanceTimersByTime(1500);
    expect(mockNavigate).not.toHaveBeenCalled();

    vi.advanceTimersByTime(500);
    expect(mockNavigate).toHaveBeenCalledWith("assets");
  });

  it("should not fire actions when disabled", () => {
    dispatcher.setEnabled(false);

    const actions: UIAction[] = [
      { type: "navigate", target: "incidents", description: "Go to incidents" },
    ];

    dispatcher.dispatch(actions);

    vi.advanceTimersByTime(3000);

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it("should fire actions when re-enabled", () => {
    dispatcher.setEnabled(false);
    dispatcher.setEnabled(true);

    const actions: UIAction[] = [
      { type: "navigate", target: "incidents", description: "Go to incidents" },
    ];

    dispatcher.dispatch(actions);

    vi.advanceTimersByTime(1500);

    expect(mockNavigate).toHaveBeenCalledWith("incidents");
  });

  it("should report enabled state correctly", () => {
    expect(dispatcher.isEnabled()).toBe(true);

    dispatcher.setEnabled(false);
    expect(dispatcher.isEnabled()).toBe(false);

    dispatcher.setEnabled(true);
    expect(dispatcher.isEnabled()).toBe(true);
  });

  it("should cancel pending actions on destroy", () => {
    const actions: UIAction[] = [
      { type: "navigate", target: "incidents", description: "Go to incidents" },
    ];

    dispatcher.dispatch(actions);
    dispatcher.destroy();

    vi.advanceTimersByTime(3000);

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it("should handle empty action arrays gracefully", () => {
    dispatcher.dispatch([]);

    vi.advanceTimersByTime(3000);

    expect(mockNavigate).not.toHaveBeenCalled();
    expect(mockHighlight).not.toHaveBeenCalled();
  });

  it("should handle unknown action types gracefully", () => {
    const actions = [
      { type: "unknown_type" as "navigate", target: "x", description: "test" },
    ];

    // Should not throw
    dispatcher.dispatch(actions);
    vi.advanceTimersByTime(1500);

    // Unknown type is silently ignored
    expect(mockNavigate).not.toHaveBeenCalled();
    expect(mockHighlight).not.toHaveBeenCalled();
  });
});
