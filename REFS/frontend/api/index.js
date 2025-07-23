import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// Раздача статических файлов из папки dist
app.use(express.static(path.join(__dirname, '../dist')));

// Все остальные запросы отправляем на index.html (для SPA маршрутизации)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../dist', 'index.html'));
});

export default app;
