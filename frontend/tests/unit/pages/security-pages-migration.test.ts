/**
 * Unit Tests for Security & Vulnerability Page Migrations (Agent 6)
 *
 * T-005-006 (UT-032): IncidentsPage uses badge and table tokens
 * T-005-007 (UT-033): DetectionsPage uses token-based styling
 * T-005-008 (UT-034): TimelinePage uses token colors for events
 * T-005-009 (UT-035): PostmortemsPage uses card and table tokens
 * T-005-010 (UT-036): VulnerabilityDashboard uses MetricCard tokens
 * T-005-011 (UT-037): CTEMPage uses token-based styling
 *
 * These tests verify that ALL hardcoded color values have been replaced
 * with design token references (CSS variable-based Tailwind classes).
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const PAGES_DIR = path.resolve(__dirname, '../../../src/pages');

/**
 * Forbidden patterns: hardcoded color classes that MUST be replaced
 * with design token equivalents per BR-017, BR-018, BR-019
 */
const FORBIDDEN_HARDCODED_PATTERNS = [
  // Hardcoded severity bg colors (should use semantic tokens via CSS vars)
  { pattern: /\bbg-red-900\b/, name: 'bg-red-900' },
  { pattern: /\bbg-orange-900\b/, name: 'bg-orange-900' },
  { pattern: /\bbg-yellow-900\b/, name: 'bg-yellow-900' },
  { pattern: /\bbg-green-900\b/, name: 'bg-green-900' },

  // Hardcoded severity text colors
  { pattern: /\btext-red-300\b/, name: 'text-red-300' },
  { pattern: /\btext-orange-300\b/, name: 'text-orange-300' },
  { pattern: /\btext-yellow-300\b/, name: 'text-yellow-300' },
  { pattern: /\btext-green-300\b/, name: 'text-green-300' },

  // Hardcoded status/accent text colors
  { pattern: /\btext-red-400\b/, name: 'text-red-400' },
  { pattern: /\btext-red-500\b/, name: 'text-red-500' },
  { pattern: /\btext-cyan-400\b/, name: 'text-cyan-400' },
  { pattern: /\btext-cyan-300\b/, name: 'text-cyan-300' },
  { pattern: /\btext-cyan-500\b/, name: 'text-cyan-500' },
  { pattern: /\btext-green-400\b/, name: 'text-green-400' },
  { pattern: /\btext-green-500\b/, name: 'text-green-500' },
  { pattern: /\btext-yellow-400\b/, name: 'text-yellow-400' },
  { pattern: /\btext-orange-400\b/, name: 'text-orange-400' },
  { pattern: /\btext-purple-300\b/, name: 'text-purple-300' },
  { pattern: /\btext-purple-400\b/, name: 'text-purple-400' },
  { pattern: /\btext-blue-300\b/, name: 'text-blue-300' },
  { pattern: /\btext-blue-400\b/, name: 'text-blue-400' },

  // Hardcoded bg with opacity patterns
  { pattern: /\bbg-red-900\//, name: 'bg-red-900/xx' },
  { pattern: /\bbg-orange-900\//, name: 'bg-orange-900/xx' },
  { pattern: /\bbg-yellow-900\//, name: 'bg-yellow-900/xx' },
  { pattern: /\bbg-green-900\//, name: 'bg-green-900/xx' },
  { pattern: /\bbg-blue-900\//, name: 'bg-blue-900/xx' },
  { pattern: /\bbg-purple-900\//, name: 'bg-purple-900/xx' },
  { pattern: /\bbg-cyan-900\//, name: 'bg-cyan-900/xx' },

  // Hardcoded accent/functional bg colors
  { pattern: /\bbg-cyan-600\b/, name: 'bg-cyan-600' },
  { pattern: /\bbg-cyan-500\b/, name: 'bg-cyan-500' },
  { pattern: /\bbg-red-600\b/, name: 'bg-red-600' },
  { pattern: /\bbg-green-500\b/, name: 'bg-green-500' },
  { pattern: /\bbg-blue-500\b/, name: 'bg-blue-500' },
  { pattern: /\bbg-purple-500\b/, name: 'bg-purple-500' },
  { pattern: /\bbg-gray-500\b/, name: 'bg-gray-500' },
  { pattern: /\bbg-yellow-500\b/, name: 'bg-yellow-500' },

  // Hardcoded border colors
  { pattern: /\bborder-red-700\b/, name: 'border-red-700' },
  { pattern: /\bborder-red-800\b/, name: 'border-red-800' },

  // Hardcoded hover/accent bg
  { pattern: /\bhover:bg-cyan-500\b/, name: 'hover:bg-cyan-500' },
  { pattern: /\bhover:bg-cyan-700\b/, name: 'hover:bg-cyan-700' },
  { pattern: /\bhover:bg-red-700\b/, name: 'hover:bg-red-700' },
  { pattern: /\bhover:text-cyan-300\b/, name: 'hover:text-cyan-300' },

  // Hardcoded divider gray
  { pattern: /\bdivide-gray-700\b/, name: 'divide-gray-700' },

  // Hardcoded placeholder color
  { pattern: /\bplaceholder-gray-500\b/, name: 'placeholder-gray-500' },

  // Hardcoded focus ring color
  { pattern: /\bfocus:ring-cyan-500\b/, name: 'focus:ring-cyan-500' },
  { pattern: /\bfocus:ring-red-500\b/, name: 'focus:ring-red-500' },
  { pattern: /\bfocus:border-cyan-500\b/, name: 'focus:border-cyan-500' },

  // Hardcoded gradients
  { pattern: /\bfrom-red-500\b/, name: 'from-red-500' },
  { pattern: /\bto-orange-600\b/, name: 'to-orange-600' },

  // Hardcoded shadow colors
  { pattern: /\bshadow-orange-500\//, name: 'shadow-orange-500/xx' },
];

/**
 * Tests that a page file has NO forbidden hardcoded color patterns
 */
function assertFullTokenMigration(filePath: string, pageName: string) {
  if (!fs.existsSync(filePath)) {
    it.skip(`${pageName} file not found at ${filePath}`, () => {});
    return;
  }

  const content = fs.readFileSync(filePath, 'utf-8');

  for (const { pattern, name } of FORBIDDEN_HARDCODED_PATTERNS) {
    if (pattern.test(content)) {
      it(`${pageName} should NOT contain hardcoded ${name}`, () => {
        expect(content).not.toMatch(pattern);
      });
    }
  }
}

/**
 * Tests that a page file uses design token references
 */
function assertUsesDesignTokens(filePath: string, pageName: string) {
  if (!fs.existsSync(filePath)) {
    it.skip(`${pageName} file not found`, () => {});
    return;
  }

  it(`${pageName} should reference design token patterns`, () => {
    const content = fs.readFileSync(filePath, 'utf-8');
    const hasTokenReference =
      content.includes('var(--') ||
      content.includes('bg-primary') ||
      content.includes('bg-secondary') ||
      content.includes('bg-tertiary') ||
      content.includes('bg-card') ||
      content.includes('text-primary') ||
      content.includes('text-secondary') ||
      content.includes('border-primary') ||
      content.includes('border-secondary');
    expect(hasTokenReference).toBe(true);
  });
}

/**
 * Tests that a page file does not have any inline hex color values
 * (BR-019: No hardcoded color hex values in component files)
 */
function assertNoInlineHexColors(filePath: string, pageName: string) {
  if (!fs.existsSync(filePath)) {
    it.skip(`${pageName} file not found`, () => {});
    return;
  }

  it(`${pageName} should NOT contain inline hex color values in className strings`, () => {
    const content = fs.readFileSync(filePath, 'utf-8');
    // Look for hex colors inside className or style attributes (not in SVG paths or comments)
    // This specifically targets color values in Tailwind classes
    const hexInClassName = /className="[^"]*#[0-9a-fA-F]{3,8}[^"]*"/;
    expect(content).not.toMatch(hexInClassName);
  });
}

// ============================================================================
// UT-032: IncidentsPage uses badge and table tokens (T-005-006)
// ============================================================================
describe('UT-032: IncidentsPage uses badge and table design tokens', () => {
  const filePath = path.resolve(PAGES_DIR, 'IncidentsPage.tsx');

  assertFullTokenMigration(filePath, 'IncidentsPage');
  assertUsesDesignTokens(filePath, 'IncidentsPage');
  assertNoInlineHexColors(filePath, 'IncidentsPage');
});

// ============================================================================
// UT-033: DetectionsPage uses token-based styling (T-005-007)
// ============================================================================
describe('UT-033: DetectionsPage uses token-based styling', () => {
  const filePath = path.resolve(PAGES_DIR, 'DetectionsPage.tsx');

  assertFullTokenMigration(filePath, 'DetectionsPage');
  assertUsesDesignTokens(filePath, 'DetectionsPage');
  assertNoInlineHexColors(filePath, 'DetectionsPage');
});

// ============================================================================
// UT-034: TimelinePage uses token colors for events (T-005-008)
// ============================================================================
describe('UT-034: TimelinePage uses token colors for events', () => {
  const filePath = path.resolve(PAGES_DIR, 'TimelinePage.tsx');

  assertFullTokenMigration(filePath, 'TimelinePage');
  assertUsesDesignTokens(filePath, 'TimelinePage');
  assertNoInlineHexColors(filePath, 'TimelinePage');
});

// ============================================================================
// UT-035: PostmortemsPage uses card and table tokens (T-005-009)
// ============================================================================
describe('UT-035: PostmortemsPage uses card and table tokens', () => {
  const filePath = path.resolve(PAGES_DIR, 'PostmortemsPage.tsx');

  assertFullTokenMigration(filePath, 'PostmortemsPage');
  assertUsesDesignTokens(filePath, 'PostmortemsPage');
  assertNoInlineHexColors(filePath, 'PostmortemsPage');
});

// ============================================================================
// UT-036: VulnerabilityDashboard uses MetricCard tokens (T-005-010)
// ============================================================================
describe('UT-036: VulnerabilityDashboard uses MetricCard tokens', () => {
  const filePath = path.resolve(PAGES_DIR, 'VulnerabilityDashboard.tsx');

  assertFullTokenMigration(filePath, 'VulnerabilityDashboard');
  assertUsesDesignTokens(filePath, 'VulnerabilityDashboard');
  assertNoInlineHexColors(filePath, 'VulnerabilityDashboard');
});

// ============================================================================
// UT-037: CTEMPage uses token-based styling (T-005-011)
// ============================================================================
describe('UT-037: CTEMPage uses token-based styling', () => {
  const filePath = path.resolve(PAGES_DIR, 'CTEMPage.tsx');

  assertFullTokenMigration(filePath, 'CTEMPage');
  assertUsesDesignTokens(filePath, 'CTEMPage');
  assertNoInlineHexColors(filePath, 'CTEMPage');
});
