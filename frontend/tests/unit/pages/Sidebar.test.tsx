/**
 * UT-028: Sidebar.tsx uses token-based styling
 * Task: T-005-002
 * Requirement: REQ-005-001-002
 *
 * Tests that Sidebar.tsx:
 * - Uses bg-secondary for sidebar background
 * - Uses text-secondary/text-primary for nav link colors
 * - Uses bg-hover/bg-active for hover and active states
 * - Does NOT contain hardcoded gray Tailwind classes
 * - Does NOT contain hardcoded cyan classes for active state (uses primary token)
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const SIDEBAR_PATH = path.resolve(__dirname, '../../../src/components/Sidebar.tsx');

describe('UT-028: Sidebar.tsx uses token-based styling (REQ-005-001-002)', () => {
  const content = fs.readFileSync(SIDEBAR_PATH, 'utf-8');

  // === AC-001: Sidebar background uses bg-secondary ===
  describe('AC-001: Sidebar background uses bg-secondary', () => {
    it('should use bg-secondary for aside element', () => {
      expect(content).toContain('bg-secondary');
    });

    it('should NOT use hardcoded bg-gray-800 or bg-gray-900', () => {
      expect(content).not.toMatch(/\bbg-gray-800\b/);
      expect(content).not.toMatch(/\bbg-gray-900\b/);
    });
  });

  // === AC-002: Nav link colors use text-secondary/text-primary tokens ===
  describe('AC-002: Nav link colors use token classes', () => {
    it('should use text-secondary for inactive nav links', () => {
      expect(content).toContain('text-secondary');
    });

    it('should use text-primary for active/hover nav links', () => {
      expect(content).toContain('text-primary');
    });

    it('should NOT use hardcoded text-gray-300 or text-gray-400', () => {
      expect(content).not.toMatch(/\btext-gray-300\b/);
      expect(content).not.toMatch(/\btext-gray-400\b/);
    });
  });

  // === AC-003: Hover and active states use token classes ===
  describe('AC-003: Hover and active states use token classes', () => {
    it('should use bg-tertiary for hover state', () => {
      expect(content).toContain('bg-tertiary');
    });

    it('should NOT use hardcoded bg-cyan-600 for active state', () => {
      expect(content).not.toMatch(/\bbg-cyan-600\b/);
    });

    it('should use primary token for active state background', () => {
      // Active link should use a primary-based tint, e.g. bg-primary or primary color ref
      const hasPrimaryActive = content.includes('bg-primary') ||
        content.includes('var(--primary') ||
        content.includes('bg-active');
      expect(hasPrimaryActive).toBe(true);
    });
  });

  // === No hardcoded colors ===
  describe('No hardcoded color classes', () => {
    it('should NOT use hardcoded bg-gray-* classes', () => {
      expect(content).not.toMatch(/\bbg-gray-\d+\b/);
    });

    it('should NOT use hardcoded border-gray-* classes', () => {
      expect(content).not.toMatch(/\bborder-gray-\d+\b/);
    });

    it('should use border-primary for borders', () => {
      expect(content).toContain('border-primary');
    });
  });

  // === Renders correctly ===
  describe('Renders correctly', () => {
    it('should contain an aside element', () => {
      expect(content).toContain('<aside');
    });

    it('should contain nav element', () => {
      expect(content).toContain('<nav');
    });
  });
});
