/**
 * Asset Highlight CSS Styles for Cytoscape Nodes
 *
 * REQ-001-004-002: Three highlight modes: pulse, glow, zoom
 * TECH-005: Asset highlight CSS animations
 *
 * These styles are applied as Cytoscape classes on graph nodes
 * when the MCP state includes highlightedAssets.
 */

export interface HighlightStyleDefinition {
  /** CSS class name applied to Cytoscape nodes */
  className: string;
  /** Description of the visual effect */
  description: string;
  /** Key CSS properties used (for documentation/testing) */
  cssProperties: string;
}

/**
 * The three highlight modes with their class names and metadata.
 */
export const HIGHLIGHT_MODES: Record<string, HighlightStyleDefinition> = {
  pulse: {
    className: 'mcp-highlight-pulse',
    description: 'Pulsing border animation that draws attention to the node',
    cssProperties: 'border-width animation',
  },
  glow: {
    className: 'mcp-highlight-glow',
    description: 'Glowing box-shadow effect around the node',
    cssProperties: 'box-shadow animation',
  },
  zoom: {
    className: 'mcp-highlight-zoom',
    description: 'Scale transform that makes the node slightly larger',
    cssProperties: 'transform scale animation',
  },
};

/**
 * Generate CSS string containing keyframes and class definitions
 * for all highlight modes. This CSS can be injected into the page
 * or used with Cytoscape's style system.
 */
export function getHighlightStyles(): string {
  return `
/* MCP Highlight Styles - Asset Node Animations */

/* Pulse keyframes */
@keyframes mcp-pulse {
  0% { border-width: 2px; border-color: #8b5cf6; }
  50% { border-width: 6px; border-color: #a78bfa; }
  100% { border-width: 2px; border-color: #8b5cf6; }
}

/* Glow keyframes */
@keyframes mcp-glow {
  0% { box-shadow: 0 0 5px rgba(139, 92, 246, 0.5); }
  50% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.8), 0 0 40px rgba(139, 92, 246, 0.3); }
  100% { box-shadow: 0 0 5px rgba(139, 92, 246, 0.5); }
}

/* Zoom keyframes */
@keyframes mcp-zoom {
  0% { transform: scale(1); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

/* Pulse mode class */
.mcp-highlight-pulse {
  animation: mcp-pulse 1.5s ease-in-out infinite;
  border-color: #8b5cf6;
}

/* Glow mode class */
.mcp-highlight-glow {
  animation: mcp-glow 2s ease-in-out infinite;
  box-shadow: 0 0 10px rgba(139, 92, 246, 0.6);
}

/* Zoom mode class */
.mcp-highlight-zoom {
  animation: mcp-zoom 2s ease-in-out infinite;
  transform: scale(1);
  transform-origin: center center;
}
`.trim();
}

/**
 * Cytoscape-specific style definitions for the three highlight modes.
 * These can be added to the Cytoscape stylesheet.
 */
export const CYTOSCAPE_HIGHLIGHT_STYLES = [
  {
    selector: 'node.mcp-highlight-pulse',
    style: {
      'border-width': 4,
      'border-color': '#8b5cf6',
      'border-style': 'solid',
      'transition-property': 'border-width border-color',
      'transition-duration': '0.3s',
    },
  },
  {
    selector: 'node.mcp-highlight-glow',
    style: {
      'border-width': 3,
      'border-color': '#a78bfa',
      'background-opacity': 0.9,
      'overlay-color': '#8b5cf6',
      'overlay-opacity': 0.2,
      'overlay-padding': 8,
    },
  },
  {
    selector: 'node.mcp-highlight-zoom',
    style: {
      width: 55,
      height: 55,
      'border-width': 3,
      'border-color': '#8b5cf6',
      'transition-property': 'width height',
      'transition-duration': '0.5s',
    },
  },
];
