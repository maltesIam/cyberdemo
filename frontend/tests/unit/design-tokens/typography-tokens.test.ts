/**
 * UT-002: REQ-001-001-002 - Typography Tokens
 * Task: T-001-002
 *
 * Verifies typography tokens: font families (Inter, JetBrains Mono),
 * font sizes (xs through 5xl), font weights (light through extrabold),
 * and line heights are defined.
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let cssContent: string;

beforeAll(() => {
  const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
  cssContent = fs.readFileSync(cssPath, 'utf-8');
});

describe('UT-002: Typography Tokens (REQ-001-001-002)', () => {
  // AC-001: Font family tokens for sans and mono
  describe('AC-001: Font family tokens', () => {
    it('should define --font-family-sans with Inter as primary', () => {
      expect(cssContent).toMatch(/--font-family-sans:\s*['"]?Inter/);
    });

    it('should define --font-family-mono with JetBrains Mono as primary', () => {
      expect(cssContent).toMatch(/--font-family-mono:\s*['"]?JetBrains Mono/);
    });

    it('should include fallback fonts for sans', () => {
      expect(cssContent).toMatch(/--font-family-sans:.*system-ui/);
    });

    it('should include fallback fonts for mono', () => {
      expect(cssContent).toMatch(/--font-family-mono:.*monospace/);
    });
  });

  // AC-002: Font size tokens from xs (0.75rem) to 5xl (3rem)
  describe('AC-002: Font size tokens xs through 5xl', () => {
    const fontSizes = [
      { token: '--font-size-xs', value: '0.75rem' },
      { token: '--font-size-sm', value: '0.875rem' },
      { token: '--font-size-base', value: '1rem' },
      { token: '--font-size-lg', value: '1.125rem' },
      { token: '--font-size-xl', value: '1.25rem' },
      { token: '--font-size-2xl', value: '1.5rem' },
      { token: '--font-size-3xl', value: '1.875rem' },
      { token: '--font-size-4xl', value: '2.25rem' },
      { token: '--font-size-5xl', value: '3rem' },
    ];

    fontSizes.forEach(({ token, value }) => {
      it(`should define ${token} as ${value}`, () => {
        const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${value.replace('.', '\\.')}`);
        expect(cssContent).toMatch(regex);
      });
    });
  });

  // AC-003: Font weight tokens from light (300) to extrabold (800)
  describe('AC-003: Font weight tokens', () => {
    const fontWeights = [
      { token: '--font-weight-light', value: '300' },
      { token: '--font-weight-normal', value: '400' },
      { token: '--font-weight-medium', value: '500' },
      { token: '--font-weight-semibold', value: '600' },
      { token: '--font-weight-bold', value: '700' },
      { token: '--font-weight-extrabold', value: '800' },
    ];

    fontWeights.forEach(({ token, value }) => {
      it(`should define ${token} as ${value}`, () => {
        const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${value}`);
        expect(cssContent).toMatch(regex);
      });
    });
  });

  // AC-004: Line height tokens (tight, snug, normal, relaxed)
  describe('AC-004: Line height tokens', () => {
    const lineHeights = [
      { token: '--leading-tight', value: '1.25' },
      { token: '--leading-snug', value: '1.375' },
      { token: '--leading-normal', value: '1.5' },
      { token: '--leading-relaxed', value: '1.625' },
    ];

    lineHeights.forEach(({ token, value }) => {
      it(`should define ${token} as ${value}`, () => {
        const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${value}`);
        expect(cssContent).toMatch(regex);
      });
    });
  });

  // AC-005: Inter and JetBrains Mono loaded via @import
  describe('AC-005: Font loading via @import', () => {
    it('should import Inter from Google Fonts', () => {
      expect(cssContent).toMatch(/@import\s+url\([^)]*fonts\.googleapis\.com[^)]*Inter/);
    });

    it('should import JetBrains Mono from Google Fonts', () => {
      expect(cssContent).toMatch(/@import\s+url\([^)]*fonts\.googleapis\.com[^)]*JetBrains/);
    });
  });
});
