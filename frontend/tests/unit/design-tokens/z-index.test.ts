/**
 * UT-008: Z-index scale values correct
 * Requirement: REQ-001-002-003
 * Task: T-001-008
 *
 * Validates z-index tokens are defined from base (0) to toast (700)
 * Acceptance Criteria:
 * - AC-001: Z-index tokens from base (0) to toast (700) defined
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let cssContent: string;

beforeAll(() => {
  const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
  cssContent = fs.readFileSync(cssPath, 'utf-8');
});

describe('UT-008: REQ-001-002-003 - Z-index scale', () => {
  describe('AC-001: Z-index tokens from base (0) to toast (700) defined', () => {
    const zIndexTokens = [
      { token: '--z-base', value: '0' },
      { token: '--z-dropdown', value: '100' },
      { token: '--z-sticky', value: '200' },
      { token: '--z-overlay', value: '300' },
      { token: '--z-modal', value: '400' },
      { token: '--z-popover', value: '500' },
      { token: '--z-tooltip', value: '600' },
      { token: '--z-toast', value: '700' },
    ];

    zIndexTokens.forEach(({ token, value }) => {
      it(`should define ${token} as ${value}`, () => {
        expect(cssContent).toContain(token);
        const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${value}`);
        expect(cssContent).toMatch(regex);
      });
    });

    it('should define z-index tokens in :root scope (shared across themes)', () => {
      // Extract the :root block content
      const rootStart = cssContent.indexOf(':root');
      expect(rootStart).not.toBe(-1);
      const braceStart = cssContent.indexOf('{', rootStart);
      let depth = 1;
      let i = braceStart + 1;
      while (i < cssContent.length && depth > 0) {
        if (cssContent[i] === '{') depth++;
        if (cssContent[i] === '}') depth--;
        i++;
      }
      const rootBlock = cssContent.substring(braceStart + 1, i - 1);
      expect(rootBlock).toContain('--z-base');
      expect(rootBlock).toContain('--z-toast');
    });

    it('should have incrementing values (each level higher than previous)', () => {
      const values = zIndexTokens.map(t => parseInt(t.value, 10));
      for (let i = 1; i < values.length; i++) {
        expect(values[i]).toBeGreaterThan(values[i - 1]);
      }
    });
  });
});
