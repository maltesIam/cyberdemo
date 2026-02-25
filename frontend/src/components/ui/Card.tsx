/**
 * Card Component - AgentFlow Design System
 *
 * T-104: Base card (bg-card, border-secondary, radius-xl, space-6)
 * T-105: Interactive card (hover border-primary + shadow + translateY)
 */
import React from 'react';

export interface CardProps {
  children: React.ReactNode;
  interactive?: boolean;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  interactive = false,
  className = '',
  style,
  onClick,
}) => {
  const baseStyle: React.CSSProperties = {
    backgroundColor: 'var(--bg-card)',
    borderColor: 'var(--border-secondary)',
    borderWidth: '1px',
    borderStyle: 'solid',
    borderRadius: 'var(--radius-xl)',
    padding: 'var(--spacing-6)',
    transition: `all var(--duration-normal) var(--ease-default)`,
    cursor: interactive ? 'pointer' : undefined,
    ...style,
  };

  return (
    <div
      data-component="card"
      className={`${interactive ? 'card-interactive' : 'card-base'} ${className}`.trim()}
      style={baseStyle}
      onClick={onClick}
    >
      {children}
    </div>
  );
};
