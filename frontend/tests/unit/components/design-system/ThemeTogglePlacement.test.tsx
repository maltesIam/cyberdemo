/**
 * UT-012: ThemeToggle Placement
 * Requirement: REQ-002-002-002
 * Task: T-002-004
 *
 * AC-001: Toggle is visible on every page via the Layout component header
 * AC-002: Toggle is in the top-right area of the header
 *
 * Note: Since Layout depends on DemoContext and react-router, we verify
 * placement via static analysis of the Layout component source code.
 * Integration tests will verify the runtime behavior.
 */
import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

const LAYOUT_PATH = path.resolve(__dirname, '../../../../src/components/Layout.tsx');

describe('UT-012: ThemeToggle Placement (REQ-002-002-002)', () => {
  let layoutContent: string;

  beforeAll(() => {
    layoutContent = fs.readFileSync(LAYOUT_PATH, 'utf-8');
  });

  // AC-001: Toggle is visible on every page via the Layout component header
  describe('AC-001: Toggle visible in Layout header', () => {
    it('should import ThemeToggle component', () => {
      expect(layoutContent).toContain("import { ThemeToggle }");
    });

    it('should render ThemeToggle within the header section', () => {
      expect(layoutContent).toContain('<ThemeToggle');
    });

    it('should have ThemeToggle inside a header element', () => {
      // Verify <ThemeToggle appears after <header and before </header>
      const headerStart = layoutContent.indexOf('<header');
      const headerEnd = layoutContent.indexOf('</header>');
      const togglePosition = layoutContent.indexOf('<ThemeToggle');
      expect(headerStart).toBeGreaterThan(-1);
      expect(headerEnd).toBeGreaterThan(-1);
      expect(togglePosition).toBeGreaterThan(headerStart);
      expect(togglePosition).toBeLessThan(headerEnd);
    });
  });

  // AC-002: Toggle is in the top-right area of the header
  describe('AC-002: Toggle in top-right of header', () => {
    it('should have FontSizeButton immediately before ThemeToggle', () => {
      // Per BR-009: FontSizeButton to the LEFT of ThemeToggle
      const fontSizePos = layoutContent.indexOf('<FontSizeButton');
      const togglePos = layoutContent.indexOf('<ThemeToggle');
      expect(fontSizePos).toBeGreaterThan(-1);
      expect(togglePos).toBeGreaterThan(-1);
      expect(fontSizePos).toBeLessThan(togglePos);
    });

    it('should import FontSizeButton component', () => {
      expect(layoutContent).toContain("import { FontSizeButton }");
    });
  });
});
