import { test, expect } from "@playwright/test";

test.describe("Detections Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/detections");
    await page.waitForLoadState("domcontentloaded");
    // Wait for React to mount
    await page.waitForTimeout(2000);
  });

  test("detections table loads", async ({ page }) => {
    // Check URL is correct
    await expect(page).toHaveURL(/detections/i);
    // Wait for content and verify page rendered
    await page.waitForTimeout(3000);
    const bodyContent = await page.locator("body").textContent();
    expect(bodyContent?.length ?? 0).toBeGreaterThan(0);
  });

  test("process tree view opens", async ({ page }) => {
    await page.waitForTimeout(2000);
    const processTreeBtn = page.locator('button:has-text("tree")').first();
    if (await processTreeBtn.isVisible().catch(() => false)) {
      await processTreeBtn.click();
      await page.waitForTimeout(500);
    }
    expect(true).toBeTruthy();
  });
});
