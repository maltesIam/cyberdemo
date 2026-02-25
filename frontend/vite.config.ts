import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import type { IncomingMessage } from "http";

/**
 * Bypass proxy for browser page navigation (SPA fallback).
 * When the browser requests text/html, let Vite serve index.html.
 * When JS code fetches JSON data, proxy to the backend.
 */
function bypassForHtml(req: IncomingMessage) {
  if (req.headers.accept?.includes("text/html")) {
    return "/index.html";
  }
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/mcp": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/health": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/narration": {
        target: "http://localhost:8000",
        changeOrigin: true,
        ws: true,
      },
      "/aip-assist": {
        target: "http://localhost:8000",
        changeOrigin: true,
        ws: true,
      },
      "/mitre": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/siem": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/edr": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/demo": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/threats": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass: bypassForHtml,
      },
      "/vulnerabilities": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass: bypassForHtml,
      },
      "/assets": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass: bypassForHtml,
      },
      "/surface": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass: bypassForHtml,
      },
      "/graph": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass: bypassForHtml,
      },
      "/agent": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/gen": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass: bypassForHtml,
      },
      "/postmortems": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass: bypassForHtml,
      },
      "/tickets": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass: bypassForHtml,
      },
      "/agent-actions": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/dashboard": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass: bypassForHtml,
      },
      "/audit": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass: bypassForHtml,
      },
      "/config": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass: bypassForHtml,
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    include: ["tests/**/*.test.{ts,tsx}", "tests/**/*.spec.tsx"],
    exclude: ["tests/**/*.spec.ts"], // Exclude Playwright E2E tests
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.d.ts", "src/main.tsx", "src/vite-env.d.ts"],
    },
  },
});
