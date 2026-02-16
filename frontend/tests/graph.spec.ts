/**
 * Graph Component Tests (Playwright)
 *
 * TDD tests for W8: Frontend Grafos with Cytoscape.js
 * Tests cover:
 * 1. Graph rendering with nodes
 * 2. Node click opens detail panel
 * 3. Panel shows 4 sections
 * 4. Node colors reflect risk
 * 5. Zoom and pan controls
 * 6. Auto layout functionality
 */

import { test, expect } from "@playwright/test";

// Test data - mock incident for testing
const TEST_INCIDENT_ID = "INC-ANCHOR-001";

test.describe("Graph Component - W8 Frontend Grafos", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to graph page
    await page.goto(`/graph/${TEST_INCIDENT_ID}`);
    // Wait for graph to initialize
    await page.waitForSelector('[data-testid="cytoscape-graph"]', {
      timeout: 10000,
    });
  });

  // TEST 1: Graph renders with nodes
  test("graph component renders with nodes", async ({ page }) => {
    // Assert graph container is visible
    const graphContainer = page.locator('[data-testid="cytoscape-graph"]');
    await expect(graphContainer).toBeVisible();

    // Verify graph has nodes
    const nodeCount = await page.evaluate(() => {
      const cy = (window as any).cy;
      return cy ? cy.nodes().length : 0;
    });

    expect(nodeCount).toBeGreaterThan(0);
  });

  // TEST 2: Nodes are clickable and open panel
  test("graph nodes are clickable and open panel", async ({ page }) => {
    // Wait for graph to be ready
    await page.waitForFunction(() => {
      const cy = (window as any).cy;
      return cy && cy.nodes().length > 0;
    });

    // Click on a node
    await page.evaluate(() => {
      const cy = (window as any).cy;
      const node = cy.nodes().first();
      node.emit("tap");
    });

    // Panel should be visible
    const panel = page.locator('[data-testid="node-detail-panel"]');
    await expect(panel).toBeVisible();
  });

  // TEST 3: Panel shows all 4 sections
  test("node panel shows correct sections", async ({ page }) => {
    // Wait for graph
    await page.waitForFunction(() => {
      const cy = (window as any).cy;
      return cy && cy.nodes().length > 0;
    });

    // Click on an asset node
    await page.evaluate(() => {
      const cy = (window as any).cy;
      const assetNode = cy.nodes('[type="asset"]').first();
      if (assetNode.length > 0) {
        assetNode.emit("tap");
      } else {
        cy.nodes().first().emit("tap");
      }
    });

    // Verify all 4 sections exist
    await expect(page.locator('[data-testid="section-asset-info"]')).toBeVisible();
    await expect(page.locator('[data-testid="section-threat"]')).toBeVisible();
    await expect(page.locator('[data-testid="section-recommendation"]')).toBeVisible();
    await expect(page.locator('[data-testid="section-status"]')).toBeVisible();
  });

  // TEST 4: Node colors reflect risk level
  test("graph nodes have correct colors based on risk", async ({ page }) => {
    // Wait for graph
    await page.waitForFunction(() => {
      const cy = (window as any).cy;
      return cy && cy.nodes().length > 0;
    });

    // Get node colors
    const nodeColors = await page.evaluate(() => {
      const cy = (window as any).cy;
      return cy.nodes().map((n: any) => ({
        id: n.id(),
        color: n.data("color"),
        type: n.data("type"),
      }));
    });

    // Verify colors are valid
    const validColors = ["green", "yellow", "red", "blue"];
    for (const node of nodeColors) {
      expect(validColors).toContain(node.color);
    }
  });

  // TEST 5: Zoom controls work
  test("graph supports zoom and pan", async ({ page }) => {
    // Wait for graph
    await page.waitForFunction(() => {
      const cy = (window as any).cy;
      return cy && cy.nodes().length > 0;
    });

    // Get initial zoom level
    const initialZoom = await page.evaluate(() => {
      const cy = (window as any).cy;
      return cy.zoom();
    });

    // Click zoom in button
    await page.click('[data-testid="zoom-in-btn"]');

    // Get new zoom level
    const newZoom = await page.evaluate(() => {
      const cy = (window as any).cy;
      return cy.zoom();
    });

    // Zoom should have increased
    expect(newZoom).toBeGreaterThan(initialZoom);
  });

  // TEST 6: Auto layout works
  test("graph has automatic layout", async ({ page }) => {
    // Wait for graph
    await page.waitForFunction(() => {
      const cy = (window as any).cy;
      return cy && cy.nodes().length > 0;
    });

    // Get initial positions
    const initialPositions = await page.evaluate(() => {
      const cy = (window as any).cy;
      return cy.nodes().map((n: any) => ({
        id: n.id(),
        position: n.position(),
      }));
    });

    // Click auto-layout button
    await page.click('[data-testid="auto-layout-btn"]');

    // Wait for animation
    await page.waitForTimeout(600);

    // Get new positions
    const newPositions = await page.evaluate(() => {
      const cy = (window as any).cy;
      return cy.nodes().map((n: any) => ({
        id: n.id(),
        position: n.position(),
      }));
    });

    // Verify nodes are not all at the same position
    const uniquePositions = new Set(
      newPositions.map((p: any) => `${Math.round(p.position.x)},${Math.round(p.position.y)}`),
    );
    expect(uniquePositions.size).toBeGreaterThan(1);
  });

  // TEST 7: Graph controls toolbar is visible
  test("graph controls toolbar is visible", async ({ page }) => {
    await expect(page.locator('[data-testid="zoom-in-btn"]')).toBeVisible();
    await expect(page.locator('[data-testid="zoom-out-btn"]')).toBeVisible();
    await expect(page.locator('[data-testid="fit-screen-btn"]')).toBeVisible();
    await expect(page.locator('[data-testid="auto-layout-btn"]')).toBeVisible();
  });

  // TEST 8: Fit to screen works
  test("fit to screen centers graph", async ({ page }) => {
    // Wait for graph
    await page.waitForFunction(() => {
      const cy = (window as any).cy;
      return cy && cy.nodes().length > 0;
    });

    // Click fit to screen
    await page.click('[data-testid="fit-screen-btn"]');

    // Graph should be visible and centered
    const graphContainer = page.locator('[data-testid="cytoscape-graph"]');
    await expect(graphContainer).toBeVisible();

    // Verify all nodes are visible in viewport
    const allNodesVisible = await page.evaluate(() => {
      const cy = (window as any).cy;
      const ext = cy.extent();
      return cy.nodes().every((n: any) => {
        const pos = n.position();
        return pos.x >= ext.x1 && pos.x <= ext.x2 && pos.y >= ext.y1 && pos.y <= ext.y2;
      });
    });

    expect(allNodesVisible).toBe(true);
  });
});

test.describe("Graph Page - Navigation", () => {
  // TEST: Navigate to graph from incidents page
  test("can navigate to graph from incidents", async ({ page }) => {
    await page.goto("/incidents");

    // Click view graph button if exists
    const viewGraphBtn = page.locator('[data-testid="view-graph-btn"]').first();
    if (await viewGraphBtn.isVisible()) {
      await viewGraphBtn.click();
      await expect(page.locator('[data-testid="cytoscape-graph"]')).toBeVisible();
    }
  });

  // TEST: Graph page without incident shows empty state
  test("graph page without incident shows empty state", async ({ page }) => {
    await page.goto("/graph");

    // Should show empty state message
    await expect(page.getByText("No graph data available")).toBeVisible();
  });
});
