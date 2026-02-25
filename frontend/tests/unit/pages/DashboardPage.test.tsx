/**
 * UT-029: DashboardPage uses MetricCard and token colors
 * Task: T-005-003
 * Requirement: REQ-005-002-001
 *
 * Tests that DashboardPage.tsx:
 * - All card backgrounds use bg-card or bg-secondary token
 * - All text colors use text-primary/text-secondary tokens
 * - All metric values use correct typography tokens
 * - No hardcoded gray, cyan, or white Tailwind classes remain
 * - Semantic colors (red, green, orange, yellow) use CSS variable tokens
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const DASHBOARD_PATH = path.resolve(__dirname, '../../../src/pages/DashboardPage.tsx');

describe('UT-029: DashboardPage uses design tokens (REQ-005-002-001)', () => {
  const content = fs.readFileSync(DASHBOARD_PATH, 'utf-8');

  // === AC-001: All card backgrounds use bg-card or bg-secondary token ===
  describe('AC-001: Card backgrounds use design tokens', () => {
    it('should use bg-secondary or bg-card for card backgrounds', () => {
      const hasTokenBg = content.includes('bg-secondary') || content.includes('bg-card');
      expect(hasTokenBg).toBe(true);
    });

    it('should NOT use hardcoded bg-gray-800 or bg-gray-900', () => {
      expect(content).not.toMatch(/\bbg-gray-800\b/);
      expect(content).not.toMatch(/\bbg-gray-900\b/);
    });
  });

  // === AC-002: All text colors use text-primary/text-secondary tokens ===
  describe('AC-002: Text colors use design tokens', () => {
    it('should use text-primary for main text', () => {
      expect(content).toContain('text-primary');
    });

    it('should use text-secondary for secondary text', () => {
      expect(content).toContain('text-secondary');
    });

    it('should use text-tertiary for tertiary text', () => {
      expect(content).toContain('text-tertiary');
    });

    it('should NOT use hardcoded text-gray-* classes', () => {
      expect(content).not.toMatch(/\btext-gray-\d+\b/);
    });

    it('should NOT use hardcoded text-white', () => {
      expect(content).not.toMatch(/\btext-white\b/);
    });
  });

  // === AC-003: Metric values use correct typography tokens ===
  describe('AC-003: Typography tokens used', () => {
    it('should use text-3xl for metric values', () => {
      expect(content).toContain('text-3xl');
    });

    it('should use font-bold for metric values', () => {
      expect(content).toContain('font-bold');
    });
  });

  // === AC-004: No hardcoded color classes ===
  describe('AC-004: No hardcoded color classes', () => {
    it('should NOT use hardcoded bg-gray-* classes', () => {
      expect(content).not.toMatch(/\bbg-gray-\d+\b/);
    });

    it('should NOT use hardcoded border-gray-* classes', () => {
      expect(content).not.toMatch(/\bborder-gray-\d+\b/);
    });

    it('should use semantic color tokens for severity (via CSS variables)', () => {
      // Severity colors should reference CSS variable tokens, not hardcoded Tailwind colors
      const usesSemanticTokens = content.includes('var(--color-error') ||
        content.includes('var(--color-warning') ||
        content.includes('var(--color-success') ||
        content.includes('var(--soc-') ||
        content.includes('color-error') ||
        content.includes('color-warning') ||
        content.includes('color-success');
      expect(usesSemanticTokens).toBe(true);
    });
  });

  // === Design token pattern present ===
  describe('Design token patterns present', () => {
    it('should use border-primary for card borders', () => {
      expect(content).toContain('border-primary');
    });

    it('should reference var(--) CSS custom properties or token-based classes', () => {
      const hasTokenRef = content.includes('var(--') ||
        content.includes('bg-secondary') ||
        content.includes('text-primary');
      expect(hasTokenRef).toBe(true);
    });
  });
});
