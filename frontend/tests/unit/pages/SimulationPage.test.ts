/**
 * UT-039: SimulationPage uses design tokens (REQ-005-005-002)
 *
 * Tests that SimulationPage.tsx has been migrated from hardcoded Tailwind
 * color classes to design token references.
 *
 * Acceptance Criteria:
 * - AC-001: All simulation controls and outputs use design tokens
 * - AC-002: Page renders correctly in both themes
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const filePath = path.resolve(__dirname, '../../../src/pages/SimulationPage.tsx');
const content = fs.readFileSync(filePath, 'utf-8');

describe('UT-039: SimulationPage uses design tokens (REQ-005-005-002)', () => {
  // Forbidden hardcoded Tailwind color classes
  const forbiddenPatterns = [
    { pattern: /\bbg-cyan-600\b/, name: 'bg-cyan-600' },
    { pattern: /\bhover:bg-cyan-700\b/, name: 'hover:bg-cyan-700' },
    { pattern: /\bbg-red-600\b/, name: 'bg-red-600' },
    { pattern: /\bhover:bg-red-700\b/, name: 'hover:bg-red-700' },
    { pattern: /\bbg-green-400\b/, name: 'bg-green-400' },
    { pattern: /\bbg-gray-500\b/, name: 'bg-gray-500' },
    { pattern: /\btext-green-400\b/, name: 'text-green-400' },
    { pattern: /\btext-cyan-400\b/, name: 'text-cyan-400' },
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

  it('should use semantic text tokens instead of hardcoded green/cyan text colors', () => {
    expect(content).not.toMatch(/\btext-green-\d+\b/);
    expect(content).not.toMatch(/\btext-cyan-\d+\b/);
  });

  it('should use design token button backgrounds instead of cyan/red backgrounds', () => {
    expect(content).not.toMatch(/\bbg-cyan-\d+\b/);
    expect(content).not.toMatch(/\bbg-red-\d+\b/);
  });

  it('should not have hardcoded bg-gray classes', () => {
    expect(content).not.toMatch(/\bbg-gray-\d+\b/);
  });
});
