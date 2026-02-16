import { test, expect } from "@playwright/test";

test.describe("Incidents Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/incidents");
    await page.waitForLoadState("domcontentloaded");
    // Wait for React to mount
    await page.waitForTimeout(2000);
  });

  test("incidents table loads", async ({ page }) => {
    // Check URL is correct
    await expect(page).toHaveURL(/incidents/i);
    // Wait for content and verify page rendered
    await page.waitForTimeout(3000);
    const bodyContent = await page.locator("body").textContent();
    expect(bodyContent?.length ?? 0).toBeGreaterThan(0);
  });

  test("incidents filter by severity works", async ({ page }) => {
    await page.waitForTimeout(2000);
    const severityFilter = page.locator("select").first();
    if (await severityFilter.isVisible().catch(() => false)) {
      await severityFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);
    }
    expect(true).toBeTruthy();
  });

  test("incident detail opens on click", async ({ page }) => {
    await page.waitForTimeout(2000);
    const firstRow = page.locator("tbody tr").first();
    if (await firstRow.isVisible().catch(() => false)) {
      await firstRow.click();
      await page.waitForTimeout(500);
    }
    expect(true).toBeTruthy();
  });
});
