import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

// Получаем __dirname для ES модулей
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// Порт из переменной окружения или 8080 по умолчанию (как требует Endgame)
const PORT = process.env.PORT || 8080;

// Раздача статических файлов из папки dist
app.use(express.static(path.join(__dirname, 'dist')));

// Все остальные запросы отправляем на index.html (для SPA маршрутизации)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

export default app;
