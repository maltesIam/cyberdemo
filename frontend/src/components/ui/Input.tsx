/**
 * Input Component - AgentFlow Design System
 *
 * T-106: Base input (bg-input, border-primary, radius-lg, 36px)
 * T-107: Focus state (border-focus + blue ring)
 * T-108: Error state (red border + red ring)
 * T-109: Placeholder (text-tertiary)
 */
import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

export const Input: React.FC<InputProps> = ({
  error = false,
  className = '',
  style,
  ...props
}) => {
  const baseStyle: React.CSSProperties = {
    backgroundColor: 'var(--bg-input)',
    borderColor: error ? 'var(--color-error)' : 'var(--border-primary)',
    borderWidth: '1px',
    borderStyle: 'solid',
    borderRadius: 'var(--radius-lg)',
    height: '36px',
    padding: '0 var(--space-3)',
    fontSize: '0.875rem',
    fontFamily: 'var(--font-sans)',
    color: 'var(--text-primary)',
    transition: `all var(--duration-normal) var(--ease-default)`,
    outline: 'none',
    width: '100%',
    boxSizing: 'border-box',
    ...style,
  };

  return (
    <input
      className={`${error ? 'input-error' : 'input-base'} ${className}`.trim()}
      style={baseStyle}
      data-focus-ring="true"
      data-placeholder-color="text-tertiary"
      aria-invalid={error ? 'true' : undefined}
      {...props}
    />
  );
};
