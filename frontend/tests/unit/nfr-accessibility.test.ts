/**
 * Unit Tests: NFR Accessibility Requirements
 * Tasks: T-160 (NFR-010), T-161 (NFR-011)
 */
import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// Helper: Calculate relative luminance
function hexToLuminance(hex: string): number {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;

  const sRGB = [r, g, b].map(c =>
    c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
  );

  return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
}

function contrastRatio(hex1: string, hex2: string): number {
  const l1 = hexToLuminance(hex1);
  const l2 = hexToLuminance(hex2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// UT-155: NFR-010 - WCAG 2.2 AA contrast compliance
describe('T-160: WCAG 2.2 AA contrast compliance', () => {
  describe('Dark theme contrast ratios', () => {
    const darkBg = '#0a0a0f';

    it('text-primary (#f1f5f9) on bg-primary (#0a0a0f) >= 4.5:1', () => {
      const ratio = contrastRatio('#f1f5f9', darkBg);
      expect(ratio).toBeGreaterThanOrEqual(4.5);
    });

    it('text-secondary (#94a3b8) on bg-primary (#0a0a0f) >= 4.5:1', () => {
      const ratio = contrastRatio('#94a3b8', darkBg);
      expect(ratio).toBeGreaterThanOrEqual(4.5);
    });

    it('text-primary (#f1f5f9) on bg-tertiary (#1a1a2e) >= 4.5:1', () => {
      const ratio = contrastRatio('#f1f5f9', '#1a1a2e');
      expect(ratio).toBeGreaterThanOrEqual(4.5);
    });

    it('primary color (#6366f1) on bg-primary (#0a0a0f) >= 3:1 (UI component)', () => {
      const ratio = contrastRatio('#6366f1', darkBg);
      expect(ratio).toBeGreaterThanOrEqual(3);
    });
  });

  describe('Light theme contrast ratios', () => {
    const lightBg = '#ffffff';

    it('text-primary (#0f172a) on bg-primary (#ffffff) >= 4.5:1', () => {
      const ratio = contrastRatio('#0f172a', lightBg);
      expect(ratio).toBeGreaterThanOrEqual(4.5);
    });

    it('text-secondary (#475569) on bg-primary (#ffffff) >= 4.5:1', () => {
      const ratio = contrastRatio('#475569', lightBg);
      expect(ratio).toBeGreaterThanOrEqual(4.5);
    });

    it('text-primary (#0f172a) on bg-tertiary (#f1f5f9) >= 4.5:1', () => {
      const ratio = contrastRatio('#0f172a', '#f1f5f9');
      expect(ratio).toBeGreaterThanOrEqual(4.5);
    });

    it('primary color (#4f46e5) on bg-primary (#ffffff) >= 3:1 (UI component)', () => {
      const ratio = contrastRatio('#4f46e5', lightBg);
      expect(ratio).toBeGreaterThanOrEqual(3);
    });
  });
});

// UT-156: NFR-011 - Consistent keyboard navigation
describe('T-161: Consistent keyboard navigation', () => {
  it('ThemeToggle component should use button elements (inherently focusable)', () => {
    const componentPath = path.resolve(__dirname, '../../src/components/ThemeToggle.tsx');
    const content = fs.readFileSync(componentPath, 'utf-8');
    expect(content).toContain('<button');
  });

  it('FontSizeButton component should use button element', () => {
    const componentPath = path.resolve(__dirname, '../../src/components/FontSizeButton.tsx');
    const content = fs.readFileSync(componentPath, 'utf-8');
    expect(content).toContain('<button');
  });

  it('ThemeToggle buttons should have aria-label attributes', () => {
    const componentPath = path.resolve(__dirname, '../../src/components/ThemeToggle.tsx');
    const content = fs.readFileSync(componentPath, 'utf-8');
    expect(content).toContain('aria-label');
  });

  it('FontSizeButton should have aria-label attribute', () => {
    const componentPath = path.resolve(__dirname, '../../src/components/FontSizeButton.tsx');
    const content = fs.readFileSync(componentPath, 'utf-8');
    expect(content).toContain('aria-label');
  });
});
