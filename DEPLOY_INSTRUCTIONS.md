# 🚀 Инструкции по деплою ITA_RENT_BOT на Railway

## ✅ Готово к деплою!

Все компоненты протестированы и готовы к production деплою:

- ✅ API сервер
- ✅ Telegram бот
- ✅ Система уведомлений
- ✅ База данных

## 🔧 Переменные окружения для Railway

### Обязательные переменные:

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

## 📦 Структура сервисов в Railway

```
ITA_RENT_BOT/
├── backend (API сервер)
├── frontend (React приложение)
├── scraper-worker (парсинг каждые 6 часов)
├── telegram-bot (Telegram бот)
├── notification-worker (уведомления каждые 30 мин)
└── postgres (база данных)
```

## 🚀 Команды для деплоя

```bash
# 1. Коммит всех изменений
git add .
git commit -m "feat: Complete Telegram bot system (Stage 6)"

# 2. Пуш в main ветку
git push origin main

# 3. Railway автоматически развернет все сервисы
```

## ⚙️ Настройка в Railway Dashboard

### 1. Переменные окружения

Добавьте все переменные из списка выше в Railway Dashboard

### 2. Сервисы

Railway автоматически создаст сервисы согласно `railway.toml`:

- `backend` - основной API
- `telegram-bot` - Telegram бот
- `notification-worker` - диспетчер уведомлений
- `scraper-worker` - парсинг данных

### 3. База данных

Railway автоматически создаст PostgreSQL и установит `DATABASE_URL`

## 🧪 Проверка после деплоя

### 1. API проверки:

```bash
curl https://your-app.railway.app/health
curl https://your-app.railway.app/api/v1/telegram/status
```

### 2. Telegram бот:

- Отправьте `/start` боту
- Попробуйте `/help`
- Проверьте `/register your@email.com`

### 3. Логи сервисов:

- Проверьте логи `telegram-bot` сервиса
- Проверьте логи `notification-worker`
- Убедитесь, что нет ошибок

## 🔔 Настройка webhook (опционально)

После деплоя можно настроить webhook для Telegram:

```bash
curl -X POST \
  "https://api.telegram.org/bot7894689920:AAFZldrCNcqv24wsIEi5pUvNIPgHWPkWlvc/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.railway.app/api/v1/telegram/webhook"
  }'
```

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
**Время деплоя**: ~10-15 минут  
**Последнее тестирование**: Январь 2025
