import path from "node:path";
import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => ({
  resolve: {
    tsconfigPaths: true,
  },
  plugins: [react()],
  test: {
    environment: "jsdom",
    env: loadEnv(mode, path.resolve(process.cwd(), ".."), ""), // to load .env from the root folder
  },
}));
