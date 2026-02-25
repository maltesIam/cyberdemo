/**
 * Button Component - AgentFlow Design System
 *
 * T-099: Primary button (primary-600 bg, hover primary-700 + translateY)
 * T-100: Destructive button (color-error bg, hover error-dark)
 * T-101: Sizes (sm=32px, md=36px, lg=44px)
 * T-102: Focus ring (2px outline primary-500)
 * T-103: Disabled (opacity 0.5, cursor-not-allowed)
 */
import React from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'destructive' | 'accent';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const SIZE_MAP: Record<ButtonSize, { height: string; fontSize: string; padding: string }> = {
  sm: { height: '32px', fontSize: '0.75rem', padding: '6px 12px' },
  md: { height: '36px', fontSize: '0.875rem', padding: '8px 16px' },
  lg: { height: '44px', fontSize: '1rem', padding: '10px 20px' },
};

const VARIANT_STYLES: Record<ButtonVariant, { backgroundColor: string; color: string }> = {
  primary: { backgroundColor: 'var(--color-primary-600)', color: 'white' },
  secondary: { backgroundColor: 'transparent', color: 'var(--text-primary)' },
  ghost: { backgroundColor: 'transparent', color: 'var(--text-secondary)' },
  destructive: { backgroundColor: 'var(--color-error)', color: 'white' },
  accent: { backgroundColor: 'var(--color-secondary-600)', color: 'white' },
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled,
  children,
  className = '',
  style,
  ...props
}) => {
  const sizeStyles = SIZE_MAP[size];
  const variantStyles = VARIANT_STYLES[variant];

  const baseStyle: React.CSSProperties = {
    height: sizeStyles.height,
    fontSize: sizeStyles.fontSize,
    padding: sizeStyles.padding,
    backgroundColor: variantStyles.backgroundColor,
    color: variantStyles.color,
    border: 'none',
    borderRadius: 'var(--radius-lg)',
    fontFamily: 'var(--font-sans)',
    fontWeight: 500,
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    transition: `all var(--duration-normal) var(--ease-default)`,
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 'var(--space-2)',
    ...style,
  };

  return (
    <button
      className={`btn-${variant} ${className}`.trim()}
      style={baseStyle}
      disabled={disabled}
      data-focus-ring="true"
      {...props}
    >
      {children}
    </button>
  );
};
