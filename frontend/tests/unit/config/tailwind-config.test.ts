/**
 * UT-049: TECH-001 - Tailwind Config for CSS Variables
 * Task: T-TECH-001
 *
 * Verifies tailwind.config.js references CSS custom properties enabling
 * utility classes like bg-[var(--bg-primary)].
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let configContent: string;

beforeAll(() => {
  const configPath = path.resolve(__dirname, '../../../tailwind.config.js');
  configContent = fs.readFileSync(configPath, 'utf-8');
});

describe('UT-049: Tailwind Config CSS Variables (TECH-001)', () => {
  // AC-001: Tailwind config extends theme with CSS variable references
  describe('AC-001: Theme extension with CSS variables', () => {
    it('should have an extend section', () => {
      expect(configContent).toContain('extend');
    });

    it('should reference var(--bg-primary) for background colors', () => {
      expect(configContent).toContain('var(--bg-primary)');
    });

    it('should reference var(--bg-secondary) for background colors', () => {
      expect(configContent).toContain('var(--bg-secondary)');
    });

    it('should reference var(--bg-tertiary) for background colors', () => {
      expect(configContent).toContain('var(--bg-tertiary)');
    });

    it('should reference var(--text-primary) for text colors', () => {
      expect(configContent).toContain('var(--text-primary)');
    });

    it('should reference var(--text-secondary) for text colors', () => {
      expect(configContent).toContain('var(--text-secondary)');
    });

    it('should reference var(--border-primary) for border colors', () => {
      expect(configContent).toContain('var(--border-primary)');
    });

    it('should reference var(--border-secondary) for border colors', () => {
      expect(configContent).toContain('var(--border-secondary)');
    });

    it('should reference var(--border-focus) for border colors', () => {
      expect(configContent).toContain('var(--border-focus)');
    });
  });

  // AC-002: Utility classes resolve to design token values
  describe('AC-002: Design token utilities', () => {
    it('should map shadow tokens to var() references', () => {
      expect(configContent).toContain('var(--shadow-sm)');
      expect(configContent).toContain('var(--shadow-md)');
      expect(configContent).toContain('var(--shadow-lg)');
      expect(configContent).toContain('var(--shadow-xl)');
    });

    it('should map border radius tokens to var() references', () => {
      expect(configContent).toContain('var(--radius-sm)');
      expect(configContent).toContain('var(--radius-lg)');
      expect(configContent).toContain('var(--radius-xl)');
    });

    it('should map transition duration tokens to var() references', () => {
      expect(configContent).toContain('var(--transition-fast)');
      expect(configContent).toContain('var(--transition-default)');
      expect(configContent).toContain('var(--transition-slow)');
    });

    it('should map font family to Inter and JetBrains Mono', () => {
      expect(configContent).toMatch(/sans.*Inter/s);
      expect(configContent).toMatch(/mono.*JetBrains Mono/s);
    });
  });
});
