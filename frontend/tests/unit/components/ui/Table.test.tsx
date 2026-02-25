/**
 * Unit Tests for Table Component
 * T-004-008: REQ-004-005-001 - Table styling
 * Verifies table container, headers, rows, hover, and pagination footer.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Table, TableHeader, TableRow } from '../../../../src/components/ui/Table';

describe('Table Component', () => {
  describe('REQ-004-005-001: Table styling', () => {
    it('AC-001: container should have border-secondary border', () => {
      render(
        <Table>
          <TableHeader columns={['Name']} />
        </Table>
      );
      const table = screen.getByRole('table');
      expect(table.style.borderColor).toBe('var(--border-secondary)');
      expect(table.style.borderWidth).toBe('1px');
    });

    it('AC-001: container should have radius-xl border radius', () => {
      render(
        <Table>
          <TableHeader columns={['Name']} />
        </Table>
      );
      const table = screen.getByRole('table');
      expect(table.style.borderRadius).toBe('var(--radius-xl)');
    });

    it('AC-001: container should have overflow hidden', () => {
      render(
        <Table>
          <TableHeader columns={['Name']} />
        </Table>
      );
      const table = screen.getByRole('table');
      expect(table.style.overflow).toBe('hidden');
    });

    it('AC-002: header should have bg-tertiary background', () => {
      render(
        <Table>
          <TableHeader columns={['Name', 'Status']} />
        </Table>
      );
      const thead = screen.getByText('Name').closest('thead');
      expect(thead?.style.backgroundColor).toBe('var(--bg-tertiary)');
    });

    it('AC-002: header cells should be text-xs, uppercase, weight-medium', () => {
      render(
        <Table>
          <TableHeader columns={['Name']} />
        </Table>
      );
      const th = screen.getByText('Name');
      expect(th.style.fontSize).toBe('0.75rem');
      expect(th.style.textTransform).toBe('uppercase');
      expect(th.style.fontWeight).toBe('500');
    });

    it('AC-002: header cells should have letter-spacing 0.05em', () => {
      render(
        <Table>
          <TableHeader columns={['Name']} />
        </Table>
      );
      const th = screen.getByText('Name');
      expect(th.style.letterSpacing).toBe('0.05em');
    });

    it('AC-003: row cells should have text-sm, text-primary', () => {
      render(
        <Table>
          <TableHeader columns={['Name']} />
          <tbody>
            <TableRow cells={['Item 1']} />
          </tbody>
        </Table>
      );
      const td = screen.getByText('Item 1');
      expect(td.style.fontSize).toBe('0.875rem');
      expect(td.style.color).toBe('var(--text-primary)');
    });

    it('AC-003: rows should have border-secondary bottom border', () => {
      render(
        <Table>
          <TableHeader columns={['Name']} />
          <tbody>
            <TableRow cells={['Item 1']} />
          </tbody>
        </Table>
      );
      const tr = screen.getByText('Item 1').closest('tr');
      expect(tr?.style.borderBottomColor).toBe('var(--border-secondary)');
    });

    it('AC-004: rows should have transition for hover effect', () => {
      render(
        <Table>
          <TableHeader columns={['Name']} />
          <tbody>
            <TableRow cells={['Item 1']} />
          </tbody>
        </Table>
      );
      const tr = screen.getByText('Item 1').closest('tr');
      expect(tr?.style.transition).toContain('var(--duration-fast)');
    });

    it('should render multiple columns correctly', () => {
      render(
        <Table>
          <TableHeader columns={['Name', 'Status', 'Priority']} />
          <tbody>
            <TableRow cells={['Server A', 'Active', 'High']} />
          </tbody>
        </Table>
      );
      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Priority')).toBeInTheDocument();
      expect(screen.getByText('Server A')).toBeInTheDocument();
      expect(screen.getByText('Active')).toBeInTheDocument();
      expect(screen.getByText('High')).toBeInTheDocument();
    });

    it('header cells should have text-secondary color', () => {
      render(
        <Table>
          <TableHeader columns={['Name']} />
        </Table>
      );
      const th = screen.getByText('Name');
      expect(th.style.color).toBe('var(--text-secondary)');
    });
  });
});
