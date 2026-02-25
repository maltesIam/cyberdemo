/**
 * UT-040: AssetsPage uses design tokens (REQ-005-006-003)
 *
 * Tests that AssetsPage.tsx has been migrated from hardcoded Tailwind
 * color classes to design token references.
 *
 * Acceptance Criteria:
 * - AC-001: Asset tables and cards use design tokens
 * - AC-002: Page renders correctly in both themes
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const filePath = path.resolve(__dirname, '../../../src/pages/AssetsPage.tsx');
const content = fs.readFileSync(filePath, 'utf-8');

describe('UT-040: AssetsPage uses design tokens (REQ-005-006-003)', () => {
  // Forbidden hardcoded Tailwind color classes
  const forbiddenPatterns = [
    { pattern: /\bbg-green-900\b/, name: 'bg-green-900' },
    { pattern: /\btext-green-300\b/, name: 'text-green-300' },
    { pattern: /\bbg-red-900\b/, name: 'bg-red-900' },
    { pattern: /\btext-red-300\b/, name: 'text-red-300' },
    { pattern: /\bbg-orange-900\b/, name: 'bg-orange-900' },
    { pattern: /\btext-orange-300\b/, name: 'text-orange-300' },
    { pattern: /\bbg-yellow-900\b/, name: 'bg-yellow-900' },
    { pattern: /\btext-yellow-300\b/, name: 'text-yellow-300' },
    { pattern: /\bbg-purple-900\/50\b/, name: 'bg-purple-900/50' },
    { pattern: /\btext-purple-300\b/, name: 'text-purple-300' },
    { pattern: /\bbg-blue-900\/50\b/, name: 'bg-blue-900/50' },
    { pattern: /\btext-blue-300\b/, name: 'text-blue-300' },
    { pattern: /\bbg-cyan-900\/50\b/, name: 'bg-cyan-900/50' },
    { pattern: /\btext-cyan-300\b/, name: 'text-cyan-300' },
    { pattern: /\btext-cyan-500\b/, name: 'text-cyan-500 (spinner)' },
    { pattern: /\btext-cyan-400\b/, name: 'text-cyan-400' },
    { pattern: /\btext-red-400\b/, name: 'text-red-400' },
    { pattern: /\bplaceholder-gray-500\b/, name: 'placeholder-gray-500' },
    { pattern: /\bfocus:ring-cyan-500\b/, name: 'focus:ring-cyan-500' },
    { pattern: /\bbg-cyan-600\b/, name: 'bg-cyan-600' },
    { pattern: /\bdivide-gray-700\b/, name: 'divide-gray-700' },
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

  it('should not contain hardcoded focus:ring-cyan classes', () => {
    expect(content).not.toMatch(/\bfocus:ring-cyan-\d+\b/);
  });
});
