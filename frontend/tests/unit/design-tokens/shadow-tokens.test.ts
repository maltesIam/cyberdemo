/**
 * UT-004: REQ-001-001-004 - Shadow and Elevation Tokens
 * Task: T-001-004
 *
 * Verifies shadow tokens from xs to xl plus glow variants.
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let cssContent: string;

beforeAll(() => {
  const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
  cssContent = fs.readFileSync(cssPath, 'utf-8');
});

describe('UT-004: Shadow and Elevation Tokens (REQ-001-001-004)', () => {
  // AC-001: Shadow tokens (xs, sm, md, lg, xl) defined
  describe('AC-001: Shadow scale tokens', () => {
    const shadows = ['--shadow-xs', '--shadow-sm', '--shadow-md', '--shadow-lg', '--shadow-xl'];
    shadows.forEach((token) => {
      it(`should define ${token}`, () => {
        expect(cssContent).toContain(`${token}:`);
      });
    });
  });

  // AC-002: Glow variants for active workflow elements
  describe('AC-002: Glow variants', () => {
    it('should define --shadow-glow-primary', () => {
      expect(cssContent).toContain('--shadow-glow-primary');
    });

    it('should define --shadow-glow-secondary', () => {
      expect(cssContent).toContain('--shadow-glow-secondary');
    });
  });
});
