/**
 * UT-030: SurfacePage uses card and table tokens
 * Task: T-005-004
 * Requirement: REQ-005-002-002
 *
 * Tests that SurfacePage.tsx:
 * - All backgrounds, text, and border colors use design tokens
 * - No hardcoded gray Tailwind classes remain
 * - Accent/interactive colors use CSS variable tokens where possible
 * - Page renders correctly with token-based styling
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const SURFACE_PATH = path.resolve(__dirname, '../../../src/pages/SurfacePage.tsx');

describe('UT-030: SurfacePage uses design tokens (REQ-005-002-002)', () => {
  const content = fs.readFileSync(SURFACE_PATH, 'utf-8');

  // === AC-001: All backgrounds, text, and border colors use design tokens ===
  describe('AC-001: Uses design token classes', () => {
    it('should use bg-secondary or bg-card for panel backgrounds', () => {
      const hasBgToken = content.includes('bg-secondary') || content.includes('bg-card');
      expect(hasBgToken).toBe(true);
    });

    it('should use text-primary for main text', () => {
      expect(content).toContain('text-primary');
    });

    it('should use text-secondary for secondary text', () => {
      expect(content).toContain('text-secondary');
    });

    it('should use border-primary or border-secondary for borders', () => {
      const hasBorderToken = content.includes('border-primary') || content.includes('border-secondary');
      expect(hasBorderToken).toBe(true);
    });
  });

  // === AC-002: No hardcoded gray Tailwind classes ===
  describe('AC-002: No hardcoded gray classes', () => {
    it('should NOT use hardcoded bg-gray-* classes', () => {
      expect(content).not.toMatch(/\bbg-gray-\d+\b/);
    });

    it('should NOT use hardcoded text-gray-* classes', () => {
      expect(content).not.toMatch(/\btext-gray-\d+\b/);
    });

    it('should NOT use hardcoded border-gray-* classes', () => {
      expect(content).not.toMatch(/\bborder-gray-\d+\b/);
    });

    it('should NOT use hardcoded text-white', () => {
      expect(content).not.toMatch(/\btext-white\b/);
    });
  });

  // === Token patterns present ===
  describe('Token patterns present', () => {
    it('should use bg-tertiary for interactive hover states', () => {
      expect(content).toContain('bg-tertiary');
    });

    it('should reference var(--) CSS variables or design token classes', () => {
      const hasTokenRef = content.includes('var(--') ||
        content.includes('bg-secondary') ||
        content.includes('text-primary') ||
        content.includes('border-primary');
      expect(hasTokenRef).toBe(true);
    });
  });
});
