# 🚀 Быстрый старт - Деплой на Railway

## ⚡ Автоматический деплой (рекомендуется)

### 1. Подготовка

```bash
# 1. Установите Railway CLI
npm install -g @railway/cli

# 2. Авторизуйтесь в Railway
railway login

# 3. Получите ScraperAPI ключ на https://scraperapi.com
export SCRAPERAPI_KEY="your-scraperapi-key-here"

# 4. (Опционально) Установите SECRET_KEY
export SECRET_KEY="your-super-secret-key"
```

### 2. Деплой одной командой

```bash
./deploy_railway.sh
```

**Это всё!** Скрипт автоматически:

- ✅ Создаст PostgreSQL базу данных
- ✅ Развернет Backend API
- ✅ Развернет Frontend
- ✅ Запустит автоматический парсер (каждые 6 часов)
- ✅ Настроит все переменные окружения

---

## 🔧 Ручной деплой

### 1. Создание проекта на Railway

1. Зайдите на [railway.app](https://railway.app)
2. Создайте новый проект из GitHub репозитория
3. Добавьте PostgreSQL базу данных

### 2. Настройка переменных окружения

**Backend сервис:**

```env
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key
SCRAPERAPI_KEY=your-scraperapi-key
```

**Scraper Worker сервис:**

```env
WORKER_TYPE=scraper
ENVIRONMENT=production
SCRAPERAPI_KEY=your-scraperapi-key
SCRAPER_WORKER_INTERVAL_HOURS=6
```

**Frontend сервис:**

```env
NODE_ENV=production
VITE_API_URL=https://your-backend-url.railway.app
```

### 3. Деплой

```bash
railway up
```

---

## 📊 Проверка деплоя

### Логи сервисов

```bash
# Backend логи
railway logs --service backend

# Воркер парсинга логи
railway logs --service scraper-worker

# Frontend логи
railway logs --service frontend
```

### Health checks

- **Backend**: `https://your-backend.railway.app/health`
- **Frontend**: `https://your-frontend.railway.app/`

### База данных

```bash
# Подключение к PostgreSQL
railway connect postgres

# Проверка объявлений
SELECT COUNT(*) FROM listings;
```

---

## 🤖 Автоматический парсинг

Воркер парсинга автоматически:

- 🕕 Запускается каждые 6 часов
- 📄 Парсит 10 страниц Immobiliare.it
- 💾 Сохраняет объявления в PostgreSQL
- 🔄 Дедуплицирует повторы
- 📸 Извлекает все фотографии
- 🗺️ Добавляет геокоординаты

### Мониторинг парсинга

```bash
# Следить за логами парсинга
railway logs --service scraper-worker --follow

# Проверка последних объявлений
railway connect postgres
SELECT title, price, created_at FROM listings ORDER BY created_at DESC LIMIT 5;
```

---

## 🔧 Настройка

### Изменить интервал парсинга

```bash
# Каждые 3 часа
railway variables set SCRAPER_WORKER_INTERVAL_HOURS=3

# Каждые 12 часов
railway variables set SCRAPER_WORKER_INTERVAL_HOURS=12
```

### Изменить объем парсинга

```bash
# Парсить 20 страниц (больше данных)
railway variables set SCRAPER_WORKER_MAX_PAGES=20

# Парсить 5 страниц (экономия ScraperAPI)
railway variables set SCRAPER_WORKER_MAX_PAGES=5
```

---

## 🎯 Результат

После деплоя у вас будет:

✅ **Полностью автоматическая система** парсинга недвижимости  
✅ **PostgreSQL база данных** с объявлениями  
✅ **Современный веб-интерфейс** для поиска  
✅ **Автоматический парсер** каждые 6 часов  
✅ **Масштабируемая архитектура** на Railway

---

## 📖 Подробная документация

Полная документация: [docs/RAILWAY_DEPLOYMENT_COMPLETE.md](docs/RAILWAY_DEPLOYMENT_COMPLETE.md)
