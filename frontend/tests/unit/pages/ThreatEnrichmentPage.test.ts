/**
 * UT-041: ThreatEnrichmentPage uses design tokens (REQ-005-007-001)
 *
 * Tests that ThreatEnrichmentPage.tsx has been migrated from hardcoded Tailwind
 * color classes to design token references.
 *
 * Acceptance Criteria:
 * - AC-001: Enrichment indicators and data displays use design tokens
 * - AC-002: Page renders correctly in both themes
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const filePath = path.resolve(__dirname, '../../../src/pages/ThreatEnrichmentPage.tsx');
const content = fs.readFileSync(filePath, 'utf-8');

describe('UT-041: ThreatEnrichmentPage uses design tokens (REQ-005-007-001)', () => {
  // Forbidden hardcoded Tailwind color classes
  const forbiddenPatterns = [
    { pattern: /\btext-red-500\b/, name: 'text-red-500 (header icon)' },
    { pattern: /\bbg-cyan-600\b/, name: 'bg-cyan-600' },
    { pattern: /\bhover:bg-cyan-700\b/, name: 'hover:bg-cyan-700' },
    { pattern: /\btext-cyan-400\b/, name: 'text-cyan-400' },
    { pattern: /\btext-red-400\b/, name: 'text-red-400' },
    { pattern: /\btext-orange-400\b/, name: 'text-orange-400' },
    { pattern: /\btext-purple-400\b/, name: 'text-purple-400' },
    { pattern: /\btext-blue-400\b/, name: 'text-blue-400' },
    { pattern: /\btext-purple-300\b/, name: 'text-purple-300' },
    { pattern: /\btext-blue-300\b/, name: 'text-blue-300' },
    { pattern: /\btext-green-400\b/, name: 'text-green-400' },
    { pattern: /\btext-amber-400\b/, name: 'text-amber-400' },
    { pattern: /\btext-yellow-400\b/, name: 'text-yellow-400' },
    { pattern: /\bbg-red-600\b/, name: 'bg-red-600' },
    { pattern: /\bhover:bg-red-700\b/, name: 'hover:bg-red-700' },
    { pattern: /\bplaceholder-gray-500\b/, name: 'placeholder-gray-500' },
    { pattern: /\bfocus:border-cyan-500\b/, name: 'focus:border-cyan-500' },
    { pattern: /\bdivide-gray-700\b/, name: 'divide-gray-700' },
    { pattern: /\bbg-gray-500\/20\b/, name: 'bg-gray-500/20' },
  ];

  for (const { pattern, name } of forbiddenPatterns) {
    it(`should NOT contain hardcoded ${name}`, () => {
      expect(content).not.toMatch(pattern);
    });
  }

  it('should reference design token-based classes', () => {
    const hasTokenReference =
      content.includes('bg-secondary') ||
      content.includes('bg-primary') ||
      content.includes('text-primary') ||
      content.includes('text-secondary') ||
      content.includes('border-primary') ||
      content.includes('border-secondary');
    expect(hasTokenReference).toBe(true);
  });

  it('should not contain divide-gray classes', () => {
    expect(content).not.toMatch(/\bdivide-gray-\d+\b/);
  });

  it('should not contain placeholder-gray classes', () => {
    expect(content).not.toMatch(/\bplaceholder-gray-\d+\b/);
  });

  it('should use CSS variable risk colors instead of hardcoded Tailwind colors for risk badges', () => {
    // The riskColors object should use var(--) references, not hardcoded text-red-500 etc.
    expect(content).not.toMatch(/\btext-red-500 bg-red-500\/20 border-red-500\/50\b/);
    expect(content).not.toMatch(/\btext-orange-500 bg-orange-500\/20 border-orange-500\/50\b/);
    expect(content).not.toMatch(/\btext-yellow-500 bg-yellow-500\/20 border-yellow-500\/50\b/);
    expect(content).not.toMatch(/\btext-green-500 bg-green-500\/20 border-green-500\/50\b/);
  });
});
