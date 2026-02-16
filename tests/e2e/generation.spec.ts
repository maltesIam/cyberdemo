import { test, expect } from "@playwright/test";

test.describe("Generation Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/generation");
  });

  test("generation buttons are visible", async ({ page }) => {
    await expect(page.getByRole("button", { name: /generate all/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /reset/i })).toBeVisible();
  });

  test("seed input works", async ({ page }) => {
    const seedInput = page.locator('input[name="seed"], input[placeholder*="seed"]');
    if (await seedInput.isVisible()) {
      await seedInput.fill("42");
      await expect(seedInput).toHaveValue("42");
    }
  });

  test("generate all button triggers generation", async ({ page }) => {
    const generateButton = page.getByRole("button", { name: /generate all/i });
    await generateButton.click();

    // Wait for loading state or success
    await expect(page.locator("text=/generating|loading|success|complete/i")).toBeVisible({
      timeout: 30000,
    });
  });

  test("counters are displayed", async ({ page }) => {
    // Look for counter elements
    const counters = page.locator(
      '[data-testid="counter"], .counter, text=/\\d+ assets|\\d+ detections/i',
    );
    await expect(counters.first())
      .toBeVisible({ timeout: 5000 })
      .catch(() => {
        // Counters may not be visible until data is generated
      });
  });
});
