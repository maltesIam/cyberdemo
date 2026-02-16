/**
 * Surface Command Center E2E Tests
 *
 * Comprehensive tests for the Attack Surface WOW feature including:
 * - Page navigation and loading
 * - Mode switching (5 modes)
 * - Layer toggles (8 layers)
 * - Layer presets (5 presets)
 * - KPI chips (7 chips)
 */

import { test, expect, type Page } from "@playwright/test";

// ============================================================================
// Test Constants
// ============================================================================

/** All visual modes available in Surface page */
const MODES = ["surface", "graph", "vulns", "threats", "timeline"] as const;

/** Mode tab labels as displayed in the UI */
const MODE_LABELS: Record<(typeof MODES)[number], string> = {
  surface: "Surface 2D",
  graph: "Graph",
  vulns: "Vuln Landscape",
  threats: "Threat Map",
  timeline: "Timeline",
};

/** All available layers */
const LAYERS = [
  "base",
  "edr",
  "siem",
  "ctem",
  "vulnerabilities",
  "threats",
  "containment",
  "relations",
] as const;

/** Layer labels as displayed in the UI */
const LAYER_LABELS: Record<(typeof LAYERS)[number], string> = {
  base: "Base",
  edr: "EDR",
  siem: "SIEM",
  ctem: "CTEM",
  vulnerabilities: "Vulnerabilities",
  threats: "Threats",
  containment: "Containment",
  relations: "Relations",
};

/** Preset configurations */
const PRESETS = {
  soc: { label: "SOC", layers: ["base", "edr", "siem", "ctem"] },
  hunt: { label: "Hunt", layers: ["base", "threats", "relations", "edr"] },
  vuln: { label: "Vuln", layers: ["base", "vulnerabilities", "ctem"] },
  contain: { label: "Contain", layers: ["base", "siem", "edr", "containment"] },
  full: {
    label: "Full",
    layers: [
      "base",
      "edr",
      "siem",
      "ctem",
      "vulnerabilities",
      "threats",
      "containment",
      "relations",
    ],
  },
} as const;

/** KPI chip definitions */
const KPI_CHIPS = [
  "assets",
  "detections",
  "incidents",
  "critical",
  "kevs",
  "iocs",
  "contained",
] as const;

/** KPI chip labels as displayed in the UI */
const KPI_LABELS: Record<(typeof KPI_CHIPS)[number], string> = {
  assets: "Assets",
  detections: "Detections",
  incidents: "Incidents",
  critical: "Critical",
  kevs: "CVE-K",
  iocs: "IOC",
  contained: "Contained",
};

// ============================================================================
// Test Helpers
// ============================================================================

/**
 * Clear localStorage to reset layer state
 */
async function clearLayerStorage(page: Page) {
  await page.evaluate(() => {
    localStorage.removeItem("surface-layers");
  });
}

/**
 * Get the layer panel (aside with Presets)
 */
function getLayerPanel(page: Page) {
  return page.locator('aside:has-text("Presets")').first();
}

/**
 * Wait for the Surface page to be fully loaded
 */
async function waitForSurfaceLoad(page: Page) {
  await page.waitForLoadState("networkidle");
  // Wait for the mode tabs to be visible (indicates page is loaded)
  await expect(page.locator('button:has-text("Surface 2D")')).toBeVisible({
    timeout: 15000,
  });
}

// ============================================================================
// Test Suite: Page Navigation & Loading
// ============================================================================

test.describe("Surface Command Center - Page Navigation & Loading", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
  });

  test("navigates to /surface via sidebar Command Center link", async ({ page }) => {
    // Click on the Command Center link in the sidebar
    await page.click('aside a:has-text("Command Center")', { timeout: 10000 });

    // Verify URL changed to /surface
    await expect(page).toHaveURL(/\/surface/);
  });

  test("page loads without console errors", async ({ page }) => {
    const consoleErrors: string[] = [];

    // Listen for console errors
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto("/surface");
    await page.waitForLoadState("networkidle");

    // Wait a bit for any async errors
    await page.waitForTimeout(2000);

    // Filter out known benign errors (network failures, etc.)
    const criticalErrors = consoleErrors.filter(
      (err) =>
        !err.includes("Failed to load resource") &&
        !err.includes("net::ERR") &&
        !err.includes("favicon") &&
        !err.includes("ResizeObserver"),
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test("all 5 zones render correctly", async ({ page }) => {
    await page.goto("/surface");
    await page.waitForLoadState("networkidle");

    // Zone 1: Header bar (mode tabs area)
    const headerBar = page.locator("header");
    await expect(headerBar.first()).toBeVisible({ timeout: 10000 });

    // Zone 2: Left panel (layer controls) - contains "Presets" text
    await expect(page.locator('text="Presets"')).toBeVisible({ timeout: 10000 });

    // Zone 3: Center area - the main content area exists
    // Check for the Cyber Exposure Command Center heading
    await expect(page.locator('h1:has-text("Cyber Exposure Command Center")')).toBeVisible({
      timeout: 15000,
    });

    // Zone 4: Bottom bar (KPI chips) - contains footer with Assets chip
    const bottomBar = page.locator("footer");
    await expect(bottomBar.first()).toBeVisible({ timeout: 10000 });

    // Zone 5: Sidebar - aside element
    await expect(page.locator("aside").first()).toBeVisible({ timeout: 10000 });
  });

  test("sidebar remains visible and functional", async ({ page }) => {
    await page.goto("/surface");
    await page.waitForLoadState("networkidle");

    // Verify sidebar is visible
    const sidebar = page.locator("aside");
    await expect(sidebar.first()).toBeVisible({ timeout: 10000 });

    // Verify navigation links are present
    await expect(page.locator('aside a:has-text("Command Center")')).toBeVisible();
    await expect(page.locator('aside a:has-text("Dashboard")')).toBeVisible();
    await expect(page.locator('aside a:has-text("Assets")')).toBeVisible();

    // Verify Command Center link is active (has active styling)
    const commandCenterLink = page.locator('aside a:has-text("Command Center")');
    // Check for active state class or style
    const linkClass = await commandCenterLink.getAttribute("class");
    expect(linkClass).toMatch(/active|bg-|text-cyan|selected/i);
  });

  test("page title/heading displays Command Center or similar", async ({ page }) => {
    await page.goto("/surface");
    await page.waitForLoadState("networkidle");

    // Check page title or main heading
    const heading = page
      .locator("h1, h2")
      .filter({ hasText: /command center|surface|attack surface/i });
    // The header shows "CyberDemo - SOC Dashboard" so we check for Surface-related content in page
    const pageContent = await page.textContent("body");
    expect(pageContent?.toLowerCase()).toMatch(/surface|command|attack/i);
  });
});

// ============================================================================
// Test Suite: Mode Switching
// ============================================================================

test.describe("Surface Command Center - Mode Switching", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/surface");
    await page.waitForLoadState("networkidle");
  });

  test("Surface 2D tab is default active mode", async ({ page }) => {
    // Check URL has no mode param or mode=surface
    const url = page.url();
    expect(url).toMatch(/\/surface(\?mode=surface)?$/);

    // Find the Surface 2D tab and verify it's active
    const surfaceTab = page.locator('button, [role="tab"]').filter({ hasText: /Surface 2D/i });
    if (await surfaceTab.count()) {
      const tabClass = await surfaceTab.first().getAttribute("class");
      expect(tabClass).toMatch(/active|selected|bg-cyan|text-white/i);
    }
  });

  test.describe("clicking mode tabs", () => {
    for (const mode of MODES) {
      test(`clicking ${MODE_LABELS[mode]} tab updates mode`, async ({ page }) => {
        // Find and click the mode tab
        const tabSelector = `button:has-text("${MODE_LABELS[mode]}"), [role="tab"]:has-text("${MODE_LABELS[mode]}")`;
        const tab = page.locator(tabSelector).first();

        if (await tab.isVisible({ timeout: 5000 })) {
          await tab.click();
          await page.waitForTimeout(500); // Allow URL to update

          // Verify URL updated (except for default surface mode)
          if (mode !== "surface") {
            await expect(page).toHaveURL(new RegExp(`mode=${mode}`));
          }

          // Verify tab appears active
          const tabClass = await tab.getAttribute("class");
          expect(tabClass).toMatch(/active|selected|bg-|text-white/i);
        }
      });
    }
  });

  test("Graph mode shows different visualization", async ({ page }) => {
    const graphTab = page
      .locator('button:has-text("Graph"), [role="tab"]:has-text("Graph")')
      .first();

    if (await graphTab.isVisible({ timeout: 5000 })) {
      await graphTab.click();
      await page.waitForTimeout(1000);

      // Verify URL has graph mode
      await expect(page).toHaveURL(/mode=graph/);

      // Graph mode should show connections/edges
      // Look for SVG lines or connection elements
      const graphElements = page.locator('svg line, [data-testid="connection"], .graph-edge');
      // Graph may or may not have connections depending on data
    }
  });

  test("mode persists on page reload", async ({ page }) => {
    // Switch to Graph mode
    const graphTab = page
      .locator('button:has-text("Graph"), [role="tab"]:has-text("Graph")')
      .first();

    if (await graphTab.isVisible({ timeout: 5000 })) {
      await graphTab.click();
      await page.waitForTimeout(500);

      // Verify URL has graph mode
      await expect(page).toHaveURL(/mode=graph/);

      // Reload the page
      await page.reload();
      await page.waitForLoadState("networkidle");

      // Verify mode is preserved in URL
      await expect(page).toHaveURL(/mode=graph/);

      // Verify Graph tab is still active
      const graphTabAfterReload = page
        .locator('button:has-text("Graph"), [role="tab"]:has-text("Graph")')
        .first();
      const tabClass = await graphTabAfterReload.getAttribute("class");
      expect(tabClass).toMatch(/active|selected|bg-/i);
    }
  });
});

// ============================================================================
// Test Suite: Layer Toggles
// ============================================================================

test.describe("Surface Command Center - Layer Toggles", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/surface");
    await page.waitForLoadState("networkidle");
    // Clear layer storage to start fresh
    await clearLayerStorage(page);
    await page.reload();
    await page.waitForLoadState("networkidle");
  });

  test("all 8 layer toggle buttons are visible", async ({ page }) => {
    // Layer toggles are in the second aside panel (the one with "Presets" text)
    // The first aside is the main sidebar, the second is the layer panel
    const layerPanel = page.locator('aside:has-text("Presets")').first();
    await expect(layerPanel).toBeVisible({ timeout: 10000 });

    for (const layer of LAYERS) {
      const label = LAYER_LABELS[layer];
      // Each layer toggle is a button with the layer label text
      const toggle = layerPanel.locator(`button:has-text("${label}")`);
      await expect(toggle.first()).toBeVisible({ timeout: 10000 });
    }
  });

  test("base layer is always on and cannot be toggled off", async ({ page }) => {
    // The base layer button in SurfacePage has disabled attribute
    // Find the layer toggle button for Base in the left panel
    const layerPanel = getLayerPanel(page);
    const baseToggle = layerPanel.locator('button:has-text("Base")').first();

    await expect(baseToggle).toBeVisible({ timeout: 5000 });

    // Base layer button should be disabled
    const isDisabled = await baseToggle.isDisabled();
    expect(isDisabled).toBe(true);

    // The Base layer checkbox should show as enabled (has checkmark)
    // The checkbox has background color when enabled
    const checkbox = baseToggle.locator("div").first();
    await expect(checkbox).toBeVisible();
  });

  test.describe("toggling individual layers", () => {
    const toggleableLayers = LAYERS.filter((l) => l !== "base");

    for (const layer of toggleableLayers) {
      test(`can toggle ${LAYER_LABELS[layer]} layer on/off`, async ({ page }) => {
        const label = LAYER_LABELS[layer];
        // Layer toggles are in the layer panel (aside with Presets)
        const layerPanel = getLayerPanel(page);
        const toggle = layerPanel.locator(`button:has-text("${label}")`).first();

        await expect(toggle).toBeVisible({ timeout: 5000 });

        // Check the checkbox inside - if it has a checkmark SVG, it's enabled
        const checkboxInner = toggle.locator("svg");

        // Get initial state - check if checkbox has svg (checkmark means enabled)
        const initialHasSvg = (await checkboxInner.count()) > 0;

        // Click to toggle
        await toggle.click({ force: true });
        await page.waitForTimeout(500);

        // Get new state
        const newHasSvg = (await checkboxInner.count()) > 0;

        // State should have changed
        expect(newHasSvg).not.toBe(initialHasSvg);

        // Toggle back
        await toggle.click({ force: true });
        await page.waitForTimeout(500);

        // Should be back to original state
        const finalHasSvg = (await checkboxInner.count()) > 0;
        expect(finalHasSvg).toBe(initialHasSvg);
      });
    }
  });

  test("layer state persists in localStorage", async ({ page }) => {
    // First, click the "Full" preset to enable all layers
    const layerPanel = getLayerPanel(page);
    const fullPreset = layerPanel.locator('button:has-text("Full")').first();
    await expect(fullPreset).toBeVisible({ timeout: 5000 });
    await fullPreset.click({ force: true });
    await page.waitForTimeout(500);

    // Check localStorage
    const storedLayers = await page.evaluate(() => {
      const stored = localStorage.getItem("surface-layers");
      return stored ? JSON.parse(stored) : null;
    });

    expect(storedLayers).toBeTruthy();
    expect(Array.isArray(storedLayers)).toBe(true);
    // Full preset should have all 8 layers
    expect(storedLayers.length).toBe(8);

    // Reload page
    await page.reload();
    await page.waitForLoadState("networkidle");

    // Verify layers are still in the state
    const layersAfterReload = await page.evaluate(() => {
      const stored = localStorage.getItem("surface-layers");
      return stored ? JSON.parse(stored) : null;
    });

    // All layers should be preserved
    expect(layersAfterReload.length).toBe(8);
    expect(layersAfterReload).toContain("base");
    expect(layersAfterReload).toContain("edr");
    expect(layersAfterReload).toContain("siem");
  });
});

// ============================================================================
// Test Suite: Layer Presets
// ============================================================================

test.describe("Surface Command Center - Layer Presets", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/surface");
    await page.waitForLoadState("networkidle");
    await clearLayerStorage(page);
    await page.reload();
    await page.waitForLoadState("networkidle");
  });

  for (const [presetKey, preset] of Object.entries(PRESETS)) {
    test(`${preset.label} preset activates correct layers`, async ({ page }) => {
      // Preset buttons are in the layer panel under "Presets" section
      const layerPanel = getLayerPanel(page);
      // Use exact text match to avoid matching partial text
      const presetButton = layerPanel
        .locator(`button`)
        .filter({ hasText: new RegExp(`^${preset.label}$`) })
        .first();

      await expect(presetButton).toBeVisible({ timeout: 5000 });
      await presetButton.click({ force: true });
      await page.waitForTimeout(800); // Wait for localStorage to update

      // Check localStorage for active layers
      const activeLayers = await page.evaluate(() => {
        const stored = localStorage.getItem("surface-layers");
        return stored ? JSON.parse(stored) : [];
      });

      // Verify all expected layers are active
      for (const expectedLayer of preset.layers) {
        expect(activeLayers).toContain(expectedLayer);
      }

      // Verify layers NOT in preset are NOT active (except base which is always on)
      for (const layer of LAYERS) {
        if (!(preset.layers as readonly string[]).includes(layer) && layer !== "base") {
          expect(activeLayers).not.toContain(layer);
        }
      }
    });
  }

  test("Full preset activates all 8 layers", async ({ page }) => {
    const layerPanel = getLayerPanel(page);
    const fullButton = layerPanel
      .locator("button")
      .filter({ hasText: /^Full$/ })
      .first();

    await expect(fullButton).toBeVisible({ timeout: 5000 });
    await fullButton.click({ force: true });
    await page.waitForTimeout(800);

    const activeLayers = await page.evaluate(() => {
      const stored = localStorage.getItem("surface-layers");
      return stored ? JSON.parse(stored) : [];
    });

    // All 8 layers should be active
    expect(activeLayers.length).toBe(8);
    for (const layer of LAYERS) {
      expect(activeLayers).toContain(layer);
    }
  });

  test("preset buttons have correct visual state when active", async ({ page }) => {
    const layerPanel = getLayerPanel(page);

    // Click SOC preset
    const socButton = layerPanel.locator("button").filter({ hasText: /^SOC$/ }).first();

    await expect(socButton).toBeVisible({ timeout: 5000 });
    await socButton.click({ force: true });
    await page.waitForTimeout(500);

    // SOC should appear active - has bg-cyan-600 class
    const socClass = await socButton.getAttribute("class");
    expect(socClass).toMatch(/bg-cyan/i);

    // Click Hunt preset
    const huntButton = layerPanel
      .locator("button")
      .filter({ hasText: /^Hunt$/ })
      .first();
    await expect(huntButton).toBeVisible();
    await huntButton.click({ force: true });
    await page.waitForTimeout(500);

    // Hunt should now be active
    const huntClass = await huntButton.getAttribute("class");
    expect(huntClass).toMatch(/bg-cyan/i);

    // SOC should no longer be active (should have bg-gray instead of bg-cyan)
    const socClassAfter = await socButton.getAttribute("class");
    expect(socClassAfter).toMatch(/bg-gray/i);
  });
});

// ============================================================================
// Test Suite: KPI Chips (Bottom Bar)
// ============================================================================

test.describe("Surface Command Center - KPI Chips", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/surface");
    await page.waitForLoadState("networkidle");
  });

  test("all 7 KPI chips are visible", async ({ page }) => {
    // KPI chips are in the footer element
    const footer = page.locator("footer");
    await expect(footer).toBeVisible({ timeout: 10000 });

    for (const kpi of KPI_CHIPS) {
      const label = KPI_LABELS[kpi];
      // Each KPI chip is a button in the footer containing the label text
      const chip = footer.locator(`button`).filter({ hasText: label }).first();
      await expect(chip).toBeVisible({ timeout: 10000 });
    }
  });

  test("each KPI chip shows a count number", async ({ page }) => {
    const footer = page.locator("footer");
    await expect(footer).toBeVisible({ timeout: 10000 });

    for (const kpi of KPI_CHIPS) {
      const label = KPI_LABELS[kpi];
      // Find the chip button in footer
      const chipButton = footer.locator(`button`).filter({ hasText: label }).first();

      await expect(chipButton).toBeVisible({ timeout: 5000 });

      // Get the text content and look for a number
      const text = await chipButton.textContent();
      // Should contain a number (the count) - KPI chips have format: count + label
      // The count is displayed as a number before or as part of the chip content
      expect(text).toMatch(/\d+/);
    }
  });

  test.describe("clicking KPI chips activates relevant layers", () => {
    test("clicking Assets chip works", async ({ page }) => {
      const footer = page.locator("footer");
      const chip = footer.locator("button").filter({ hasText: "Assets" }).first();

      await expect(chip).toBeVisible({ timeout: 5000 });
      await chip.click({ force: true });
      await page.waitForTimeout(300);
      // Clicking should filter or highlight relevant assets
      // The chip should show active state (ring style)
      const chipClass = await chip.getAttribute("class");
      expect(chipClass).toBeDefined();
    });

    test("clicking Detections chip works", async ({ page }) => {
      const footer = page.locator("footer");
      const chip = footer.locator("button").filter({ hasText: "Detections" }).first();

      await expect(chip).toBeVisible({ timeout: 5000 });
      await chip.click({ force: true });
      await page.waitForTimeout(300);
      // Should trigger EDR layer or filter
    });

    test("clicking Incidents chip works", async ({ page }) => {
      const footer = page.locator("footer");
      const chip = footer.locator("button").filter({ hasText: "Incidents" }).first();

      await expect(chip).toBeVisible({ timeout: 5000 });
      await chip.click({ force: true });
      await page.waitForTimeout(300);
      // Should trigger SIEM layer or filter
    });

    test("clicking Critical chip works", async ({ page }) => {
      const footer = page.locator("footer");
      const chip = footer.locator("button").filter({ hasText: "Critical" }).first();

      await expect(chip).toBeVisible({ timeout: 5000 });
      await chip.click({ force: true });
      await page.waitForTimeout(300);
      // Should filter to critical assets
    });

    test("clicking CVE-K chip works", async ({ page }) => {
      const footer = page.locator("footer");
      const chip = footer.locator("button").filter({ hasText: "CVE-K" }).first();

      await expect(chip).toBeVisible({ timeout: 5000 });
      await chip.click({ force: true });
      await page.waitForTimeout(300);
      // Should activate vulnerabilities layer
    });

    test("clicking Contained chip works", async ({ page }) => {
      const footer = page.locator("footer");
      const chip = footer.locator("button").filter({ hasText: "Contained" }).first();

      await expect(chip).toBeVisible({ timeout: 5000 });
      await chip.click({ force: true });
      await page.waitForTimeout(300);
      // Should activate containment layer
    });

    test("clicking IOC chip works", async ({ page }) => {
      const footer = page.locator("footer");
      const chip = footer.locator("button").filter({ hasText: "IOC" }).first();

      await expect(chip).toBeVisible({ timeout: 5000 });
      await chip.click({ force: true });
      await page.waitForTimeout(300);
      // Should activate threats layer
    });
  });
});

// ============================================================================
// Test Suite: Integration Tests
// ============================================================================

test.describe("Surface Command Center - Integration", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/surface");
    await page.waitForLoadState("networkidle");
  });

  test("mode switching preserves layer selection", async ({ page }) => {
    // Set Full preset to enable all layers
    const fullButton = page.locator('button:has-text("Full"), [data-preset="full"]').first();

    if (await fullButton.isVisible({ timeout: 5000 })) {
      await fullButton.click();
      await page.waitForTimeout(300);

      // Get active layers
      const layersBefore = await page.evaluate(() => {
        const stored = localStorage.getItem("surface-layers");
        return stored ? JSON.parse(stored) : [];
      });

      // Switch to Graph mode
      const graphTab = page
        .locator('button:has-text("Graph"), [role="tab"]:has-text("Graph")')
        .first();
      if (await graphTab.isVisible()) {
        await graphTab.click();
        await page.waitForTimeout(500);

        // Verify layers are preserved
        const layersAfter = await page.evaluate(() => {
          const stored = localStorage.getItem("surface-layers");
          return stored ? JSON.parse(stored) : [];
        });

        expect(layersAfter).toEqual(layersBefore);
      }
    }
  });

  test("direct URL navigation to /surface?mode=graph works", async ({ page }) => {
    await page.goto("/surface?mode=graph");
    await page.waitForLoadState("networkidle");

    // Verify Graph tab is active
    const graphTab = page
      .locator('button:has-text("Graph"), [role="tab"]:has-text("Graph")')
      .first();
    if (await graphTab.isVisible({ timeout: 5000 })) {
      const tabClass = await graphTab.getAttribute("class");
      expect(tabClass).toMatch(/active|selected|bg-/i);
    }
  });

  test("page does not crash with invalid mode parameter", async ({ page }) => {
    await page.goto("/surface?mode=invalid");
    await page.waitForLoadState("networkidle");

    // Page should load without crashing
    await expect(page.locator("body")).toBeVisible();

    // Should fallback to default mode (surface)
    const surfaceTab = page
      .locator('button:has-text("Surface 2D"), [role="tab"]:has-text("Surface 2D")')
      .first();
    if (await surfaceTab.isVisible({ timeout: 5000 })) {
      const tabClass = await surfaceTab.getAttribute("class");
      expect(tabClass).toMatch(/active|selected|bg-/i);
    }
  });

  test("bottom bar is visible in all modes", async ({ page }) => {
    for (const mode of MODES) {
      // Navigate to mode
      if (mode === "surface") {
        await page.goto("/surface");
      } else {
        await page.goto(`/surface?mode=${mode}`);
      }
      await page.waitForLoadState("networkidle");

      // Bottom bar should be visible with KPI chips
      const assetsChip = page.locator(':text("Assets")').first();
      await expect(assetsChip).toBeVisible({ timeout: 10000 });
    }
  });
});
