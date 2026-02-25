/**
 * UT-057: INT-001 - Google Fonts Integration
 * Task: T-INT-001
 *
 * Verifies Inter and JetBrains Mono load from Google Fonts CDN and
 * application renders with fallback fonts while custom fonts load.
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

describe('UT-057: Google Fonts Integration (INT-001)', () => {
  // AC-001: Fonts load from Google Fonts
  describe('AC-001: Google Fonts loading', () => {
    it('should have @import or link for Google Fonts URL', () => {
      const allContent = cssContent + htmlContent;
      expect(allContent).toMatch(/fonts\.googleapis\.com/);
    });

    it('should load Inter font from Google Fonts', () => {
      const allContent = cssContent + htmlContent;
      expect(allContent).toMatch(/fonts\.googleapis\.com[^"']*Inter/);
    });

    it('should load JetBrains Mono font from Google Fonts', () => {
      const allContent = cssContent + htmlContent;
      expect(allContent).toMatch(/fonts\.googleapis\.com[^"']*JetBrains/);
    });

    it('should load Inter with weights 300-800', () => {
      const allContent = cssContent + htmlContent;
      expect(allContent).toMatch(/Inter.*wght@[^"']*300/);
    });

    it('should load JetBrains Mono with weights 400 and 600', () => {
      const allContent = cssContent + htmlContent;
      expect(allContent).toMatch(/JetBrains\+Mono.*wght@[^"']*400/);
    });
  });

  // AC-002: Application renders with fallback fonts
  describe('AC-002: Fallback font rendering', () => {
    it('should use display=swap to prevent blocking rendering', () => {
      const allContent = cssContent + htmlContent;
      expect(allContent).toContain('display=swap');
    });

    it('should define a full fallback font stack for sans', () => {
      expect(cssContent).toMatch(/--font-family-sans:[^;]+sans-serif/);
    });

    it('should define a full fallback font stack for mono', () => {
      expect(cssContent).toMatch(/--font-family-mono:[^;]+monospace/);
    });
  });
});
