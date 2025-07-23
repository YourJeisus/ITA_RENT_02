# Dockerfile для production
FROM node:18-alpine

# Рабочая директория
WORKDIR /app

# Копирование package files
COPY package*.json ./

# Установка всех зависимостей (включая dev для сборки)
RUN npm ci

# Копирование исходного кода
COPY . .

# Сборка проекта
RUN npm run build

# Удаление dev зависимостей для уменьшения размера
RUN npm prune --production

# Переменные окружения для production
ENV NODE_ENV=production
ENV PORT=8080

# Порт для Railway
EXPOSE 8080

# Команда запуска production сервера
CMD ["npm", "start"] 