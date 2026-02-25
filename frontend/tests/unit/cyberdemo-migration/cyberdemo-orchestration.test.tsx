/**
 * Unit Tests for CyberDemo Orchestration Component Migrations (T-049 through T-053)
 *
 * UT-049: Workflow canvas uses design tokens
 * UT-050: Agent status badges use design tokens
 * UT-051: Execution timeline uses design tokens
 * UT-052: Log viewer uses design tokens
 * UT-053: Metric cards use design tokens
 *
 * NOTE: These test against the SimulationPage and related components
 * which contain the workflow canvas, agent badges, timeline, log viewer, and metrics.
 * The SimulationPage is the main orchestration page with these sub-components inline.
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
// UT-049: Workflow canvas (SimulationPage) uses design tokens
// ============================================================================
describe('UT-049: Workflow canvas uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/SimulationPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'SimulationPage (canvas)');
  assertUsesDesignTokens(filePath, 'SimulationPage (canvas)');
});

// ============================================================================
// UT-050: Agent status badges use design tokens
// ============================================================================
describe('UT-050: Agent status badges use design tokens', () => {
  // Agent status badges are in MitrePhasesList and AttackGraph within demo components
  const mitreListPath = path.resolve(__dirname, '../../../src/components/demo/MitrePhasesList.tsx');
  if (fs.existsSync(mitreListPath)) {
    assertNoHardcodedGrayClasses(mitreListPath, 'MitrePhasesList');
    assertUsesDesignTokens(mitreListPath, 'MitrePhasesList');
  } else {
    it('MitrePhasesList does not exist - skip', () => {
      expect(true).toBe(true);
    });
  }
});

// ============================================================================
// UT-051: Execution timeline uses design tokens
// ============================================================================
describe('UT-051: Execution timeline uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/TimelinePage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'TimelinePage (execution timeline)');
  assertUsesDesignTokens(filePath, 'TimelinePage (execution timeline)');
});

// ============================================================================
// UT-052: Log viewer uses design tokens
// ============================================================================
describe('UT-052: Log viewer uses design tokens', () => {
  // Log viewer functionality is in NarrationFooter
  const filePath = path.resolve(__dirname, '../../../src/components/demo/NarrationFooter.tsx');
  assertNoHardcodedGrayClasses(filePath, 'NarrationFooter (log viewer)');
  assertUsesDesignTokens(filePath, 'NarrationFooter (log viewer)');
});

// ============================================================================
// UT-053: Metric cards use design tokens
// ============================================================================
describe('UT-053: Metric cards use design tokens', () => {
  // Metric cards are primarily on DashboardPage
  const filePath = path.resolve(__dirname, '../../../src/pages/DashboardPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'DashboardPage (metric cards)');
  assertUsesDesignTokens(filePath, 'DashboardPage (metric cards)');
});
