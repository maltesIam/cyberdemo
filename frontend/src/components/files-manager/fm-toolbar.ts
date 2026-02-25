/**
 * Files Manager Toolbar - AgentFlow Integration
 *
 * Provides the toolbar HTML template that includes the theme-toggle and
 * font-size-button Lit web components, positioned in the toolbar actions area.
 *
 * T-095: theme-toggle in toolbar
 * T-096: font-size-button in toolbar (left of theme-toggle)
 */

export function getFilesManagerToolbarHTML(): string {
  return `
<div class="fm-toolbar" style="
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-4);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
">
  <div class="toolbar-search">
    <input
      type="text"
      placeholder="Search files..."
      style="
        background: var(--bg-input);
        color: var(--text-primary);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-md);
        padding: var(--space-1) var(--space-3);
        font-family: var(--font-sans);
        font-size: 0.875rem;
      "
    />
  </div>
  <div class="toolbar-actions" style="display: flex; align-items: center; gap: var(--space-2);">
    <font-size-button></font-size-button>
    <theme-toggle></theme-toggle>
  </div>
</div>
`;
}
