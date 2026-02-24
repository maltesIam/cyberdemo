/**
 * Rate Limiter for Agent UI Actions.
 *
 * REQ-001-003-004 / T-031
 *
 * Limits agent UI actions to a configurable maximum per second
 * (default: 2) to prevent UI flooding. Actions exceeding the limit
 * are queued and executed when the rate window resets.
 */

export interface RateLimiterOptions {
  /** Maximum number of actions allowed per second. Default: 2 */
  maxPerSecond?: number;
}

export interface RateLimiter {
  /** Execute an action, deferring it if the rate limit is reached. */
  execute: (action: () => void) => void;
  /** Get the count of pending (deferred) actions in the queue. */
  getPendingCount: () => number;
  /** Clear all pending actions and reset state. */
  reset: () => void;
}

export function createRateLimiter(options?: RateLimiterOptions): RateLimiter {
  const maxPerSecond = options?.maxPerSecond ?? 2;
  const windowMs = 1000 / maxPerSecond;

  let queue: Array<() => void> = [];
  let executedInWindow = 0;
  let windowStart = 0;
  let drainTimer: ReturnType<typeof setTimeout> | null = null;

  function scheduleNext(): void {
    if (queue.length === 0) return;
    if (drainTimer !== null) return;

    const now = Date.now();
    const elapsed = now - windowStart;
    const delay = Math.max(0, windowMs - elapsed);

    drainTimer = setTimeout(() => {
      drainTimer = null;
      windowStart = Date.now();
      executedInWindow = 0;

      const next = queue.shift();
      if (next) {
        executedInWindow++;
        next();
      }

      if (queue.length > 0) {
        scheduleNext();
      }
    }, delay);
  }

  function execute(action: () => void): void {
    const now = Date.now();

    // Reset window if enough time has passed
    if (now - windowStart >= windowMs) {
      windowStart = now;
      executedInWindow = 0;
    }

    if (executedInWindow < maxPerSecond) {
      executedInWindow++;
      action();
    } else {
      queue.push(action);
      scheduleNext();
    }
  }

  function getPendingCount(): number {
    return queue.length;
  }

  function reset(): void {
    if (drainTimer !== null) {
      clearTimeout(drainTimer);
      drainTimer = null;
    }
    queue = [];
    executedInWindow = 0;
    windowStart = 0;
  }

  return { execute, getPendingCount, reset };
}
