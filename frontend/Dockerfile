# Многоэтапная сборка для Railway
FROM node:20-alpine as builder

WORKDIR /app

# Копируем package files
COPY package*.json ./
RUN npm ci

# Копируем весь код
COPY . .

# Переменные окружения для сборки
ENV VITE_API_URL=https://itarent02back-production.up.railway.app

# Сборка приложения
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Копируем package.json для production зависимостей
COPY package*.json ./
RUN npm ci --only=production

# Копируем собранное приложение
COPY --from=builder /app/dist ./dist
COPY server.js ./

# Переменные окружения
ENV NODE_ENV=production
ENV PORT=8080

# Открываем порт
EXPOSE 8080

# Запуск production сервера
CMD ["node", "server.js"] 