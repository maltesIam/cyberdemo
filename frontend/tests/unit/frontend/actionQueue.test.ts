/**
 * Unit Tests for Action Queue During User Interaction (UT-014)
 *
 * Requirement: REQ-001-003-005
 * Task: T-032
 *
 * If the user is interacting (clicking, typing), queue incoming agent UI
 * actions and replay them when interaction ends.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { createActionQueue } from "../../../src/utils/actionQueue";

describe("actionQueue", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("should execute actions immediately when user is NOT interacting", () => {
    const queue = createActionQueue();
    const action = vi.fn();

    queue.enqueue(action);

    expect(action).toHaveBeenCalledTimes(1);
  });

  it("should queue actions when user IS interacting", () => {
    const queue = createActionQueue();
    const action = vi.fn();

    queue.setUserInteracting(true);
    queue.enqueue(action);

    expect(action).toHaveBeenCalledTimes(0);
  });

  it("should replay queued actions when user stops interacting", () => {
    const queue = createActionQueue();
    const action1 = vi.fn();
    const action2 = vi.fn();

    queue.setUserInteracting(true);
    queue.enqueue(action1);
    queue.enqueue(action2);

    expect(action1).toHaveBeenCalledTimes(0);
    expect(action2).toHaveBeenCalledTimes(0);

    queue.setUserInteracting(false);

    expect(action1).toHaveBeenCalledTimes(1);
    expect(action2).toHaveBeenCalledTimes(1);
  });

  it("should replay actions in FIFO order", () => {
    const queue = createActionQueue();
    const order: number[] = [];

    queue.setUserInteracting(true);
    queue.enqueue(() => order.push(1));
    queue.enqueue(() => order.push(2));
    queue.enqueue(() => order.push(3));

    queue.setUserInteracting(false);

    expect(order).toEqual([1, 2, 3]);
  });

  it("should return the current queue size", () => {
    const queue = createActionQueue();

    queue.setUserInteracting(true);
    queue.enqueue(vi.fn());
    queue.enqueue(vi.fn());

    expect(queue.getQueueSize()).toBe(2);
  });

  it("should return 0 queue size when not interacting", () => {
    const queue = createActionQueue();
    queue.enqueue(vi.fn()); // executes immediately

    expect(queue.getQueueSize()).toBe(0);
  });

  it("should clear the queue without replaying", () => {
    const queue = createActionQueue();
    const action = vi.fn();

    queue.setUserInteracting(true);
    queue.enqueue(action);

    queue.clear();

    queue.setUserInteracting(false);
    expect(action).toHaveBeenCalledTimes(0);
    expect(queue.getQueueSize()).toBe(0);
  });

  it("should report interacting state correctly", () => {
    const queue = createActionQueue();

    expect(queue.isUserInteracting()).toBe(false);

    queue.setUserInteracting(true);
    expect(queue.isUserInteracting()).toBe(true);

    queue.setUserInteracting(false);
    expect(queue.isUserInteracting()).toBe(false);
  });

  it("should handle rapid interacting state changes correctly", () => {
    const queue = createActionQueue();
    const action1 = vi.fn();
    const action2 = vi.fn();

    queue.setUserInteracting(true);
    queue.enqueue(action1);
    queue.setUserInteracting(false); // replays action1
    expect(action1).toHaveBeenCalledTimes(1);

    queue.setUserInteracting(true);
    queue.enqueue(action2);
    queue.setUserInteracting(false); // replays action2
    expect(action2).toHaveBeenCalledTimes(1);
  });

  it("should limit queue size to prevent memory overflow", () => {
    const queue = createActionQueue({ maxQueueSize: 3 });

    queue.setUserInteracting(true);
    queue.enqueue(vi.fn());
    queue.enqueue(vi.fn());
    queue.enqueue(vi.fn());
    queue.enqueue(vi.fn()); // this one should be dropped

    expect(queue.getQueueSize()).toBe(3);
  });

  it("should default to 50 max queue size", () => {
    const queue = createActionQueue();

    queue.setUserInteracting(true);
    for (let i = 0; i < 60; i++) {
      queue.enqueue(vi.fn());
    }

    expect(queue.getQueueSize()).toBe(50);
  });
});
