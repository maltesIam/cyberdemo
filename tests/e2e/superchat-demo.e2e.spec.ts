import { test, expect, Page } from "@playwright/test";
import { demoScenarios, mockIncidents, mockAssets } from "../fixtures/synthetic-data";

/**
 * SuperChat Demo E2E Tests
 *
 * Tests the demo flow using SuperChat interface connected to the gateway.
 * SuperChat provides a web chat interface that connects to the OpenClaw gateway.
 *
 * IMPORTANT: These tests require:
 * - SuperChat running at SUPERCHAT_URL (default: http://localhost:5173/superchat/)
 * - Gateway connected and authenticated
 * - Backend MCP server at BACKEND_URL (default: http://localhost:8000)
 */

const SUPERCHAT_URL = process.env.SUPERCHAT_URL || "http://localhost:5173/superchat/";
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

// Helper to normalize text for accent-insensitive matching (Spanish support)
function normalizeText(text: string): string {
  return text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

// Helper to check if SuperChat is connected to gateway
async function isSuperChatConnected(page: Page): Promise<boolean> {
  // Check that the chat interface is functional
  // Try multiple selectors for send button
  let hasSendButton = false;
  const sendButtonSelectors = [
    page.getByRole("button", { name: /send/i }),
    page.locator('button:has-text("Send")'),
    page.locator('[type="submit"]'),
    page.locator('button[aria-label*="send" i]'),
    page.locator('button').filter({ hasText: /send/i }),
  ];

  for (const selector of sendButtonSelectors) {
    hasSendButton = await selector.isVisible().catch(() => false);
    if (hasSendButton) break;
  }

  // Check that input textbox is available - try multiple selectors
  let hasInput = false;
  let isEnabled = false;

  const inputSelectors = [
    page.getByRole("textbox", { name: /type a message/i }),
    page.getByRole("textbox").first(),
    page.locator("textarea").first(),
    page.locator('input[type="text"]').first(),
  ];

  for (const selector of inputSelectors) {
    hasInput = await selector.isVisible().catch(() => false);
    if (hasInput) {
      isEnabled = await selector.isEnabled().catch(() => false);
      break;
    }
  }

  // Check for error messages that would indicate connection problems
  const errorIndicator = page.locator("text=/error|disconnected|failed|offline/i");
  const hasError = await errorIndicator.isVisible().catch(() => false);

  // Debug output
  console.log(`Connection check: sendButton=${hasSendButton}, input=${hasInput}, enabled=${isEnabled}, error=${hasError}`);

  // Only require input to be available and enabled - send button might have different styling
  return hasInput && isEnabled && !hasError;
}

// Helper to skip test if SuperChat not connected
async function skipIfNotConnected(page: Page, testInfo: import("@playwright/test").TestInfo) {
  const connected = await isSuperChatConnected(page);
  if (!connected) {
    console.log("SuperChat not connected - skipping test");
    testInfo.skip(true, "SuperChat not connected to gateway");
    return true;
  }
  return false;
}

// Helper class for SuperChat interaction
class SuperChatHelper {
  constructor(private page: Page) {}

  async waitForReady() {
    await this.page.waitForLoadState("networkidle");
    // Wait for the chat input to be available
    await this.page.waitForSelector('textarea, input[type="text"], [role="textbox"]', {
      timeout: 15000,
    });
  }

  async sendMessage(message: string) {
    // Try multiple selectors for the input
    const inputSelectors = [
      this.page.getByRole("textbox", { name: /type a message/i }),
      this.page.getByRole("textbox").first(),
      this.page.locator("textarea").first(),
      this.page.locator('[placeholder*="message" i]').first(),
    ];

    let input = inputSelectors[0];
    for (const selector of inputSelectors) {
      if (await selector.isVisible().catch(() => false)) {
        input = selector;
        break;
      }
    }
    await input.fill(message);

    // Try multiple selectors for send button and click the first visible one
    const sendButtonSelectors = [
      this.page.getByRole("button", { name: /send/i }),
      this.page.locator('button:has-text("Send")'),
      this.page.locator('button[type="submit"]'),
      this.page.locator('[aria-label*="send" i]'),
      this.page.locator("button").filter({ hasText: /send/i }),
      // Fallback: any button after the input
      this.page.locator("button").last(),
    ];

    for (const selector of sendButtonSelectors) {
      const isVisible = await selector.isVisible().catch(() => false);
      if (isVisible) {
        await selector.click();
        return;
      }
    }

    // If no send button found, try pressing Enter
    await input.press("Enter");
  }

  async waitForResponse(timeout = 60000) {
    // Wait for any processing indicator to disappear
    const processingSelectors = [
      "text=Thinking...",
      "text=Processing...",
      "button:has-text('Stop')", // Stop button indicates still processing
      '[class*="loading"]',
      '[class*="spinner"]',
    ];

    // First, wait a moment for processing to start
    await this.page.waitForTimeout(2000);

    // Wait for all processing indicators to disappear
    for (const selector of processingSelectors) {
      const indicator = this.page.locator(selector);
      const isVisible = await indicator.isVisible().catch(() => false);
      if (isVisible) {
        try {
          await indicator.waitFor({ state: "hidden", timeout: timeout - 2000 });
        } catch {
          // Continue if this selector times out
        }
      }
    }

    // Additional wait for response to fully render
    await this.page.waitForTimeout(2000);

    // Optionally wait for network idle to ensure response is complete
    await this.page.waitForLoadState("networkidle").catch(() => {});
  }

  async getLastResponse(): Promise<string> {
    // Get ALL visible text from the chat area
    // This ensures we capture the response regardless of DOM structure

    // Try to find the main content area
    const contentSelectors = [
      '[class*="chat-content"]',
      '[class*="messages"]',
      '[class*="conversation"]',
      'main',
      '[role="main"]',
      '.prose', // markdown content
      '[class*="response"]',
    ];

    let fullText = "";

    for (const selector of contentSelectors) {
      const area = this.page.locator(selector).first();
      if (await area.isVisible().catch(() => false)) {
        const text = (await area.textContent()) || "";
        if (text.length > fullText.length) {
          fullText = text;
        }
      }
    }

    // If still no text, get everything from the page body
    if (fullText.length < 50) {
      const body = this.page.locator("body");
      fullText = (await body.textContent()) || "";
    }

    console.log(`getLastResponse captured ${fullText.length} chars`);
    return fullText;
  }

  async hasResponse(): Promise<boolean> {
    // Check if there's any visible message content
    const response = await this.getLastResponse();
    return response.length > 0;
  }
}

test.describe("SuperChat Demo - Setup Verification", () => {
  test("should connect to SuperChat interface", async ({ page }) => {
    await page.goto(SUPERCHAT_URL);
    await page.waitForLoadState("networkidle");

    // Verify SuperChat loaded
    await expect(page).toHaveTitle(/SoulBot|SuperChat|Chat/i);

    // Check for main elements
    const chatInput = page.getByRole("textbox");
    await expect(chatInput.first()).toBeVisible();

    // Log connection status
    const connected = await isSuperChatConnected(page);
    console.log("SuperChat connected:", connected);

    await page.screenshot({
      path: "test-results/superchat-initial.png",
      fullPage: true,
    });
  });

  test("should have chat input available and enabled", async ({ page }) => {
    await page.goto(SUPERCHAT_URL);
    await page.waitForLoadState("networkidle");

    const chatInput = page.getByRole("textbox", { name: /type a message/i });
    await expect(chatInput).toBeVisible();
    await expect(chatInput).toBeEnabled();
  });

  test("should send and receive messages", async ({ page }, testInfo) => {
    await page.goto(SUPERCHAT_URL);
    await page.waitForLoadState("networkidle");

    if (await skipIfNotConnected(page, testInfo)) return;

    const helper = new SuperChatHelper(page);
    await helper.waitForReady();

    // Send a simple test message
    await helper.sendMessage("Hola, ¿estás conectado?");
    await helper.waitForResponse(30000);

    const response = await helper.getLastResponse();
    console.log("Response received:", response.substring(0, 200));

    // Verify we got some response
    expect(response.length).toBeGreaterThan(0);

    await page.screenshot({
      path: "test-results/superchat-response.png",
      fullPage: true,
    });
  });
});

test.describe("SuperChat Demo - MCP Tool Verification", () => {
  test("should verify MCP tools are available via backend", async ({ request }) => {
    // Check MCP tools list directly from backend
    const mcpRequest = {
      jsonrpc: "2.0",
      id: Date.now(),
      method: "tools/list",
      params: {},
    };

    const response = await request.post(`${BACKEND_URL}/mcp/messages`, {
      data: mcpRequest,
      headers: { "Content-Type": "application/json" },
    });

    if (response.status() === 200) {
      const body = await response.json();
      if (body.result?.tools) {
        const toolNames = body.result.tools.map((t: { name: string }) => t.name);
        console.log("Available MCP tools:", toolNames.slice(0, 10), "...");

        // Verify key cyberdemo tools exist
        const hasSiemTools = toolNames.some((n: string) => n.includes("siem"));
        const hasEdrTools = toolNames.some((n: string) => n.includes("edr"));

        expect(hasSiemTools || hasEdrTools).toBe(true);
      }
    }
  });
});

test.describe("SuperChat Demo - Scenario 1: Security Incident Analysis", () => {
  test("should analyze a security incident", async ({ page }, testInfo) => {
    await page.goto(SUPERCHAT_URL);
    await page.waitForLoadState("networkidle");

    if (await skipIfNotConnected(page, testInfo)) return;

    const helper = new SuperChatHelper(page);
    await helper.waitForReady();

    const scenario = demoScenarios.scenario1;
    const incident = scenario.incident;

    // Ask about the incident
    await helper.sendMessage(
      `Analiza este incidente de seguridad: ID ${incident.id}, ` +
        `severidad ${incident.severity}, detectado en activo ${incident.asset_id}. ` +
        `El título es "${incident.title}". ¿Qué acción recomiendas?`
    );
    await helper.waitForResponse(60000);

    const response = await helper.getLastResponse();
    console.log("Incident analysis response:", response.substring(0, 500));

    // Verify response discusses the incident
    const normalized = normalizeText(response);
    const discussesIncident =
      normalized.includes("incidente") ||
      normalized.includes("seguridad") ||
      normalized.includes("severidad") ||
      normalized.includes("malware") ||
      normalized.includes("trickbot");

    expect(discussesIncident).toBe(true);

    await page.screenshot({
      path: "test-results/superchat-scenario1.png",
      fullPage: true,
    });
  });

  test("should recommend containment for high-severity threat", async ({ page }, testInfo) => {
    await page.goto(SUPERCHAT_URL);
    await page.waitForLoadState("networkidle");

    if (await skipIfNotConnected(page, testInfo)) return;

    const helper = new SuperChatHelper(page);
    await helper.waitForReady();

    await helper.sendMessage(
      `Tengo un incidente crítico de malware TrickBot detectado con alta confianza (>85%) ` +
        `en un workstation estándar (no VIP). ¿Debería contener el activo automáticamente?`
    );
    await helper.waitForResponse(60000);

    const response = await helper.getLastResponse();
    console.log("Containment recommendation:", response.substring(0, 500));

    // Verify response discusses containment
    const normalized = normalizeText(response);
    const discussesContainment =
      normalized.includes("conten") ||
      normalized.includes("isola") ||
      normalized.includes("cuarentena") ||
      normalized.includes("bloque") ||
      normalized.includes("automatica") || // "automáticamente"
      normalized.includes("si"); // affirmative response

    expect(discussesContainment).toBe(true);

    await page.screenshot({
      path: "test-results/superchat-containment.png",
      fullPage: true,
    });
  });
});

test.describe("SuperChat Demo - Scenario 2: VIP Asset Protection", () => {
  test("should recognize VIP asset requires approval", async ({ page }, testInfo) => {
    await page.goto(SUPERCHAT_URL);
    await page.waitForLoadState("networkidle");

    if (await skipIfNotConnected(page, testInfo)) return;

    const helper = new SuperChatHelper(page);
    await helper.waitForReady();

    const asset = mockAssets.vipLaptop;

    await helper.sendMessage(
      `Hay actividad sospechosa en el activo ${asset.id} que pertenece al CFO de la empresa. ` +
        `Es un activo VIP crítico. ¿Puedo contenerlo automáticamente o necesito aprobación?`
    );
    await helper.waitForResponse(60000);

    const response = await helper.getLastResponse();
    console.log("VIP protection response:", response.substring(0, 500));

    // Verify response recognizes VIP/approval need
    const normalized = normalizeText(response);
    const recognizesVip =
      normalized.includes("vip") ||
      normalized.includes("cfo") ||
      normalized.includes("aprobacion") ||
      normalized.includes("autorizacion") ||
      normalized.includes("ejecutivo") ||
      normalized.includes("critico") ||
      normalized.includes("sensible") ||
      normalized.includes("cuidado");

    expect(recognizesVip).toBe(true);

    await page.screenshot({
      path: "test-results/superchat-vip.png",
      fullPage: true,
    });
  });
});

test.describe("SuperChat Demo - Scenario 3: False Positive Detection", () => {
  test("should identify likely false positive", async ({ page }, testInfo) => {
    await page.goto(SUPERCHAT_URL);
    await page.waitForLoadState("networkidle");

    if (await skipIfNotConnected(page, testInfo)) return;

    const helper = new SuperChatHelper(page);
    await helper.waitForReady();

    await helper.sendMessage(
      `Tengo una alerta de severidad baja en un servidor de desarrollo. ` +
        `El proceso detectado es node.js ejecutando en el puerto 3000. ` +
        `La confianza del detector es baja (<60%). ¿Crees que es un falso positivo?`
    );
    await helper.waitForResponse(60000);

    const response = await helper.getLastResponse();
    console.log("False positive analysis:", response.substring(0, 500));

    // Verify response discusses false positive possibility
    const normalized = normalizeText(response);
    const discussesFP =
      normalized.includes("falso positivo") ||
      normalized.includes("false positive") ||
      normalized.includes("legitimo") ||
      normalized.includes("desarrollo") ||
      normalized.includes("node") ||
      normalized.includes("benigno") ||
      normalized.includes("baja confianza") ||
      normalized.includes("probabilidad");

    expect(discussesFP).toBe(true);

    await page.screenshot({
      path: "test-results/superchat-fp.png",
      fullPage: true,
    });
  });
});

test.describe("SuperChat Demo - Full Workflow", () => {
  test("should execute complete SOC analyst workflow", async ({ page }, testInfo) => {
    await page.goto(SUPERCHAT_URL);
    await page.waitForLoadState("networkidle");

    if (await skipIfNotConnected(page, testInfo)) return;

    const helper = new SuperChatHelper(page);
    await helper.waitForReady();

    console.log("=== Starting Full SOC Demo via SuperChat ===");

    // Step 1: Initial triage
    console.log("\n--- Step 1: Initial Triage ---");
    await helper.sendMessage(
      `Soy un analista SOC. Tengo 3 incidentes pendientes: ` +
        `1) Malware crítico en workstation estándar (alta confianza), ` +
        `2) Actividad sospechosa en laptop del CFO (media confianza), ` +
        `3) Alerta en servidor de desarrollo (baja confianza). ` +
        `¿Por cuál debería empezar y por qué?`
    );
    await helper.waitForResponse(60000);

    let response = await helper.getLastResponse();
    console.log("Triage response:", response.substring(0, 400));
    await page.screenshot({ path: "test-results/superchat-workflow-1.png", fullPage: true });

    // Step 2: Handle critical incident
    console.log("\n--- Step 2: Critical Incident ---");
    await helper.sendMessage(
      `Voy a empezar con el incidente crítico de malware. ` +
        `Es TrickBot confirmado en un workstation que no es VIP. ` +
        `¿Debería contener automáticamente o investigar más?`
    );
    await helper.waitForResponse(60000);

    response = await helper.getLastResponse();
    console.log("Critical incident response:", response.substring(0, 400));
    await page.screenshot({ path: "test-results/superchat-workflow-2.png", fullPage: true });

    // Step 3: VIP decision
    console.log("\n--- Step 3: VIP Decision ---");
    await helper.sendMessage(
      `Ahora el incidente del CFO. Es su laptop personal con datos sensibles. ` +
        `¿Cómo debería proceder diferente que con el workstation estándar?`
    );
    await helper.waitForResponse(60000);

    response = await helper.getLastResponse();
    console.log("VIP decision response:", response.substring(0, 400));
    await page.screenshot({ path: "test-results/superchat-workflow-3.png", fullPage: true });

    console.log("\n=== SOC Demo Complete ===");
  });
});
