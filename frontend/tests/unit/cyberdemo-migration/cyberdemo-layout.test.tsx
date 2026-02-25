/**
 * Unit Tests for CyberDemo Layout Migration (T-036, T-037, T-038, T-039)
 *
 * UT-036: CyberDemo sidebar uses design tokens (not hardcoded gray-800, gray-700, etc.)
 * UT-037: CyberDemo header uses design tokens + contains ThemeToggle and FontSizeButton
 * UT-038: DemoControlBar, NarrationFooter, DemoFloatingWidget use design tokens
 * UT-039: CyberDemo imports design-tokens.css
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import React from 'react';
import fs from 'fs';
import path from 'path';

// ============================================================================
// UT-039: Verify design-tokens.css is imported in CyberDemo entry point
// ============================================================================

describe('UT-039: CyberDemo imports design-tokens.css', () => {
  it('should have design-tokens.css file in styles directory', () => {
    const tokensPath = path.resolve(__dirname, '../../../src/styles/design-tokens.css');
    expect(fs.existsSync(tokensPath)).toBe(true);
  });

  it('should import design-tokens.css in main.tsx', () => {
    const mainPath = path.resolve(__dirname, '../../../src/main.tsx');
    const mainContent = fs.readFileSync(mainPath, 'utf-8');
    expect(mainContent).toContain('design-tokens');
  });
});

// ============================================================================
// UT-036: CyberDemo sidebar uses design tokens
// ============================================================================

describe('UT-036: CyberDemo sidebar uses design tokens', () => {
  it('should NOT contain hardcoded bg-gray-800 in sidebar component', () => {
    const sidebarPath = path.resolve(__dirname, '../../../src/components/Sidebar.tsx');
    const content = fs.readFileSync(sidebarPath, 'utf-8');
    // Sidebar should use token-based classes, not hardcoded gray-800
    expect(content).not.toMatch(/\bbg-gray-800\b/);
  });

  it('should NOT contain hardcoded border-gray-700 in sidebar component', () => {
    const sidebarPath = path.resolve(__dirname, '../../../src/components/Sidebar.tsx');
    const content = fs.readFileSync(sidebarPath, 'utf-8');
    expect(content).not.toMatch(/\bborder-gray-700\b/);
  });

  it('should NOT contain hardcoded text-gray-300 or text-gray-400 in sidebar', () => {
    const sidebarPath = path.resolve(__dirname, '../../../src/components/Sidebar.tsx');
    const content = fs.readFileSync(sidebarPath, 'utf-8');
    expect(content).not.toMatch(/\btext-gray-300\b/);
    expect(content).not.toMatch(/\btext-gray-400\b/);
  });

  it('should NOT contain hardcoded bg-gray-600 or bg-gray-700 in sidebar', () => {
    const sidebarPath = path.resolve(__dirname, '../../../src/components/Sidebar.tsx');
    const content = fs.readFileSync(sidebarPath, 'utf-8');
    expect(content).not.toMatch(/\bbg-gray-600\b/);
    expect(content).not.toMatch(/\bbg-gray-700\b/);
  });

  it('should use design token CSS variables or token-based Tailwind classes', () => {
    const sidebarPath = path.resolve(__dirname, '../../../src/components/Sidebar.tsx');
    const content = fs.readFileSync(sidebarPath, 'utf-8');
    // Should reference at least some design token pattern
    const hasTokenReference = content.includes('var(--') ||
      content.includes('bg-secondary') ||
      content.includes('bg-tertiary') ||
      content.includes('text-primary') ||
      content.includes('text-secondary') ||
      content.includes('border-primary');
    expect(hasTokenReference).toBe(true);
  });

  it('should render without errors', async () => {
    const { Sidebar } = await import('../../../src/components/Sidebar');
    const { container } = render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>,
    );
    expect(container.querySelector('aside')).toBeTruthy();
  });
});

// ============================================================================
// UT-037: CyberDemo header uses design tokens + ThemeToggle + FontSizeButton
// ============================================================================

describe('UT-037: CyberDemo header uses design tokens', () => {
  it('should NOT contain hardcoded bg-gray-800 in Layout header', () => {
    const layoutPath = path.resolve(__dirname, '../../../src/components/Layout.tsx');
    const content = fs.readFileSync(layoutPath, 'utf-8');
    // The header element specifically should not have hardcoded colors
    expect(content).not.toMatch(/\bbg-gray-800\b/);
  });

  it('should NOT contain hardcoded bg-gray-900 in Layout', () => {
    const layoutPath = path.resolve(__dirname, '../../../src/components/Layout.tsx');
    const content = fs.readFileSync(layoutPath, 'utf-8');
    expect(content).not.toMatch(/\bbg-gray-900\b/);
  });

  it('should NOT contain hardcoded border-gray-700 in Layout', () => {
    const layoutPath = path.resolve(__dirname, '../../../src/components/Layout.tsx');
    const content = fs.readFileSync(layoutPath, 'utf-8');
    expect(content).not.toMatch(/\bborder-gray-700\b/);
  });

  it('should NOT contain hardcoded text-gray-400 in Layout', () => {
    const layoutPath = path.resolve(__dirname, '../../../src/components/Layout.tsx');
    const content = fs.readFileSync(layoutPath, 'utf-8');
    expect(content).not.toMatch(/\btext-gray-400\b/);
  });

  it('should import ThemeToggle component', () => {
    const layoutPath = path.resolve(__dirname, '../../../src/components/Layout.tsx');
    const content = fs.readFileSync(layoutPath, 'utf-8');
    expect(content).toContain('ThemeToggle');
  });

  it('should import FontSizeButton component', () => {
    const layoutPath = path.resolve(__dirname, '../../../src/components/Layout.tsx');
    const content = fs.readFileSync(layoutPath, 'utf-8');
    expect(content).toContain('FontSizeButton');
  });
});

// ============================================================================
// UT-038: DemoControlBar, NarrationFooter, DemoFloatingWidget use design tokens
// ============================================================================

describe('UT-038: DemoControlBar uses design tokens', () => {
  it('should NOT contain hardcoded bg-gray-800 in DemoControlBar', () => {
    const filePath = path.resolve(__dirname, '../../../src/components/demo/DemoControlBar.tsx');
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).not.toMatch(/\bbg-gray-800\b/);
  });

  it('should NOT contain hardcoded border-gray-700 in DemoControlBar', () => {
    const filePath = path.resolve(__dirname, '../../../src/components/demo/DemoControlBar.tsx');
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).not.toMatch(/\bborder-gray-700\b/);
  });

  it('should NOT contain hardcoded text-gray-400 in DemoControlBar', () => {
    const filePath = path.resolve(__dirname, '../../../src/components/demo/DemoControlBar.tsx');
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).not.toMatch(/\btext-gray-400\b/);
  });

  it('should NOT contain hardcoded bg-gray-600 in DemoControlBar', () => {
    const filePath = path.resolve(__dirname, '../../../src/components/demo/DemoControlBar.tsx');
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).not.toMatch(/\bbg-gray-600\b/);
  });

  it('should NOT contain hardcoded bg-gray-700 in DemoControlBar', () => {
    const filePath = path.resolve(__dirname, '../../../src/components/demo/DemoControlBar.tsx');
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).not.toMatch(/\bbg-gray-700\b/);
  });
});

describe('UT-038: NarrationFooter uses design tokens', () => {
  it('should NOT contain hardcoded bg-gray-900 in NarrationFooter', () => {
    const filePath = path.resolve(__dirname, '../../../src/components/demo/NarrationFooter.tsx');
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).not.toMatch(/\bbg-gray-900\b/);
  });

  it('should NOT contain hardcoded border-gray-700 in NarrationFooter', () => {
    const filePath = path.resolve(__dirname, '../../../src/components/demo/NarrationFooter.tsx');
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).not.toMatch(/\bborder-gray-700\b/);
  });

  it('should NOT contain hardcoded bg-gray-800 in NarrationFooter', () => {
    const filePath = path.resolve(__dirname, '../../../src/components/demo/NarrationFooter.tsx');
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).not.toMatch(/\bbg-gray-800\b/);
  });

  it('should NOT contain hardcoded text-gray-500 in NarrationFooter', () => {
    const filePath = path.resolve(__dirname, '../../../src/components/demo/NarrationFooter.tsx');
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).not.toMatch(/\btext-gray-500\b/);
  });
});

describe('UT-038: DemoFloatingWidget uses design tokens', () => {
  it('should NOT contain hardcoded border-gray-700 in DemoFloatingWidget', () => {
    const filePath = path.resolve(__dirname, '../../../src/components/demo/DemoFloatingWidget.tsx');
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).not.toMatch(/\bborder-gray-700\b/);
  });
});
