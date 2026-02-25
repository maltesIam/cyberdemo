/**
 * UT-010: FOUC prevention script injects correct class
 * Requirement: REQ-002-001-002
 * Task: T-002-002
 *
 * Validates FOUC (Flash of Unstyled Content) prevention.
 * Acceptance Criteria:
 * - AC-001: Theme is applied in <head> script or as early as possible in the render cycle
 * - AC-002: No visible flash when loading in light mode on a dark-default app (or vice versa)
 */
import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

let indexHtml: string;

beforeAll(() => {
  const htmlPath = path.resolve(__dirname, '../../../index.html');
  indexHtml = fs.readFileSync(htmlPath, 'utf-8');
});

describe('UT-010: REQ-002-001-002 - FOUC prevention', () => {
  // AC-001: Theme is applied in <head> script
  describe('AC-001: Theme applied in <head> before body', () => {
    it('should have an inline script in <head> section', () => {
      const headContent = indexHtml.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
      expect(headContent).toContain('<script>');
    });

    it('should read from localStorage key "theme-preference"', () => {
      const headContent = indexHtml.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
      expect(headContent).toContain('theme-preference');
    });

    it('should set data-theme attribute on documentElement', () => {
      const headContent = indexHtml.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
      expect(headContent).toContain('data-theme');
    });

    it('should execute synchronously (no async/defer)', () => {
      const headContent = indexHtml.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
      // Find the inline theme script (no src attribute)
      const scriptMatch = headContent.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/);
      expect(scriptMatch).toBeTruthy();
      const scriptTag = scriptMatch![0].split('>')[0];
      expect(scriptTag).not.toContain('async');
      expect(scriptTag).not.toContain('defer');
    });

    it('should default to "dark" if no stored preference', () => {
      const headContent = indexHtml.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
      // The script should set dark as default
      expect(headContent).toMatch(/theme\s*=\s*['"]dark['"]/);
    });
  });

  // AC-002: Handles system preference detection
  describe('AC-002: FOUC script handles all theme modes', () => {
    it('should handle "light" stored preference', () => {
      const headContent = indexHtml.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
      expect(headContent).toContain('light');
    });

    it('should handle "system" stored preference with prefers-color-scheme detection', () => {
      const headContent = indexHtml.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
      expect(headContent).toContain('system');
      expect(headContent).toContain('prefers-color-scheme');
    });

    it('should also restore font-size-step from localStorage', () => {
      const headContent = indexHtml.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
      expect(headContent).toContain('font-size-step');
    });

    it('should wrap in try-catch for error safety', () => {
      const headContent = indexHtml.match(/<head>([\s\S]*?)<\/head>/)?.[1] || '';
      expect(headContent).toContain('try');
      expect(headContent).toContain('catch');
    });
  });
});
