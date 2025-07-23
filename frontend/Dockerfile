# Простой Dockerfile для frontend (MVP)
FROM node:18-alpine

# Рабочая директория
WORKDIR /app

# Копирование package files
COPY package*.json ./

# Установка зависимостей
RUN npm ci

# Копирование исходного кода
COPY . .

# Переменные окружения
ENV NODE_ENV=development

# Порт по умолчанию
EXPOSE 5173

# Команда запуска для разработки
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 