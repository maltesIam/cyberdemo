import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "jsdom",
    include: [
      "tests/**/*.spec.ts",
      "tests/**/*.spec.tsx",
      "tests/**/*.test.ts",
      "tests/**/*.test.tsx",
    ],
    exclude: [
      "tests/**/*.e2e.spec.ts",
      "tests/e2e/**",
      "tests/graph.spec.ts",
      "tests/enrichment.spec.ts",
    ],
    setupFiles: ["./tests/setup.ts"],
  },
});
