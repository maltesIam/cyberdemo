/**
 * AgentStatusBadge Component - AgentFlow Design System
 *
 * Task: T-006-001
 * Requirement: REQ-006-001-001
 *
 * Agent status badges with animated pulsing dots for running/error states.
 * Uses CSS variable-based agent status color tokens from design-tokens.css.
 *
 * AC-001: Six status variants: idle (slate), running (blue), success (green), error (red), waiting (amber), queued (cyan)
 * AC-002: Running and error dots have pulse animation (2s infinite)
 * AC-003: Badge uses correct agent status color tokens
 */
import React from 'react';

export type AgentStatus = 'idle' | 'running' | 'success' | 'error' | 'waiting' | 'queued';

interface AgentStatusConfigEntry {
  color: string;
  label: string;
  pulse: boolean;
}

export const AGENT_STATUS_CONFIG: Record<AgentStatus, AgentStatusConfigEntry> = {
  idle: {
    color: 'var(--color-agent-idle)',
    label: 'Idle',
    pulse: false,
  },
  running: {
    color: 'var(--color-agent-running)',
    label: 'Running',
    pulse: true,
  },
  success: {
    color: 'var(--color-agent-success)',
    label: 'Success',
    pulse: false,
  },
  error: {
    color: 'var(--color-agent-error)',
    label: 'Error',
    pulse: true,
  },
  waiting: {
    color: 'var(--color-agent-waiting)',
    label: 'Waiting',
    pulse: false,
  },
  queued: {
    color: 'var(--color-agent-queued)',
    label: 'Queued',
    pulse: false,
  },
};

export interface AgentStatusBadgeProps {
  status: AgentStatus;
  label?: string;
  className?: string;
}

export const AgentStatusBadge: React.FC<AgentStatusBadgeProps> = ({
  status,
  label,
  className = '',
}) => {
  const config = AGENT_STATUS_CONFIG[status];
  const displayLabel = label ?? config.label.toLowerCase();

  const dotStyle: React.CSSProperties = {
    width: '8px',
    height: '8px',
    borderRadius: 'var(--radius-full)',
    backgroundColor: config.color,
    display: 'inline-block',
    flexShrink: 0,
    animation: config.pulse ? 'pulse 2s infinite' : 'none',
  };

  const badgeStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    borderRadius: 'var(--radius-full)',
    fontSize: '0.75rem',
    fontWeight: 500,
    padding: '2px 10px 2px 8px',
    backgroundColor: `color-mix(in srgb, ${config.color} 15%, transparent)`,
    color: config.color,
  };

  return (
    <span
      data-testid={`agent-status-${status}`}
      className={`agent-status-badge ${className}`.trim()}
      style={badgeStyle}
      aria-label={`Agent status: ${status}`}
    >
      <span
        data-testid={`agent-status-${status}-dot`}
        style={dotStyle}
      />
      {displayLabel}
    </span>
  );
};
