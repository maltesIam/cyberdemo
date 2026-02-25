/**
 * UT-038: GraphPage uses design tokens (REQ-005-005-001)
 *
 * Tests that GraphPage.tsx has been migrated from hardcoded Tailwind
 * color classes to design token references.
 *
 * Acceptance Criteria:
 * - AC-001: Canvas background uses bg-secondary with dot grid pattern
 * - AC-002: Node colors use agent status tokens
 * - AC-003: Page renders correctly in both themes (no hardcoded colors)
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const filePath = path.resolve(__dirname, '../../../src/pages/GraphPage.tsx');
const content = fs.readFileSync(filePath, 'utf-8');

describe('UT-038: GraphPage uses design tokens (REQ-005-005-001)', () => {
  // Forbidden hardcoded Tailwind gray classes
  const forbiddenPatterns = [
    { pattern: /\bbg-slate-800\b/, name: 'bg-slate-800' },
    { pattern: /\bbg-slate-600\b/, name: 'bg-slate-600' },
    { pattern: /\bborder-slate-700\b/, name: 'border-slate-700' },
    { pattern: /\btext-slate-400\b/, name: 'text-slate-400' },
    { pattern: /\btext-red-500\b/, name: 'text-red-500' },
    { pattern: /\bborder-blue-500\b/, name: 'border-blue-500 (spinner)' },
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

  it('should use semantic text tokens instead of hardcoded slate text colors', () => {
    // Should use text-secondary or text-tertiary, not text-slate-400
    expect(content).not.toMatch(/\btext-slate-\d+\b/);
  });

  it('should use semantic border tokens instead of slate borders', () => {
    expect(content).not.toMatch(/\bborder-slate-\d+\b/);
  });

  it('should use semantic background tokens for header/legend areas', () => {
    expect(content).not.toMatch(/\bbg-slate-\d+\b/);
  });

  it('should use design token spinner instead of border-blue-500', () => {
    // The loading spinner should use a token-based border color
    expect(content).not.toMatch(/\bborder-b-2 border-blue-500\b/);
  });
});
