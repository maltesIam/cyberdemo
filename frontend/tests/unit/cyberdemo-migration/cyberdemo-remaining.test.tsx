/**
 * Unit Tests for CyberDemo Remaining Page Migrations (T-054 through T-062)
 *
 * UT-054: /timeline page uses design tokens
 * UT-055: /postmortems page uses design tokens
 * UT-056: /tickets page uses design tokens
 * UT-057: /graph pages use design tokens
 * UT-058: /collab page uses design tokens
 * UT-059: /config page uses design tokens
 * UT-060: /audit page uses design tokens
 * UT-061: /simulation page uses design tokens
 * UT-062: /assets page uses design tokens
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

/** Helper: assert file does NOT contain common hardcoded Tailwind gray classes */
function assertNoHardcodedGrayClasses(filePath: string, label: string) {
  const content = fs.readFileSync(filePath, 'utf-8');

  const forbiddenPatterns = [
    { pattern: /\bbg-gray-800\b/, name: 'bg-gray-800' },
    { pattern: /\bbg-gray-900\b/, name: 'bg-gray-900' },
    { pattern: /\bborder-gray-700\b/, name: 'border-gray-700' },
    { pattern: /\btext-white\b/, name: 'text-white' },
  ];

  for (const { pattern, name } of forbiddenPatterns) {
    it(`${label} should NOT contain hardcoded ${name}`, () => {
      expect(content).not.toMatch(pattern);
    });
  }
}

/** Helper: assert a file uses at least some design tokens */
function assertUsesDesignTokens(filePath: string, label: string) {
  it(`${label} should reference design token patterns`, () => {
    const content = fs.readFileSync(filePath, 'utf-8');
    const hasTokenReference = content.includes('var(--') ||
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

// ============================================================================
// UT-054: /timeline page uses design tokens
// ============================================================================
describe('UT-054: /timeline page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/TimelinePage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'TimelinePage');
  assertUsesDesignTokens(filePath, 'TimelinePage');
});

// ============================================================================
// UT-055: /postmortems page uses design tokens
// ============================================================================
describe('UT-055: /postmortems page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/PostmortemsPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'PostmortemsPage');
  assertUsesDesignTokens(filePath, 'PostmortemsPage');
});

// ============================================================================
// UT-056: /tickets page uses design tokens
// ============================================================================
describe('UT-056: /tickets page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/TicketsPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'TicketsPage');
  assertUsesDesignTokens(filePath, 'TicketsPage');
});

// ============================================================================
// UT-057: /graph pages use design tokens
// ============================================================================
describe('UT-057: /graph pages use design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/GraphPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'GraphPage');
  assertUsesDesignTokens(filePath, 'GraphPage');
});

// ============================================================================
// UT-058: /collab page uses design tokens
// ============================================================================
describe('UT-058: /collab page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/CollabPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'CollabPage');
  assertUsesDesignTokens(filePath, 'CollabPage');
});

// ============================================================================
// UT-059: /config page uses design tokens
// ============================================================================
describe('UT-059: /config page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/ConfigPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'ConfigPage');
  assertUsesDesignTokens(filePath, 'ConfigPage');
});

// ============================================================================
// UT-060: /audit page uses design tokens
// ============================================================================
describe('UT-060: /audit page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/AuditPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'AuditPage');
  assertUsesDesignTokens(filePath, 'AuditPage');
});

// ============================================================================
// UT-061: /simulation page uses design tokens
// ============================================================================
describe('UT-061: /simulation page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/SimulationPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'SimulationPage');
  assertUsesDesignTokens(filePath, 'SimulationPage');
});

// ============================================================================
// UT-062: /assets page uses design tokens
// ============================================================================
describe('UT-062: /assets page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/AssetsPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'AssetsPage');
  assertUsesDesignTokens(filePath, 'AssetsPage');
});
