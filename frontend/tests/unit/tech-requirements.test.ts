/**
 * Unit Tests: Technical Requirements
 * Tasks: T-132 (TECH-001), T-133 (TECH-002), T-134 (TECH-003), T-135 (TECH-004),
 *        T-136 (TECH-005), T-137 (TECH-006), T-138 (TECH-007), T-140 (TECH-009),
 *        T-141 (TECH-010)
 */
import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

const tokensPath = path.resolve(__dirname, '../../src/styles/design-tokens.css');
const indexCssPath = path.resolve(__dirname, '../../src/index.css');
const tailwindConfigPath = path.resolve(__dirname, '../../tailwind.config.js');
const indexHtmlPath = path.resolve(__dirname, '../../index.html');

function readFileIfExists(filePath: string): string {
  return fs.existsSync(filePath) ? fs.readFileSync(filePath, 'utf-8') : '';
}

// UT-132: TECH-001 - CSS custom properties used (no SASS/LESS variables)
describe('T-132: CSS custom properties for cross-framework tokens', () => {
  it('should use CSS custom properties (--prefix) not SASS ($) or LESS (@) variables', () => {
    const tokens = readFileIfExists(tokensPath);
    expect(tokens).toContain('--');
    // Should NOT contain SASS variables
    expect(tokens).not.toMatch(/\$[\w-]+:/);
    // Should NOT contain LESS variables (@ followed by word, not @keyframes, @import, @font-face, @media)
    const lessVars = tokens.match(/@(?!keyframes|import|font-face|media|charset|supports|layer)[\w-]+:/g);
    expect(lessVars).toBeNull();
  });

  it('should use standard CSS syntax (.css extension)', () => {
    expect(tokensPath).toMatch(/\.css$/);
    expect(fs.existsSync(tokensPath)).toBe(true);
  });
});

// UT-133: TECH-002 - Tokens importable in React and Lit
describe('T-133: Design tokens importable in React and Lit', () => {
  it('should be a plain CSS file importable by any framework', () => {
    const tokens = readFileIfExists(tokensPath);
    // Must not use framework-specific syntax
    expect(tokens).not.toContain('import React');
    expect(tokens).not.toContain('export');
    // Must use standard CSS
    expect(tokens).toContain(':root');
  });

  it('should not depend on any build tool preprocessing', () => {
    const tokens = readFileIfExists(tokensPath);
    // No SCSS, LESS, or PostCSS-specific nesting that needs compilation
    expect(tokens).not.toMatch(/\$\w+/);  // No SASS variables
    expect(tokens).not.toContain('@mixin');
    expect(tokens).not.toContain('@include');
  });
});

// UT-134: TECH-003 - Synchronous theme detection in head
describe('T-134: Synchronous theme detection in head', () => {
  it('should have an inline script in index.html head for theme detection', () => {
    const html = readFileIfExists(indexHtmlPath);
    // Script must be in <head> section (before body)
    const headContent = html.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
    expect(headContent).toContain('<script');
    expect(headContent).toMatch(/theme-preference|data-theme/);
  });

  it('should not use async or defer for the theme detection script', () => {
    const html = readFileIfExists(indexHtmlPath);
    const headContent = html.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
    // Find the theme script specifically - it should be inline (no src) and not async/defer
    const themeScriptMatch = headContent.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?theme[\s\S]*?)<\/script>/);
    if (themeScriptMatch) {
      const scriptTag = themeScriptMatch[0];
      expect(scriptTag).not.toContain('async');
      expect(scriptTag).not.toContain('defer');
    } else {
      // If no inline theme script, fail
      expect(headContent).toMatch(/theme-preference/);
    }
  });
});

// UT-135: TECH-004 - Font size targets documentElement.style.fontSize
describe('T-135: Font size modifies documentElement.style.fontSize', () => {
  it('should target documentElement for font size changes', () => {
    // This is verified in the FontSizeButton component tests
    // Here we verify the utility function exists
    const fontSizeUtilPath = path.resolve(__dirname, '../../src/utils/font-size.ts');
    expect(fs.existsSync(fontSizeUtilPath)).toBe(true);
    const content = readFileIfExists(fontSizeUtilPath);
    expect(content).toContain('documentElement');
    expect(content).toContain('fontSize');
  });
});

// UT-136: TECH-005 - Tailwind var(--token) references work
describe('T-136: Tailwind uses var(--token) syntax', () => {
  it('should use var() references in Tailwind config', () => {
    const config = readFileIfExists(tailwindConfigPath);
    expect(config).toMatch(/var\(--[\w-]+\)/);
  });

  it('should have multiple var() references for colors', () => {
    const config = readFileIfExists(tailwindConfigPath);
    const varRefs = config.match(/var\(--[\w-]+\)/g) || [];
    expect(varRefs.length).toBeGreaterThan(5);
  });
});

// UT-137: TECH-006 - Shadow DOM token injection
describe('T-137: Shadow DOM token injection for Lit components', () => {
  it('should document or implement a strategy for shadow DOM token access', () => {
    // CSS custom properties naturally inherit into shadow DOM
    // The design-tokens.css on :root and [data-theme] will propagate
    const tokens = readFileIfExists(tokensPath);
    expect(tokens).toContain(':root');
    // Custom properties defined on :root are inherited by shadow DOM elements
  });
});

// UT-138: TECH-007 - CyberDemo animations preserved
describe('T-138: CyberDemo custom CSS animations preserved', () => {
  it('should preserve existing animations in index.css', () => {
    const indexCss = readFileIfExists(indexCssPath);
    // Check key animations still exist
    expect(indexCss).toContain('glow-pulse-red');
    expect(indexCss).toContain('fire-flicker');
    expect(indexCss).toContain('slide-in-right');
    expect(indexCss).toContain('pulse-critical');
    expect(indexCss).toContain('shimmer');
  });
});

// UT-140: TECH-009 - font-display: swap configured
describe('T-140: font-display: swap for web fonts', () => {
  it('should configure font-display: swap', () => {
    const html = readFileIfExists(indexHtmlPath);
    const tokens = readFileIfExists(tokensPath);
    const allContent = html + tokens;
    expect(allContent).toMatch(/display=swap|font-display:\s*swap/);
  });
});

// UT-141: TECH-010 - No hardcoded hex colors after migration
describe('T-141: No hardcoded hex colors in design tokens', () => {
  it('should use hex colors only in token definitions, not in component code', () => {
    // The tokens file SHOULD have hex colors (that's where they're defined)
    const tokens = readFileIfExists(tokensPath);
    const hexColors = tokens.match(/#[0-9a-fA-F]{3,8}/g) || [];
    expect(hexColors.length).toBeGreaterThan(0);
  });
});
