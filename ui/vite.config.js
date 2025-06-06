import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 4000,
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: "http://173.249.7.24:8011",
        changeOrigin: true,
      },
    },
  },
});
