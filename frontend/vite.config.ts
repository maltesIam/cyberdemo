import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

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
      },
      "/vulnerabilities": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/assets": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/surface": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/graph": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/agent": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/gen": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/postmortems": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/tickets": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/agent-actions": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/dashboard": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/audit": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/config": {
        target: "http://localhost:8000",
        changeOrigin: true,
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
