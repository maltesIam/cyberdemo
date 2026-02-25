/**
 * UT-007: Light theme color mappings correct
 * Requirement: REQ-001-002-002
 * Task: T-001-007
 *
 * Validates all light theme semantic tokens are defined in [data-theme="light"]
 * Acceptance Criteria:
 * - AC-001: All background tokens defined with light values (white, neutral-50, neutral-100)
 * - AC-002: All text tokens defined with dark values (neutral-900, neutral-600, neutral-500)
 * - AC-003: All border tokens defined with light values (neutral-200, neutral-100)
 * - AC-004: Shadow card token defined for light (lower opacity than dark)
 * - AC-005: color-scheme: light is set
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let lightBlock: string;

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
  lightBlock = extractThemeBlock(cssContent, 'light');
});

describe('UT-007: REQ-001-002-002 - Light theme tokens', () => {
  // AC-001: Background tokens with light values
  describe('AC-001: Background tokens defined with light values', () => {
    const bgTokens = [
      { token: '--bg-primary', expectedValue: '#ffffff' },
      { token: '--bg-secondary', expectedValue: '#f8fafc' },
      { token: '--bg-tertiary', expectedValue: '#f1f5f9' },
      { token: '--bg-card', expectedValue: '#ffffff' },
      { token: '--bg-elevated', expectedValue: '#ffffff' },
      { token: '--bg-hover' },
      { token: '--bg-active' },
      { token: '--bg-input', expectedValue: '#f8fafc' },
    ];

    bgTokens.forEach(({ token, expectedValue }) => {
      it(`should define ${token}${expectedValue ? ` as ${expectedValue}` : ''}`, () => {
        expect(lightBlock).toContain(token);
        if (expectedValue) {
          const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${expectedValue.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`);
          expect(lightBlock).toMatch(regex);
        }
      });
    });
  });

  // AC-002: Text tokens with dark values
  describe('AC-002: Text tokens defined with dark values', () => {
    const textTokens = [
      { token: '--text-primary', expectedValue: '#0f172a' },
      { token: '--text-secondary', expectedValue: '#475569' },
      { token: '--text-tertiary', expectedValue: '#64748b' },
      { token: '--text-inverse', expectedValue: '#ffffff' },
      { token: '--text-link', expectedValue: '#4f46e5' },
    ];

    textTokens.forEach(({ token, expectedValue }) => {
      it(`should define ${token} as ${expectedValue}`, () => {
        expect(lightBlock).toContain(token);
        const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${expectedValue.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`);
        expect(lightBlock).toMatch(regex);
      });
    });
  });

  // AC-003: Border tokens with light values
  describe('AC-003: Border tokens defined with light values', () => {
    const borderTokens = [
      { token: '--border-primary', expectedValue: '#e2e8f0' },
      { token: '--border-secondary', expectedValue: '#cbd5e1' },
      { token: '--border-focus', expectedValue: '#4f46e5' },
    ];

    borderTokens.forEach(({ token, expectedValue }) => {
      it(`should define ${token} as ${expectedValue}`, () => {
        expect(lightBlock).toContain(token);
        const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${expectedValue.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`);
        expect(lightBlock).toMatch(regex);
      });
    });
  });

  // AC-004: Shadow card token (lighter for light theme)
  describe('AC-004: Shadow card token defined for light', () => {
    it('should define --shadow-card', () => {
      expect(lightBlock).toContain('--shadow-card');
    });

    it('should use lower opacity for light theme shadows', () => {
      // Light theme shadow-card should have lower opacity values (e.g., 0.08, 0.04)
      // vs dark theme (0.3, 0.2)
      const shadowMatch = lightBlock.match(/--shadow-card:[^;]+/);
      expect(shadowMatch).toBeTruthy();
      // Extract all rgba opacity values
      const opacities = shadowMatch![0].match(/rgba\([^)]+,\s*([\d.]+)\)/g);
      if (opacities) {
        opacities.forEach(op => {
          const opacityValue = parseFloat(op.match(/,\s*([\d.]+)\)/)![1]);
          expect(opacityValue).toBeLessThan(0.2); // Light theme should have < 0.2 opacity
        });
      }
    });
  });

  // AC-005: color-scheme: light is set
  describe('AC-005: color-scheme: light is set', () => {
    it('should set color-scheme: light', () => {
      expect(lightBlock).toMatch(/color-scheme:\s*light/);
    });
  });
});
