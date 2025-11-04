import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { fileURLToPath } from "url";

// Определяем __dirname для ES-модулей
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const resolvedAliasPath = path.resolve(__dirname, "./src");

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolvedAliasPath,
    },
  },
  define: {
    // Явно определяем переменные окружения для production
    "import.meta.env.VITE_API_URL": JSON.stringify(
      process.env.VITE_API_URL ||
        "https://itarent02back-production.up.railway.app/api/v1"
    ),
  },
  server: {
    port: 3000,
  },
  build: {
    outDir: "dist",
    assetsDir: "assets",
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          // Разделяем большие библиотеки на отдельные чанки для оптимизации
          vendor: ["react", "react-dom"],
          router: ["react-router-dom"],
          ui: ["@mui/material", "@mui/icons-material"],
          maps: ["leaflet", "react-leaflet"],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  base: "./", // Относительные пути для статического хостинга
});
