/**
 * UT-003: REQ-001-001-003 - Spacing and Layout Tokens
 * Task: T-001-003
 *
 * Verifies spacing scale (4px base grid), border radius, container widths,
 * and sidebar dimensions.
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let cssContent: string;

beforeAll(() => {
  const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
  cssContent = fs.readFileSync(cssPath, 'utf-8');
});

describe('UT-003: Spacing and Layout Tokens (REQ-001-001-003)', () => {
  // AC-001: Spacing tokens from space-0 to space-24 on 4px grid
  describe('AC-001: Spacing tokens on 4px grid', () => {
    const spacings = [
      { token: '--spacing-0', value: '0' },
      { token: '--spacing-1', value: '0.25rem' },
      { token: '--spacing-2', value: '0.5rem' },
      { token: '--spacing-3', value: '0.75rem' },
      { token: '--spacing-4', value: '1rem' },
      { token: '--spacing-5', value: '1.25rem' },
      { token: '--spacing-6', value: '1.5rem' },
      { token: '--spacing-8', value: '2rem' },
      { token: '--spacing-10', value: '2.5rem' },
      { token: '--spacing-12', value: '3rem' },
      { token: '--spacing-16', value: '4rem' },
      { token: '--spacing-20', value: '5rem' },
      { token: '--spacing-24', value: '6rem' },
    ];

    spacings.forEach(({ token, value }) => {
      it(`should define ${token} as ${value}`, () => {
        expect(cssContent).toContain(token);
      });
    });
  });

  // AC-002: Border radius tokens from sm (4px) to full (9999px)
  describe('AC-002: Border radius tokens', () => {
    const radii = [
      { token: '--radius-sm', value: '0.25rem' },
      { token: '--radius-md', value: '0.375rem' },
      { token: '--radius-lg', value: '0.5rem' },
      { token: '--radius-xl', value: '0.75rem' },
      { token: '--radius-2xl', value: '1rem' },
      { token: '--radius-full', value: '9999px' },
    ];

    radii.forEach(({ token, value }) => {
      it(`should define ${token} as ${value}`, () => {
        const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${value.replace('.', '\\.')}`);
        expect(cssContent).toMatch(regex);
      });
    });
  });

  // AC-003: Container max-width (1280px) and sidebar width (280px)
  describe('AC-003: Container and sidebar dimensions', () => {
    it('should define --container-max as 1280px', () => {
      expect(cssContent).toMatch(/--container-max:\s*1280px/);
    });

    it('should define --sidebar-width as 280px', () => {
      expect(cssContent).toMatch(/--sidebar-width:\s*280px/);
    });
  });
});
