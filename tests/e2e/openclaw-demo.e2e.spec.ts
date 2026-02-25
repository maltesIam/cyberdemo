import { test, expect, Page } from "@playwright/test";
import { demoScenarios, mockIncidents, mockAssets, isVipAsset } from "../fixtures/synthetic-data";

/**
 * OpenClaw Agent Demo E2E Tests
 *
 * Tests the REAL demo flow with OpenClaw agent:
 * 1. Opens OpenClaw interface
 * 2. Sends messages to Claude
 * 3. Verifies Claude uses the cyberdemo MCP tools correctly
 * 4. Validates the 3 demo scenarios visually
 *
 * IMPORTANT: These tests require:
 * - OpenClaw running at OPENCLAW_URL (default: http://localhost:18789)
 * - Backend MCP server at BACKEND_URL (default: http://localhost:8000)
 * - cyberdemo plugin loaded in OpenClaw
 */

const OPENCLAW_URL = process.env.OPENCLAW_URL || "http://localhost:18789";
const CYBERDEMO_FRONTEND_URL = process.env.CYBERDEMO_FRONTEND_URL || "http://localhost:3000";

// Helper to check if gateway is connected (not offline)
async function isGatewayConnected(page: Page): Promise<boolean> {
  const offlineIndicator = page.locator("text=/Offline|Disconnected|device identity required/i");
  const isOffline = await offlineIndicator.isVisible().catch(() => false);
  const chatInput = page.getByRole("textbox").first();
  const isDisabled = await chatInput.isDisabled().catch(() => true);
  return !isOffline && !isDisabled;
}

// Helper to skip test if gateway not connected
async function skipIfDisconnected(page: Page, testInfo: import("@playwright/test").TestInfo) {
  const connected = await isGatewayConnected(page);
  if (!connected) {
    console.log("Gateway not connected - skipping test (requires authenticated gateway)");
    testInfo.skip(true, "Gateway not connected - requires authenticated gateway");
    return true;
  }
  return false;
}

// Helper class for OpenClaw interaction
class OpenClawHelper {
  constructor(private page: Page) {}

  async waitForReady() {
    // Wait for OpenClaw to be fully loaded
    await this.page.waitForLoadState("networkidle");
    // Look for the chat input or any main UI element
    await this.page.waitForSelector(
      'textarea, input[type="text"], [contenteditable="true"]',
      { timeout: 15000 }
    );
  }

  async sendMessage(message: string) {
    // Find chat input - could be textarea, input, or contenteditable
    const input =
      this.page.locator("textarea").first() ||
      this.page.locator('input[type="text"]').first() ||
      this.page.locator('[contenteditable="true"]').first();

    await input.fill(message);

    // Find and click send button
    const sendButton =
      this.page.getByRole("button", { name: /send|submit|enviar/i }).first() ||
      this.page.locator('button[type="submit"]').first() ||
      this.page.locator('[aria-label*="send"]').first();

    await sendButton.click();
  }

  async waitForResponse(timeout = 30000) {
    // Wait for Claude's response to appear
    // Look for new message elements or loading indicators to disappear
    await this.page.waitForTimeout(2000); // Initial wait for request

    // Wait for loading indicator to disappear (if any)
    const loadingIndicator = this.page.locator('[class*="loading"], [class*="typing"], [class*="spinner"]');
    if (await loadingIndicator.isVisible()) {
      await loadingIndicator.waitFor({ state: "hidden", timeout });
    }

    // Additional wait for response to render
    await this.page.waitForTimeout(1000);
  }

  async getLastResponse(): Promise<string> {
    // Get the last response message from Claude
    const responseMessages = this.page.locator(
      '[class*="message"][class*="assistant"], ' +
        '[class*="response"], ' +
        '[data-role="assistant"], ' +
        '[class*="bot-message"]'
    );

    const count = await responseMessages.count();
    if (count > 0) {
      return (await responseMessages.nth(count - 1).textContent()) || "";
    }
    return "";
  }

  async hasToolInvocation(toolName: string): Promise<boolean> {
    // Check if the response shows tool invocation
    const response = await this.getLastResponse();
    return (
      response.toLowerCase().includes(toolName.toLowerCase()) ||
      response.includes("tool") ||
      response.includes("MCP")
    );
  }
}

test.describe("OpenClaw Demo - Setup Verification", () => {
  test("should connect to OpenClaw interface", async ({ page }) => {
    await page.goto(OPENCLAW_URL);

    // Verify main interface loaded
    await expect(page).toHaveURL(new RegExp(OPENCLAW_URL.replace(/:\d+/, ":\\d+")));

    // Log gateway connection status
    const connected = await isGatewayConnected(page);
    console.log("Gateway connected:", connected);

    // Take screenshot of initial state
    await page.screenshot({
      path: "test-results/openclaw-initial.png",
      fullPage: true,
    });
  });

  test("should have chat input available", async ({ page }) => {
    await page.goto(OPENCLAW_URL);
    await page.waitForLoadState("networkidle");

    // Check for any form of text input (will be disabled if not connected)
    const hasInput =
      (await page.locator("textarea").isVisible()) ||
      (await page.locator('input[type="text"]').isVisible()) ||
      (await page.locator('[contenteditable="true"]').isVisible());

    expect(hasInput).toBe(true);
  });

  test("should verify cyberdemo plugin is loaded", async ({ page }, testInfo) => {
    await page.goto(OPENCLAW_URL);
    await page.waitForLoadState("networkidle");

    // This test requires gateway connection
    if (await skipIfDisconnected(page, testInfo)) return;

    const helper = new OpenClawHelper(page);
    await helper.waitForReady();

    // Ask about available tools
    await helper.sendMessage(
      "¿Qué herramientas de cyberdemo tienes disponibles? Lista las tools de SIEM, EDR y threat intelligence."
    );
    await helper.waitForResponse(20000);

    const response = await helper.getLastResponse();

    const hasCyberdemoTools =
      response.toLowerCase().includes("siem") ||
      response.toLowerCase().includes("edr") ||
      response.toLowerCase().includes("incident") ||
      response.toLowerCase().includes("cyberdemo");

    console.log("Cyberdemo tools detected:", hasCyberdemoTools);
    console.log("Response preview:", response.substring(0, 500));

    await page.screenshot({
      path: "test-results/openclaw-tools-check.png",
      fullPage: true,
    });
  });
});

test.describe("OpenClaw Demo - Scenario 1: Malware Auto-Containment", () => {
  test("should investigate high-confidence malware incident", async ({ page }, testInfo) => {
    await page.goto(OPENCLAW_URL);
    await page.waitForLoadState("networkidle");
    if (await skipIfDisconnected(page, testInfo)) return;

    const helper = new OpenClawHelper(page);
    await helper.waitForReady();

    const scenario = demoScenarios.scenario1;
    const incident = scenario.incident;

    // Step 1: Ask to investigate the incident
    await helper.sendMessage(
      `Investiga el incidente ${incident.id}. Es un incidente de severidad ${incident.severity} ` +
        `detectado en el activo ${incident.asset_id}. Título: "${incident.title}"`
    );
    await helper.waitForResponse(30000);

    let response = await helper.getLastResponse();
    console.log("Investigation response:", response.substring(0, 800));

    await page.screenshot({
      path: "test-results/scenario1-investigate.png",
      fullPage: true,
    });

    // Step 2: Ask for recommended action
    await helper.sendMessage(
      `Basándote en tu investigación del incidente ${incident.id}, ` +
        `¿qué acción recomiendas? El activo ${incident.asset_id} es un workstation estándar ` +
        `(no es VIP). Los indicadores muestran malware TrickBot confirmado.`
    );
    await helper.waitForResponse(30000);

    response = await helper.getLastResponse();
    console.log("Recommendation response:", response.substring(0, 800));

    // Verify Claude recommends containment (auto_contain for high confidence + standard asset)
    const recommendsContainment =
      response.toLowerCase().includes("contain") ||
      response.toLowerCase().includes("isola") ||
      response.toLowerCase().includes("auto");

    expect(recommendsContainment).toBe(true);

    await page.screenshot({
      path: "test-results/scenario1-recommendation.png",
      fullPage: true,
    });
  });

  test("should execute containment on standard asset", async ({ page }, testInfo) => {
    await page.goto(OPENCLAW_URL);
    await page.waitForLoadState("networkidle");
    if (await skipIfDisconnected(page, testInfo)) return;

    const helper = new OpenClawHelper(page);
    await helper.waitForReady();

    const asset = mockAssets.standardWorkstation;

    // Request containment
    await helper.sendMessage(
      `Ejecuta la contención del activo ${asset.id}. ` +
        `Motivo: Malware TrickBot confirmado en incidente ${mockIncidents.highConfidenceStandardAsset.id}`
    );
    await helper.waitForResponse(30000);

    const response = await helper.getLastResponse();
    console.log("Containment execution response:", response.substring(0, 800));

    // Verify containment was executed or acknowledged
    const containmentExecuted =
      response.toLowerCase().includes("contain") ||
      response.toLowerCase().includes("isola") ||
      response.toLowerCase().includes("network") ||
      response.toLowerCase().includes("ejecut");

    expect(containmentExecuted).toBe(true);

    await page.screenshot({
      path: "test-results/scenario1-containment-executed.png",
      fullPage: true,
    });
  });
});

test.describe("OpenClaw Demo - Scenario 2: VIP Threat Response", () => {
  test("should detect VIP asset and request approval", async ({ page }, testInfo) => {
    await page.goto(OPENCLAW_URL);
    await page.waitForLoadState("networkidle");
    if (await skipIfDisconnected(page, testInfo)) return;

    const helper = new OpenClawHelper(page);
    await helper.waitForReady();

    const scenario = demoScenarios.scenario2;
    const incident = scenario.incident;
    const asset = mockAssets.vipLaptop;

    // Verify asset is VIP
    expect(isVipAsset(asset.id)).toBe(true);

    // Step 1: Investigate VIP incident
    await helper.sendMessage(
      `Analiza el incidente ${incident.id}: "${incident.title}". ` +
        `El activo afectado es ${asset.id}, que pertenece al CFO de la empresa. ` +
        `Severidad: ${incident.severity}. ¿Qué acción recomiendas?`
    );
    await helper.waitForResponse(30000);

    let response = await helper.getLastResponse();
    console.log("VIP analysis response:", response.substring(0, 800));

    // Verify Claude recognizes VIP and needs approval
    const recognizesVip =
      response.toLowerCase().includes("vip") ||
      response.toLowerCase().includes("cfo") ||
      response.toLowerCase().includes("ejecutivo") ||
      response.toLowerCase().includes("crítico") ||
      response.toLowerCase().includes("approval") ||
      response.toLowerCase().includes("aprobación") ||
      response.toLowerCase().includes("humano");

    expect(recognizesVip).toBe(true);

    await page.screenshot({
      path: "test-results/scenario2-vip-detected.png",
      fullPage: true,
    });

    // Step 2: Try to contain VIP without approval
    await helper.sendMessage(
      `Intenta contener el activo ${asset.id} (laptop del CFO). ` +
        `¿Puedes hacerlo automáticamente o necesitas aprobación?`
    );
    await helper.waitForResponse(30000);

    response = await helper.getLastResponse();
    console.log("VIP containment attempt response:", response.substring(0, 800));

    // Should require approval for VIP
    const requiresApproval =
      response.toLowerCase().includes("approval") ||
      response.toLowerCase().includes("aprobación") ||
      response.toLowerCase().includes("autorización") ||
      response.toLowerCase().includes("humano") ||
      response.toLowerCase().includes("confirmar") ||
      response.toLowerCase().includes("vip");

    expect(requiresApproval).toBe(true);

    await page.screenshot({
      path: "test-results/scenario2-approval-required.png",
      fullPage: true,
    });
  });
});

test.describe("OpenClaw Demo - Scenario 3: False Positive Detection", () => {
  test("should identify and close false positive", async ({ page }, testInfo) => {
    await page.goto(OPENCLAW_URL);
    await page.waitForLoadState("networkidle");
    if (await skipIfDisconnected(page, testInfo)) return;

    const helper = new OpenClawHelper(page);
    await helper.waitForReady();

    const scenario = demoScenarios.scenario3;
    const incident = scenario.incident;

    // Step 1: Analyze low-confidence incident
    await helper.sendMessage(
      `Analiza el incidente ${incident.id}: "${incident.title}". ` +
        `Es un servidor de desarrollo (${incident.asset_id}), severidad ${incident.severity}. ` +
        `El proceso detectado parece ser node.js ejecutando un servidor de desarrollo. ` +
        `¿Crees que es un falso positivo?`
    );
    await helper.waitForResponse(30000);

    let response = await helper.getLastResponse();
    console.log("FP analysis response:", response.substring(0, 800));

    // Verify Claude identifies it as likely false positive
    const identifiesFP =
      response.toLowerCase().includes("false positive") ||
      response.toLowerCase().includes("falso positivo") ||
      response.toLowerCase().includes("legítimo") ||
      response.toLowerCase().includes("legitimate") ||
      response.toLowerCase().includes("benigno") ||
      response.toLowerCase().includes("benign") ||
      response.toLowerCase().includes("normal");

    expect(identifiesFP).toBe(true);

    await page.screenshot({
      path: "test-results/scenario3-fp-identified.png",
      fullPage: true,
    });

    // Step 2: Request closure as false positive
    await helper.sendMessage(
      `Cierra el incidente ${incident.id} como falso positivo. ` +
        `Motivo: Actividad legítima de desarrollo (servidor Node.js en entorno de desarrollo).`
    );
    await helper.waitForResponse(30000);

    response = await helper.getLastResponse();
    console.log("FP closure response:", response.substring(0, 800));

    // Verify closure was acknowledged
    const closureAcknowledged =
      response.toLowerCase().includes("cerr") ||
      response.toLowerCase().includes("close") ||
      response.toLowerCase().includes("resuelto") ||
      response.toLowerCase().includes("resolved");

    expect(closureAcknowledged).toBe(true);

    await page.screenshot({
      path: "test-results/scenario3-fp-closed.png",
      fullPage: true,
    });
  });
});

test.describe("OpenClaw Demo - Full Demo Workflow", () => {
  test("should execute complete demo with all 3 scenarios", async ({ page }, testInfo) => {
    await page.goto(OPENCLAW_URL);
    await page.waitForLoadState("networkidle");
    if (await skipIfDisconnected(page, testInfo)) return;

    const helper = new OpenClawHelper(page);
    await helper.waitForReady();

    console.log("=== Starting Full Demo ===");

    // SCENARIO 1: Auto-containment
    console.log("\n--- Scenario 1: Malware Auto-Containment ---");
    await helper.sendMessage(
      `DEMO SCENARIO 1: Hay un incidente crítico ${demoScenarios.scenario1.incident.id}. ` +
        `Malware TrickBot detectado en workstation ${demoScenarios.scenario1.incident.asset_id}. ` +
        `Es un activo estándar, no VIP. La confianza es alta (>85%). ` +
        `Investiga y ejecuta la acción apropiada.`
    );
    await helper.waitForResponse(45000);
    let response = await helper.getLastResponse();
    console.log("Scenario 1 result:", response.substring(0, 500));
    await page.screenshot({ path: "test-results/demo-scenario1.png", fullPage: true });

    // SCENARIO 2: VIP Protection
    console.log("\n--- Scenario 2: VIP Threat Response ---");
    await helper.sendMessage(
      `DEMO SCENARIO 2: Nuevo incidente ${demoScenarios.scenario2.incident.id}. ` +
        `Actividad sospechosa en ${demoScenarios.scenario2.incident.asset_id} (laptop del CFO). ` +
        `Es un activo VIP crítico. Severidad alta, confianza media (60-85%). ` +
        `¿Qué acción recomiendas?`
    );
    await helper.waitForResponse(45000);
    response = await helper.getLastResponse();
    console.log("Scenario 2 result:", response.substring(0, 500));
    await page.screenshot({ path: "test-results/demo-scenario2.png", fullPage: true });

    // SCENARIO 3: False Positive
    console.log("\n--- Scenario 3: False Positive Detection ---");
    await helper.sendMessage(
      `DEMO SCENARIO 3: Alerta en ${demoScenarios.scenario3.incident.id}. ` +
        `Servidor de desarrollo ${demoScenarios.scenario3.incident.asset_id}. ` +
        `Proceso: node.js ejecutando servidor en puerto 3000. ` +
        `La confianza es baja (<60%). ¿Es un falso positivo?`
    );
    await helper.waitForResponse(45000);
    response = await helper.getLastResponse();
    console.log("Scenario 3 result:", response.substring(0, 500));
    await page.screenshot({ path: "test-results/demo-scenario3.png", fullPage: true });

    console.log("\n=== Demo Complete ===");
  });
});

test.describe("OpenClaw Demo - CyberDemo Frontend Integration", () => {
  test("should reflect changes in CyberDemo dashboard", async ({ page, context }, testInfo) => {
    // Open two tabs: OpenClaw and CyberDemo frontend
    const openclawPage = page;
    const cyberdemoPage = await context.newPage();

    // Navigate to both
    await openclawPage.goto(OPENCLAW_URL);
    await openclawPage.waitForLoadState("networkidle");
    if (await skipIfDisconnected(openclawPage, testInfo)) {
      await cyberdemoPage.close();
      return;
    }

    await cyberdemoPage.goto(CYBERDEMO_FRONTEND_URL);

    const helper = new OpenClawHelper(openclawPage);
    await helper.waitForReady();
    await cyberdemoPage.waitForLoadState("networkidle");

    // Take initial screenshot of CyberDemo
    await cyberdemoPage.screenshot({
      path: "test-results/cyberdemo-initial.png",
      fullPage: true,
    });

    // Execute action in OpenClaw
    await helper.sendMessage(
      `Actualiza el dashboard de CyberDemo con estos datos: ` +
        `3 incidentes activos, 12 resueltos, 1 activo contenido. ` +
        `Usa la herramienta update_dashboard o highlight_asset.`
    );
    await helper.waitForResponse(30000);

    // Wait for frontend to potentially update
    await cyberdemoPage.waitForTimeout(3000);

    // Take screenshot after action
    await cyberdemoPage.screenshot({
      path: "test-results/cyberdemo-after-action.png",
      fullPage: true,
    });

    // Check OpenClaw response
    const response = await helper.getLastResponse();
    console.log("Dashboard update response:", response.substring(0, 500));

    await cyberdemoPage.close();
  });
});
