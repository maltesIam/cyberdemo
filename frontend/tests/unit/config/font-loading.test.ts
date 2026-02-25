/**
 * UT-053: TECH-005 - Font Loading Strategy
 * Task: T-TECH-005
 *
 * Verifies Inter and JetBrains Mono loaded with display=swap and
 * fallback font stack defined in CSS variables.
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let cssContent: string;
let htmlContent: string;

beforeAll(() => {
  const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
  cssContent = fs.readFileSync(cssPath, 'utf-8');
  const htmlPath = path.resolve(__dirname, '../../../index.html');
  htmlContent = fs.existsSync(htmlPath) ? fs.readFileSync(htmlPath, 'utf-8') : '';
});

describe('UT-053: Font Loading Strategy (TECH-005)', () => {
  // AC-001: Inter and JetBrains Mono loaded with display=swap
  describe('AC-001: Fonts loaded with display=swap', () => {
    it('should load Inter with display=swap', () => {
      const allContent = cssContent + htmlContent;
      expect(allContent).toMatch(/Inter[^"']*display=swap/);
    });

    it('should load JetBrains Mono with display=swap', () => {
      const allContent = cssContent + htmlContent;
      expect(allContent).toMatch(/JetBrains[^"']*display=swap/);
    });
  });

  // AC-002: Fallback font stack defined in CSS variables
  describe('AC-002: Fallback font stack', () => {
    it('should include system-ui in sans fallback stack', () => {
      expect(cssContent).toMatch(/--font-family-sans:.*system-ui/);
    });

    it('should include ui-sans-serif in sans fallback stack', () => {
      expect(cssContent).toMatch(/--font-family-sans:.*ui-sans-serif/);
    });

    it('should include monospace in mono fallback stack', () => {
      expect(cssContent).toMatch(/--font-family-mono:.*monospace/);
    });

    it('should include ui-monospace in mono fallback stack', () => {
      expect(cssContent).toMatch(/--font-family-mono:.*ui-monospace/);
    });
  });
});
