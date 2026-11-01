import { cloudflare } from "@cloudflare/vite-plugin";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// One deployment: the React app is built to static assets and the Worker in
// worker/index.ts serves /api/*. See wrangler.jsonc.
export default defineConfig({
  plugins: [react(), cloudflare()],
});
