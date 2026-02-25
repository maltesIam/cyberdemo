/**
 * UT-006: Dark theme color mappings correct
 * Requirement: REQ-001-002-001
 * Task: T-001-006
 *
 * Validates all dark theme semantic tokens are defined in [data-theme="dark"]
 * Acceptance Criteria:
 * - AC-001: Background tokens (primary, secondary, tertiary, elevated, hover, active, input, card) defined for dark
 * - AC-002: Text tokens (primary, secondary, tertiary, inverse, link) defined for dark
 * - AC-003: Border tokens (primary, secondary, focus) defined for dark
 * - AC-004: Shadow card token defined for dark
 * - AC-005: color-scheme: dark is set
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let darkBlock: string;

/**
 * Extract the CSS content of [data-theme="dark"] { ... } block
 */
function extractThemeBlock(css: string, theme: string): string {
  const startIndex = css.indexOf(`[data-theme="${theme}"]`);
  if (startIndex === -1) return '';
  const braceStart = css.indexOf('{', startIndex);
  if (braceStart === -1) return '';
  let depth = 1;
  let i = braceStart + 1;
  while (i < css.length && depth > 0) {
    if (css[i] === '{') depth++;
    if (css[i] === '}') depth--;
    i++;
  }
  return css.substring(braceStart + 1, i - 1);
}

beforeAll(() => {
  const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
  const cssContent = fs.readFileSync(cssPath, 'utf-8');
  darkBlock = extractThemeBlock(cssContent, 'dark');
});

describe('UT-006: REQ-001-002-001 - Dark theme tokens', () => {
  // AC-001: Background tokens
  describe('AC-001: Background tokens defined for dark', () => {
    const bgTokens = [
      { token: '--bg-primary', expectedValue: '#0a0a0f' },
      { token: '--bg-secondary', expectedValue: '#12121a' },
      { token: '--bg-tertiary', expectedValue: '#1a1a2e' },
      { token: '--bg-elevated', expectedValue: '#1e1e32' },
      { token: '--bg-hover' },
      { token: '--bg-active' },
      { token: '--bg-input', expectedValue: '#12121a' },
      { token: '--bg-card', expectedValue: '#1a1a2e' },
    ];

    bgTokens.forEach(({ token, expectedValue }) => {
      it(`should define ${token}${expectedValue ? ` as ${expectedValue}` : ''}`, () => {
        expect(darkBlock).toContain(token);
        if (expectedValue) {
          const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${expectedValue.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`);
          expect(darkBlock).toMatch(regex);
        }
      });
    });
  });

  // AC-002: Text tokens
  describe('AC-002: Text tokens defined for dark', () => {
    const textTokens = [
      { token: '--text-primary', expectedValue: '#f1f5f9' },
      { token: '--text-secondary', expectedValue: '#94a3b8' },
      { token: '--text-tertiary', expectedValue: '#64748b' },
      { token: '--text-inverse', expectedValue: '#020617' },
      { token: '--text-link', expectedValue: '#818cf8' },
    ];

    textTokens.forEach(({ token, expectedValue }) => {
      it(`should define ${token} as ${expectedValue}`, () => {
        expect(darkBlock).toContain(token);
        const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${expectedValue.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`);
        expect(darkBlock).toMatch(regex);
      });
    });
  });

  // AC-003: Border tokens
  describe('AC-003: Border tokens defined for dark', () => {
    const borderTokens = [
      { token: '--border-primary', expectedValue: '#1e293b' },
      { token: '--border-secondary', expectedValue: '#334155' },
      { token: '--border-focus', expectedValue: '#6366f1' },
    ];

    borderTokens.forEach(({ token, expectedValue }) => {
      it(`should define ${token} as ${expectedValue}`, () => {
        expect(darkBlock).toContain(token);
        const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${expectedValue.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`);
        expect(darkBlock).toMatch(regex);
      });
    });
  });

  // AC-004: Shadow card token
  describe('AC-004: Shadow card token defined for dark', () => {
    it('should define --shadow-card', () => {
      expect(darkBlock).toContain('--shadow-card');
    });
  });

  // AC-005: color-scheme: dark is set
  describe('AC-005: color-scheme: dark is set', () => {
    it('should set color-scheme: dark', () => {
      expect(darkBlock).toMatch(/color-scheme:\s*dark/);
    });
  });
});
