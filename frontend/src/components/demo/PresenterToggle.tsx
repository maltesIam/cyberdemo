/**
 * Presenter Toggle Component.
 *
 * REQ-001-003-003 / T-030
 *
 * A toggle switch for the demo control panel that enables/disables
 * auto-UI-actions from the agent. When enabled, the agent's phase
 * analysis will trigger UI navigation and highlighting automatically.
 */

export interface PresenterToggleProps {
  /** Whether auto UI actions are currently enabled. */
  enabled: boolean;
  /** Callback when the toggle is clicked. Receives the new state. */
  onToggle: (enabled: boolean) => void;
}

export function PresenterToggle({ enabled, onToggle }: PresenterToggleProps) {
  const handleClick = () => {
    onToggle(!enabled);
  };

  return (
    <div
      data-testid="presenter-toggle"
      className="flex items-center justify-between py-2"
    >
      <span className="text-xs text-secondary">Auto UI Actions</span>
      <button
        type="button"
        role="switch"
        aria-checked={enabled}
        aria-label="Toggle auto UI actions"
        onClick={handleClick}
        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
          enabled ? "bg-cyan-600" : "bg-tertiary"
        }`}
      >
        <span
          className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
            enabled ? "translate-x-4" : "translate-x-0.5"
          }`}
        />
      </button>
    </div>
  );
}
