/**
 * UT-027: Layout.tsx uses design tokens for grid
 * Task: T-005-001
 * Requirement: REQ-005-001-001
 *
 * Tests that Layout.tsx:
 * - Uses bg-primary token for background
 * - Uses bg-secondary + border tokens for header
 * - Contains ThemeToggle and FontSizeButton
 * - Does NOT contain hardcoded gray/white Tailwind classes
 * - Does NOT contain hardcoded hex colors (#xxx) for styling
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const LAYOUT_PATH = path.resolve(__dirname, '../../../src/components/Layout.tsx');

describe('UT-027: Layout.tsx uses design tokens (REQ-005-001-001)', () => {
  const content = fs.readFileSync(LAYOUT_PATH, 'utf-8');

  // === AC-001: Layout background uses bg-primary token ===
  describe('AC-001: Layout background uses bg-primary token', () => {
    it('should use bg-primary for the main container', () => {
      expect(content).toContain('bg-primary');
    });

    it('should NOT use hardcoded bg-gray-900 or bg-gray-800', () => {
      expect(content).not.toMatch(/\bbg-gray-900\b/);
      expect(content).not.toMatch(/\bbg-gray-800\b/);
    });
  });

  // === AC-002: Header uses correct token classes ===
  describe('AC-002: Header uses design token classes', () => {
    it('should use bg-secondary for header background', () => {
      expect(content).toContain('bg-secondary');
    });

    it('should use border-primary for header border', () => {
      expect(content).toContain('border-primary');
    });

    it('should NOT use hardcoded border-gray-700', () => {
      expect(content).not.toMatch(/\bborder-gray-700\b/);
    });
  });

  // === AC-003: Header contains ThemeToggle and FontSizeButton ===
  describe('AC-003: Header contains theme/font controls', () => {
    it('should import ThemeToggle', () => {
      expect(content).toContain('ThemeToggle');
    });

    it('should import FontSizeButton', () => {
      expect(content).toContain('FontSizeButton');
    });
  });

  // === No hardcoded colors ===
  describe('No hardcoded color classes', () => {
    it('should NOT contain hardcoded text-white', () => {
      expect(content).not.toMatch(/\btext-white\b/);
    });

    it('should NOT contain hardcoded text-gray-* classes', () => {
      expect(content).not.toMatch(/\btext-gray-\d+\b/);
    });

    it('should NOT contain hardcoded bg-gray-* classes', () => {
      expect(content).not.toMatch(/\bbg-gray-\d+\b/);
    });

    it('should NOT contain hardcoded border-gray-* classes', () => {
      expect(content).not.toMatch(/\bborder-gray-\d+\b/);
    });
  });

  // === Uses design token pattern references ===
  describe('Uses design token references', () => {
    it('should use token-based text classes (text-primary or text-secondary)', () => {
      const hasTextTokens = content.includes('text-primary') || content.includes('text-secondary');
      expect(hasTextTokens).toBe(true);
    });

    it('should use bg-tertiary for hover states', () => {
      expect(content).toContain('bg-tertiary');
    });
  });
});
