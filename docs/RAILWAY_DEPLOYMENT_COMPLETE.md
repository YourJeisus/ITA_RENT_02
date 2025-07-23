# 🚀 Полный деплой ITA_RENT_BOT на Railway

## 📋 Обзор

Этот гид поможет развернуть полную систему ITA_RENT_BOT на Railway с:

- 🗄️ PostgreSQL базой данных
- 🖥️ Backend API (FastAPI)
- 🌐 Frontend (React)
- 🤖 Автоматическим парсером каждые 6 часов

## 🏗️ Архитектура деплоя

```
Railway Project: ITA_RENT_BOT
├── 🗄️ postgres (PostgreSQL база данных)
├── 🖥️ backend (FastAPI API сервер)
├── 🌐 frontend (React приложение)
└── 🤖 scraper-worker (Автоматический парсинг каждые 6ч)
```

## 📋 Пошаговая инструкция

### 1️⃣ Подготовка к деплою

Убедитесь, что у вас есть:

- ✅ Аккаунт на [Railway.app](https://railway.app)
- ✅ ScraperAPI ключ с [scraperapi.com](https://scraperapi.com)
- ✅ Git репозиторий на GitHub

### 2️⃣ Создание проекта на Railway

1. Зайдите на [railway.app](https://railway.app) и войдите в аккаунт
2. Создайте новый проект: **"New Project"**
3. Выберите **"Deploy from GitHub repo"**
4. Выберите ваш репозиторий `ITA_RENT_02`

### 3️⃣ Добавление PostgreSQL базы данных

1. В вашем проекте нажмите **"+ Add Service"**
2. Выберите **"Database"** → **"PostgreSQL"**
3. Railway автоматически создаст базу данных
4. Скопируйте `DATABASE_URL` из переменных окружения PostgreSQL сервиса

### 4️⃣ Настройка Backend сервиса

Railway автоматически создаст backend сервис из `railway.toml`. Настройте переменные окружения:

**Обязательные переменные:**

```env
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key-change-me-12345
SCRAPERAPI_KEY=your-scraperapi-key-here
DATABASE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway
```

**Опциональные переменные:**

```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
STRIPE_SECRET_KEY=sk_live_...
SENTRY_DSN=https://your-sentry-dsn@sentry.io/...
```

### 5️⃣ Настройка Frontend сервиса

Frontend также создается автоматически. Настройте:

```env
NODE_ENV=production
VITE_API_URL=https://your-backend-url.railway.app
```

### 6️⃣ Настройка Scraper Worker

Воркер парсинга создается автоматически из `railway.toml`. Настройте:

```env
ENVIRONMENT=production
WORKER_TYPE=scraper
SCRAPERAPI_KEY=your-scraperapi-key-here
DATABASE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway
SCRAPER_WORKER_INTERVAL_HOURS=6
SCRAPER_WORKER_MAX_PAGES=10
```

## 🔧 Команды для локального деплоя

### Установка Railway CLI

```bash
# macOS
brew install railway

# Windows/Linux
npm install -g @railway/cli

# Вход в аккаунт
railway login
```

### Деплой всех сервисов

```bash
# Из корня проекта
railway up

# Или по отдельности
railway service connect backend
railway up

railway service connect frontend
railway up

railway service connect scraper-worker
railway up
```

## 📊 Мониторинг деплоя

### Проверка статуса сервисов

```bash
# Логи backend
railway logs --service backend

# Логи воркера парсинга
railway logs --service scraper-worker

# Логи frontend
railway logs --service frontend

# Статус всех сервисов
railway status
```

### Health Check endpoints

- **Backend API**: `https://your-backend.railway.app/health`
- **Frontend**: `https://your-frontend.railway.app/`
- **Database**: Проверяется автоматически через backend

## 🗄️ Управление базой данных

### Подключение к PostgreSQL

```bash
# Через Railway CLI
railway connect postgres

# Или напрямую с credentials из Railway Dashboard
psql postgresql://postgres:password@host:port/railway
```

### Миграции базы данных

```bash
# Railway автоматически запускает миграции при деплое backend
# Если нужно запустить вручную:
railway run --service backend alembic upgrade head
```

### Просмотр данных

```sql
-- Подключиться к БД и проверить таблицы
\dt

-- Посмотреть объявления
SELECT id, title, price, source, created_at
FROM listings
ORDER BY created_at DESC
LIMIT 10;

-- Статистика парсинга
SELECT source, COUNT(*) as count
FROM listings
GROUP BY source;
```

## 🤖 Автоматический парсинг

### Как работает

1. **Scraper Worker** запускается автоматически
2. Парсит каждые 6 часов (настраивается через `SCRAPER_WORKER_INTERVAL_HOURS`)
3. Сохраняет найденные объявления в PostgreSQL
4. Логирует все операции

### Настройка интервала

```env
# Каждые 6 часов (по умолчанию)
SCRAPER_WORKER_INTERVAL_HOURS=6

# Каждые 3 часа
SCRAPER_WORKER_INTERVAL_HOURS=3

# Каждые 12 часов
SCRAPER_WORKER_INTERVAL_HOURS=12
```

### Настройка объема парсинга

```env
# Парсить 10 страниц за раз (по умолчанию)
SCRAPER_WORKER_MAX_PAGES=10

# Парсить больше страниц (осторожно с лимитами ScraperAPI)
SCRAPER_WORKER_MAX_PAGES=20
```

### Мониторинг парсинга

```bash
# Логи воркера парсинга
railway logs --service scraper-worker --follow

# Поиск в логах
railway logs --service scraper-worker | grep "Парсинг завершен"

# Статистика парсинга из базы данных
railway connect postgres
SELECT DATE(created_at), COUNT(*)
FROM listings
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY DATE(created_at);
```

## 🔧 Troubleshooting

### Проблемы с базой данных

```bash
# Проверка подключения к БД
railway run --service backend python -c "
from src.db.database import test_database_connection
print('✅ Подключение OK' if test_database_connection() else '❌ Ошибка подключения')
"

# Создание таблиц вручную
railway run --service backend python -c "
from src.db.database import init_database
init_database()
"
```

### Проблемы с парсингом

```bash
# Тест парсинга вручную
railway run --service backend python src/parsers/run_scraping.py

# Проверка ScraperAPI ключа
railway run --service backend python -c "
from src.core.config import settings
print('ScraperAPI ключ:', '✅ настроен' if settings.SCRAPERAPI_KEY else '❌ НЕ настроен')
"
```

### Проблемы с воркером

```bash
# Перезапуск воркера
railway service restart scraper-worker

# Проверка переменных окружения воркера
railway variables --service scraper-worker
```

## 📈 Оптимизация для продакшена

### 1. Лимиты ресурсов

В Railway Dashboard установите лимиты:

- **Backend**: 512MB RAM, 0.5 vCPU
- **Frontend**: 256MB RAM, 0.25 vCPU
- **Scraper Worker**: 256MB RAM, 0.25 vCPU
- **PostgreSQL**: 512MB RAM, 0.5 vCPU

### 2. ScraperAPI лимиты

Следите за использованием ScraperAPI:

- **Free план**: 1,000 запросов/месяц
- **Startup план**: 10,000 запросов/месяц ($29)
- **Professional план**: 100,000 запросов/месяц ($99)

### 3. Автоматическое масштабирование

Railway автоматически масштабирует сервисы, но можно настроить:

- **Min instances**: 1 (всегда работает)
- **Max instances**: 3 (при высокой нагрузке)

### 4. Мониторинг и алерты

Настройте уведомления в Railway:

- При падении сервисов
- При превышении лимитов ресурсов
- При ошибках в логах

## 🎯 Результат

После успешного деплоя у вас будет:

✅ **Полностью автоматическая система парсинга недвижимости**

- Парсит Immobiliare.it каждые 6 часов
- Сохраняет все объявления в PostgreSQL
- Дедуплицирует повторные объявления
- Извлекает фотографии и геокоординаты

✅ **Современный веб-интерфейс**

- Поиск и фильтрация объявлений
- Интерактивные карты
- Аутентификация пользователей
- Адаптивный дизайн

✅ **Масштабируемая архитектура**

- Микросервисная структура
- Автоматические миграции БД
- Health checks для всех сервисов
- Логирование и мониторинг

## 🚀 Следующие шаги

1. **Добавить новые источники**: Idealista.it, Subito.it
2. **Telegram уведомления**: Интеграция с ботом
3. **Платная подписка**: Stripe интеграция
4. **Мобильное приложение**: React Native
5. **AI рекомендации**: Машинное обучение для предложений

---

**Создано**: Январь 2025  
**Автор**: AI Assistant  
**Версия**: 1.0
