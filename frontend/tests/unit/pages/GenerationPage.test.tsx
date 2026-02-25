/**
 * UT-031: GenerationPage uses token-based styling
 * Task: T-005-005
 * Requirement: REQ-005-002-003
 *
 * Tests that GenerationPage.tsx:
 * - All backgrounds, text, and border colors use design tokens
 * - No hardcoded gray Tailwind classes remain
 * - Button variants use design token colors (not hardcoded cyan/red)
 * - Progress indicators use CSS variable tokens
 * - Success/error states use semantic color tokens
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const GENERATION_PATH = path.resolve(__dirname, '../../../src/pages/GenerationPage.tsx');

describe('UT-031: GenerationPage uses design tokens (REQ-005-002-003)', () => {
  const content = fs.readFileSync(GENERATION_PATH, 'utf-8');

  // === AC-001: All backgrounds, text, and border colors use design tokens ===
  describe('AC-001: Uses design token classes', () => {
    it('should use bg-secondary for section backgrounds', () => {
      expect(content).toContain('bg-secondary');
    });

    it('should use text-primary for main text', () => {
      expect(content).toContain('text-primary');
    });

    it('should use text-secondary for secondary text', () => {
      expect(content).toContain('text-secondary');
    });

    it('should use border-primary for section borders', () => {
      expect(content).toContain('border-primary');
    });
  });

  // === AC-002: No hardcoded color classes ===
  describe('AC-002: No hardcoded color classes', () => {
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

  // === Button variants use design tokens ===
  describe('Button variants use design tokens', () => {
    it('should NOT use hardcoded bg-cyan-600 for primary buttons', () => {
      expect(content).not.toMatch(/\bbg-cyan-600\b/);
    });

    it('should NOT use hardcoded bg-cyan-700 for hover states', () => {
      expect(content).not.toMatch(/\bbg-cyan-700\b/);
    });

    it('should NOT use hardcoded bg-cyan-800 for disabled states', () => {
      expect(content).not.toMatch(/\bbg-cyan-800\b/);
    });

    it('should NOT use hardcoded bg-red-600 for danger button', () => {
      expect(content).not.toMatch(/\bbg-red-600\b/);
    });

    it('should use design token button styles', () => {
      const hasTokenButton = content.includes('var(--primary') ||
        content.includes('bg-primary') ||
        content.includes('var(--color-error') ||
        content.includes('bg-error');
      expect(hasTokenButton).toBe(true);
    });
  });

  // === Progress/status indicators use design tokens ===
  describe('Progress/status indicators use design tokens', () => {
    it('should NOT use hardcoded bg-cyan-500 for progress bars', () => {
      expect(content).not.toMatch(/\bbg-cyan-500\b/);
    });

    it('should NOT use hardcoded text-cyan-500 for spinners', () => {
      expect(content).not.toMatch(/\btext-cyan-500\b/);
    });

    it('should use semantic color tokens for success/error states', () => {
      const usesSemanticTokens = content.includes('var(--color-success') ||
        content.includes('var(--color-error') ||
        content.includes('color-success') ||
        content.includes('color-error');
      expect(usesSemanticTokens).toBe(true);
    });
  });

  // === Input styling uses tokens ===
  describe('Input styling uses design tokens', () => {
    it('should NOT use hardcoded placeholder-gray-500', () => {
      expect(content).not.toMatch(/\bplaceholder-gray-\d+\b/);
    });

    it('should NOT use hardcoded focus:ring-cyan-500', () => {
      expect(content).not.toMatch(/focus:ring-cyan-500/);
    });
  });

  // === Design token patterns present ===
  describe('Design token patterns present', () => {
    it('should use bg-tertiary for hover/disabled states', () => {
      expect(content).toContain('bg-tertiary');
    });

    it('should reference var(--) CSS variables', () => {
      expect(content).toContain('var(--');
    });
  });
});
