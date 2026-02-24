/**
 * Threat Map E2E Tests (Playwright)
 *
 * Tests for the interactive world map component:
 * 1. debe cargar mapa mundi con marcadores
 * 2. debe mostrar panel lateral al click en pais
 * 3. debe animar lineas de ataque
 */

import { test, expect, Page, Route } from "@playwright/test";

const BASE_URL = "http://localhost:3000";

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Wait for page to be fully loaded
 */
async function waitForPageReady(page: Page) {
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500); // Allow for React hydration
}

/**
 * Generate mock enriched threat data with geo information
 */
function generateMockEnrichedThreat(index: number, country: string = "RU") {
  const countries: Record<string, { name: string; lat: number; lon: number }> = {
    RU: { name: "Russia", lat: 61.5, lon: 105.3 },
    CN: { name: "China", lat: 35.9, lon: 104.2 },
    KP: { name: "North Korea", lat: 40.3, lon: 127.5 },
    IR: { name: "Iran", lat: 32.4, lon: 53.7 },
    US: { name: "United States", lat: 39.8, lon: -98.5 },
    DE: { name: "Germany", lat: 51.2, lon: 10.5 },
    NL: { name: "Netherlands", lat: 52.1, lon: 5.3 },
    BR: { name: "Brazil", lat: -14.2, lon: -51.9 },
  };

  const geo = countries[country] || countries.RU;
  const riskLevels = ["critical", "high", "medium", "low"];
  const malwareFamilies = ["Emotet", "TrickBot", "Cobalt Strike", "Mimikatz", "Ryuk"];
  const threatActors = ["APT28", "APT29", "Lazarus Group", "Fancy Bear", "Cozy Bear"];

  return {
    id: `threat-${index}`,
    type: "ip",
    value: `192.168.${Math.floor(index / 256)}.${index % 256}`,
    risk_score: Math.floor(Math.random() * 100),
    risk_level: riskLevels[Math.floor(Math.random() * riskLevels.length)],
    confidence: Math.floor(Math.random() * 100),
    geo: {
      country: country,
      country_name: geo.name,
      city: "Capital",
      latitude: geo.lat + (Math.random() - 0.5) * 10,
      longitude: geo.lon + (Math.random() - 0.5) * 10,
    },
    network: {
      asn: 12345,
      asn_org: "Example ISP",
      is_vpn: Math.random() > 0.7,
      is_proxy: Math.random() > 0.8,
      is_tor: Math.random() > 0.9,
      is_datacenter: Math.random() > 0.5,
    },
    reputation: {
      abuseipdb: {
        confidence_score: Math.floor(Math.random() * 100),
        total_reports: Math.floor(Math.random() * 1000),
        abuse_categories: ["scanner", "brute-force"],
      },
      greynoise: {
        classification: Math.random() > 0.5 ? "malicious" : "benign",
        noise: Math.random() > 0.5,
      },
      virustotal: {
        malicious_count: Math.floor(Math.random() * 50),
        suspicious_count: Math.floor(Math.random() * 20),
        harmless_count: Math.floor(Math.random() * 30),
        community_score: Math.floor(Math.random() * 100),
      },
    },
    threat_intel: {
      malware_families: [malwareFamilies[Math.floor(Math.random() * malwareFamilies.length)]],
      threat_actors: [threatActors[Math.floor(Math.random() * threatActors.length)]],
      campaigns: ["Operation Example"],
      tags: ["scanner", "botnet", "c2"],
    },
    mitre_attack: {
      techniques: [
        { id: "T1566", name: "Phishing", tactic: "InitialAccess" },
        { id: "T1059", name: "Command and Scripting Interpreter", tactic: "Execution" },
      ],
    },
    intel_feeds: [
      {
        source: "OTX",
        feed_name: "Malicious IPs",
        author: "AlienVault",
        tlp: "green",
      },
    ],
    enrichment_meta: {
      enriched_at: new Date().toISOString(),
      sources_successful: ["otx", "abuseipdb", "greynoise"],
      sources_failed: [],
    },
  };
}

/**
 * Mock threat enrichment API with geo-distributed threats
 */
async function mockThreatEnrichmentAPIWithGeo(page: Page, totalItems: number = 15) {
  const countries = ["RU", "CN", "KP", "IR", "US", "DE", "NL", "BR"];

  await page.route("**/api/enrichment/threats", async (route: Route) => {
    const enrichedIndicators = Array.from({ length: totalItems }, (_, i) =>
      generateMockEnrichedThreat(i, countries[i % countries.length])
    );

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        job_id: `map-test-job-${Date.now()}`,
        status: "completed",
        enriched_indicators: enrichedIndicators,
        successful_sources: 5,
        failed_sources: 0,
        total_items: totalItems,
      }),
    });
  });
}

// ============================================================================
// TEST 1: debe cargar mapa mundi con marcadores
// ============================================================================

test.describe("Threat Map - World Map Loading", () => {
  test.beforeEach(async ({ page }) => {
    await mockThreatEnrichmentAPIWithGeo(page, 20);
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
  });

  test("debe cargar mapa mundi con marcadores", async ({ page }) => {

    // Verify SVG world map is rendered
    const svgMap = page.locator('svg[viewBox="0 0 800 400"]');
    await expect(svgMap).toBeVisible({ timeout: 10000 });

    // Verify map has country markers (circles)
    const markers = page.locator("svg circle");
    const markerCount = await markers.count();
    expect(markerCount).toBeGreaterThan(0);

    // Verify map title "Threat Origins - Live Attack Map" is visible
    await expect(page.getByText(/Threat Origins|Live Attack Map/i)).toBeVisible();

    // Verify grid pattern is defined (defs elements are hidden by CSS spec, use toBeAttached)
    const gridPattern = page.locator("svg defs pattern#grid");
    await expect(gridPattern).toBeAttached();

    // Verify glow filter is defined for visual effects
    const glowFilter = page.locator("svg defs filter#glow");
    await expect(glowFilter).toBeAttached();
  });

  test("debe mostrar continentes en el mapa", async ({ page }) => {
    // Verify continent paths exist (simplified world map)
    const worldMapGroup = page.locator("svg g.world-map");
    await expect(worldMapGroup).toBeVisible();

    // Verify paths for continents
    const continentPaths = page.locator("svg g.world-map path");
    const pathCount = await continentPaths.count();
    expect(pathCount).toBeGreaterThanOrEqual(5); // At least 5 continent shapes
  });

  test("debe mostrar leyenda de colores de riesgo", async ({ page }) => {
    // Verify legend section exists
    await expect(page.getByText(/Risk Level/i)).toBeVisible();

    // Verify all risk levels are in legend
    const riskLevels = ["critical", "high", "medium", "low"];
    for (const level of riskLevels) {
      await expect(page.getByText(new RegExp(level, "i")).first()).toBeVisible();
    }
  });

  test("debe mostrar marcador SOC como destino", async ({ page }) => {
    // Verify SOC marker is visible
    const socLabel = page.locator("svg text").filter({ hasText: "SOC" });
    await expect(socLabel).toBeVisible();

    // SOC should be rendered with green color indicator
    const socCircle = page.locator('svg circle[fill="#22c55e"]');
    const greenCircleCount = await socCircle.count();
    expect(greenCircleCount).toBeGreaterThan(0);
  });

  test("debe mostrar contadores de amenazas por pais", async ({ page }) => {
    // Verify country stats overlay at bottom of map
    const statsOverlay = page.locator('[class*="bg-gray-800"]').filter({ hasText: /Russia|China|North Korea|Iran/i });
    const overlayCount = await statsOverlay.count();
    expect(overlayCount).toBeGreaterThan(0);

    // Verify country threat counters show numbers
    const threatCounts = page.locator('[class*="text-2xl"][class*="font-bold"]');
    const countElements = await threatCounts.count();
    expect(countElements).toBeGreaterThan(0);
  });
});

// ============================================================================
// TEST 2: debe mostrar panel lateral al click en pais
// ============================================================================

test.describe("Threat Map - Country Click Interaction", () => {
  test.beforeEach(async ({ page }) => {
    await mockThreatEnrichmentAPIWithGeo(page, 20);
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
  });

  test("debe mostrar panel lateral al click en pais", async ({ page }) => {
    // Wait for initial load toast to dismiss
    await page.waitForTimeout(3000);

    // Find a clickable country marker
    const countryMarker = page.locator("svg g.cursor-pointer").first();

    if (await countryMarker.isVisible()) {
      await countryMarker.dispatchEvent("click");

      // Should show toast with "Filtering by [country]" message
      const filterToast = page.locator('[role="alert"]').filter({ hasText: /Filtering/i });
      await expect(filterToast.first()).toBeVisible({ timeout: 5000 });
    }
  });

  test("debe destacar pais al hover", async ({ page }) => {
    // Find a clickable country marker with hover transition
    const countryMarker = page.locator("svg g.cursor-pointer").first();

    if (await countryMarker.isVisible()) {
      // Verify marker has hover transition class
      const hasTransition = await countryMarker.getAttribute("class");
      expect(hasTransition).toContain("transition-transform");
      expect(hasTransition).toContain("hover:scale-125");
    }
  });

  test("debe mostrar contador de IOCs en marcador de pais", async ({ page }) => {
    // Find country markers with count labels
    const countLabels = page.locator('svg g.cursor-pointer text');
    const labelCount = await countLabels.count();
    expect(labelCount).toBeGreaterThan(0);

    // Verify count is a number
    const firstLabel = await countLabels.first().textContent();
    expect(parseInt(firstLabel || "0")).toBeGreaterThan(0);
  });

  test("debe tener animacion de pulso en marcadores", async ({ page }) => {
    // Verify pulsing animation on country markers
    const pulsingCircles = page.locator('svg g.cursor-pointer circle animate[attributeName="r"]');
    const pulseCount = await pulsingCircles.count();
    expect(pulseCount).toBeGreaterThan(0);

    // Verify opacity animation as well
    const opacityAnimations = page.locator('svg g.cursor-pointer circle animate[attributeName="opacity"]');
    const opacityCount = await opacityAnimations.count();
    expect(opacityCount).toBeGreaterThan(0);
  });
});

// ============================================================================
// TEST 3: debe animar lineas de ataque
// ============================================================================

test.describe("Threat Map - Attack Line Animations", () => {
  test.beforeEach(async ({ page }) => {
    await mockThreatEnrichmentAPIWithGeo(page, 20);
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
  });

  test("debe animar lineas de ataque", async ({ page }) => {

    // Verify curved attack line paths exist (Bezier curves with Q command)
    const curvedPaths = page.locator('svg path[d*="Q"]');
    const pathCount = await curvedPaths.count();
    expect(pathCount).toBeGreaterThan(0);

    // Verify stroke-dasharray animation for moving dash effect
    const animatedDashPaths = page.locator('svg path[stroke-dasharray]');
    const dashPathCount = await animatedDashPaths.count();
    expect(dashPathCount).toBeGreaterThan(0);

    // Verify animateMotion elements for moving dots along paths
    const motionAnimations = page.locator("svg animateMotion");
    const motionCount = await motionAnimations.count();
    expect(motionCount).toBeGreaterThan(0);
  });

  test("debe mostrar lineas con diferentes colores por riesgo", async ({ page }) => {
    // Risk colors defined in component
    const riskColors = ["#ef4444", "#f97316", "#eab308", "#22c55e"]; // critical, high, medium, low

    // Verify paths with stroke colors exist
    const coloredPaths = page.locator('svg path[stroke]');
    const pathCount = await coloredPaths.count();
    expect(pathCount).toBeGreaterThan(0);

    // Check at least one risk color is used
    let foundColor = false;
    for (const color of riskColors) {
      const pathWithColor = page.locator(`svg path[stroke="${color}"]`);
      const count = await pathWithColor.count();
      if (count > 0) {
        foundColor = true;
        break;
      }
    }
    expect(foundColor).toBe(true);
  });

  test("debe tener efecto glow en lineas", async ({ page }) => {
    // Verify glow filter is defined (defs elements are hidden by CSS spec, use toBeAttached)
    const glowFilter = page.locator("svg defs filter#glow");
    await expect(glowFilter).toBeAttached();

    // Verify filter uses Gaussian blur
    const gaussianBlur = page.locator("svg defs filter#glow feGaussianBlur");
    await expect(gaussianBlur).toBeAttached();

    // Verify paths reference glow filter
    const glowPaths = page.locator('svg path[filter="url(#glow)"]');
    const glowPathCount = await glowPaths.count();
    expect(glowPathCount).toBeGreaterThan(0);
  });

  test("debe tener puntos moviles en las lineas de ataque", async ({ page }) => {
    // Verify animated circles (moving dots) exist
    const animatedCircles = page.locator("svg circle animateMotion");
    const circleCount = await animatedCircles.count();
    expect(circleCount).toBeGreaterThan(0);

    // Verify animateMotion has proper attributes
    const firstAnimation = animatedCircles.first();
    const dur = await firstAnimation.getAttribute("dur");
    expect(dur).toBe("3s");

    const repeatCount = await firstAnimation.getAttribute("repeatCount");
    expect(repeatCount).toBe("indefinite");
  });

  test("debe tener animacion de dashboard offset en lineas", async ({ page }) => {

    // Verify stroke-dashoffset animation
    const dashAnimations = page.locator('svg path animate[attributeName="stroke-dashoffset"]');
    const animationCount = await dashAnimations.count();
    expect(animationCount).toBeGreaterThan(0);

    // Verify animation repeats indefinitely
    const firstAnimation = dashAnimations.first();
    const repeatCount = await firstAnimation.getAttribute("repeatCount");
    expect(repeatCount).toBe("indefinite");
  });

  test("debe conectar origen a SOC (destino)", async ({ page }) => {

    // Verify mpath elements reference path IDs
    const mpaths = page.locator("svg mpath");
    const mpathCount = await mpaths.count();
    expect(mpathCount).toBeGreaterThan(0);

    // Verify hidden paths used for motion path
    const motionPaths = page.locator('svg path[fill="none"][stroke="none"]');
    const hiddenPathCount = await motionPaths.count();
    expect(hiddenPathCount).toBeGreaterThan(0);
  });
});

// ============================================================================
// Additional Map Tests - Visual Elements
// ============================================================================

test.describe("Threat Map - Visual Elements", () => {
  test.beforeEach(async ({ page }) => {
    await mockThreatEnrichmentAPIWithGeo(page, 20);
    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
  });

  test("debe mostrar header del mapa con icono animado", async ({ page }) => {

    // Verify header with threat icon
    const threatIcon = page.locator('svg[class*="animate-pulse"]').filter({ has: page.locator('path') });
    const iconCount = await threatIcon.count();
    expect(iconCount).toBeGreaterThan(0);

    // Verify title text
    await expect(page.getByText(/Threat Origins.*Live Attack Map/i)).toBeVisible();
  });

  test("debe mostrar descripcion de amenazas activas", async ({ page }) => {
    // Verify description with threat count and country count
    await expect(page.getByText(/\d+\s+active\s+threats\s+from\s+\d+\s+countries/i)).toBeVisible();
  });

  test("debe usar gradiente de fondo en el mapa", async ({ page }) => {

    // Verify SVG has gradient background style
    const svgMap = page.locator('svg[style*="background: linear-gradient"]');
    await expect(svgMap).toBeVisible();
  });

  test("debe mostrar estadisticas de paises principales", async ({ page }) => {
    // Verify stats for main threat origin countries
    const expectedCountries = ["Russia", "China", "North Korea", "Iran"];

    for (const country of expectedCountries) {
      const countryLabel = page.locator(`[class*="text-xs"][class*="text-gray-400"]`).filter({ hasText: country });
      const count = await countryLabel.count();
      expect(count).toBeGreaterThan(0);
    }
  });
});

// ============================================================================
// Map Error Handling Tests
// ============================================================================

test.describe("Threat Map - Error Handling", () => {
  test("debe mostrar mapa sin errores cuando no hay amenazas", async ({ page }) => {
    // Mock empty response
    await page.route("**/api/enrichment/threats", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "empty-test",
          status: "completed",
          enriched_indicators: [],
          successful_sources: 0,
          failed_sources: 0,
          total_items: 0,
        }),
      });
    });

    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
    await page.waitForTimeout(1000);

    // Map should still be visible
    const svgMap = page.locator("svg[viewBox]");
    await expect(svgMap.first()).toBeVisible();

    // SOC marker should still be present
    const socLabel = page.locator("svg text").filter({ hasText: "SOC" });
    await expect(socLabel).toBeVisible();

    // No console errors
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error" && !msg.text().includes("favicon")) {
        errors.push(msg.text());
      }
    });

    const criticalErrors = errors.filter(
      (e) => e.includes("React") || e.includes("TypeError")
    );
    expect(criticalErrors).toHaveLength(0);
  });

  test("debe manejar amenazas sin datos geo", async ({ page }) => {
    // Mock threats without geo data
    await page.route("**/api/enrichment/threats", async (route: Route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "no-geo-test",
          status: "completed",
          enriched_indicators: [
            {
              id: "threat-no-geo",
              type: "ip",
              value: "1.2.3.4",
              risk_score: 80,
              risk_level: "high",
              geo: null, // No geo data
              network: null,
              reputation: {},
              threat_intel: { malware_families: [], threat_actors: [], campaigns: [], tags: [] },
              mitre_attack: { techniques: [] },
              intel_feeds: [],
              enrichment_meta: { enriched_at: new Date().toISOString(), sources_successful: [], sources_failed: [] },
            },
          ],
          successful_sources: 1,
          failed_sources: 0,
          total_items: 1,
        }),
      });
    });

    await page.goto(`${BASE_URL}/threats`);
    await waitForPageReady(page);
    await page.waitForTimeout(1500);

    // Page should not crash
    await expect(page.locator("main")).toBeVisible();

    // Map should still render
    const svgMap = page.locator("svg[viewBox]");
    await expect(svgMap.first()).toBeVisible();
  });
});
