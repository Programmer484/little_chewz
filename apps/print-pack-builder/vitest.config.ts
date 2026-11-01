import { defineConfig } from "vitest/config";

// Tests run in Node against the same modules the browser and Worker use.
export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts"],
    environment: "node",
  },
});
