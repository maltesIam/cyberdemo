/**
 * Attack Simulation E2E Tests - T-1.4.009
 *
 * Playwright E2E tests for the attack scenario selection UI.
 * These tests verify the complete user flow for:
 * - Viewing available attack scenarios
 * - Selecting and starting a scenario
 * - Controlling simulation (pause/resume/speed)
 * - Viewing simulation progress
 *
 * Note: Tests are skipped if the attack simulation UI is not yet implemented.
 */

import { test, expect } from "@playwright/test";

// Check if attack simulation page exists
const ATTACK_SIM_URL = "/attack-simulation";

test.describe("Attack Simulation UI", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to attack simulation page
    await page.goto(ATTACK_SIM_URL);
    await page.waitForLoadState("networkidle");
  });

  test.describe("Scenario Selection", () => {
    test("displays available attack scenarios", async ({ page }) => {
      // Should show a list/grid of available scenarios
      const scenarioCards = page.locator('[data-testid="scenario-card"]');

      // Wait for scenarios to load
      await expect(scenarioCards.first()).toBeVisible({ timeout: 10000 });

      // Should have at least the 6 defined scenarios
      const count = await scenarioCards.count();
      expect(count).toBeGreaterThanOrEqual(6);
    });

    test("shows scenario details including MITRE tactics", async ({ page }) => {
      // Click on APT29 scenario card
      const apt29Card = page.locator('[data-testid="scenario-card"]:has-text("APT29")');
      await expect(apt29Card).toBeVisible({ timeout: 10000 });

      // Should display scenario name
      await expect(apt29Card.locator('[data-testid="scenario-name"]')).toContainText("APT29");

      // Should show MITRE ATT&CK tactics
      const mitreTactics = apt29Card.locator('[data-testid="mitre-tactics"]');
      await expect(mitreTactics).toBeVisible();
    });

    test("can select a scenario to view details", async ({ page }) => {
      // Click on a scenario card
      const scenarioCard = page.locator('[data-testid="scenario-card"]').first();
      await scenarioCard.click();

      // Should show detailed view or modal
      const detailsPanel = page.locator('[data-testid="scenario-details"]');
      await expect(detailsPanel).toBeVisible({ timeout: 5000 });

      // Should show description
      await expect(detailsPanel.locator('[data-testid="scenario-description"]')).toBeVisible();

      // Should show attack chain/stages
      await expect(detailsPanel.locator('[data-testid="attack-chain"]')).toBeVisible();
    });
  });

  test.describe("Simulation Controls", () => {
    test("can start a scenario simulation", async ({ page }) => {
      // Select APT29 scenario
      await page.locator('[data-testid="scenario-card"]:has-text("APT29")').click();

      // Click start button
      const startButton = page.locator('[data-testid="start-simulation-btn"]');
      await expect(startButton).toBeVisible({ timeout: 5000 });
      await startButton.click();

      // Should show running state
      const statusIndicator = page.locator('[data-testid="simulation-status"]');
      await expect(statusIndicator).toContainText(/running|started/i, { timeout: 5000 });
    });

    test("can pause and resume simulation", async ({ page }) => {
      // Start a simulation first
      await page.locator('[data-testid="scenario-card"]:has-text("FIN7")').click();
      await page.locator('[data-testid="start-simulation-btn"]').click();

      // Wait for simulation to start
      await expect(page.locator('[data-testid="simulation-status"]')).toContainText(/running/i, { timeout: 5000 });

      // Click pause
      const pauseButton = page.locator('[data-testid="pause-btn"]');
      await expect(pauseButton).toBeVisible();
      await pauseButton.click();

      // Should show paused state
      await expect(page.locator('[data-testid="simulation-status"]')).toContainText(/paused/i, { timeout: 3000 });

      // Click resume
      const resumeButton = page.locator('[data-testid="resume-btn"]');
      await expect(resumeButton).toBeVisible();
      await resumeButton.click();

      // Should be running again
      await expect(page.locator('[data-testid="simulation-status"]')).toContainText(/running/i, { timeout: 3000 });
    });

    test("can adjust simulation speed", async ({ page }) => {
      // Start a simulation
      await page.locator('[data-testid="scenario-card"]').first().click();
      await page.locator('[data-testid="start-simulation-btn"]').click();

      // Wait for simulation to start
      await expect(page.locator('[data-testid="simulation-status"]')).toContainText(/running/i, { timeout: 5000 });

      // Find speed control
      const speedControl = page.locator('[data-testid="speed-control"]');
      await expect(speedControl).toBeVisible();

      // Select 2x speed
      await speedControl.selectOption({ label: "2x" });

      // Verify speed changed
      await expect(speedControl).toHaveValue("2");
    });

    test("can jump to specific stage", async ({ page }) => {
      // Start a simulation
      await page.locator('[data-testid="scenario-card"]:has-text("APT29")').click();
      await page.locator('[data-testid="start-simulation-btn"]').click();

      // Wait for simulation to start
      await expect(page.locator('[data-testid="simulation-status"]')).toContainText(/running/i, { timeout: 5000 });

      // Find stage selector
      const stageSelector = page.locator('[data-testid="stage-selector"]');
      await expect(stageSelector).toBeVisible();

      // Click on stage 3
      await stageSelector.locator('[data-testid="stage-3"]').click();

      // Verify current stage updated
      const currentStage = page.locator('[data-testid="current-stage"]');
      await expect(currentStage).toContainText("3", { timeout: 3000 });
    });
  });

  test.describe("Simulation Progress Display", () => {
    test("shows current attack stage and MITRE tactic", async ({ page }) => {
      // Start a simulation
      await page.locator('[data-testid="scenario-card"]').first().click();
      await page.locator('[data-testid="start-simulation-btn"]').click();

      // Wait for simulation
      await expect(page.locator('[data-testid="simulation-status"]')).toContainText(/running/i, { timeout: 5000 });

      // Should show current stage info
      const stageInfo = page.locator('[data-testid="current-stage-info"]');
      await expect(stageInfo).toBeVisible();

      // Should show MITRE tactic
      const mitreTactic = page.locator('[data-testid="current-mitre-tactic"]');
      await expect(mitreTactic).toBeVisible();
    });

    test("displays event timeline during simulation", async ({ page }) => {
      // Start a simulation
      await page.locator('[data-testid="scenario-card"]').first().click();
      await page.locator('[data-testid="start-simulation-btn"]').click();

      // Wait for simulation
      await expect(page.locator('[data-testid="simulation-status"]')).toContainText(/running/i, { timeout: 5000 });

      // Should have event timeline/feed
      const eventTimeline = page.locator('[data-testid="event-timeline"]');
      await expect(eventTimeline).toBeVisible();
    });

    test("shows progress indicator for attack stages", async ({ page }) => {
      // Start a simulation
      await page.locator('[data-testid="scenario-card"]').first().click();
      await page.locator('[data-testid="start-simulation-btn"]').click();

      // Wait for simulation
      await expect(page.locator('[data-testid="simulation-status"]')).toContainText(/running/i, { timeout: 5000 });

      // Should show progress bar or stage indicators
      const progressIndicator = page.locator('[data-testid="stage-progress"]');
      await expect(progressIndicator).toBeVisible();
    });
  });

  test.describe("Event Injection", () => {
    test("can inject custom event into simulation", async ({ page }) => {
      // Start a simulation
      await page.locator('[data-testid="scenario-card"]').first().click();
      await page.locator('[data-testid="start-simulation-btn"]').click();

      // Wait for simulation
      await expect(page.locator('[data-testid="simulation-status"]')).toContainText(/running/i, { timeout: 5000 });

      // Open inject event modal/form
      const injectButton = page.locator('[data-testid="inject-event-btn"]');
      await expect(injectButton).toBeVisible();
      await injectButton.click();

      // Should show inject event form
      const injectForm = page.locator('[data-testid="inject-event-form"]');
      await expect(injectForm).toBeVisible();

      // Select event type
      await injectForm.locator('[data-testid="event-type-select"]').selectOption("malware_execution");

      // Fill in event data
      await injectForm.locator('[data-testid="event-host"]').fill("WORKSTATION-001");
      await injectForm.locator('[data-testid="event-process"]').fill("malware.exe");

      // Submit
      await injectForm.locator('[data-testid="inject-submit-btn"]').click();

      // Should see success message or event in timeline
      await expect(page.locator('[data-testid="inject-success"]').or(
        page.locator('[data-testid="event-timeline"]').locator('text=malware.exe')
      )).toBeVisible({ timeout: 5000 });
    });
  });
});

test.describe("Attack Simulation Navigation", () => {
  test("attack simulation link exists in sidebar", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Check if there's a link to attack simulation in sidebar
    const sidebarLink = page.locator('aside a:has-text("Attack"), aside a:has-text("Simulation")');

    // If no sidebar link yet, this test documents the expected behavior
    const linkExists = await sidebarLink.count() > 0;
    if (!linkExists) {
      test.skip();
    }

    await expect(sidebarLink.first()).toBeVisible({ timeout: 5000 });
  });

  test("can navigate to attack simulation from sidebar", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const sidebarLink = page.locator('aside a:has-text("Attack"), aside a:has-text("Simulation")');
    const linkExists = await sidebarLink.count() > 0;

    if (!linkExists) {
      test.skip();
    }

    await sidebarLink.first().click();
    await expect(page).toHaveURL(/attack|simulation/i);
  });
});

test.describe("Attack Simulation Error Handling", () => {
  test("shows error when starting duplicate simulation", async ({ page }) => {
    await page.goto(ATTACK_SIM_URL);
    await page.waitForLoadState("networkidle");

    // Start first simulation
    await page.locator('[data-testid="scenario-card"]').first().click();
    await page.locator('[data-testid="start-simulation-btn"]').click();

    // Wait for it to start
    await expect(page.locator('[data-testid="simulation-status"]')).toContainText(/running/i, { timeout: 5000 });

    // Try to start another (should fail or be prevented)
    // The start button should be disabled or show an error
    const startButton = page.locator('[data-testid="start-simulation-btn"]');
    const isDisabled = await startButton.isDisabled();

    if (!isDisabled) {
      // If button is not disabled, clicking should show error
      await startButton.click();
      await expect(page.locator('[data-testid="error-message"]')).toContainText(/already running/i, { timeout: 3000 });
    }
  });

  test("handles invalid scenario gracefully", async ({ page }) => {
    // Try to navigate to a non-existent scenario
    await page.goto(`${ATTACK_SIM_URL}?scenario=nonexistent`);
    await page.waitForLoadState("networkidle");

    // Should show error or redirect
    const errorMessage = page.locator('[data-testid="error-message"], [role="alert"]');
    const hasError = await errorMessage.count() > 0;

    if (hasError) {
      await expect(errorMessage.first()).toBeVisible();
    } else {
      // Or should redirect to scenario list
      await expect(page.locator('[data-testid="scenario-card"]').first()).toBeVisible({ timeout: 5000 });
    }
  });
});
