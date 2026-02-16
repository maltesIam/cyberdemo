import { test, expect } from "@playwright/test";

test.describe("Navigation and Layout", () => {
  test("app loads correctly", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await expect(page).toHaveTitle(/CyberDemo|SOC/i);
    await expect(page.locator("body")).toBeVisible();
  });

  test("sidebar is visible", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    const sidebar = page.locator("aside");
    await expect(sidebar.first()).toBeVisible({ timeout: 10000 });
  });

  test("navigate to generation page", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    // Click on sidebar nav link
    await page.click('aside a:has-text("Generation")', { timeout: 10000 });
    await expect(page).toHaveURL(/generation/i);
  });

  test("navigate to dashboard page", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    // Click on sidebar nav link specifically, not the header
    await page.click('aside a:has-text("Dashboard")', { timeout: 10000 });
    await expect(page).toHaveURL(/dashboard/i);
  });

  test("navigate to assets page", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.click('aside a:has-text("Assets")', { timeout: 10000 });
    await expect(page).toHaveURL(/assets/i);
  });

  test("navigate to incidents page", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.click('aside a:has-text("Incidents")', { timeout: 10000 });
    await expect(page).toHaveURL(/incidents/i);
  });

  test("navigate to detections page", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.click('aside a:has-text("Detections")', { timeout: 10000 });
    await expect(page).toHaveURL(/detections/i);
  });

  test("navigate to timeline page", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.click('aside a:has-text("Timeline")', { timeout: 10000 });
    await expect(page).toHaveURL(/timeline/i);
  });

  test("navigate to postmortems page", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.click('aside a:has-text("Postmortems")', { timeout: 10000 });
    await expect(page).toHaveURL(/postmortems/i);
  });

  test("navigate to tickets page", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.click('aside a:has-text("Tickets")', { timeout: 10000 });
    await expect(page).toHaveURL(/tickets/i);
  });
});
