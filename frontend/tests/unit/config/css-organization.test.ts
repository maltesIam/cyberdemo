/**
 * UT-050: TECH-002 - CSS File Organization
 * Task: T-TECH-002
 *
 * Verifies design-tokens.css is organized with clear sections: base tokens,
 * dark theme, light theme, component defaults.
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let cssContent: string;

beforeAll(() => {
  const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
  cssContent = fs.readFileSync(cssPath, 'utf-8');
});

describe('UT-050: CSS File Organization (TECH-002)', () => {
  // AC-001: File structure follows section organization
  describe('AC-001: Proper section organization', () => {
    it('should have a :root section for base/shared tokens', () => {
      expect(cssContent).toContain(':root');
    });

    it('should have a [data-theme="dark"] section', () => {
      expect(cssContent).toContain('[data-theme="dark"]');
    });

    it('should have a [data-theme="light"] section', () => {
      expect(cssContent).toContain('[data-theme="light"]');
    });

    it('should have font loading section (Google Fonts @import)', () => {
      expect(cssContent).toMatch(/@import\s+url.*fonts\.googleapis\.com/);
    });

    it('should have body transition section', () => {
      expect(cssContent).toMatch(/body\s*\{/);
      expect(cssContent).toContain('transition');
    });
  });

  // AC-002: Comments clearly delimit each section
  describe('AC-002: Section comments', () => {
    it('should have comment headers containing section identifiers', () => {
      // Check for delimited comment sections
      const commentBlocks = cssContent.match(/\/\*[\s\S]*?\*\//g) || [];
      expect(commentBlocks.length).toBeGreaterThanOrEqual(3);
    });

    it('should have a Font Loading section comment', () => {
      expect(cssContent).toMatch(/\/\*[\s\S]*?Font Loading[\s\S]*?\*\//);
    });

    it('should have a Base / Shared Tokens section comment', () => {
      expect(cssContent).toMatch(/\/\*[\s\S]*?(Base|Shared|root)[\s\S]*?\*\//i);
    });

    it('should have a Dark Theme section comment', () => {
      expect(cssContent).toMatch(/\/\*[\s\S]*?Dark Theme[\s\S]*?\*\//i);
    });

    it('should have a Light Theme section comment', () => {
      expect(cssContent).toMatch(/\/\*[\s\S]*?Light Theme[\s\S]*?\*\//i);
    });
  });
});
