/**
 * Tabs Component - AgentFlow Design System
 *
 * REQ-004-004-002: Horizontal tabs with text-sm, weight-medium,
 * 2px bottom border, active state with primary-400.
 */
import React from 'react';

export interface TabItem {
  id: string;
  label: string;
}

export interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onTabChange,
  className = '',
}) => {
  return (
    <div
      role="tablist"
      className={className}
      style={{
        display: 'flex',
        gap: 'var(--spacing-6)',
        borderBottomWidth: '1px',
        borderBottomStyle: 'solid',
        borderBottomColor: 'var(--border-secondary)',
      }}
    >
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            onClick={() => onTabChange(tab.id)}
            style={{
              fontSize: '0.875rem',
              fontWeight: '500',
              color: isActive ? 'var(--color-primary-400)' : 'var(--text-secondary)',
              borderTop: 'none',
              borderLeft: 'none',
              borderRight: 'none',
              borderBottomWidth: '2px',
              borderBottomStyle: 'solid',
              borderBottomColor: isActive ? 'var(--color-primary-400)' : 'transparent',
              paddingBottom: 'var(--spacing-3)',
              paddingTop: 'var(--spacing-3)',
              background: 'none',
              cursor: 'pointer',
              transition: `color var(--duration-normal) var(--ease-default), border-color var(--duration-normal) var(--ease-default)`,
            }}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
};
