import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  timeout: 60000, // Increase test timeout to 60s
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["json", { outputFile: "test-results.json" }],
    ["list"],
  ],
  use: {
    baseURL: process.env.FRONTEND_URL || "http://localhost:3003",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    actionTimeout: 15000, // Increase action timeout to 15s
    navigationTimeout: 30000, // Increase navigation timeout to 30s
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  // webServer disabled - start services manually with ./start.sh
});
