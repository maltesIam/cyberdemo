/**
 * Action Queue for User Interaction Deferral.
 *
 * REQ-001-003-005 / T-032
 *
 * Queues incoming agent UI actions while the user is actively interacting
 * (clicking, typing, scrolling). When the user stops interacting, all
 * queued actions are replayed in FIFO order.
 */

export interface ActionQueueOptions {
  /** Maximum number of actions to queue before dropping new ones. Default: 50 */
  maxQueueSize?: number;
}

export interface ActionQueue {
  /** Enqueue an action. Executes immediately if user is not interacting. */
  enqueue: (action: () => void) => void;
  /** Set whether the user is currently interacting. */
  setUserInteracting: (interacting: boolean) => void;
  /** Get the current interacting state. */
  isUserInteracting: () => boolean;
  /** Get the number of queued actions. */
  getQueueSize: () => number;
  /** Clear all queued actions without replaying. */
  clear: () => void;
}

export function createActionQueue(options?: ActionQueueOptions): ActionQueue {
  const maxQueueSize = options?.maxQueueSize ?? 50;

  let queue: Array<() => void> = [];
  let interacting = false;

  function enqueue(action: () => void): void {
    if (!interacting) {
      action();
      return;
    }

    if (queue.length < maxQueueSize) {
      queue.push(action);
    }
    // Drop actions exceeding maxQueueSize
  }

  function replayQueue(): void {
    const pending = [...queue];
    queue = [];
    for (const action of pending) {
      action();
    }
  }

  function setUserInteracting(value: boolean): void {
    const wasInteracting = interacting;
    interacting = value;

    // When user stops interacting, replay all queued actions
    if (wasInteracting && !value) {
      replayQueue();
    }
  }

  function isUserInteracting(): boolean {
    return interacting;
  }

  function getQueueSize(): number {
    return queue.length;
  }

  function clear(): void {
    queue = [];
  }

  return { enqueue, setUserInteracting, isUserInteracting, getQueueSize, clear };
}
