import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  test: {
    globals: true,
    environment: "jsdom",
    include: [
      "frontend/tests/**/*.spec.ts",
      "frontend/tests/**/*.spec.tsx",
      "frontend/tests/**/*.test.ts",
      "frontend/tests/**/*.test.tsx",
    ],
    exclude: [
      "frontend/tests/**/*.e2e.spec.ts",
      "frontend/tests/e2e/**",
      "frontend/tests/graph.spec.ts",
      "frontend/tests/enrichment.spec.ts",
    ],
    setupFiles: [path.resolve(__dirname, "frontend/tests/setup.ts")],
    deps: {
      optimizer: {
        web: {
          include: ["@testing-library/jest-dom"],
        },
      },
    },
  },
  resolve: {
    alias: {
      "~": path.resolve(__dirname, "frontend/src"),
    },
  },
});
