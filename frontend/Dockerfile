# Простой Dockerfile для Railway
FROM node:20-alpine

WORKDIR /app

# Копируем package files
COPY package*.json ./

# Установка всех зависимостей
RUN npm ci --verbose

# Копируем весь код
COPY . .

# Переменные окружения для сборки
ENV VITE_API_URL=https://itarent02back-production.up.railway.app
ENV NODE_ENV=production
ENV PORT=8080

# Сборка приложения
RUN npm run build

# Очистка dev зависимостей после сборки
RUN npm prune --omit=dev

# Открываем порт
EXPOSE 8080

# Запуск production сервера
CMD ["node", "server.js"] 