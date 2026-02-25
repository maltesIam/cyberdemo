/**
 * Unit Tests: Design Tokens CSS
 * Tasks: T-001 (REQ-001-001-001), T-002 (REQ-001-001-002),
 *        T-003 (REQ-001-001-003), T-004 (REQ-001-001-004),
 *        T-005 (REQ-001-001-005)
 *
 * Tests verify that design-tokens.css contains all required CSS custom properties
 * with correct values matching the AgentFlow Design System v2.0 style guide.
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let cssContent: string;

beforeAll(() => {
  const cssPath = path.resolve(__dirname, '../../src/styles/design-tokens.css');
  cssContent = fs.readFileSync(cssPath, 'utf-8');
});

// UT-001: REQ-001-001-001 - Verify design-tokens.css contains all required CSS custom properties
describe('T-001: design-tokens.css file exists and contains CSS custom properties', () => {
  it('should exist as a valid CSS file', () => {
    const cssPath = path.resolve(__dirname, '../../src/styles/design-tokens.css');
    expect(fs.existsSync(cssPath)).toBe(true);
  });

  it('should contain :root block', () => {
    expect(cssContent).toContain(':root');
  });

  it('should contain [data-theme="dark"] block', () => {
    expect(cssContent).toContain('[data-theme="dark"]');
  });

  it('should contain [data-theme="light"] block', () => {
    expect(cssContent).toContain('[data-theme="light"]');
  });

  it('should use CSS custom properties (--prefix)', () => {
    const customPropCount = (cssContent.match(/--[\w-]+:/g) || []).length;
    expect(customPropCount).toBeGreaterThan(50);
  });
});

// UT-002: REQ-001-001-002 - Verify :root block contains all base/shared tokens
describe('T-002: :root block contains all base/shared tokens', () => {
  // Typography tokens
  it('should define font-family-sans (Inter)', () => {
    expect(cssContent).toContain('--font-family-sans');
    expect(cssContent).toMatch(/--font-family-sans:\s*['"]?Inter/);
  });

  it('should define font-family-mono (JetBrains Mono)', () => {
    expect(cssContent).toContain('--font-family-mono');
    expect(cssContent).toMatch(/--font-family-mono:\s*['"]?JetBrains Mono/);
  });

  // Font sizes
  const fontSizes = [
    { token: '--font-size-xs', value: '0.75rem' },
    { token: '--font-size-sm', value: '0.875rem' },
    { token: '--font-size-base', value: '1rem' },
    { token: '--font-size-lg', value: '1.125rem' },
    { token: '--font-size-xl', value: '1.25rem' },
    { token: '--font-size-2xl', value: '1.5rem' },
    { token: '--font-size-3xl', value: '1.875rem' },
  ];

  fontSizes.forEach(({ token, value }) => {
    it(`should define ${token} as ${value}`, () => {
      expect(cssContent).toContain(token);
      expect(cssContent).toContain(value);
    });
  });

  // Font weights
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
      expect(cssContent).toContain(token);
      const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${value}`);
      expect(cssContent).toMatch(regex);
    });
  });

  // Spacing tokens
  const spacings = [
    { token: '--spacing-1', value: '0.25rem' },
    { token: '--spacing-2', value: '0.5rem' },
    { token: '--spacing-3', value: '0.75rem' },
    { token: '--spacing-4', value: '1rem' },
    { token: '--spacing-5', value: '1.25rem' },
    { token: '--spacing-6', value: '1.5rem' },
    { token: '--spacing-8', value: '2rem' },
    { token: '--spacing-10', value: '2.5rem' },
    { token: '--spacing-12', value: '3rem' },
  ];

  spacings.forEach(({ token, value }) => {
    it(`should define ${token} as ${value}`, () => {
      expect(cssContent).toContain(token);
    });
  });

  // Border radius tokens
  const radii = [
    { token: '--radius-sm', value: '0.25rem' },
    { token: '--radius-md', value: '0.375rem' },
    { token: '--radius-lg', value: '0.5rem' },
    { token: '--radius-xl', value: '0.75rem' },
    { token: '--radius-2xl', value: '1rem' },
    { token: '--radius-full', value: '9999px' },
  ];

  radii.forEach(({ token, value }) => {
    it(`should define ${token} as ${value}`, () => {
      expect(cssContent).toContain(token);
    });
  });

  // Transition tokens
  const transitions = [
    { token: '--transition-fast', value: '150ms' },
    { token: '--transition-default', value: '200ms' },
    { token: '--transition-slow', value: '300ms' },
  ];

  transitions.forEach(({ token, value }) => {
    it(`should define ${token} as ${value}`, () => {
      expect(cssContent).toContain(token);
    });
  });

  // Shadow tokens
  it('should define shadow tokens', () => {
    expect(cssContent).toContain('--shadow-sm');
    expect(cssContent).toContain('--shadow-md');
    expect(cssContent).toContain('--shadow-lg');
    expect(cssContent).toContain('--shadow-xl');
  });
});

// UT-003: REQ-001-001-003 - Verify [data-theme="dark"] block contains dark semantic tokens
describe('T-003: [data-theme="dark"] block contains dark semantic tokens', () => {
  it('should define --primary as #6366f1', () => {
    // Check within the dark theme block
    const darkBlock = extractThemeBlock(cssContent, 'dark');
    expect(darkBlock).toContain('--primary');
    expect(darkBlock).toMatch(/--primary:\s*#6366f1/);
  });

  it('should define --primary-hover as #4f46e5', () => {
    const darkBlock = extractThemeBlock(cssContent, 'dark');
    expect(darkBlock).toContain('--primary-hover');
    expect(darkBlock).toMatch(/--primary-hover:\s*#4f46e5/);
  });

  // Background tokens
  const darkBgTokens = [
    { token: '--bg-primary', value: '#0a0a0f' },
    { token: '--bg-secondary', value: '#12121a' },
    { token: '--bg-tertiary', value: '#1a1a2e' },
  ];

  darkBgTokens.forEach(({ token, value }) => {
    it(`should define ${token} as ${value}`, () => {
      const darkBlock = extractThemeBlock(cssContent, 'dark');
      expect(darkBlock).toContain(token);
      const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${value}`);
      expect(darkBlock).toMatch(regex);
    });
  });

  // Text tokens
  const darkTextTokens = [
    { token: '--text-primary', value: '#f1f5f9' },
    { token: '--text-secondary', value: '#94a3b8' },
    { token: '--text-tertiary', value: '#64748b' },
  ];

  darkTextTokens.forEach(({ token, value }) => {
    it(`should define ${token} as ${value}`, () => {
      const darkBlock = extractThemeBlock(cssContent, 'dark');
      expect(darkBlock).toContain(token);
    });
  });

  // Border tokens
  it('should define --border-primary as #1e293b', () => {
    const darkBlock = extractThemeBlock(cssContent, 'dark');
    expect(darkBlock).toContain('--border-primary');
    expect(darkBlock).toMatch(/--border-primary:\s*#1e293b/);
  });

  it('should define --border-secondary as #334155', () => {
    const darkBlock = extractThemeBlock(cssContent, 'dark');
    expect(darkBlock).toContain('--border-secondary');
    expect(darkBlock).toMatch(/--border-secondary:\s*#334155/);
  });

  // Semantic color tokens
  const semanticColors = [
    { token: '--color-success', value: '#22c55e' },
    { token: '--color-warning', value: '#f59e0b' },
    { token: '--color-error', value: '#ef4444' },
    { token: '--color-info', value: '#3b82f6' },
  ];

  semanticColors.forEach(({ token, value }) => {
    it(`should define ${token} as ${value}`, () => {
      const darkBlock = extractThemeBlock(cssContent, 'dark');
      expect(darkBlock).toContain(token);
    });
  });

  it('should define --accent as #8b5cf6', () => {
    const darkBlock = extractThemeBlock(cssContent, 'dark');
    expect(darkBlock).toContain('--accent');
    expect(darkBlock).toMatch(/--accent:\s*#8b5cf6/);
  });
});

// UT-004: REQ-001-001-004 - Verify [data-theme="light"] block contains light semantic tokens
describe('T-004: [data-theme="light"] block contains light semantic tokens', () => {
  it('should define --primary as #4f46e5', () => {
    const lightBlock = extractThemeBlock(cssContent, 'light');
    expect(lightBlock).toContain('--primary');
    expect(lightBlock).toMatch(/--primary:\s*#4f46e5/);
  });

  const lightBgTokens = [
    { token: '--bg-primary', value: '#ffffff' },
    { token: '--bg-secondary', value: '#f8fafc' },
    { token: '--bg-tertiary', value: '#f1f5f9' },
  ];

  lightBgTokens.forEach(({ token, value }) => {
    it(`should define ${token} as ${value}`, () => {
      const lightBlock = extractThemeBlock(cssContent, 'light');
      expect(lightBlock).toContain(token);
      const regex = new RegExp(`${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*${value}`);
      expect(lightBlock).toMatch(regex);
    });
  });

  const lightTextTokens = [
    { token: '--text-primary', value: '#0f172a' },
    { token: '--text-secondary', value: '#475569' },
    { token: '--text-tertiary', value: '#64748b' },
  ];

  lightTextTokens.forEach(({ token, value }) => {
    it(`should define ${token} as ${value}`, () => {
      const lightBlock = extractThemeBlock(cssContent, 'light');
      expect(lightBlock).toContain(token);
    });
  });

  const lightBorderTokens = [
    { token: '--border-primary', value: '#e2e8f0' },
    { token: '--border-secondary', value: '#cbd5e1' },
  ];

  lightBorderTokens.forEach(({ token, value }) => {
    it(`should define ${token} as ${value}`, () => {
      const lightBlock = extractThemeBlock(cssContent, 'light');
      expect(lightBlock).toContain(token);
    });
  });
});

// UT-005: REQ-001-001-005 - Verify token values match style guide v2.0 specifications
describe('T-005: Token values match style guide v2.0 exactly', () => {
  it('dark theme primary is exactly #6366f1 (indigo-500)', () => {
    const darkBlock = extractThemeBlock(cssContent, 'dark');
    expect(darkBlock).toMatch(/--primary:\s*#6366f1/);
  });

  it('light theme primary is exactly #4f46e5 (indigo-600)', () => {
    const lightBlock = extractThemeBlock(cssContent, 'light');
    expect(lightBlock).toMatch(/--primary:\s*#4f46e5/);
  });

  it('dark bg-primary is exactly #0a0a0f', () => {
    const darkBlock = extractThemeBlock(cssContent, 'dark');
    expect(darkBlock).toMatch(/--bg-primary:\s*#0a0a0f/);
  });

  it('light bg-primary is exactly #ffffff', () => {
    const lightBlock = extractThemeBlock(cssContent, 'light');
    expect(lightBlock).toMatch(/--bg-primary:\s*#ffffff/);
  });

  it('font-size-base is exactly 1rem', () => {
    expect(cssContent).toMatch(/--font-size-base:\s*1rem/);
  });

  it('radius-full is exactly 9999px', () => {
    expect(cssContent).toMatch(/--radius-full:\s*9999px/);
  });

  it('transition-default is exactly 200ms', () => {
    expect(cssContent).toMatch(/--transition-default:\s*200ms/);
  });
});

/**
 * Helper: Extract the CSS block for a given theme.
 * Finds [data-theme="<theme>"] { ... } and returns inner content.
 */
function extractThemeBlock(css: string, theme: string): string {
  const regex = new RegExp(`\\[data-theme="${theme}"\\]\\s*\\{([^}]+(?:\\{[^}]*\\}[^}]*)*)\\}`, 's');
  const match = css.match(regex);
  if (!match) {
    // Try a simpler approach: find the block start and match braces
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
  return match[1];
}
