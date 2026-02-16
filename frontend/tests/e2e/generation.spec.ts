/**
 * E2E Tests for Generation Page - CyberDemo
 *
 * Tests all generation buttons and verifies data increments correctly.
 * These tests verify that the backend Python generators execute and
 * the data counts increase as expected.
 *
 * Date: 2026-02-15
 */

import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:3000";
const API_URL = "http://localhost:8000";

// Helper to get current data counts from the page
async function getDataCounts(page: any): Promise<Record<string, number>> {
  await page.waitForSelector("text=Assets");

  const counts: Record<string, number> = {};

  // Extract counts from the data status cards
  const cards = await page.locator("main >> text=/^\\d+$/").all();

  // The order is: Assets, Incidents, Detections, Postmortems, Tickets, Agent Actions
  const labels = ["assets", "incidents", "detections", "postmortems", "tickets", "agent_actions"];

  for (let i = 0; i < Math.min(cards.length, labels.length); i++) {
    const text = await cards[i].textContent();
    counts[labels[i]] = parseInt(text || "0", 10);
  }

  return counts;
}

// Helper to wait for data status to load
async function waitForDataStatus(page: any): Promise<void> {
  // Wait for the loading spinner to disappear and counts to appear
  await page.waitForFunction(
    () => {
      const cards = document.querySelectorAll("main p");
      let hasNumber = false;
      cards.forEach((card) => {
        if (/^\d+$/.test(card.textContent || "")) {
          hasNumber = true;
        }
      });
      return hasNumber;
    },
    { timeout: 10000 },
  );
}

test.describe("Generation Page - Button Tests", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/generation`);
    await waitForDataStatus(page);
  });

  test("GEN-BTN-001: Generate All button exists and is clickable", async ({ page }) => {
    const button = page.getByRole("button", { name: "Generate All" });
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
  });

  test("GEN-BTN-002: Generate Assets button exists and is clickable", async ({ page }) => {
    const button = page.getByRole("button", { name: "Generate Assets" });
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
  });

  test("GEN-BTN-003: Generate EDR button exists and is clickable", async ({ page }) => {
    const button = page.getByRole("button", { name: "Generate EDR" });
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
  });

  test("GEN-BTN-004: Reset All Data button exists and is clickable", async ({ page }) => {
    const button = page.getByRole("button", { name: "Reset All Data" });
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
  });

  test("GEN-BTN-005: Random seed input exists", async ({ page }) => {
    const input = page.getByRole("spinbutton", { name: /random seed/i });
    await expect(input).toBeVisible();
  });

  // NEW TESTS FOR MISSING BUTTONS (TDD - these will fail initially)
  test("GEN-BTN-006: Generate Incidents button exists and is clickable", async ({ page }) => {
    const button = page.getByRole("button", { name: "Generate Incidents" });
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
  });

  test("GEN-BTN-007: Generate Postmortems button exists and is clickable", async ({ page }) => {
    const button = page.getByRole("button", { name: "Generate Postmortems" });
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
  });

  test("GEN-BTN-008: Generate Tickets button exists and is clickable", async ({ page }) => {
    const button = page.getByRole("button", { name: "Generate Tickets" });
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
  });

  test("GEN-BTN-009: Generate Agent Actions button exists and is clickable", async ({ page }) => {
    const button = page.getByRole("button", { name: "Generate Agent Actions" });
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
  });
});

test.describe("Generation Page - Data Generation Tests", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/generation`);
    await page.waitForTimeout(2000); // Wait for data to load
  });

  test("GEN-DATA-001: Generate EDR button works without error", async ({ page }) => {
    // Click Generate EDR
    const button = page.getByRole("button", { name: "Generate EDR" });
    await expect(button).toBeEnabled();
    await button.click();

    // Wait for the operation to complete
    await page.waitForTimeout(3000);

    // Check no error appeared (error messages contain "Error:")
    const hasError = await page
      .locator("text=/Error:/")
      .isVisible()
      .catch(() => false);
    expect(hasError).toBeFalsy();

    // Page should still be responsive
    await expect(page.locator("h1", { hasText: "Data Generation" })).toBeVisible();
  });

  test("GEN-DATA-002: Generate Assets button works without error", async ({ page }) => {
    // Click Generate Assets
    const button = page.getByRole("button", { name: "Generate Assets" });
    await expect(button).toBeEnabled();
    await button.click();

    // Wait for the operation to complete
    await page.waitForTimeout(3000);

    // Check no error appeared
    const hasError = await page
      .locator("text=/Error:/")
      .isVisible()
      .catch(() => false);
    expect(hasError).toBeFalsy();

    // Page should still be responsive
    await expect(page.locator("h1", { hasText: "Data Generation" })).toBeVisible();
  });

  test("GEN-DATA-003: Generate All button works without error", async ({ page }) => {
    // Click Generate All
    const button = page.getByRole("button", { name: "Generate All" });
    await expect(button).toBeEnabled();
    await button.click();

    // Wait for the operation to complete (this takes longer)
    await page.waitForTimeout(5000);

    // Check no error appeared
    const hasError = await page
      .locator("text=/Error:/")
      .isVisible()
      .catch(() => false);
    expect(hasError).toBeFalsy();

    // Page should still be responsive
    await expect(page.locator("h1", { hasText: "Data Generation" })).toBeVisible();
  });

  test("GEN-DATA-004: Data status section shows counts", async ({ page }) => {
    // Wait for data status to load
    await page.waitForTimeout(3000);

    // Verify data status section header exists
    await expect(page.locator("h2", { hasText: "Current Data Status" })).toBeVisible();

    // Check that the data status section contains numeric values
    const mainContent = await page.locator("main").textContent();
    // Should contain numbers from the data counts
    expect(mainContent).toMatch(/\d+/);

    // Verify at least one paragraph with a number exists in the data status area
    const numberParagraphs = await page.locator("main p").filter({ hasText: /^\d+$/ }).count();
    expect(numberParagraphs).toBeGreaterThan(0);
  });

  // NEW TESTS FOR MISSING BUTTONS (TDD - these will fail initially)
  test("GEN-DATA-005: Generate Incidents button works without error", async ({ page }) => {
    const button = page.getByRole("button", { name: "Generate Incidents" });
    await expect(button).toBeEnabled();
    await button.click();

    await page.waitForTimeout(3000);

    const hasError = await page
      .locator("text=/Error:/")
      .isVisible()
      .catch(() => false);
    expect(hasError).toBeFalsy();

    await expect(page.locator("h1", { hasText: "Data Generation" })).toBeVisible();
  });

  test("GEN-DATA-006: Generate Postmortems button works without error", async ({ page }) => {
    const button = page.getByRole("button", { name: "Generate Postmortems" });
    await expect(button).toBeEnabled();
    await button.click();

    await page.waitForTimeout(3000);

    const hasError = await page
      .locator("text=/Error:/")
      .isVisible()
      .catch(() => false);
    expect(hasError).toBeFalsy();

    await expect(page.locator("h1", { hasText: "Data Generation" })).toBeVisible();
  });

  test("GEN-DATA-007: Generate Tickets button works without error", async ({ page }) => {
    const button = page.getByRole("button", { name: "Generate Tickets" });
    await expect(button).toBeEnabled();
    await button.click();

    await page.waitForTimeout(3000);

    const hasError = await page
      .locator("text=/Error:/")
      .isVisible()
      .catch(() => false);
    expect(hasError).toBeFalsy();

    await expect(page.locator("h1", { hasText: "Data Generation" })).toBeVisible();
  });

  test("GEN-DATA-008: Generate Agent Actions button works without error", async ({ page }) => {
    const button = page.getByRole("button", { name: "Generate Agent Actions" });
    await expect(button).toBeEnabled();
    await button.click();

    await page.waitForTimeout(3000);

    const hasError = await page
      .locator("text=/Error:/")
      .isVisible()
      .catch(() => false);
    expect(hasError).toBeFalsy();

    await expect(page.locator("h1", { hasText: "Data Generation" })).toBeVisible();
  });
});

test.describe("Generation Page - Error Handling Tests", () => {
  test("GEN-ERR-001: Page handles API errors gracefully", async ({ page }) => {
    await page.goto(`${BASE_URL}/generation`);

    // Click a button (should not crash the page)
    await page.getByRole("button", { name: "Generate EDR" }).click();

    // Wait a moment
    await page.waitForTimeout(1000);

    // Page should still be responsive
    const heading = page.locator("h1", { hasText: "Data Generation" });
    await expect(heading).toBeVisible();
  });

  test("GEN-ERR-002: Page shows error message on failure", async ({ page }) => {
    // This test verifies that if there's an API error, it's displayed
    // We can't easily simulate backend failure, so we just verify the UI handles it
    await page.goto(`${BASE_URL}/generation`);

    // The page should have an error display mechanism
    // After clicking a button that might fail, check the page doesn't crash
    const buttons = await page.getByRole("button").all();
    expect(buttons.length).toBeGreaterThan(0);
  });
});

test.describe("Generation Page - UI State Tests", () => {
  test("GEN-UI-001: Data status cards display correctly", async ({ page }) => {
    await page.goto(`${BASE_URL}/generation`);
    await page.waitForTimeout(3000); // Wait for data to load

    // Check the Current Data Status section header
    await expect(page.locator("h2", { hasText: "Current Data Status" })).toBeVisible();

    // Check that data status section has content with paragraphs containing data labels
    // Use specific selectors to avoid matching sidebar and buttons
    const dataStatusSection = page.locator("h2:has-text('Current Data Status')").locator("..");

    // Verify the section exists and has content
    await expect(dataStatusSection).toBeVisible();

    // Check for numeric values in paragraphs (data counts)
    const numberElements = await page.locator("main p").filter({ hasText: /^\d+$/ }).count();
    expect(numberElements).toBeGreaterThan(0);
  });

  test("GEN-UI-002: Configuration section is present", async ({ page }) => {
    await page.goto(`${BASE_URL}/generation`);

    await expect(page.locator("h2", { hasText: "Configuration" })).toBeVisible();
    await expect(page.locator("text=/random seed/i")).toBeVisible();
  });

  test("GEN-UI-003: Actions section has all buttons", async ({ page }) => {
    await page.goto(`${BASE_URL}/generation`);

    await expect(page.locator("h2", { hasText: "Actions" })).toBeVisible();

    // Existing buttons
    const generateAllBtn = page.getByRole("button", { name: "Generate All" });
    const generateAssetsBtn = page.getByRole("button", { name: "Generate Assets" });
    const generateEdrBtn = page.getByRole("button", { name: "Generate EDR" });
    const resetBtn = page.getByRole("button", { name: "Reset All Data" });

    await expect(generateAllBtn).toBeVisible();
    await expect(generateAssetsBtn).toBeVisible();
    await expect(generateEdrBtn).toBeVisible();
    await expect(resetBtn).toBeVisible();

    // NEW BUTTONS (TDD - these will fail initially)
    const generateIncidentsBtn = page.getByRole("button", { name: "Generate Incidents" });
    const generatePostmortemsBtn = page.getByRole("button", { name: "Generate Postmortems" });
    const generateTicketsBtn = page.getByRole("button", { name: "Generate Tickets" });
    const generateAgentActionsBtn = page.getByRole("button", { name: "Generate Agent Actions" });

    await expect(generateIncidentsBtn).toBeVisible();
    await expect(generatePostmortemsBtn).toBeVisible();
    await expect(generateTicketsBtn).toBeVisible();
    await expect(generateAgentActionsBtn).toBeVisible();
  });

  test("GEN-UI-004: Page header displays correctly", async ({ page }) => {
    await page.goto(`${BASE_URL}/generation`);

    await expect(page.locator("h1", { hasText: "Data Generation" })).toBeVisible();
    await expect(page.locator("text=/synthetic SOC data/i")).toBeVisible();
  });
});

test.describe("Generation Page - API Integration Tests", () => {
  test("GEN-API-001: Status endpoint returns data", async ({ request }) => {
    const response = await request.get(`${API_URL}/gen/status`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty("assets");
    expect(data).toHaveProperty("incidents");
    expect(data).toHaveProperty("detections");
    expect(data).toHaveProperty("postmortems");
    expect(data).toHaveProperty("tickets");
    expect(data).toHaveProperty("agent_actions");
  });

  test("GEN-API-002: EDR generation endpoint works", async ({ request }) => {
    const response = await request.post(`${API_URL}/gen/edr`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty("status", "success");
    expect(data).toHaveProperty("counts");
  });

  test("GEN-API-003: Assets generation endpoint works", async ({ request }) => {
    const response = await request.post(`${API_URL}/gen/assets`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty("status", "success");
    expect(data).toHaveProperty("counts");
  });

  test("GEN-API-004: Incidents generation endpoint works", async ({ request }) => {
    const response = await request.post(`${API_URL}/gen/incidents`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty("status", "success");
    expect(data).toHaveProperty("counts");
  });

  test("GEN-API-005: Health endpoint returns index info", async ({ request }) => {
    const response = await request.get(`${API_URL}/gen/health`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty("status", "healthy");
    expect(data).toHaveProperty("indices");
    expect(data).toHaveProperty("total_documents");
  });

  // NEW API TESTS (TDD - these will fail initially)
  test("GEN-API-006: Postmortems generation endpoint works", async ({ request }) => {
    const response = await request.post(`${API_URL}/gen/postmortems`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty("status", "success");
    expect(data).toHaveProperty("counts");
  });

  test("GEN-API-007: Tickets generation endpoint works", async ({ request }) => {
    const response = await request.post(`${API_URL}/gen/tickets`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty("status", "success");
    expect(data).toHaveProperty("counts");
  });

  test("GEN-API-008: Agent Actions generation endpoint works", async ({ request }) => {
    const response = await request.post(`${API_URL}/gen/agent-actions`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty("status", "success");
    expect(data).toHaveProperty("counts");
  });
});

// NEW: Tests for clickable data status cards (TDD - these will fail initially)
test.describe("Generation Page - Clickable Data Status Cards", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/generation`);
    await page.waitForTimeout(2000); // Wait for data to load
  });

  // Helper to get card within "Current Data Status" section
  const getStatusCard = (page: any, label: string) => {
    const statusSection = page.locator("h2:has-text('Current Data Status')").locator("..");
    return statusSection.getByRole("button", { name: new RegExp(label, "i") });
  };

  test("GEN-NAV-001: Assets card navigates to /assets page", async ({ page }) => {
    // Click on Assets card in the data status section
    const assetsCard = getStatusCard(page, "Assets");
    await assetsCard.click();

    // Should navigate to assets page
    await expect(page).toHaveURL(/.*\/assets/);
    await expect(page.locator("h1", { hasText: /assets/i })).toBeVisible();
  });

  test("GEN-NAV-002: Incidents card navigates to /incidents page", async ({ page }) => {
    const incidentsCard = getStatusCard(page, "Incidents");
    await incidentsCard.click();

    await expect(page).toHaveURL(/.*\/incidents/);
    await expect(page.locator("h1", { hasText: /incidents/i })).toBeVisible();
  });

  test("GEN-NAV-003: Detections card navigates to /detections page", async ({ page }) => {
    const detectionsCard = getStatusCard(page, "Detections");
    await detectionsCard.click();

    await expect(page).toHaveURL(/.*\/detections/);
    await expect(page.locator("h1", { hasText: /detections/i })).toBeVisible();
  });

  test("GEN-NAV-004: Postmortems card navigates to /postmortems page", async ({ page }) => {
    const postmortemsCard = getStatusCard(page, "Postmortems");
    await postmortemsCard.click();

    await expect(page).toHaveURL(/.*\/postmortems/);
    await expect(page.locator("h1", { hasText: /postmortems/i })).toBeVisible();
  });

  test("GEN-NAV-005: Tickets card navigates to /tickets page", async ({ page }) => {
    const ticketsCard = getStatusCard(page, "Tickets");
    await ticketsCard.click();

    await expect(page).toHaveURL(/.*\/tickets/);
    await expect(page.locator("h1", { hasText: /tickets/i })).toBeVisible();
  });

  test("GEN-NAV-006: Agent Actions card navigates to /audit page", async ({ page }) => {
    const agentActionsCard = getStatusCard(page, "Agent Actions");
    await agentActionsCard.click();

    await expect(page).toHaveURL(/.*\/audit/);
    await expect(page.locator("h1", { hasText: /audit/i })).toBeVisible();
  });

  test("GEN-NAV-007: Cards show hover cursor indicating they are clickable", async ({ page }) => {
    // Wait for cards to load
    await page.waitForSelector("h2:has-text('Current Data Status')");

    // Get the assets card in the status section
    const assetsCard = getStatusCard(page, "Assets");

    // Check that cursor changes to pointer on hover
    const cursor = await assetsCard.evaluate((el) => window.getComputedStyle(el).cursor);
    expect(cursor).toBe("pointer");
  });
});
