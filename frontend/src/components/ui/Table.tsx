/**
 * Table Component - AgentFlow Design System
 *
 * T-110: Headers (bg-tertiary, text-xs, uppercase)
 * T-111: Rows (text-sm, border-secondary, hover bg-hover)
 */
import React from 'react';

export interface TableProps {
  children: React.ReactNode;
  className?: string;
}

export const Table: React.FC<TableProps> = ({ children, className = '' }) => {
  return (
    <table
      className={className}
      style={{
        width: '100%',
        borderCollapse: 'collapse',
        borderSpacing: 0,
        borderColor: 'var(--border-secondary)',
        borderWidth: '1px',
        borderStyle: 'solid',
        borderRadius: 'var(--radius-xl)',
        overflow: 'hidden',
      }}
    >
      {children}
    </table>
  );
};

export interface TableHeaderProps {
  columns: string[];
}

export const TableHeader: React.FC<TableHeaderProps> = ({ columns }) => {
  return (
    <thead style={{ backgroundColor: 'var(--bg-tertiary)' }}>
      <tr>
        {columns.map((col, idx) => (
          <th
            key={idx}
            style={{
              textTransform: 'uppercase',
              fontSize: '0.75rem',
              fontWeight: 500,
              letterSpacing: '0.05em',
              color: 'var(--text-secondary)',
              padding: 'var(--space-3) var(--space-4)',
              textAlign: 'left',
            }}
          >
            {col}
          </th>
        ))}
      </tr>
    </thead>
  );
};

export interface TableRowProps {
  cells: React.ReactNode[];
}

export const TableRow: React.FC<TableRowProps> = ({ cells }) => {
  return (
    <tr
      style={{
        borderBottomWidth: '1px',
        borderBottomStyle: 'solid',
        borderBottomColor: 'var(--border-secondary)',
        transition: `background var(--duration-fast) var(--ease-default)`,
      }}
    >
      {cells.map((cell, idx) => (
        <td
          key={idx}
          style={{
            fontSize: '0.875rem',
            color: 'var(--text-primary)',
            padding: 'var(--space-3) var(--space-4)',
          }}
        >
          {cell}
        </td>
      ))}
    </tr>
  );
};
