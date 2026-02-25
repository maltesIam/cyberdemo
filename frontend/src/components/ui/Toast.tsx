/**
 * Toast Component - AgentFlow Design System
 *
 * T-113: Toasts (bg-elevated, border-primary, shadow-lg, 380px)
 * T-123: Toast role="status" for accessibility
 */
import React from 'react';

export type ToastVariant = 'info' | 'success' | 'warning' | 'error';

export interface ToastProps {
  message: string;
  variant?: ToastVariant;
  onClose?: () => void;
}

export const Toast: React.FC<ToastProps> = ({
  message,
  variant = 'info',
  onClose,
}) => {
  return (
    <div
      role="status"
      aria-live="polite"
      className={`toast-${variant}`}
      style={{
        backgroundColor: 'var(--bg-elevated)',
        borderColor: 'var(--border-primary)',
        borderWidth: '1px',
        borderStyle: 'solid',
        boxShadow: 'var(--shadow-lg)',
        borderRadius: 'var(--radius-xl)',
        padding: 'var(--space-3) var(--space-4)',
        maxWidth: '380px',
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-3)',
        fontFamily: 'var(--font-sans)',
        fontSize: '0.875rem',
        color: 'var(--text-primary)',
      }}
    >
      <span style={{ flex: 1 }}>{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          aria-label="Close notification"
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-tertiary)',
            cursor: 'pointer',
            padding: 'var(--space-1)',
          }}
        >
          x
        </button>
      )}
    </div>
  );
};
