import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    reporter: "default",
    setupFiles: ["./vitest.setup.ts"],
  },
});
