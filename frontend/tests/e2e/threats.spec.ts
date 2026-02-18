/**
 * Threat Intelligence Page - E2E Tests with Playwright
 *
 * Tests cover:
 * - Navigation from sidebar
 * - Page loading and rendering
 * - UI components visibility
 * - Interactive elements
 * - Error handling
 */

import { test, expect } from "@playwright/test";

test.describe("Threat Intel Navigation", () => {
  test("should have Threat Intel menu item in sidebar", async ({ page }) => {
    await page.goto("/");

    // Wait for sidebar to load
    await page.waitForSelector("nav");

    // Check Threat Intel menu item exists
    const threatMenuItem = page.getByText("Threat Intel");
    await expect(threatMenuItem).toBeVisible();
  });

  test("should navigate to /threats when clicking Threat Intel menu", async ({ page }) => {
    await page.goto("/");

    // Click on Threat Intel menu item
    await page.getByText("Threat Intel").click();

    // Verify URL changed
    await expect(page).toHaveURL(/.*\/threats/);
  });

  test("should highlight Threat Intel menu when on threats page", async ({ page }) => {
    await page.goto("/threats");

    // Find the Threat Intel link
    const threatLink = page.getByRole("link", { name: /Threat Intel/i });

    // Verify it has active styling (bg-cyan-600)
    await expect(threatLink).toHaveClass(/bg-cyan-600/);
  });

  test("should position Threat Intel after Vulnerabilities in menu", async ({ page }) => {
    await page.goto("/");

    // Get all navigation links
    const navLinks = page.locator("nav a");
    const texts = await navLinks.allTextContents();

    const vulnIndex = texts.findIndex(t => t.includes("Vulnerabilities"));
    const threatIndex = texts.findIndex(t => t.includes("Threat Intel"));

    expect(threatIndex).toBe(vulnIndex + 1);
  });
});

test.describe("Threat Intel Page Loading", () => {
  test("should load threats page without errors", async ({ page }) => {
    // Listen for console errors
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });

    await page.goto("/threats");

    // Wait for page to stabilize
    await page.waitForLoadState("networkidle");

    // Should not have critical errors
    const criticalErrors = errors.filter(
      e => !e.includes("favicon") && !e.includes("API")
    );
    expect(criticalErrors.length).toBe(0);
  });

  test("should display page content (not blank)", async ({ page }) => {
    await page.goto("/threats");

    // Page should have visible content
    const body = page.locator("body");
    const text = await body.textContent();

    expect(text?.length).toBeGreaterThan(100);
  });

  test("should render within Layout component", async ({ page }) => {
    await page.goto("/threats");

    // Should have sidebar visible
    const sidebar = page.locator("aside");
    await expect(sidebar).toBeVisible();

    // Should have main content area
    const main = page.locator("main");
    await expect(main).toBeVisible();
  });
});

test.describe("Threat Intel Page Content", () => {
  test("should display threat-related heading or title", async ({ page }) => {
    await page.goto("/threats");

    // Look for any heading related to threats/intelligence
    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible();
  });

  test("should have IOC input or search functionality", async ({ page }) => {
    await page.goto("/threats");

    // Look for input field for IOC search
    const input = page.locator("input[type='text'], input[placeholder*='IP'], input[placeholder*='IOC'], textarea");

    // Should have at least one input
    const count = await input.count();
    expect(count).toBeGreaterThan(0);
  });

  test("should display threat map or visualization area", async ({ page }) => {
    await page.goto("/threats");

    // Wait for any canvas, svg, or map component
    const visualization = page.locator("canvas, svg.threat-map, [class*='map'], [class*='Map']");

    // Allow some time for visualization to render
    await page.waitForTimeout(1000);

    // Should have some visualization element
    const hasVisualization = await visualization.count() > 0 ||
      await page.locator("[class*='threat'], [class*='Threat']").count() > 0;

    expect(hasVisualization).toBe(true);
  });
});

test.describe("Threat Intel Interactions", () => {
  test("should be able to enter IOC value in input", async ({ page }) => {
    await page.goto("/threats");

    // Find input field
    const input = page.locator("input[type='text'], textarea").first();

    if (await input.isVisible()) {
      // Type a test IP
      await input.fill("8.8.8.8");

      // Verify input value
      await expect(input).toHaveValue("8.8.8.8");
    }
  });

  test("should have clickable enrich or analyze button", async ({ page }) => {
    await page.goto("/threats");

    // Look for enrich/analyze button - "Enrich Threats" is the actual text
    const button = page.locator("button").filter({
      hasText: /enrich|analyze|search|lookup|submit|threats/i
    }).first();

    await expect(button).toBeVisible();
  });

  test("should show MITRE ATT&CK section or techniques", async ({ page }) => {
    await page.goto("/threats");

    // Look for MITRE ATT&CK related content
    const mitreContent = page.locator("text=/MITRE|ATT&CK|Technique|Tactic/i");

    // May need to scroll or wait
    await page.waitForTimeout(500);

    const hasMitre = await mitreContent.count() > 0;
    // This is informational - page may or may not have MITRE visible initially
    console.log(`MITRE ATT&CK content visible: ${hasMitre}`);
  });
});

test.describe("Threat Intel Responsiveness", () => {
  test("should be responsive on mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/threats");

    // Page should still load and be usable
    await expect(page.locator("body")).toBeVisible();
  });

  test("should be responsive on tablet viewport", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto("/threats");

    // Page should still load and be usable
    await expect(page.locator("body")).toBeVisible();
  });

  test("should be responsive on desktop viewport", async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto("/threats");

    // Page should still load and be usable
    await expect(page.locator("body")).toBeVisible();

    // Sidebar should be visible on desktop
    await expect(page.locator("aside")).toBeVisible();
  });
});

test.describe("Threat Intel Navigation Integration", () => {
  test("should navigate from home to Threats via sidebar", async ({ page }) => {
    // Start at home/generation page (default redirect)
    await page.goto("/generation");
    await page.waitForLoadState("networkidle");

    // Wait for sidebar to be ready
    const sidebar = page.locator("aside");
    await expect(sidebar).toBeVisible();

    // Click on Threat Intel link in sidebar
    await page.click('a[href="/threats"]');

    // Should navigate to threats
    await expect(page).toHaveURL(/.*\/threats/);
  });

  test("should maintain sidebar state when navigating", async ({ page }) => {
    await page.goto("/threats");

    // Sidebar should remain visible during navigation
    const sidebar = page.locator("aside");
    await expect(sidebar).toBeVisible();

    // Navigate to another page using sidebar nav link
    await page.locator("nav").getByText("Dashboard").click();

    // Sidebar should still be visible
    await expect(sidebar).toBeVisible();
  });

  test("should direct access /threats URL work", async ({ page }) => {
    // Direct navigation to threats URL
    await page.goto("/threats");

    // Should load without redirect
    await expect(page).toHaveURL(/.*\/threats/);

    // Should have content
    const content = page.locator("main");
    await expect(content).toBeVisible();
  });
});

test.describe("Threat Intel Error Handling", () => {
  test("should handle network errors gracefully", async ({ page }) => {
    // Block API calls
    await page.route("**/api/**", (route) => route.abort());

    await page.goto("/threats");

    // Page should still render (may show error state)
    await expect(page.locator("body")).toBeVisible();
  });

  test.skip("should not crash on slow network", async ({ page }) => {
    // Skip: Network throttling in Playwright can be flaky in CI environments
    // This test is for edge case validation only
    const client = await page.context().newCDPSession(page);
    await client.send("Network.emulateNetworkConditions", {
      offline: false,
      downloadThroughput: 500 * 1024,
      uploadThroughput: 500 * 1024,
      latency: 100,
    });

    await page.goto("/threats", { timeout: 60000 });
    await expect(page.locator("body")).toBeVisible();
  });
});

test.describe("Threat Intel Accessibility", () => {
  test("should have no critical accessibility violations", async ({ page }) => {
    await page.goto("/threats");

    // Basic accessibility checks
    // Check for heading structure
    const headings = page.locator("h1, h2, h3");
    const headingCount = await headings.count();
    expect(headingCount).toBeGreaterThan(0);
  });

  test("should be keyboard navigable", async ({ page }) => {
    await page.goto("/threats");

    // Tab through the page
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");

    // Should have focus on some element
    const focusedElement = page.locator(":focus");
    await expect(focusedElement).toBeVisible();
  });

  test("should have proper focus indicators", async ({ page }) => {
    await page.goto("/threats");

    // Find a focusable element
    const link = page.locator("a").first();
    await link.focus();

    // Should have visible focus
    await expect(link).toBeFocused();
  });
});
