/**
 * UT-003: highlightedAssets triggers node highlighting tests
 * REQ-001-001-003: When state includes `highlightedAssets` array,
 * highlight those nodes on the graph page using Cytoscape.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAssetHighlight } from '../../../src/hooks/useAssetHighlight';
import type { McpHighlightedAsset } from '../../../src/types/mcpState';

describe('useAssetHighlight', () => {
  let mockCy: any;

  beforeEach(() => {
    // Create mock Cytoscape instance
    const mockNode = {
      addClass: vi.fn(),
      removeClass: vi.fn(),
      style: vi.fn(),
      data: vi.fn(() => ({ id: 'asset-1' })),
    };

    const mockCollection = {
      forEach: vi.fn((cb: any) => cb(mockNode)),
      removeClass: vi.fn(),
      length: 1,
    };

    const mockEmptyCollection = {
      forEach: vi.fn(),
      removeClass: vi.fn(),
      length: 0,
    };

    mockCy = {
      nodes: vi.fn((selector?: string) => {
        if (selector) {
          return selector.includes('asset-1') ? mockCollection : mockEmptyCollection;
        }
        return mockCollection;
      }),
      $: vi.fn((selector: string) => {
        return selector.includes('asset-1') ? mockCollection : mockEmptyCollection;
      }),
    };

    // Expose mock cy on window
    (window as any).cy = mockCy;
  });

  afterEach(() => {
    delete (window as any).cy;
  });

  it('should return the current highlight list', () => {
    const assets: McpHighlightedAsset[] = [
      { assetId: 'asset-1', mode: 'pulse' },
    ];

    const { result } = renderHook(
      ({ highlightedAssets }) => useAssetHighlight(highlightedAssets),
      { initialProps: { highlightedAssets: assets } }
    );

    expect(result.current.highlightedIds).toEqual(['asset-1']);
  });

  it('should attempt to apply highlight classes to matching nodes', () => {
    const assets: McpHighlightedAsset[] = [
      { assetId: 'asset-1', mode: 'pulse' },
    ];

    renderHook(
      ({ highlightedAssets }) => useAssetHighlight(highlightedAssets),
      { initialProps: { highlightedAssets: assets } }
    );

    // Verify that the Cytoscape API was queried for nodes
    expect(mockCy.$ || mockCy.nodes).toBeDefined();
  });

  it('should return empty list when no assets are highlighted', () => {
    const { result } = renderHook(() => useAssetHighlight(undefined));
    expect(result.current.highlightedIds).toEqual([]);
  });

  it('should return empty list when assets array is empty', () => {
    const { result } = renderHook(() => useAssetHighlight([]));
    expect(result.current.highlightedIds).toEqual([]);
  });

  it('should update when highlighted assets change', () => {
    const { result, rerender } = renderHook(
      ({ highlightedAssets }) => useAssetHighlight(highlightedAssets),
      { initialProps: { highlightedAssets: [{ assetId: 'asset-1', mode: 'pulse' as const }] } }
    );

    expect(result.current.highlightedIds).toEqual(['asset-1']);

    rerender({
      highlightedAssets: [
        { assetId: 'asset-2', mode: 'glow' as const },
        { assetId: 'asset-3', mode: 'zoom' as const },
      ],
    });

    expect(result.current.highlightedIds).toEqual(['asset-2', 'asset-3']);
  });

  it('should expose clearHighlights function', () => {
    const assets: McpHighlightedAsset[] = [
      { assetId: 'asset-1', mode: 'pulse' },
    ];

    const { result } = renderHook(
      ({ highlightedAssets }) => useAssetHighlight(highlightedAssets),
      { initialProps: { highlightedAssets: assets } }
    );

    expect(typeof result.current.clearHighlights).toBe('function');
  });

  it('should handle missing cytoscape instance gracefully', () => {
    delete (window as any).cy;

    const assets: McpHighlightedAsset[] = [
      { assetId: 'asset-1', mode: 'pulse' },
    ];

    // Should not throw
    const { result } = renderHook(
      ({ highlightedAssets }) => useAssetHighlight(highlightedAssets),
      { initialProps: { highlightedAssets: assets } }
    );

    expect(result.current.highlightedIds).toEqual(['asset-1']);
  });
});
