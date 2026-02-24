/**
 * UT-016: Asset highlight CSS effects tests
 * REQ-001-004-002: Three highlight modes: pulse, glow, zoom.
 * Applied via CSS animations on Cytoscape nodes.
 * TECH-005: Asset highlight CSS animations
 */
import { describe, it, expect } from 'vitest';
import {
  getHighlightStyles,
  HIGHLIGHT_MODES,
  type HighlightStyleDefinition,
} from '../../../src/styles/highlightStyles';

describe('Asset Highlight CSS Modes', () => {
  it('should define exactly 3 highlight modes: pulse, glow, zoom', () => {
    expect(Object.keys(HIGHLIGHT_MODES)).toHaveLength(3);
    expect(HIGHLIGHT_MODES).toHaveProperty('pulse');
    expect(HIGHLIGHT_MODES).toHaveProperty('glow');
    expect(HIGHLIGHT_MODES).toHaveProperty('zoom');
  });

  it('pulse mode should have animation CSS properties', () => {
    const pulseStyle = HIGHLIGHT_MODES.pulse;
    expect(pulseStyle.className).toBe('mcp-highlight-pulse');
    expect(pulseStyle.cssProperties).toBeDefined();
    expect(pulseStyle.cssProperties).toContain('animation');
  });

  it('glow mode should have box-shadow related CSS', () => {
    const glowStyle = HIGHLIGHT_MODES.glow;
    expect(glowStyle.className).toBe('mcp-highlight-glow');
    expect(glowStyle.cssProperties).toBeDefined();
    expect(glowStyle.cssProperties).toContain('shadow');
  });

  it('zoom mode should have transform/scale CSS', () => {
    const zoomStyle = HIGHLIGHT_MODES.zoom;
    expect(zoomStyle.className).toBe('mcp-highlight-zoom');
    expect(zoomStyle.cssProperties).toBeDefined();
    expect(zoomStyle.cssProperties).toContain('transform');
  });

  it('getHighlightStyles should return full CSS string for Cytoscape', () => {
    const css = getHighlightStyles();
    expect(typeof css).toBe('string');
    expect(css.length).toBeGreaterThan(0);
  });

  it('generated CSS should include all 3 class selectors', () => {
    const css = getHighlightStyles();
    expect(css).toContain('.mcp-highlight-pulse');
    expect(css).toContain('.mcp-highlight-glow');
    expect(css).toContain('.mcp-highlight-zoom');
  });

  it('each mode should have a description', () => {
    Object.values(HIGHLIGHT_MODES).forEach((mode: HighlightStyleDefinition) => {
      expect(typeof mode.description).toBe('string');
      expect(mode.description.length).toBeGreaterThan(0);
    });
  });

  it('pulse mode should use a pulsing animation keyframe name', () => {
    const css = getHighlightStyles();
    expect(css).toContain('@keyframes mcp-pulse');
  });

  it('glow mode should use box-shadow for the glow effect', () => {
    const css = getHighlightStyles();
    expect(css).toContain('box-shadow');
  });

  it('zoom mode should use transform: scale for the zoom effect', () => {
    const css = getHighlightStyles();
    expect(css).toContain('transform');
    expect(css).toContain('scale');
  });
});
