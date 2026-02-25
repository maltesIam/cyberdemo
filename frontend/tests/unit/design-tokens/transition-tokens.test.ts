/**
 * UT-005: REQ-001-001-005 - Transition and Motion Tokens
 * Task: T-001-005
 *
 * Verifies transition duration tokens (fast, normal, slow, slower) and
 * easing functions (default, in, out, spring).
 */
import { describe, it, expect, beforeAll } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let cssContent: string;

beforeAll(() => {
  const cssPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
  cssContent = fs.readFileSync(cssPath, 'utf-8');
});

describe('UT-005: Transition and Motion Tokens (REQ-001-001-005)', () => {
  // AC-001: Duration tokens (100ms, 200ms, 300ms, 500ms)
  describe('AC-001: Duration tokens', () => {
    it('should define --transition-fast as 150ms', () => {
      expect(cssContent).toMatch(/--transition-fast:\s*150ms/);
    });

    it('should define --transition-default as 200ms', () => {
      expect(cssContent).toMatch(/--transition-default:\s*200ms/);
    });

    it('should define --transition-slow as 300ms', () => {
      expect(cssContent).toMatch(/--transition-slow:\s*300ms/);
    });

    it('should define --transition-slower as 500ms', () => {
      expect(cssContent).toMatch(/--transition-slower:\s*500ms/);
    });

    // Verify aliases
    it('should define --duration-fast alias', () => {
      expect(cssContent).toContain('--duration-fast');
    });

    it('should define --duration-normal alias', () => {
      expect(cssContent).toContain('--duration-normal');
    });

    it('should define --duration-slow alias', () => {
      expect(cssContent).toContain('--duration-slow');
    });
  });

  // AC-002: Easing function tokens
  describe('AC-002: Easing function tokens', () => {
    it('should define --ease-default as cubic-bezier(0.4, 0, 0.2, 1)', () => {
      expect(cssContent).toMatch(/--ease-default:\s*cubic-bezier\(0\.4,\s*0,\s*0\.2,\s*1\)/);
    });

    it('should define --ease-in as cubic-bezier(0.4, 0, 1, 1)', () => {
      expect(cssContent).toMatch(/--ease-in:\s*cubic-bezier\(0\.4,\s*0,\s*1,\s*1\)/);
    });

    it('should define --ease-out as cubic-bezier(0, 0, 0.2, 1)', () => {
      expect(cssContent).toMatch(/--ease-out:\s*cubic-bezier\(0,\s*0,\s*0\.2,\s*1\)/);
    });

    it('should define --ease-spring as cubic-bezier(0.34, 1.56, 0.64, 1)', () => {
      expect(cssContent).toMatch(/--ease-spring:\s*cubic-bezier\(0\.34,\s*1\.56,\s*0\.64,\s*1\)/);
    });
  });
});
