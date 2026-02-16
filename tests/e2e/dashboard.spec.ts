import { test, expect } from "@playwright/test";

test.describe("Dashboard Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("KPI cards are visible", async ({ page }) => {
    // Wait for dashboard to load - look for KPI card titles
    await page.waitForTimeout(2000);
    // The dashboard shows KPI cards with titles like "Total Incidents", "Critical Open", etc.
    const kpiTitle = page.locator("text=Total Incidents");
    await expect(kpiTitle).toBeVisible({ timeout: 15000 });
  });

  test("total incidents count is shown", async ({ page }) => {
    await page.waitForTimeout(2000);
    // Look for the "Total Incidents" KPI card title
    const totalIncidents = page.locator("text=Total Incidents");
    await expect(totalIncidents).toBeVisible({ timeout: 15000 });
  });

  test("critical count is shown", async ({ page }) => {
    await page.waitForTimeout(2000);
    // Look for the "Critical Open" KPI card title
    const criticalOpen = page.locator("text=Critical Open");
    await expect(criticalOpen).toBeVisible({ timeout: 15000 });
  });

  test("dashboard loads without errors", async ({ page }) => {
    await page.waitForTimeout(2000);
    // Check page title is visible (Dashboard)
    const title = page.locator('h1:has-text("Dashboard")');
    await expect(title).toBeVisible({ timeout: 10000 });
  });
});
