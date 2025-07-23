import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import process from "process";

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

// Раздача статических файлов из папки dist
app.use(express.static(path.join(__dirname, "dist")));

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// Все остальные запросы отправляем на index.html (для SPA маршрутизации)
app.get("*", (req, res) => {
  const indexPath = path.join(__dirname, "dist", "index.html");
  console.log("Serving index.html from:", indexPath);
  res.sendFile(indexPath);
});

app.listen(PORT, HOST, () => {
  console.log(`Server is running on http://${HOST}:${PORT}`);
  console.log("Ready to accept connections");
});

export default app;
