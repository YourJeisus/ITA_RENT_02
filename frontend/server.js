import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import process from "process";
import http from "http";

// Получаем __dirname для ES модулей
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// Порт из переменной окружения или 8080 по умолчанию
const PORT = process.env.PORT || 8080;
const HOST = "0.0.0.0"; // Принимаем соединения со всех интерфейсов

console.log("Starting server...");
console.log("Environment:", {
  NODE_ENV: process.env.NODE_ENV,
  PORT: PORT,
  __dirname: __dirname,
});

// Проверяем существование папки dist
const distPath = path.join(__dirname, "dist");
console.log("Checking dist folder:", distPath);
console.log("Dist folder exists:", fs.existsSync(distPath));

if (fs.existsSync(distPath)) {
  const distFiles = fs.readdirSync(distPath);
  console.log("Files in dist:", distFiles);
}

// Добавляем middleware для логирования запросов
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  next();
});

// 🔴 ВАЖНО: Проксируем API запросы на backend ДО статических файлов!
app.use("/api", (req, res) => {
  const backendUrl = "http://localhost:8000";
  // ВАЖНО: Добавляем /api перед путем потому что express.Router удаляет его
  const fullPath = `/api${req.url}`;
  
  console.log(`🔗 Проксирую запрос: ${req.method} ${req.url} -> ${fullPath}`);
  
  const options = {
    hostname: "localhost",
    port: 8000,
    path: fullPath,
    method: req.method,
    headers: req.headers,
  };
  
  // Удаляем host header чтобы не было конфликтов
  delete options.headers.host;
  
  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });
  
  proxyReq.on("error", (err) => {
    console.error("❌ Proxy error:", err);
    res.status(503).json({ error: "Backend unavailable", details: err.message });
  });
  
  req.pipe(proxyReq);
});

// Root endpoint для быстрой проверки
app.get("/", (req, res) => {
  try {
    const indexPath = path.join(__dirname, "dist", "index.html");
    console.log("Serving root from:", indexPath);

    if (!fs.existsSync(indexPath)) {
      console.error("index.html not found at:", indexPath);
      return res.status(404).json({ error: "index.html not found" });
    }

    res.sendFile(indexPath);
  } catch (error) {
    console.error("Error serving root:", error);
    res
      .status(500)
      .json({ error: "Error serving root", message: error.message });
  }
});

// Health check endpoint
app.get("/health", (req, res) => {
  console.log("Health check requested");
  res.json({
    status: "ok",
    timestamp: new Date().toISOString(),
    env: process.env.NODE_ENV,
    port: PORT,
    distExists: fs.existsSync(distPath),
  });
});

// Test endpoint
app.get("/test", (req, res) => {
  res.json({
    message: "Server is working!",
    timestamp: new Date().toISOString(),
  });
});

// Раздача статических файлов из папки dist
app.use(
  express.static(path.join(__dirname, "dist"), {
    fallthrough: true,
    maxAge: "1d",
  })
);

// Все остальные запросы отправляем на index.html (для SPA маршрутизации)
app.get("*", (req, res) => {
  try {
    const indexPath = path.join(__dirname, "dist", "index.html");
    console.log("Serving SPA route from:", indexPath);

    if (!fs.existsSync(indexPath)) {
      console.error("index.html not found for SPA route:", indexPath);
      return res.status(404).json({ error: "index.html not found" });
    }

    res.sendFile(indexPath);
  } catch (error) {
    console.error("Error serving SPA route:", error);
    res
      .status(500)
      .json({ error: "Error serving SPA route", message: error.message });
  }
});

// Добавляем middleware для обработки ошибок Express (ДОЛЖЕН БЫТЬ В КОНЦЕ)
app.use((err, req, res, next) => {
  console.error("Express error:", err);
  res
    .status(500)
    .json({ error: "Internal server error", message: err.message });
});

// Обработка uncaught exceptions
process.on("uncaughtException", (err) => {
  console.error("Uncaught Exception:", err);
});

process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
});

const server = app.listen(PORT, HOST, () => {
  console.log(`Server is running on http://${HOST}:${PORT}`);
  console.log("Ready to accept connections");
});

// Graceful shutdown
process.on("SIGTERM", () => {
  console.log("SIGTERM received, shutting down gracefully");
  server.close(() => {
    console.log("Process terminated");
  });
});

export default app;
