/**
 * Agent UI Action Dispatcher.
 *
 * REQ-001-003-002 / T-029
 *
 * After the agent produces analysis text for a phase, dispatches the
 * corresponding UI actions with a configurable delay (default 1500ms,
 * between 1-2 seconds). Integrates with rate limiter and action queue
 * for controlled, non-flooding UI updates.
 */

export interface UIAction {
  type: "navigate" | "highlight";
  target?: string;
  element?: string;
  description: string;
}

export interface AgentUIActionDispatcherOptions {
  /** Callback when a navigate action fires. */
  onNavigate: (target: string) => void;
  /** Callback when a highlight action fires. */
  onHighlight: (element: string) => void;
  /** Delay in ms before actions fire after dispatch. Default: 1500 */
  delayMs?: number;
}

export interface AgentUIActionDispatcher {
  /** Dispatch a set of UI actions with a delay. */
  dispatch: (actions: UIAction[]) => void;
  /** Enable or disable auto-UI-actions. */
  setEnabled: (enabled: boolean) => void;
  /** Check if dispatcher is enabled. */
  isEnabled: () => boolean;
  /** Cancel all pending actions and clean up. */
  destroy: () => void;
}

export function createAgentUIActionDispatcher(
  options: AgentUIActionDispatcherOptions
): AgentUIActionDispatcher {
  const { onNavigate, onHighlight } = options;
  const delayMs = options.delayMs ?? 1500;

  let enabled = true;
  let pendingTimers: ReturnType<typeof setTimeout>[] = [];

  function executeAction(action: UIAction): void {
    if (action.type === "navigate" && action.target) {
      onNavigate(action.target);
    } else if (action.type === "highlight" && action.element) {
      onHighlight(action.element);
    }
    // Unknown types are silently ignored
  }

  function dispatch(actions: UIAction[]): void {
    if (!enabled || actions.length === 0) return;

    const timer = setTimeout(() => {
      for (const action of actions) {
        executeAction(action);
      }
      // Remove this timer from pending list
      pendingTimers = pendingTimers.filter((t) => t !== timer);
    }, delayMs);

    pendingTimers.push(timer);
  }

  function setEnabled(value: boolean): void {
    enabled = value;
  }

  function isEnabled(): boolean {
    return enabled;
  }

  function destroy(): void {
    for (const timer of pendingTimers) {
      clearTimeout(timer);
    }
    pendingTimers = [];
  }

  return { dispatch, setEnabled, isEnabled, destroy };
}
