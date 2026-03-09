import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@keyfiles": path.resolve(__dirname, "../Key Files"),
    },
  },
  server: {
    fs: {
      allow: [path.resolve(__dirname, "..")],
    },
    proxy: {
      "/neo4j-api": {
        target: "https://ac63a8e5.databases.neo4j.io",
        changeOrigin: true,
        secure: true,
        rewrite: (p) => p.replace(/^\/neo4j-api/, ""),
      },
    },
  },
});
