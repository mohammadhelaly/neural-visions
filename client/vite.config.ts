import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";

const usePolling = process.env.VITE_USE_POLLING === "true";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    svgr({
      // svgr options: https://react-svgr.com/docs/options/
      svgrOptions: {
        exportType: "default",
        ref: true,
        svgo: false,
        titleProp: true,
      },
      include: "**/*.svg",
    }),
  ],
  server: {
    port: 3000,
    watch: usePolling
      ? {
          usePolling: true,
          interval: 300,
        }
      : undefined,
  },
  resolve: {
    alias: {
      "@": "/src",
    },
  },
});
