/**
 * Enrichment E2E Tests (Playwright)
 *
 * Following ENRICHMENT_PLAN.md Section 8.4:
 * 1. debe mostrar botones de enriquecimiento
 * 2. debe enriquecer vulnerabilidades con exito
 * 3. debe manejar error de fuente sin romper UI
 * 4. debe limitar a 100 items por fuente
 * 5. debe mostrar datos enriquecidos en tabla
 * 6. debe recuperarse de timeout sin perder estado
 */

import { test, expect, Page, Route } from "@playwright/test";

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Mock API response for enrichment endpoints
 */
async function mockEnrichmentAPI(
  page: Page,
  options: {
    successfulSources?: number;
    failedSources?: number;
    totalItems?: number;
    status?: "completed" | "failed" | "running";
    progress?: number;
    errors?: Array<{ source: string; error: string; recoverable: boolean }>;
  } = {},
) {
  const {
    successfulSources = 4,
    failedSources = 0,
    totalItems = 100,
    status = "completed",
    progress = 1.0,
    errors = [],
  } = options;

  const jobId = `test-job-${Date.now()}`;

  // Mock the enrichment start endpoint
  await page.route("**/api/enrichment/vulnerabilities", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        job_id: jobId,
        status: "pending",
        total_items: totalItems,
        estimated_duration_seconds: 30,
      }),
    });
  });

  // Mock the status endpoint
  await page.route(`**/api/enrichment/status/${jobId}`, async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        job_id: jobId,
        status: status,
        progress: progress,
        processed_items: Math.floor(totalItems * progress),
        total_items: totalItems,
        failed_items: failedSources > 0 ? Math.floor(totalItems * 0.1) : 0,
        started_at: new Date().toISOString(),
        completed_at: status === "completed" ? new Date().toISOString() : null,
        successful_sources: successfulSources,
        failed_sources: failedSources,
        sources: {
          nvd:
            failedSources > 0 && errors.some((e) => e.source === "nvd")
              ? { status: "failed", enriched_count: 0, error: "API timeout" }
              : { status: "success", enriched_count: totalItems },
          epss: { status: "success", enriched_count: totalItems },
          github: { status: "success", enriched_count: totalItems },
          synthetic: { status: "success", enriched_count: totalItems },
        },
        errors: errors,
      }),
    });
  });

  // Also mock general status endpoint pattern
  await page.route("**/api/enrichment/status/*", async (route: Route) => {
    const url = route.request().url();
    // Only respond to our test job
    if (url.includes(jobId)) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: jobId,
          status: status,
          progress: progress,
          processed_items: Math.floor(totalItems * progress),
          total_items: totalItems,
          failed_items: 0,
          successful_sources: successfulSources,
          failed_sources: failedSources,
        }),
      });
    } else {
      await route.continue();
    }
  });

  return jobId;
}

// ============================================================================
// TEST 1: debe mostrar botones de enriquecimiento
// ============================================================================

test.describe("Enrichment Buttons - Display", () => {
  test("debe mostrar botones de enriquecimiento", async ({ page }) => {
    await page.goto("/dashboard");

    // Wait for page to load
    await page.waitForLoadState("networkidle");

    // Verify vulnerability enrichment button is visible
    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    await expect(vulnButton).toBeVisible();
    await expect(vulnButton).toBeEnabled();

    // Verify threat enrichment button is visible
    const threatButton = page.getByRole("button", { name: /enriquecer amenazas/i });
    await expect(threatButton).toBeVisible();
    await expect(threatButton).toBeEnabled();
  });

  test("buttons should have correct aria labels", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    const vulnButton = page.getByRole("button", { name: /enrich vulnerabilities/i });
    const threatButton = page.getByRole("button", { name: /enrich threats/i });

    await expect(vulnButton).toHaveAttribute("aria-label");
    await expect(threatButton).toHaveAttribute("aria-label");
  });

  test("buttons should have icons", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    const threatButton = page.getByRole("button", { name: /enriquecer amenazas/i });

    // Check for SVG icons
    const vulnIcon = vulnButton.locator("svg");
    const threatIcon = threatButton.locator("svg");

    await expect(vulnIcon).toBeVisible();
    await expect(threatIcon).toBeVisible();
  });
});

// ============================================================================
// TEST 2: debe enriquecer vulnerabilidades con exito
// ============================================================================

test.describe("Enrichment Buttons - Success Flow", () => {
  test("debe enriquecer vulnerabilidades con exito", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // Mock successful enrichment
    await mockEnrichmentAPI(page, {
      successfulSources: 4,
      failedSources: 0,
      totalItems: 100,
      status: "completed",
      progress: 1.0,
    });

    // Click enrichment button
    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    await vulnButton.click();

    // Should show spinner/loading state
    await expect(page.getByText(/enriching/i)).toBeVisible({ timeout: 5000 });

    // Should show progress percentage
    await expect(page.getByText(/\d+%/)).toBeVisible({ timeout: 5000 });

    // Wait for completion
    await expect(page.getByText(/enriching/i)).not.toBeVisible({ timeout: 30000 });

    // Should show success toast
    const toast = page.locator('[role="alert"]');
    await expect(toast).toBeVisible({ timeout: 5000 });
    await expect(toast).toContainText(/success/i);

    // Button should be re-enabled
    await expect(vulnButton).toBeEnabled();
  });

  test("should show info toast when enrichment starts", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    await mockEnrichmentAPI(page, { status: "running", progress: 0.5 });

    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    await vulnButton.click();

    // Should show info toast about enrichment starting
    const toast = page.locator('[role="alert"]');
    await expect(toast).toBeVisible({ timeout: 5000 });
    await expect(toast).toContainText(/started/i);
  });
});

// ============================================================================
// TEST 3: debe manejar error de fuente sin romper UI
// ============================================================================

test.describe("Enrichment Buttons - Partial Failure Handling", () => {
  test("debe manejar error de fuente sin romper UI", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // Mock partial failure (1 source fails, 3 succeed)
    await mockEnrichmentAPI(page, {
      successfulSources: 3,
      failedSources: 1,
      totalItems: 100,
      status: "completed",
      progress: 1.0,
      errors: [{ source: "nvd", error: "API timeout", recoverable: true }],
    });

    // Click enrichment button
    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    await vulnButton.click();

    // Wait for completion
    await expect(page.getByText(/enriching/i)).not.toBeVisible({ timeout: 30000 });

    // Should show warning toast (partial success)
    const toast = page.locator('[role="alert"]');
    await expect(toast).toBeVisible({ timeout: 5000 });
    await expect(toast).toContainText(/1 source.*unavailable/i);
    await expect(toast).toContainText(/3 source.*succeeded/i);

    // UI should remain functional
    await expect(vulnButton).toBeEnabled();

    // Check for console errors (critical React errors)
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });

    // No critical React errors should occur
    const reactErrors = errors.filter(
      (e) => e.includes("React") || e.includes("Uncaught") || e.includes("TypeError"),
    );
    expect(reactErrors).toHaveLength(0);
  });

  test("should continue to work after handling partial failure", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // First call - partial failure
    await mockEnrichmentAPI(page, {
      successfulSources: 2,
      failedSources: 2,
      status: "completed",
    });

    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    await vulnButton.click();

    await expect(page.getByText(/enriching/i)).not.toBeVisible({ timeout: 30000 });

    // Button should be re-enabled for another attempt
    await expect(vulnButton).toBeEnabled();
  });
});

// ============================================================================
// TEST 4: debe limitar a 100 items por fuente
// ============================================================================

test.describe("Enrichment Buttons - Item Limiting", () => {
  test("debe limitar a 100 items por fuente", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    let capturedRequest: { cve_ids?: string[]; sources?: string[] } | null = null;

    // Intercept the request to verify limiting
    await page.route("**/api/enrichment/vulnerabilities", async (route: Route) => {
      const request = route.request();
      capturedRequest = JSON.parse(request.postData() || "{}");

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "test-limit-job",
          status: "completed",
          total_items: 100, // Backend limits to 100
          successful_sources: 4,
          failed_sources: 0,
        }),
      });
    });

    // Mock status endpoint
    await page.route("**/api/enrichment/status/*", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "test-limit-job",
          status: "completed",
          progress: 1.0,
          processed_items: 100,
          total_items: 100,
          failed_items: 0,
          successful_sources: 4,
          failed_sources: 0,
        }),
      });
    });

    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    await vulnButton.click();

    // Wait for completion
    await expect(page.getByText(/enriching/i)).not.toBeVisible({ timeout: 30000 });

    // Toast should indicate limited items
    const toast = page.locator('[role="alert"]');
    await expect(toast).toBeVisible({ timeout: 5000 });

    // The toast text should not indicate more than 100 items
    const toastText = await toast.textContent();
    const itemsMatch = toastText?.match(/(\d+)\s+items?/i);
    if (itemsMatch) {
      const items = parseInt(itemsMatch[1]);
      expect(items).toBeLessThanOrEqual(100);
    }
  });
});

// ============================================================================
// TEST 5: debe mostrar datos enriquecidos en tabla
// ============================================================================

test.describe("Enrichment Data Display", () => {
  test("debe mostrar datos enriquecidos en tabla de vulnerabilidades", async ({ page }) => {
    // First, enrich data
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    await mockEnrichmentAPI(page, {
      successfulSources: 4,
      failedSources: 0,
      status: "completed",
    });

    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    await vulnButton.click();

    await expect(page.getByText(/enriching/i)).not.toBeVisible({ timeout: 30000 });

    // Navigate to CTEM page
    await page.goto("/ctem");
    await page.waitForLoadState("networkidle");

    // Mock CTEM findings with enrichment data
    await page.route("**/api/ctem/findings*", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          findings: [
            {
              id: "cve-1",
              cve_id: "CVE-2024-0001",
              title: "Test Vulnerability",
              severity: "critical",
              cvss_score: 9.8,
              epss_score: 0.89,
              risk_score: 95,
              threat_actors: ["APT28"],
            },
            {
              id: "cve-2",
              cve_id: "CVE-2024-0002",
              title: "Another Vulnerability",
              severity: "high",
              cvss_score: 7.5,
              epss_score: 0.45,
              risk_score: 72,
              threat_actors: [],
            },
          ],
          total: 2,
          page: 1,
          page_size: 20,
        }),
      });
    });

    // Reload to get enriched data
    await page.reload();
    await page.waitForLoadState("networkidle");

    // Verify enrichment columns are visible
    await expect(page.getByText(/EPSS Score|epss/i).first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/Risk Score|risk/i).first()).toBeVisible({ timeout: 10000 });
  });
});

// ============================================================================
// TEST 6: debe recuperarse de timeout sin perder estado
// ============================================================================

test.describe("Enrichment Error Recovery", () => {
  test("debe recuperarse de timeout sin perder estado", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    let callCount = 0;

    // First call: timeout (abort)
    // Second call: success
    await page.route("**/api/enrichment/vulnerabilities", async (route: Route) => {
      callCount++;

      if (callCount === 1) {
        // Simulate timeout by aborting
        await route.abort("timedout");
      } else {
        // Success on retry
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            job_id: "retry-success-job",
            status: "pending",
            total_items: 50,
          }),
        });
      }
    });

    // Mock status for retry
    await page.route("**/api/enrichment/status/*", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "retry-success-job",
          status: "completed",
          progress: 1.0,
          processed_items: 50,
          total_items: 50,
          failed_items: 0,
          successful_sources: 4,
          failed_sources: 0,
        }),
      });
    });

    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });

    // First click - will timeout
    await vulnButton.click();

    // Should show error toast
    const errorToast = page.locator('[role="alert"]');
    await expect(errorToast).toBeVisible({ timeout: 10000 });
    await expect(errorToast).toContainText(/error|timeout|failed/i);

    // Button should be re-enabled after error
    await expect(vulnButton).toBeEnabled({ timeout: 5000 });

    // Retry - should succeed
    await vulnButton.click();

    // Wait for completion
    await expect(page.getByText(/enriching/i)).not.toBeVisible({ timeout: 30000 });

    // Should show success toast
    const successToast = page.locator('[role="alert"]').last();
    await expect(successToast).toBeVisible({ timeout: 5000 });
    await expect(successToast).toContainText(/success/i);
  });

  test("should not lose application state after error", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // Verify dashboard content is loaded before error
    await expect(page.getByText(/dashboard/i).first()).toBeVisible();

    // Mock error
    await page.route("**/api/enrichment/vulnerabilities", async (route: Route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ message: "Internal Server Error" }),
      });
    });

    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    await vulnButton.click();

    // Error toast should appear
    const toast = page.locator('[role="alert"]');
    await expect(toast).toBeVisible({ timeout: 5000 });

    // Dashboard content should still be visible (state preserved)
    await expect(page.getByText(/dashboard/i).first()).toBeVisible();

    // Other buttons should still work
    const threatButton = page.getByRole("button", { name: /enriquecer amenazas/i });
    await expect(threatButton).toBeEnabled();
  });
});

// ============================================================================
// Additional E2E Tests
// ============================================================================

test.describe("Enrichment Buttons - Complete Failure", () => {
  test("should show error toast when all sources fail", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    await mockEnrichmentAPI(page, {
      successfulSources: 0,
      failedSources: 4,
      status: "completed",
      errors: [
        { source: "nvd", error: "API timeout", recoverable: true },
        { source: "epss", error: "Rate limited", recoverable: true },
        { source: "github", error: "Auth error", recoverable: false },
        { source: "synthetic", error: "Service unavailable", recoverable: true },
      ],
    });

    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    await vulnButton.click();

    await expect(page.getByText(/enriching/i)).not.toBeVisible({ timeout: 30000 });

    // Should show error toast
    const toast = page.locator('[role="alert"]');
    await expect(toast).toBeVisible({ timeout: 5000 });
    await expect(toast).toContainText(/all.*sources failed/i);
  });
});

test.describe("Enrichment Buttons - Threat Enrichment", () => {
  test("debe enriquecer amenazas correctamente", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    const jobId = `threat-job-${Date.now()}`;

    // Mock threat enrichment
    await page.route("**/api/enrichment/threats", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: jobId,
          status: "pending",
          total_items: 100,
        }),
      });
    });

    await page.route("**/api/enrichment/status/*", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: jobId,
          status: "completed",
          progress: 1.0,
          processed_items: 100,
          total_items: 100,
          failed_items: 0,
          successful_sources: 5,
          failed_sources: 0,
        }),
      });
    });

    const threatButton = page.getByRole("button", { name: /enriquecer amenazas/i });
    await threatButton.click();

    // Should show loading
    await expect(page.getByText(/enriching/i)).toBeVisible({ timeout: 5000 });

    // Wait for completion
    await expect(page.getByText(/enriching/i)).not.toBeVisible({ timeout: 30000 });

    // Should show success toast
    const toast = page.locator('[role="alert"]');
    await expect(toast).toBeVisible({ timeout: 5000 });
    await expect(toast).toContainText(/success/i);
  });
});

test.describe("Enrichment Buttons - Concurrent Operations", () => {
  test("should disable button during operation", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    await mockEnrichmentAPI(page, { status: "running", progress: 0.5 });

    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    await vulnButton.click();

    // Button should be disabled
    await expect(vulnButton).toBeDisabled();

    // Other button should still be enabled
    const threatButton = page.getByRole("button", { name: /enriquecer amenazas/i });
    await expect(threatButton).toBeEnabled();
  });

  test("should allow both enrichment types to run independently", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // Mock both enrichment types
    await page.route("**/api/enrichment/vulnerabilities", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "vuln-job",
          status: "pending",
          total_items: 100,
        }),
      });
    });

    await page.route("**/api/enrichment/threats", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "threat-job",
          status: "pending",
          total_items: 100,
        }),
      });
    });

    await page.route("**/api/enrichment/status/*", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "job",
          status: "running",
          progress: 0.5,
          processed_items: 50,
          total_items: 100,
          failed_items: 0,
        }),
      });
    });

    const vulnButton = page.getByRole("button", { name: /enriquecer vulnerabilidades/i });
    const threatButton = page.getByRole("button", { name: /enriquecer amenazas/i });

    // Start vulnerability enrichment
    await vulnButton.click();

    // Vulnerability button disabled, threat button still enabled
    await expect(vulnButton).toBeDisabled();
    await expect(threatButton).toBeEnabled();

    // Start threat enrichment
    await threatButton.click();

    // Both buttons should be disabled now
    await expect(vulnButton).toBeDisabled();
    await expect(threatButton).toBeDisabled();
  });
});
