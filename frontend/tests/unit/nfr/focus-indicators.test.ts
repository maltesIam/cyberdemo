/**
 * Unit Tests: NFR-004 - Visible Focus Indicators
 * Task: T-NFR-004
 * Test ID: UT-064
 *
 * Acceptance Criteria:
 * - AC-001: Focus indicator uses border-focus + 2px outline
 * - AC-002: Focus is visible in both Dark and Light themes
 */
import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

describe('T-NFR-004: Visible Focus Indicators (NFR-004)', () => {
  // AC-001: Focus indicator uses border-focus + 2px outline
  describe('AC-001: Focus indicators use correct design tokens', () => {
    it('should define focus ring CSS with 2px outline using primary-500', () => {
      const utilsPath = path.resolve(__dirname, '../../../src/components/ui/accessibility-utils.ts');
      const content = fs.readFileSync(utilsPath, 'utf-8');
      // Must contain focus-visible rule with 2px outline
      expect(content).toContain('focus-visible');
      expect(content).toContain('outline: 2px solid');
      expect(content).toContain('primary-500');
    });

    it('should have global focus-visible styles in design-tokens.css', () => {
      const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
      const css = fs.readFileSync(cssPath, 'utf-8');
      // Must have a focus-visible rule
      expect(css).toContain('focus-visible');
      // Must reference the border-focus token or primary-500
      expect(css).toMatch(/focus-visible[^}]*outline.*2px/s);
    });

    it('should define border-focus token in dark theme', () => {
      const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
      const css = fs.readFileSync(cssPath, 'utf-8');
      expect(css).toContain('--border-focus');
    });

    it('should define border-focus token in light theme', () => {
      const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
      const css = fs.readFileSync(cssPath, 'utf-8');
      // Light theme section should also have --border-focus
      const lightSection = css.match(/\[data-theme="light"\]\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}/)?.[1] || '';
      expect(lightSection).toContain('--border-focus');
    });
  });

  // AC-002: Focus is visible in both Dark and Light themes
  describe('AC-002: Focus visible in both themes', () => {
    it('should have focus ring that works with CSS variable (theme-agnostic)', () => {
      const utilsPath = path.resolve(__dirname, '../../../src/components/ui/accessibility-utils.ts');
      const content = fs.readFileSync(utilsPath, 'utf-8');
      // The focus ring should use a CSS variable or explicit color that adapts
      expect(content).toMatch(/var\(--.*\)|#[0-9a-fA-F]{3,6}/);
    });

    it('should use outline-offset for clear visibility against backgrounds', () => {
      const utilsPath = path.resolve(__dirname, '../../../src/components/ui/accessibility-utils.ts');
      const content = fs.readFileSync(utilsPath, 'utf-8');
      expect(content).toContain('outline-offset');
    });

    it('Button component should have data-focus-ring attribute', () => {
      const btnPath = path.resolve(__dirname, '../../../src/components/ui/Button.tsx');
      const content = fs.readFileSync(btnPath, 'utf-8');
      expect(content).toContain('data-focus-ring');
    });

    it('ThemeToggle buttons should be focusable (use <button>)', () => {
      const togglePath = path.resolve(__dirname, '../../../src/components/ThemeToggle.tsx');
      const content = fs.readFileSync(togglePath, 'utf-8');
      expect(content).toContain('<button');
    });

    it('FontSizeButton should be focusable (use <button>)', () => {
      const fsbPath = path.resolve(__dirname, '../../../src/components/FontSizeButton.tsx');
      const content = fs.readFileSync(fsbPath, 'utf-8');
      expect(content).toContain('<button');
    });
  });
});
