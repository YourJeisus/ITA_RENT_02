# Инструкции по деплою фронтенда ITA Rent Bot

## Готовые файлы для деплоя:

- ✅ `server.js` - Express сервер для продакшна
- ✅ `Dockerfile` - для деплоя через Docker
- ✅ `railway.toml` - конфигурация для Railway
- ✅ `vercel.json` - конфигурация для Vercel
- ✅ `api/index.js` - serverless функция для Vercel

## Варианты деплоя:

### 1. Railway (Рекомендуется)

```bash
# 1. Зайдите на railway.app
# 2. Подключите GitHub репозиторий
# 3. Выберите папку frontend
# 4. Railway автоматически определит настройки из railway.toml
# 5. Деплой произойдет автоматически
```

### 2. Render

```bash
# 1. Зайдите на render.com
# 2. Создайте новый Web Service
# 3. Подключите GitHub репозиторий
# 4. Настройки:
#    - Build Command: npm install && npm run build
#    - Start Command: npm start
#    - Root Directory: frontend
```

### 3. Heroku

```bash
# Из папки frontend выполните:
heroku create ita-rent-frontend
git init
git add .
git commit -m "Deploy frontend"
heroku git:remote -a ita-rent-frontend
git push heroku main
```

### 4. Vercel

```bash
# Из папки frontend выполните:
npx vercel --prod
# Или через веб-интерфейс vercel.com
```

### 5. Docker (любая платформа)

```bash
# Из папки frontend:
docker build -t ita-rent-frontend .
docker run -p 8080:8080 ita-rent-frontend
```

## Переменные окружения для продакшна:

```
PORT=8080
NODE_ENV=production
VITE_API_URL=https://your-backend-url.com
```

## Текущий статус:

- ✅ Локальное тестирование пройдено
- ✅ Express сервер работает корректно
- ✅ SPA маршрутизация настроена
- ✅ Оптимизация сборки включена
- ⏳ Ожидаем доступности Endgame для автоматического деплоя

## URL для тестирования после деплоя:

После успешного деплоя проверьте:

- `/` - главная страница
- `/search` - страница поиска
- `/filters` - страница фильтров
- `/map` - страница карты

Все маршруты должны корректно загружаться без ошибок 404.
