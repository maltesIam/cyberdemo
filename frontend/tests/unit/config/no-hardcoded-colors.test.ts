/**
 * Unit Tests for Hardcoded Color Cleanup
 * T-TECH-004: TECH-004 - Hardcoded color cleanup
 * Verifies that UI component files do not use hardcoded hex colors or Tailwind gray-* classes.
 *
 * Note: SVG chart/visualization components are exempt because SVG attributes
 * require actual color values (CSS custom properties don't work in SVG attributes).
 * Page files that are being migrated by other agents are also exempt here.
 */
import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// UI component files that MUST be free of hardcoded colors
const UI_COMPONENT_DIR = path.resolve(__dirname, '../../../src/components/ui');
const CORE_COMPONENTS_DIR = path.resolve(__dirname, '../../../src/components');

// Files exempt from hardcoded color checks (SVG chart components, visualization components)
const EXEMPT_FILES = new Set([
  'DetectionTrendChart.tsx',
  'IncidentsByHourChart.tsx',
  'IncidentTimelineChart.tsx',
  'ThreatMap.tsx',
  'AttackChainVisualization.tsx',
  'EnrichmentButtons.tsx',
]);

// Get all .tsx files in a directory (non-recursive)
function getTsxFiles(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter(f => f.endsWith('.tsx'));
}

describe('TECH-004: Hardcoded Color Cleanup', () => {
  describe('AC-001: No hardcoded hex colors in UI component files', () => {
    const uiFiles = getTsxFiles(UI_COMPONENT_DIR);

    it('should have UI component files to check', () => {
      expect(uiFiles.length).toBeGreaterThan(0);
    });

    uiFiles.forEach(file => {
      it(`${file} should not contain hardcoded hex colors`, () => {
        const content = fs.readFileSync(path.join(UI_COMPONENT_DIR, file), 'utf-8');
        // Match hex colors like #fff, #ffffff, #000000 etc.
        // Exclude comments (lines starting with * or //)
        const lines = content.split('\n');
        const violations: string[] = [];

        lines.forEach((line, idx) => {
          const trimmed = line.trim();
          // Skip comments
          if (trimmed.startsWith('*') || trimmed.startsWith('//') || trimmed.startsWith('/*')) return;
          // Match hex color patterns in actual code
          const hexMatches = trimmed.match(/#[0-9a-fA-F]{3,8}\b/g);
          if (hexMatches) {
            violations.push(`Line ${idx + 1}: ${trimmed.substring(0, 80)} (found: ${hexMatches.join(', ')})`);
          }
        });

        expect(violations, `Hardcoded hex colors found in ${file}:\n${violations.join('\n')}`).toHaveLength(0);
      });
    });
  });

  describe('AC-002: No bg-gray-*, text-gray-*, border-gray-* Tailwind classes in core component files', () => {
    const coreFiles = getTsxFiles(CORE_COMPONENTS_DIR)
      .filter(f => !EXEMPT_FILES.has(f));

    it('should have core component files to check', () => {
      expect(coreFiles.length).toBeGreaterThan(0);
    });

    coreFiles.forEach(file => {
      it(`${file} should not contain gray-* Tailwind classes`, () => {
        const content = fs.readFileSync(path.join(CORE_COMPONENTS_DIR, file), 'utf-8');
        const grayPattern = /(?:bg|text|border)-gray-\d+/g;
        const matches = content.match(grayPattern);

        expect(
          matches,
          `Tailwind gray-* classes found in ${file}: ${matches?.join(', ')}`
        ).toBeNull();
      });
    });
  });
});
