/**
 * Unit Tests for Agent UI Actions Rate Limiter (UT-013)
 *
 * Requirement: REQ-001-003-004
 * Task: T-031
 *
 * Rate limit agent UI actions to maximum 2 per second to prevent UI flooding.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { createRateLimiter } from "../../../src/utils/rateLimiter";

describe("rateLimiter", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("should allow actions under the rate limit", () => {
    const limiter = createRateLimiter({ maxPerSecond: 2 });
    const action1 = vi.fn();
    const action2 = vi.fn();

    limiter.execute(action1);
    limiter.execute(action2);

    expect(action1).toHaveBeenCalledTimes(1);
    expect(action2).toHaveBeenCalledTimes(1);
  });

  it("should defer actions exceeding the rate limit", () => {
    const limiter = createRateLimiter({ maxPerSecond: 2 });
    const action1 = vi.fn();
    const action2 = vi.fn();
    const action3 = vi.fn();

    limiter.execute(action1);
    limiter.execute(action2);
    limiter.execute(action3);

    // First two execute immediately
    expect(action1).toHaveBeenCalledTimes(1);
    expect(action2).toHaveBeenCalledTimes(1);
    // Third is deferred
    expect(action3).toHaveBeenCalledTimes(0);
  });

  it("should execute deferred actions after the window resets", () => {
    const limiter = createRateLimiter({ maxPerSecond: 2 });
    const action1 = vi.fn();
    const action2 = vi.fn();
    const action3 = vi.fn();

    limiter.execute(action1);
    limiter.execute(action2);
    limiter.execute(action3);

    // Advance 500ms (half the window)
    vi.advanceTimersByTime(500);
    expect(action3).toHaveBeenCalledTimes(1);
  });

  it("should respect the max-per-second configuration", () => {
    const limiter = createRateLimiter({ maxPerSecond: 1 });
    const action1 = vi.fn();
    const action2 = vi.fn();

    limiter.execute(action1);
    limiter.execute(action2);

    expect(action1).toHaveBeenCalledTimes(1);
    expect(action2).toHaveBeenCalledTimes(0);

    vi.advanceTimersByTime(1000);
    expect(action2).toHaveBeenCalledTimes(1);
  });

  it("should default to 2 actions per second", () => {
    const limiter = createRateLimiter();
    const actions = Array.from({ length: 5 }, () => vi.fn());

    actions.forEach((a) => limiter.execute(a));

    // Only first 2 execute immediately
    expect(actions[0]).toHaveBeenCalledTimes(1);
    expect(actions[1]).toHaveBeenCalledTimes(1);
    expect(actions[2]).toHaveBeenCalledTimes(0);
  });

  it("should drain deferred queue in order", () => {
    const limiter = createRateLimiter({ maxPerSecond: 1 });
    const order: number[] = [];
    const action1 = vi.fn(() => order.push(1));
    const action2 = vi.fn(() => order.push(2));
    const action3 = vi.fn(() => order.push(3));

    limiter.execute(action1);
    limiter.execute(action2);
    limiter.execute(action3);

    expect(order).toEqual([1]);

    vi.advanceTimersByTime(1000);
    expect(order).toEqual([1, 2]);

    vi.advanceTimersByTime(1000);
    expect(order).toEqual([1, 2, 3]);
  });

  it("should report pending count correctly", () => {
    const limiter = createRateLimiter({ maxPerSecond: 1 });

    limiter.execute(vi.fn());
    limiter.execute(vi.fn());
    limiter.execute(vi.fn());

    expect(limiter.getPendingCount()).toBe(2);

    vi.advanceTimersByTime(1000);
    expect(limiter.getPendingCount()).toBe(1);

    vi.advanceTimersByTime(1000);
    expect(limiter.getPendingCount()).toBe(0);
  });

  it("should clear all pending actions when reset is called", () => {
    const limiter = createRateLimiter({ maxPerSecond: 1 });
    const action1 = vi.fn();
    const action2 = vi.fn();
    const action3 = vi.fn();

    limiter.execute(action1);
    limiter.execute(action2);
    limiter.execute(action3);

    limiter.reset();

    vi.advanceTimersByTime(5000);
    expect(action2).toHaveBeenCalledTimes(0);
    expect(action3).toHaveBeenCalledTimes(0);
    expect(limiter.getPendingCount()).toBe(0);
  });

  it("should allow new actions after window passes even without queued items", () => {
    const limiter = createRateLimiter({ maxPerSecond: 2 });
    const action1 = vi.fn();
    const action2 = vi.fn();

    limiter.execute(action1);
    limiter.execute(action2);

    // Wait for window to pass
    vi.advanceTimersByTime(1000);

    const action3 = vi.fn();
    const action4 = vi.fn();

    limiter.execute(action3);
    limiter.execute(action4);

    expect(action3).toHaveBeenCalledTimes(1);
    expect(action4).toHaveBeenCalledTimes(1);
  });
});
