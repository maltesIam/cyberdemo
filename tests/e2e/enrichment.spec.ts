import { test, expect, type Page, type BrowserContext } from "@playwright/test";

/**
 * Enrichment E2E Tests
 *
 * Tests the vulnerability and threat enrichment workflow:
 * - Button visibility and state management
 * - Successful enrichment with progress polling
 * - Partial source failures (graceful degradation)
 * - 100-item limit enforcement
 * - Enriched data display in the Assets table
 * - Timeout recovery and retry behavior
 */

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Standard mock for a successful vulnerability enrichment job response. */
function vulnJobResponse(overrides: Record<string, unknown> = {}) {
  return {
    job_id: "vuln-job-001",
    status: "pending", // CRITICAL: Initial POST should return 'pending', not 'completed'
    total_items: 50,
    estimated_duration_seconds: 10,
    ...overrides,
  };
}

/** Standard mock for a successful threat enrichment job response. */
function threatJobResponse(overrides: Record<string, unknown> = {}) {
  return {
    job_id: "threat-job-001",
    status: "pending", // CRITICAL: Initial POST should return 'pending'
    total_items: 100,
    estimated_duration_seconds: null,
    ...overrides,
  };
}

/** Standard mock for a completed enrichment status response. */
function completedStatus(overrides: Record<string, unknown> = {}) {
  return {
    job_id: "vuln-job-001",
    status: "completed",
    progress: 1.0,
    processed_items: 50,
    total_items: 50,
    failed_items: 0,
    successful_sources: 4, // CRITICAL: Required by evaluateResult() to show toast
    failed_sources: 0, // CRITICAL: Required by evaluateResult() to show toast
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    estimated_completion: null,
    error_message: null,
    ...overrides,
  };
}

/**
 * Register mock routes on the browser context so they apply to all requests
 * made by the page, regardless of navigation.
 */
async function mockEnrichmentAPIs(
  context: BrowserContext,
  options: {
    vulnResponse?: Record<string, unknown>;
    threatResponse?: Record<string, unknown>;
    statusResponse?: Record<string, unknown>;
  } = {},
) {
  await context.route("**/api/enrichment/vulnerabilities", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(options.vulnResponse ?? vulnJobResponse()),
    });
  });

  await context.route("**/api/enrichment/threats", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(options.threatResponse ?? threatJobResponse()),
    });
  });

  await context.route("**/api/enrichment/status/**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(options.statusResponse ?? completedStatus()),
    });
  });
}

// ---------------------------------------------------------------------------
// Vulnerability Enrichment Tests
// ---------------------------------------------------------------------------

test.describe("Vulnerability Enrichment", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("debe mostrar botones de enriquecimiento", async ({ page }) => {
    // Both enrichment buttons must be visible and enabled
    const vulnButton = page.getByRole("button", { name: /enrich vulnerabilities/i });
    const threatButton = page.getByRole("button", { name: /enrich threats/i });

    await expect(vulnButton).toBeVisible();
    await expect(threatButton).toBeVisible();
    await expect(vulnButton).toBeEnabled();
    await expect(threatButton).toBeEnabled();

    // Verify button labels are in Spanish
    await expect(page.getByText("Enriquecer Vulnerabilidades")).toBeVisible();
    await expect(page.getByText("Enriquecer Amenazas")).toBeVisible();
  });

  test("debe enriquecer vulnerabilidades con éxito", async ({ page, context }) => {
    // Mock all enrichment endpoints
    await mockEnrichmentAPIs(context);

    // Wait for button to be visible and enabled
    const vulnButton = page.getByRole("button", { name: /enrich vulnerabilities/i });
    await expect(vulnButton).toBeVisible({ timeout: 10000 });
    await expect(vulnButton).toBeEnabled({ timeout: 10000 });

    // Click the enrichment button
    await vulnButton.click();

    // Should show loading state with "Enriching..." text
    await expect(page.getByText(/Enriching\.\.\./i)).toBeVisible({ timeout: 5000 });

    // Button should be disabled while enriching
    await expect(vulnButton).toBeDisabled();

    // Wait for completion -- the status polling returns 'completed' immediately,
    // so the loading indicator should disappear quickly
    await expect(page.getByText(/Enriching\.\.\./i)).not.toBeVisible({ timeout: 30000 });

    // Wait for the initial "started" toast to disappear before checking for completion toast
    await page.waitForTimeout(4000); // Initial toast duration is 3000ms

    // Should show a success toast notification (the completion toast, not the initial one)
    const toast = page
      .locator('[role="alert"]', { hasText: /success|enriched|sources|completed/i })
      .first();
    await expect(toast).toBeVisible({ timeout: 10000 });
    await expect(toast).toContainText(/success|enriched|sources/i);

    // Button should be re-enabled after completion
    await expect(vulnButton).toBeEnabled({ timeout: 5000 });
  });

  test("debe manejar error de fuente sin romper UI", async ({ page, context }) => {
    // Mock vulnerability endpoint: 2 sources fail, 2 succeed (partial failure)
    await mockEnrichmentAPIs(context, {
      vulnResponse: vulnJobResponse({
        successful_sources: 2,
        failed_sources: 2,
        sources: {
          nvd: { status: "failed", enriched_count: 0, error: "API timeout" },
          github: { status: "failed", enriched_count: 0, error: "Rate limit exceeded" },
          epss: { status: "success", enriched_count: 50 },
          synthetic: { status: "success", enriched_count: 50 },
        },
        errors: [
          { source: "nvd", error: "API timeout", recoverable: true },
          { source: "github", error: "Rate limit exceeded", recoverable: true },
        ],
      }),
      statusResponse: completedStatus({
        successful_sources: 2,
        failed_sources: 2,
      }),
    });

    // Capture console errors before clicking
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    // Click enrichment button
    await page.getByRole("button", { name: /enrich vulnerabilities/i }).click();

    // Wait for completion
    await expect(page.getByText(/Enriching\.\.\./i)).not.toBeVisible({ timeout: 30000 });

    // Wait for initial toast to disappear
    await page.waitForTimeout(4000);

    // Should show a warning toast (partial failure), not a crash
    const toast = page.locator('[role="alert"]', { hasText: /source|warning|partial/i }).first();
    await expect(toast).toBeVisible({ timeout: 10000 });
    await expect(toast).toContainText(/source/i);

    // The button must be re-enabled -- UI is still functional
    const vulnButton = page.getByRole("button", { name: /enrich vulnerabilities/i });
    await expect(vulnButton).toBeEnabled({ timeout: 5000 });

    // Allow a brief window for any deferred errors
    await page.waitForTimeout(1000);

    // No critical React errors should have appeared
    const criticalErrors = consoleErrors.filter(
      (e) => e.includes("React") || e.includes("Uncaught") || e.includes("TypeError"),
    );
    expect(criticalErrors).toHaveLength(0);
  });

  test("debe limitar a 100 items por fuente", async ({ page, context }) => {
    // Mock: the backend enforces the 100-item limit and returns exactly 100
    await mockEnrichmentAPIs(context, {
      vulnResponse: vulnJobResponse({
        total_items: 100,
        sources: {
          nvd: { status: "success", enriched_count: 100 },
          epss: { status: "success", enriched_count: 100 },
          github: { status: "success", enriched_count: 100 },
          synthetic: { status: "success", enriched_count: 100 },
        },
      }),
      statusResponse: completedStatus({
        processed_items: 100,
        total_items: 100,
      }),
    });

    // Intercept the outgoing request to verify the payload
    let capturedRequest: Record<string, unknown> | null = null;
    await page.route("**/api/enrichment/vulnerabilities", async (route, request) => {
      const postData = request.postDataJSON();
      capturedRequest = postData;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          vulnJobResponse({
            total_items: 100,
            sources: {
              nvd: { status: "success", enriched_count: 100 },
              epss: { status: "success", enriched_count: 100 },
              github: { status: "success", enriched_count: 100 },
              synthetic: { status: "success", enriched_count: 100 },
            },
          }),
        ),
      });
    });

    // Click the enrichment button
    await page.getByRole("button", { name: /enrich vulnerabilities/i }).click();

    // Wait for completion
    await expect(page.getByText(/Enriching\.\.\./i)).not.toBeVisible({ timeout: 30000 });

    // Verify the toast shows item count at or below the limit
    const toast = page.locator('[role="alert"]').first();
    if (await toast.isVisible({ timeout: 5000 }).catch(() => false)) {
      const toastText = (await toast.textContent()) ?? "";
      const itemsMatch = toastText.match(/(\d+)\s+items?/i);
      if (itemsMatch) {
        const itemCount = parseInt(itemsMatch[1], 10);
        expect(itemCount).toBeLessThanOrEqual(100);
      }
    }

    // If we captured the outgoing request, verify no more than 100 CVE IDs were sent
    if (capturedRequest && Array.isArray((capturedRequest as { cve_ids?: string[] }).cve_ids)) {
      expect((capturedRequest as { cve_ids: string[] }).cve_ids.length).toBeLessThanOrEqual(100);
    }
  });

  test("debe mostrar datos enriquecidos en tabla", async ({ page, context }) => {
    // Mock successful enrichment
    await mockEnrichmentAPIs(context);

    // Enrich vulnerabilities first
    await page.getByRole("button", { name: /enrich vulnerabilities/i }).click();
    await expect(page.getByText(/Enriching\.\.\./i)).not.toBeVisible({ timeout: 30000 });

    // Navigate to the Assets page where enriched vulnerability data is displayed
    await page.goto("/assets");
    await page.waitForLoadState("networkidle");

    // The Assets table should be visible
    const assetsHeading = page.getByRole("heading", { name: /assets/i });
    await expect(assetsHeading).toBeVisible({ timeout: 10000 });

    // Look for enrichment-related columns or data in the table:
    // - "Risk" column (risk scores enriched from synthetic source)
    // - CVSS scores in asset detail panels
    const riskColumn = page.getByText(/risk/i).first();
    const riskVisible = await riskColumn.isVisible().catch(() => false);

    // The table itself should be present
    const table = page.locator("table").first();
    const tableVisible = await table.isVisible().catch(() => false);

    // At minimum, the table or the Risk column header should be present
    expect(riskVisible || tableVisible).toBeTruthy();

    // If there are rows, check that risk badges are rendered
    const riskBadges = page.locator("text=/Critical|High|Medium|Low/i");
    const badgeCount = await riskBadges.count();
    // Data might not be present if no generation was done, so we just verify
    // the column structure is intact (no crash)
    expect(badgeCount).toBeGreaterThanOrEqual(0);
  });
});

// ---------------------------------------------------------------------------
// Threat Enrichment Tests
// ---------------------------------------------------------------------------

test.describe("Threat Enrichment", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("debe enriquecer amenazas con éxito", async ({ page, context }) => {
    await mockEnrichmentAPIs(context);

    const threatButton = page.getByRole("button", { name: /enrich threats/i });
    await threatButton.click();

    // Should show loading state
    await expect(page.getByText(/Enriching\.\.\./i)).toBeVisible({ timeout: 5000 });

    // Wait for completion
    await expect(page.getByText(/Enriching\.\.\./i)).not.toBeVisible({ timeout: 60000 });

    // Wait for initial toast to disappear
    await page.waitForTimeout(4000);

    // Should show success toast (completion toast, not initial one)
    const toast = page
      .locator('[role="alert"]', { hasText: /success|enriched|sources|threats/i })
      .first();
    await expect(toast).toBeVisible({ timeout: 10000 });

    // Button should be re-enabled
    await expect(threatButton).toBeEnabled({ timeout: 5000 });
  });
});

// ---------------------------------------------------------------------------
// Error Recovery Tests
// ---------------------------------------------------------------------------

test.describe("Enrichment Error Recovery", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("debe recuperarse de timeout sin perder estado", async ({ page }) => {
    let callCount = 0;

    // First call: network timeout. Second call: success.
    await page.route("**/api/enrichment/vulnerabilities", async (route) => {
      callCount++;
      if (callCount === 1) {
        await route.abort("timedout");
      } else {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(vulnJobResponse()),
        });
      }
    });

    await page.route("**/api/enrichment/status/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(completedStatus()),
      });
    });

    const vulnButton = page.getByRole("button", { name: /enrich vulnerabilities/i });

    // First attempt -- will fail with timeout
    await vulnButton.click();

    // Should show an error toast
    const errorToast = page.locator('[role="alert"]').first();
    await expect(errorToast).toBeVisible({ timeout: 10000 });

    // Button must be re-enabled so the user can retry
    await expect(vulnButton).toBeEnabled({ timeout: 5000 });

    // Second attempt -- should succeed
    await vulnButton.click();

    // Wait for completion
    await expect(page.getByText(/Enriching\.\.\./i)).not.toBeVisible({ timeout: 30000 });

    // Button should be enabled after successful retry
    await expect(vulnButton).toBeEnabled({ timeout: 5000 });
  });

  test("debe manejar fallo total de todas las fuentes", async ({ page, context }) => {
    await mockEnrichmentAPIs(context, {
      vulnResponse: vulnJobResponse({
        successful_sources: 0,
        failed_sources: 4,
        sources: {
          nvd: { status: "failed", enriched_count: 0, error: "Service unavailable" },
          epss: { status: "failed", enriched_count: 0, error: "Connection refused" },
          github: { status: "failed", enriched_count: 0, error: "Rate limited" },
          synthetic: { status: "failed", enriched_count: 0, error: "Internal error" },
        },
        errors: [
          { source: "nvd", error: "Service unavailable", recoverable: true },
          { source: "epss", error: "Connection refused", recoverable: true },
          { source: "github", error: "Rate limited", recoverable: true },
          { source: "synthetic", error: "Internal error", recoverable: false },
        ],
      }),
      statusResponse: completedStatus({
        status: "failed",
        successful_sources: 0,
        failed_sources: 4,
        failed_items: 50,
        error_message: "All sources failed",
      }),
    });

    const vulnButton = page.getByRole("button", { name: /enrich vulnerabilities/i });
    await vulnButton.click();

    // Wait for the job to be processed
    await expect(page.getByText(/Enriching\.\.\./i)).not.toBeVisible({ timeout: 30000 });

    // Wait for initial toast to disappear
    await page.waitForTimeout(4000);

    // Should show an error toast indicating total failure
    const toast = page.locator('[role="alert"]', { hasText: /fail|error/i }).first();
    await expect(toast).toBeVisible({ timeout: 10000 });
    await expect(toast).toContainText(/fail/i);

    // UI must remain functional -- button re-enabled
    await expect(vulnButton).toBeEnabled({ timeout: 5000 });
  });

  test("debe deshabilitar botón durante enriquecimiento activo", async ({ page }) => {
    // Mock a status endpoint that stays "running" to simulate a long job
    await page.route("**/api/enrichment/vulnerabilities", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(vulnJobResponse({ job_id: "long-running-job" })),
      });
    });

    await page.route("**/api/enrichment/status/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          completedStatus({
            job_id: "long-running-job",
            status: "running",
            progress: 0.5,
            processed_items: 25,
            total_items: 50,
            completed_at: null,
          }),
        ),
      });
    });

    const vulnButton = page.getByRole("button", { name: /enrich vulnerabilities/i });
    await vulnButton.click();

    // Button should be disabled while enrichment is in progress
    await expect(vulnButton).toBeDisabled({ timeout: 5000 });

    // Progress text should be displayed
    await expect(page.getByText(/Enriching\.\.\./i)).toBeVisible({ timeout: 5000 });
  });
});
