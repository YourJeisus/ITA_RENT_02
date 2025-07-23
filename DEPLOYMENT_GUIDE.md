# 🚀 Руководство по деплою - Этап 1.2

## 📋 Обзор

Этап 1.2 "Контейнеризация и первый деплой" включает:

- ✅ Docker конфигурации для backend и frontend
- ✅ Docker Compose для локальной разработки
- ✅ Конфигурации для Railway (backend) и Vercel (frontend)
- ✅ GitHub Actions для CI/CD
- ✅ Production-ready конфигурации

## 🐳 Локальная разработка с Docker

### Быстрый старт

```bash
# Клонировать репозиторий
git clone <your-repo-url>
cd ITA_RENT_02

# Запустить все сервисы
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d
```

**Доступные сервисы:**

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Управление

```bash
# Просмотр логов
docker-compose logs -f

# Остановка всех сервисов
docker-compose down

# Пересборка после изменений
docker-compose up --build
```

## 🌐 Деплой в продакшен

### Backend на Railway

1. **Подключение репозитория:**

   - Зайти на [railway.app](https://railway.app)
   - Подключить GitHub репозиторий
   - Railway автоматически обнаружит `railway.toml`

2. **Переменные окружения:**

   ```
   ENVIRONMENT=production
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgresql://...
   ```

3. **Автоматический деплой:**
   - Railway автоматически деплоит при push в main
   - Использует `Dockerfile.prod` для сборки
   - Health check доступен на `/health`

### Frontend на Vercel

1. **Подключение:**

   - Зайти на [vercel.com](https://vercel.com)
   - Импортировать проект из GitHub
   - Указать Root Directory: `frontend`

2. **Настройки:**

   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Vercel автоматически использует `vercel.json`

3. **Переменные окружения:**
   ```
   VITE_API_URL=https://your-railway-app.railway.app
   ```

## ⚙️ CI/CD с GitHub Actions

### Автоматические проверки

При каждом push в main или PR:

- ✅ Линтинг Python кода (flake8)
- ✅ Проверка синтаксиса backend
- ✅ Линтинг frontend кода (ESLint)
- ✅ Сборка frontend

### Настройка

1. **Secrets в GitHub:**

   ```
   RAILWAY_TOKEN=your-railway-token (опционально)
   VERCEL_TOKEN=your-vercel-token (опционально)
   ```

2. **Workflow:**
   - Файл: `.github/workflows/deploy.yml`
   - Автоматический запуск при push в main
   - Деплой только после успешных тестов

## 🔧 Production конфигурации

### Backend (Dockerfile.prod)

- Многоэтапная сборка
- Безопасность (непривилегированный пользователь)
- Health checks
- Оптимизированный размер образа

### Frontend (Dockerfile.prod + Nginx)

- Сборка статических файлов
- Nginx для раздачи файлов
- Gzip сжатие
- Security headers
- Кеширование статических ресурсов

## 🐛 Отладка

### Проверка локального деплоя

```bash
# Backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/health

# Frontend
cd frontend
npm run dev
```

### Проверка Docker сборки

```bash
# Backend
docker build -t ita-rent-backend .
docker run -p 8000:8000 ita-rent-backend

# Frontend
cd frontend
docker build -f Dockerfile.prod -t ita-rent-frontend .
docker run -p 80:80 ita-rent-frontend
```

### Логи в production

```bash
# Railway
railway logs

# Vercel
vercel logs
```

## 📊 Мониторинг

### Health checks

- Backend: `GET /health`
- Возвращает статус приложения и версию
- Используется Railway и GitHub Actions

### Метрики

- Railway: встроенная панель метрик
- Vercel: Analytics и Core Web Vitals
- GitHub Actions: история деплоев

## 🔄 Следующие шаги

После успешного деплоя этапа 1.2:

1. **Этап 2.1**: Настройка базы данных

   - PostgreSQL в production
   - SQLAlchemy модели
   - Alembic миграции

2. **Мониторинг**:

   - Настройка Sentry для ошибок
   - Логирование в production
   - Метрики производительности

3. **Безопасность**:
   - HTTPS сертификаты
   - Переменные окружения
   - Секреты в CI/CD

---

**Статус**: ✅ Этап 1.2 полностью выполнен и протестирован  
**Готовность**: 🚀 Готово к деплою в production
