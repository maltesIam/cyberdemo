/**
 * Unit Tests for CyberDemo Page Migrations (T-040 through T-048)
 *
 * UT-040: /dashboard page uses design tokens
 * UT-041: /generation page uses design tokens
 * UT-042: /surface page uses design tokens
 * UT-043: vulnerability pages use design tokens
 * UT-044: /threats page uses design tokens
 * UT-045: /incidents page uses design tokens
 * UT-046: /detections page uses design tokens
 * UT-047: /ctem page uses design tokens
 * UT-048: /vulnerabilities/ssvc page uses design tokens
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

/** Helper: assert that a file does NOT contain common hardcoded Tailwind gray classes */
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
// UT-040: /dashboard page uses design tokens
// ============================================================================
describe('UT-040: /dashboard page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/DashboardPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'DashboardPage');
  assertUsesDesignTokens(filePath, 'DashboardPage');
});

// ============================================================================
// UT-041: /generation page uses design tokens
// ============================================================================
describe('UT-041: /generation page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/GenerationPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'GenerationPage');
  assertUsesDesignTokens(filePath, 'GenerationPage');
});

// ============================================================================
// UT-042: /surface page uses design tokens
// ============================================================================
describe('UT-042: /surface page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/SurfacePage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'SurfacePage');
  assertUsesDesignTokens(filePath, 'SurfacePage');
});

// ============================================================================
// UT-043: Vulnerability pages use design tokens
// ============================================================================
describe('UT-043: Vulnerability pages use design tokens', () => {
  const vulnDir = path.resolve(__dirname, '../../../src/pages/vuln-pages');
  const mainVulnPath = path.resolve(__dirname, '../../../src/pages/VulnerabilityDashboard.tsx');

  describe('VulnerabilityDashboard', () => {
    assertNoHardcodedGrayClasses(mainVulnPath, 'VulnerabilityDashboard');
    assertUsesDesignTokens(mainVulnPath, 'VulnerabilityDashboard');
  });

  const vulnFiles = ['CVEDetailPage.tsx', 'CVEAssetsPage.tsx', 'CVEExploitsPage.tsx', 'SSVCDashboard.tsx'];
  for (const file of vulnFiles) {
    const fp = path.resolve(vulnDir, file);
    if (fs.existsSync(fp)) {
      describe(file, () => {
        assertNoHardcodedGrayClasses(fp, file);
        assertUsesDesignTokens(fp, file);
      });
    }
  }
});

// ============================================================================
// UT-044: /threats page uses design tokens
// ============================================================================
describe('UT-044: /threats page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/ThreatEnrichmentPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'ThreatEnrichmentPage');
  assertUsesDesignTokens(filePath, 'ThreatEnrichmentPage');
});

// ============================================================================
// UT-045: /incidents page uses design tokens
// ============================================================================
describe('UT-045: /incidents page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/IncidentsPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'IncidentsPage');
  assertUsesDesignTokens(filePath, 'IncidentsPage');
});

// ============================================================================
// UT-046: /detections page uses design tokens
// ============================================================================
describe('UT-046: /detections page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/DetectionsPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'DetectionsPage');
  assertUsesDesignTokens(filePath, 'DetectionsPage');
});

// ============================================================================
// UT-047: /ctem page uses design tokens
// ============================================================================
describe('UT-047: /ctem page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/CTEMPage.tsx');
  assertNoHardcodedGrayClasses(filePath, 'CTEMPage');
  assertUsesDesignTokens(filePath, 'CTEMPage');
});

// ============================================================================
// UT-048: /vulnerabilities/ssvc page uses design tokens
// ============================================================================
describe('UT-048: /vulnerabilities/ssvc page uses design tokens', () => {
  const filePath = path.resolve(__dirname, '../../../src/pages/vuln-pages/SSVCDashboard.tsx');
  if (fs.existsSync(filePath)) {
    assertNoHardcodedGrayClasses(filePath, 'SSVCDashboard');
    assertUsesDesignTokens(filePath, 'SSVCDashboard');
  }
});
