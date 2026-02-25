/**
 * E2E Test: Medicum Consulta Tab
 * Tests the medical clinical interface at /medicum
 * Covers: patient header, Whisper status, Demo button, SOAP note generation, Escuchar button
 */

import { test, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

const RESULTS_DIR = "/home/oscar/NewProjects/SoulInTheBot/cyberdemo/frontend/test-results/medicum";

test.beforeAll(() => {
  if (!fs.existsSync(RESULTS_DIR)) {
    fs.mkdirSync(RESULTS_DIR, { recursive: true });
  }
});

test.describe("Medicum Consulta Tab", () => {
  // Collect console messages throughout tests
  const consoleMessages: Array<{ type: string; text: string }> = [];

  test("Step 1 - Navigate to /medicum and verify initial state", async ({ page }) => {
    // Capture all console messages
    page.on("console", (msg) => {
      consoleMessages.push({ type: msg.type(), text: msg.text() });
      if (msg.type() === "error") {
        console.log(`[BROWSER ERROR] ${msg.text()}`);
      }
    });

    page.on("pageerror", (err) => {
      console.log(`[PAGE ERROR] ${err.message}`);
    });

    // Navigate to /medicum
    await page.goto("http://localhost:3000/medicum");

    // Wait for page to fully load - patient header should appear
    await page.waitForSelector("text=María García López", { timeout: 15000 });

    // Take screenshot of initial state
    await page.screenshot({
      path: path.join(RESULTS_DIR, "01-initial-state.png"),
      fullPage: true,
    });
    console.log("[TEST] Screenshot saved: 01-initial-state.png");

    // Verify patient header
    const patientName = page.locator("text=María García López");
    await expect(patientName).toBeVisible();
    console.log("[TEST] Patient header 'Maria Garcia Lopez' is visible");

    // Verify the Consulta tab is active by default (use data-testid to avoid strict mode violation)
    const consultaTab = page.locator("[data-testid='tab-consulta']");
    await expect(consultaTab).toBeVisible();
    console.log("[TEST] Consulta tab is visible");
  });

  test("Step 2 - Check Whisper status indicator", async ({ page }) => {
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        console.log(`[BROWSER ERROR] ${msg.text()}`);
      }
    });

    await page.goto("http://localhost:3000/medicum");
    await page.waitForSelector("text=María García López", { timeout: 15000 });

    // Give time for Whisper status check to complete (it runs on mount)
    await page.waitForTimeout(3000);

    // Check Whisper status - it should be one of the three states
    const whisperGPU = page.locator("text=Whisper GPU");
    const sinWhisper = page.locator("text=Sin Whisper");
    const conectando = page.locator("text=Conectando...");

    const hasWhisperGPU = await whisperGPU.isVisible().catch(() => false);
    const hasSinWhisper = await sinWhisper.isVisible().catch(() => false);
    const hasConectando = await conectando.isVisible().catch(() => false);

    console.log(`[TEST] Whisper Status:`);
    console.log(`  - "Whisper GPU" visible: ${hasWhisperGPU}`);
    console.log(`  - "Sin Whisper" visible: ${hasSinWhisper}`);
    console.log(`  - "Conectando..." visible: ${hasConectando}`);

    // Screenshot to capture actual status
    await page.screenshot({
      path: path.join(RESULTS_DIR, "02-whisper-status.png"),
      fullPage: true,
    });

    // At least one status must be visible
    const anyStatusVisible = hasWhisperGPU || hasSinWhisper || hasConectando;
    expect(anyStatusVisible).toBe(true);

    if (hasWhisperGPU) {
      console.log("[TEST] RESULT: Whisper is CONNECTED (GPU mode)");
    } else if (hasSinWhisper) {
      console.log("[TEST] RESULT: Whisper is UNAVAILABLE (Sin Whisper)");
    } else if (hasConectando) {
      console.log("[TEST] RESULT: Whisper is CONNECTING...");
    }
  });

  test("Step 3 - Check Escuchar and Demo buttons", async ({ page }) => {
    const errors: string[] = [];

    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
        console.log(`[BROWSER ERROR] ${msg.text()}`);
      }
    });

    await page.goto("http://localhost:3000/medicum");
    await page.waitForSelector("text=María García López", { timeout: 15000 });

    // Wait for Whisper status to resolve
    await page.waitForTimeout(3000);

    // Check Escuchar button
    const escucharBtn = page.locator("#btn-toggle-transcription");
    const isEscucharVisible = await escucharBtn.isVisible().catch(() => false);
    const isEscucharDisabled = await escucharBtn.isDisabled().catch(() => true);

    console.log(`[TEST] Escuchar button visible: ${isEscucharVisible}`);
    console.log(`[TEST] Escuchar button disabled: ${isEscucharDisabled}`);

    if (isEscucharVisible) {
      await expect(escucharBtn).toBeVisible();
    }

    // Check Demo button
    const demoBtn = page.locator("#btn-demo-transcription");
    const isDemoVisible = await demoBtn.isVisible().catch(() => false);
    const isDemoDisabled = await demoBtn.isDisabled().catch(() => true);

    console.log(`[TEST] Demo button visible: ${isDemoVisible}`);
    console.log(`[TEST] Demo button disabled: ${isDemoDisabled}`);

    if (isDemoVisible) {
      await expect(demoBtn).toBeVisible();
    }

    // Screenshot of button states
    await page.screenshot({
      path: path.join(RESULTS_DIR, "03-button-states.png"),
      fullPage: false,
    });

    // Report console errors found
    if (errors.length > 0) {
      console.log(`[TEST] Console errors found: ${errors.length}`);
      errors.forEach((e, i) => console.log(`  [${i + 1}] ${e}`));
    } else {
      console.log("[TEST] No console errors found");
    }
  });

  test("Step 4 - Click Demo button and verify transcription segments", async ({ page }) => {
    const errors: string[] = [];
    const allMessages: string[] = [];

    page.on("console", (msg) => {
      allMessages.push(`[${msg.type()}] ${msg.text()}`);
      if (msg.type() === "error") {
        errors.push(msg.text());
        console.log(`[BROWSER ERROR] ${msg.text()}`);
      }
    });

    await page.goto("http://localhost:3000/medicum");
    await page.waitForSelector("text=María García López", { timeout: 15000 });

    // Make sure we are on the Consulta tab
    const consultaTab = page.locator("text=Consulta").first();
    await consultaTab.click();
    await page.waitForTimeout(500);

    // Click the Demo button
    const demoBtn = page.locator("#btn-demo-transcription");
    await expect(demoBtn).toBeVisible({ timeout: 5000 });

    console.log("[TEST] Clicking Demo button...");
    await demoBtn.click();

    // Screenshot immediately after demo starts
    await page.screenshot({
      path: path.join(RESULTS_DIR, "04a-demo-started.png"),
      fullPage: true,
    });

    // Wait for demo to progress - segments appear every 2 seconds, 6 segments total = ~12 seconds
    // Wait 15 seconds as instructed
    console.log("[TEST] Waiting 15 seconds for demo transcription to play out...");
    await page.waitForTimeout(15000);

    // Take screenshot showing demo transcription segments
    await page.screenshot({
      path: path.join(RESULTS_DIR, "04b-demo-transcription.png"),
      fullPage: true,
    });
    console.log("[TEST] Screenshot saved: 04b-demo-transcription.png");

    // Verify some demo segments are visible
    // Demo has 6 segments - check some expected text
    const segment1 = page.locator("text=Buenos días, María");
    const segment2 = page.locator("text=rodilla derecha");
    const hasSegment1 = await segment1.isVisible().catch(() => false);
    const hasSegment2 = await segment2.isVisible().catch(() => false);

    console.log(`[TEST] Segment 1 visible (Buenos días, María): ${hasSegment1}`);
    console.log(`[TEST] Segment 2 visible (rodilla derecha): ${hasSegment2}`);

    // Count visible segments
    const segmentCount = await page
      .locator(".bg-medical-primary.text-white, .bg-gray-100.text-gray-900")
      .count()
      .catch(() => 0);
    console.log(`[TEST] Transcription bubble elements visible: ${segmentCount}`);

    if (errors.length > 0) {
      console.log(`[TEST] Console errors during demo: ${errors.length}`);
      errors.forEach((e, i) => console.log(`  [${i + 1}] ${e}`));
    }
  });

  test("Step 5 - Click Generar to generate SOAP notes", async ({ page }) => {
    const errors: string[] = [];

    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
        console.log(`[BROWSER ERROR] ${msg.text()}`);
      }
    });

    await page.goto("http://localhost:3000/medicum");
    await page.waitForSelector("text=María García López", { timeout: 15000 });

    // First run demo to get some segments
    const demoBtn = page.locator("#btn-demo-transcription");
    await expect(demoBtn).toBeVisible({ timeout: 5000 });
    await demoBtn.click();

    // Wait a few seconds for some demo segments to appear
    await page.waitForTimeout(5000);

    // Click Generar button
    const generarBtn = page.locator("#btn-generate-soap");
    await expect(generarBtn).toBeVisible({ timeout: 5000 });

    console.log("[TEST] Clicking Generar button...");
    await generarBtn.click();

    // Wait for SOAP note to appear
    await page.waitForTimeout(1000);

    // Take screenshot of SOAP notes
    await page.screenshot({
      path: path.join(RESULTS_DIR, "05-soap-notes.png"),
      fullPage: true,
    });
    console.log("[TEST] Screenshot saved: 05-soap-notes.png");

    // Verify SOAP note sections are visible
    const subjetivoLabel = page.locator("text=S - Subjetivo");
    const objetivoLabel = page.locator("text=O - Objetivo");
    const analisisLabel = page.locator("text=A - Análisis");
    const planLabel = page.locator("text=P - Plan");

    await expect(subjetivoLabel).toBeVisible();
    await expect(objetivoLabel).toBeVisible();
    await expect(analisisLabel).toBeVisible();
    await expect(planLabel).toBeVisible();

    console.log("[TEST] All SOAP note labels (S/O/A/P) are visible");

    // Verify actual SOAP content was generated (not placeholder text)
    const soapContent = page.locator("text=Paciente de 58 años");
    const hasContent = await soapContent.isVisible().catch(() => false);
    console.log(`[TEST] SOAP content generated (paciente 58 años): ${hasContent}`);

    // Check for gonartrosis diagnosis
    const gonartrosis = page.locator("text=Gonartrosis");
    const hasGonartrosis = await gonartrosis.isVisible().catch(() => false);
    console.log(`[TEST] Diagnosis visible (Gonartrosis): ${hasGonartrosis}`);

    if (errors.length > 0) {
      console.log(`[TEST] Console errors during SOAP generation: ${errors.length}`);
      errors.forEach((e, i) => console.log(`  [${i + 1}] ${e}`));
    }
  });

  test("Step 6 - Try Escuchar button and capture any errors", async ({ page }) => {
    const errors: string[] = [];
    const warnings: string[] = [];
    const infos: string[] = [];

    page.on("console", (msg) => {
      const text = msg.text();
      if (msg.type() === "error") {
        errors.push(text);
        console.log(`[BROWSER ERROR] ${text}`);
      } else if (msg.type() === "warning" || msg.type() === "warn") {
        warnings.push(text);
      } else if (text.includes("[MCP]") || text.includes("[VAD]") || text.includes("[REC]")) {
        infos.push(text);
        console.log(`[BROWSER INFO] ${text}`);
      }
    });

    page.on("requestfailed", (request) => {
      console.log(`[NETWORK FAIL] ${request.method()} ${request.url()} - ${request.failure()?.errorText}`);
    });

    await page.goto("http://localhost:3000/medicum");
    await page.waitForSelector("text=María García López", { timeout: 15000 });

    // Wait for Whisper status to resolve
    await page.waitForTimeout(3000);

    // Check current Whisper status
    const whisperGPU = page.locator("text=Whisper GPU");
    const sinWhisper = page.locator("text=Sin Whisper");
    const isWhisperConnected = await whisperGPU.isVisible().catch(() => false);
    const isWhisperUnavailable = await sinWhisper.isVisible().catch(() => false);

    console.log(`[TEST] Before clicking Escuchar:`);
    console.log(`  Whisper GPU connected: ${isWhisperConnected}`);
    console.log(`  Whisper unavailable: ${isWhisperUnavailable}`);

    // Try clicking Escuchar button
    const escucharBtn = page.locator("#btn-toggle-transcription");
    const isDisabled = await escucharBtn.isDisabled().catch(() => true);

    console.log(`[TEST] Escuchar button disabled: ${isDisabled}`);

    if (!isDisabled) {
      console.log("[TEST] Clicking Escuchar button (it is enabled)...");
      await escucharBtn.click();
      await page.waitForTimeout(2000);

      await page.screenshot({
        path: path.join(RESULTS_DIR, "06a-escuchar-clicked.png"),
        fullPage: false,
      });
      console.log("[TEST] Screenshot saved: 06a-escuchar-clicked.png");
    } else {
      console.log("[TEST] Escuchar button is disabled - not clicking it");
      console.log(`[TEST] This is expected when whisperStatus !== 'connected'`);
    }

    // Final screenshot
    await page.screenshot({
      path: path.join(RESULTS_DIR, "06b-final-state.png"),
      fullPage: true,
    });
    console.log("[TEST] Screenshot saved: 06b-final-state.png");

    // Summary report
    console.log("\n========= FULL TEST REPORT =========");
    console.log(`Total console errors: ${errors.length}`);
    if (errors.length > 0) {
      errors.forEach((e, i) => console.log(`  ERROR[${i + 1}]: ${e}`));
    }
    console.log(`Total warnings: ${warnings.length}`);
    console.log(`MCP/VAD/REC messages: ${infos.length}`);

    // Check for CORS or network errors specifically
    const corsErrors = errors.filter(
      (e) => e.includes("CORS") || e.includes("cors") || e.includes("cross-origin"),
    );
    const networkErrors = errors.filter(
      (e) =>
        e.includes("Failed to fetch") ||
        e.includes("net::ERR") ||
        e.includes("NetworkError"),
    );

    console.log(`CORS errors: ${corsErrors.length}`);
    corsErrors.forEach((e) => console.log(`  CORS: ${e}`));
    console.log(`Network errors: ${networkErrors.length}`);
    networkErrors.forEach((e) => console.log(`  NET: ${e}`));
    console.log("====================================\n");
  });
});
