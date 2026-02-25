/**
 * Badge Component - AgentFlow Design System
 *
 * T-112: Badges (pill shape, text-xs, semantic 15% opacity bg)
 */
import React from 'react';

export type BadgeVariant = 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

const VARIANT_STYLES: Record<BadgeVariant, { backgroundColor: string; color: string }> = {
  default: { backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-secondary)' },
  primary: { backgroundColor: 'rgba(59, 130, 246, 0.15)', color: 'var(--color-primary-400)' },
  secondary: { backgroundColor: 'rgba(6, 182, 212, 0.15)', color: 'var(--color-secondary-400)' },
  success: { backgroundColor: 'rgba(34, 197, 94, 0.15)', color: 'var(--color-success)' },
  warning: { backgroundColor: 'rgba(245, 158, 11, 0.15)', color: 'var(--color-accent-400)' },
  error: { backgroundColor: 'rgba(239, 68, 68, 0.15)', color: 'var(--color-error)' },
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  className = '',
}) => {
  const variantStyle = VARIANT_STYLES[variant];

  return (
    <span
      className={`badge-${variant} ${className}`.trim()}
      style={{
        borderRadius: 'var(--radius-full)',
        fontSize: '0.75rem',
        fontWeight: 500,
        padding: '2px 8px',
        display: 'inline-flex',
        alignItems: 'center',
        backgroundColor: variantStyle.backgroundColor,
        color: variantStyle.color,
      }}
    >
      {children}
    </span>
  );
};
