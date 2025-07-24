# 🚀 Инструкции по деплою ITA_RENT_BOT на Railway

## ✅ Готово к деплою!

Все компоненты протестированы и готовы к production деплою:

- ✅ API сервер
- ✅ Telegram бот
- ✅ Система уведомлений
- ✅ База данных

## 🚀 ПОШАГОВОЕ СОЗДАНИЕ СЕРВИСОВ В RAILWAY

### ШАГ 1: Создание основного проекта

1. Зайдите на [railway.app](https://railway.app)
2. Нажмите **"New Project"**
3. Выберите **"Deploy from GitHub repo"**
4. Подключите ваш репозиторий `ITA_RENT_02`
5. Railway создаст **первый сервис автоматически** (это будет backend API)

### ШАГ 2: Создание PostgreSQL базы данных

1. В проекте нажмите **"+ New Service"**
2. Выберите **"Database"** → **"PostgreSQL"**
3. База данных создается автоматически
4. Railway автоматически установит переменную `DATABASE_URL` для всех сервисов

### ШАГ 3: Настройка основного сервиса (Backend API)

1. Кликните на **первый созданный сервис** (обычно называется по имени репозитория)
2. Перейдите в **"Settings"** → **"General"**
3. Измените **Service Name** на `backend`
4. В **"Settings"** → **"Deploy"** убедитесь, что:
   - **Source Repo**: ваш репозиторий
   - **Branch**: main
   - **Start Command**: оставьте пустым (будет использован Dockerfile)

### ШАГ 4: Добавление переменных окружения для Backend

1. В сервисе `backend` перейдите в **"Variables"**
2. Добавьте переменные **одну за одной**:

```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=production-super-secret-key-change-me-12345
TELEGRAM_BOT_TOKEN=7894689920:AAFZldrCNcqv24wsIEi5pUvNIPgHWPkWlvc
SCRAPERAPI_KEY=ff8892f744de6a7c18a7a02ff41d8da3
SCRAPER_WORKER_INTERVAL_HOURS=6
SCRAPER_WORKER_MAX_PAGES=10
```

3. Нажмите **"Deploy"** для применения изменений

### ШАГ 5: Создание Telegram Bot сервиса

1. В проекте нажмите **"+ New Service"**
2. Выберите **"GitHub Repo"**
3. Выберите тот же репозиторий `ITA_RENT_02`
4. После создания:
   - **Settings** → **General** → **Service Name**: `telegram-bot`
   - **Settings** → **Deploy** → **Start Command**: `python run_telegram_bot.py`

### ШАГ 6: Переменные окружения для Telegram Bot

В сервисе `telegram-bot` → **"Variables"** добавьте:

```bash
ENVIRONMENT=production
SECRET_KEY=production-super-secret-key-change-me-12345
TELEGRAM_BOT_TOKEN=7894689920:AAFZldrCNcqv24wsIEi5pUvNIPgHWPkWlvc
SERVICE_TYPE=telegram-bot
PYTHONPATH=/app
```

### ШАГ 7: Создание Notification Worker сервиса

1. **"+ New Service"** → **"GitHub Repo"** → тот же репозиторий
2. Настройки:
   - **Service Name**: `notification-worker`
   - **Start Command**: `while true; do python cron_notifications.py; sleep 1800; done`

### ШАГ 8: Переменные окружения для Notification Worker

```bash
ENVIRONMENT=production
SECRET_KEY=production-super-secret-key-change-me-12345
TELEGRAM_BOT_TOKEN=7894689920:AAFZldrCNcqv24wsIEi5pUvNIPgHWPkWlvc
SERVICE_TYPE=notification-worker
PYTHONPATH=/app
```

### ШАГ 9: Создание Scraper Worker сервиса

1. **"+ New Service"** → **"GitHub Repo"** → тот же репозиторий
2. Настройки:
   - **Service Name**: `scraper-worker`
   - **Start Command**: `while true; do python cron_scraper.py; sleep 21600; done`

### ШАГ 10: Переменные окружения для Scraper Worker

```bash
ENVIRONMENT=production
SECRET_KEY=production-super-secret-key-change-me-12345
SCRAPERAPI_KEY=ff8892f744de6a7c18a7a02ff41d8da3
SCRAPER_WORKER_INTERVAL_HOURS=6
SCRAPER_WORKER_MAX_PAGES=10
SERVICE_TYPE=scraper-worker
PYTHONPATH=/app
```

### ШАГ 11: Создание Frontend сервиса (если нужен)

1. **"+ New Service"** → **"GitHub Repo"** → тот же репозиторий
2. Настройки:
   - **Service Name**: `frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Start Command**: `npm run start`

## 📦 Итоговая структура сервисов

После создания у вас должно быть **5 сервисов**:

```
📊 Railway Project: ITA_RENT_BOT
├── 🌐 backend (API сервер)
├── 🤖 telegram-bot (Telegram бот)
├── 🔔 notification-worker (уведомления каждые 30 мин)
├── 🕷️ scraper-worker (парсинг каждые 6 часов)
├── 💻 frontend (React приложение, опционально)
└── 🗄️ postgres (база данных)
```

## 🔧 Переменные окружения для Railway

### Обязательные переменные для ВСЕХ сервисов:

```bash
# Основные настройки
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=production-super-secret-key-change-me-12345

# Telegram Bot
TELEGRAM_BOT_TOKEN=7894689920:AAFZldrCNcqv24wsIEi5pUvNIPgHWPkWlvc

# ScraperAPI (для парсинга)
SCRAPERAPI_KEY=ff8892f744de6a7c18a7a02ff41d8da3

# Воркер настройки
SCRAPER_WORKER_INTERVAL_HOURS=6
SCRAPER_WORKER_MAX_PAGES=10
```

### Автоматические переменные Railway:

- `DATABASE_URL` - PostgreSQL (создается автоматически)
- `PORT` - порт приложения
- `RAILWAY_ENVIRONMENT=production`

## ⚡ ВАЖНЫЕ КОМАНДЫ ЗАПУСКА

Убедитесь, что **Start Command** установлены правильно:

| Сервис                | Start Command                                                   |
| --------------------- | --------------------------------------------------------------- |
| `backend`             | _(пусто - использует Dockerfile)_                               |
| `telegram-bot`        | `python run_telegram_bot.py`                                    |
| `notification-worker` | `while true; do python cron_notifications.py; sleep 1800; done` |
| `scraper-worker`      | `while true; do python cron_scraper.py; sleep 21600; done`      |
| `frontend`            | `npm run start`                                                 |

## 🧪 Проверка после деплоя

### 1. Проверьте статус всех сервисов:

- Все сервисы должны показывать **"Active"** статус
- Нет ошибок в логах

### 2. API проверки:

```bash
curl https://your-backend-url.railway.app/health
curl https://your-backend-url.railway.app/api/v1/telegram/status
```

### 3. Telegram бот:

- Отправьте `/start` боту
- Попробуйте `/help`
- Проверьте `/register your@email.com`

### 4. Логи сервисов:

- **backend**: API запросы и ответы
- **telegram-bot**: Сообщения от пользователей
- **notification-worker**: Отправка уведомлений каждые 30 мин
- **scraper-worker**: Парсинг данных каждые 6 часов

## 🔔 Настройка webhook (опционально)

После деплоя можно настроить webhook для Telegram:

```bash
curl -X POST \
  "https://api.telegram.org/bot7894689920:AAFZldrCNcqv24wsIEi5pUvNIPgHWPkWlvc/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-backend-url.railway.app/api/v1/telegram/webhook"
  }'
```

## 🚨 Решение типичных проблем

### ❌ Ошибка: "Module not found"

**Решение**: Добавьте переменную `PYTHONPATH=/app` во все Python сервисы

### ❌ Ошибка: "Database connection failed"

**Решение**: Убедитесь, что PostgreSQL сервис создан и переменная `DATABASE_URL` установлена

### ❌ Ошибка: "Telegram bot не отвечает"

**Решение**:

1. Проверьте логи `telegram-bot` сервиса
2. Убедитесь, что `TELEGRAM_BOT_TOKEN` правильный
3. Проверьте, что сервис показывает "Active" статус

### ❌ Ошибка: "Build failed"

**Решение**:

1. Убедитесь, что все файлы закоммичены в git
2. Проверьте, что `requirements.txt` содержит все зависимости
3. Перезапустите деплой

## 📊 Мониторинг

После деплоя отслеживайте:

- Логи всех сервисов в Railway Dashboard
- Ответы бота в Telegram
- Работу cron задач (каждые 30 минут)
- Отправку уведомлений пользователям

## 🐛 Диагностика проблем

### Если бот не отвечает:

1. Проверьте логи `telegram-bot` сервиса
2. Убедитесь, что `TELEGRAM_BOT_TOKEN` установлен
3. Проверьте статус сервиса в Railway

### Если не приходят уведомления:

1. Проверьте логи `notification-worker`
2. Убедитесь, что у пользователя есть активные фильтры
3. Проверьте, что пользователь связал Telegram аккаунт

---

**Статус**: ✅ Готово к деплою  
**Время деплоя**: ~20-30 минут (создание сервисов вручную)  
**Последнее тестирование**: Январь 2025
