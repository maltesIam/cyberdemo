/**
 * MetricCard Component - AgentFlow Design System
 *
 * REQ-004-003-002: Metric card with label (uppercase, tertiary),
 * value (3xl, bold), and change indicator.
 */
import React from 'react';

export interface MetricCardProps {
  label: string;
  value: string;
  change?: number;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  change,
  className = '',
}) => {
  return (
    <div
      data-testid="metric-card"
      className={className}
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: 'var(--border-secondary)',
        borderWidth: '1px',
        borderStyle: 'solid',
        borderRadius: 'var(--radius-xl)',
        padding: 'var(--spacing-6)',
      }}
    >
      <div
        style={{
          fontSize: '0.75rem',
          textTransform: 'uppercase',
          color: 'var(--text-tertiary)',
          fontWeight: '500',
          letterSpacing: '0.05em',
          marginBottom: 'var(--spacing-2)',
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: '1.875rem',
          fontWeight: '700',
          letterSpacing: '-0.02em',
          color: 'var(--text-primary)',
        }}
      >
        {value}
      </div>
      {change !== undefined && (
        <div
          data-testid="metric-change"
          style={{
            fontSize: '0.875rem',
            fontWeight: '500',
            marginTop: 'var(--spacing-1)',
            color: change >= 0 ? 'var(--color-success)' : 'var(--color-error)',
            display: 'flex',
            alignItems: 'center',
            gap: '2px',
          }}
        >
          <span>{change >= 0 ? '\u2191' : '\u2193'}</span>
          <span>{Math.abs(change)}%</span>
        </div>
      )}
    </div>
  );
};
