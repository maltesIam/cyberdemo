/**
 * Files Manager Epic002 Styles - Hardcoded color fix
 *
 * T-098: Replaces hardcoded inline styles (modal backdrop rgba, shadow values)
 * with CSS custom property references.
 */

export function getFilesEpic002Styles(): string {
  return `
/* Modal overlay - uses CSS custom property instead of hardcoded rgba */
.fm-modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay-backdrop, rgba(0,0,0,0.6));
  backdrop-filter: blur(4px);
  z-index: var(--z-overlay, 300);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Modal container */
.fm-modal {
  background: var(--bg-elevated);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-width: 480px;
  width: 90%;
  padding: var(--space-6);
}

/* Modal header */
.fm-modal-header {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

/* Modal footer */
.fm-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

/* Delete confirmation modal */
.fm-delete-modal .fm-warning-text {
  color: var(--color-error);
  font-size: 0.875rem;
}

/* Upload progress bar */
.fm-upload-progress {
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.fm-upload-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary-600, #2563eb), var(--color-secondary-500, #06b6d4));
  transition: width var(--duration-normal) var(--ease-default);
}

/* Toast notifications */
.fm-toast {
  background: var(--bg-elevated);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-xl);
  padding: var(--space-3) var(--space-4);
  max-width: 380px;
}

/* File action buttons - uses tokens instead of inline styles */
.fm-action-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-md);
  transition: background var(--duration-fast) var(--ease-default),
              color var(--duration-fast) var(--ease-default);
}

.fm-action-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
`;
}
