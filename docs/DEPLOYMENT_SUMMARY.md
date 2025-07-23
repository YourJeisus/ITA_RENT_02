# 🎉 ITA_RENT_BOT - Готов к production!

## 📋 Что готово

✅ **Полная система парсинга недвижимости**

- Автоматический парсинг Immobiliare.it каждые 6 часов
- PostgreSQL база данных с полной структурой
- Современный React веб-интерфейс
- FastAPI REST API с документацией
- Система аутентификации и авторизации

✅ **Production-ready архитектура**

- Микросервисная структура на Railway
- Автоматические миграции базы данных
- Health checks для всех сервисов
- Полное логирование и мониторинг
- Обработка ошибок и retry-логика

✅ **Автоматический деплой**

- Скрипт `./deploy_railway.sh` для одной команды
- Railway конфигурация для всех сервисов
- Автоматическое создание PostgreSQL БД
- Настройка переменных окружения

## 🚀 Как развернуть

### Быстрый деплой (5 минут)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/YourJeisus/ITA_RENT_02.git
cd ITA_RENT_02

# 2. Установите Railway CLI
npm install -g @railway/cli
railway login

# 3. Получите ScraperAPI ключ
# Зарегистрируйтесь на https://scraperapi.com
export SCRAPERAPI_KEY="your-scraperapi-key"

# 4. Деплой одной командой
./deploy_railway.sh
```

**Готово!** Через 5-10 минут у вас будет работающая система.

### Что создается автоматически

1. **PostgreSQL база данных**

   - Все таблицы создаются автоматически
   - Индексы для быстрого поиска
   - Миграции применяются автоматически

2. **Backend API сервис**

   - FastAPI приложение на production
   - Swagger документация на `/docs`
   - Health check на `/health`

3. **Frontend веб-интерфейс**

   - React приложение с современным UI
   - Поиск и фильтрация объявлений
   - Интерактивные карты
   - Система аутентификации

4. **Scraper Worker**
   - Автоматический парсинг каждые 6 часов
   - Обработка 10 страниц за цикл
   - Извлечение фотографий и координат
   - Дедупликация объявлений

## 📊 Мониторинг системы

### Проверка работы сервисов

```bash
# Логи backend API
railway logs --service backend

# Логи воркера парсинга
railway logs --service scraper-worker --follow

# Статус всех сервисов
railway status
```

### Проверка базы данных

```bash
# Подключение к PostgreSQL
railway connect postgres

# Проверка количества объявлений
SELECT COUNT(*) FROM listings;

# Последние добавленные объявления
SELECT title, price, source, created_at
FROM listings
ORDER BY created_at DESC
LIMIT 10;

# Статистика по источникам
SELECT source, COUNT(*) as count, MAX(created_at) as last_update
FROM listings
GROUP BY source;
```

### Health Checks

- **Backend API**: `https://your-backend.railway.app/health`
- **API документация**: `https://your-backend.railway.app/docs`
- **Frontend**: `https://your-frontend.railway.app/`

## ⚙️ Настройка системы

### Изменение частоты парсинга

```bash
# Каждые 3 часа (более частый сбор данных)
railway variables set SCRAPER_WORKER_INTERVAL_HOURS=3

# Каждые 12 часов (экономия ресурсов)
railway variables set SCRAPER_WORKER_INTERVAL_HOURS=12

# Перезапуск воркера для применения изменений
railway service restart scraper-worker
```

### Изменение объема парсинга

```bash
# Больше страниц (больше объявлений, больше ScraperAPI запросов)
railway variables set SCRAPER_WORKER_MAX_PAGES=20

# Меньше страниц (экономия ScraperAPI лимитов)
railway variables set SCRAPER_WORKER_MAX_PAGES=5

# Перезапуск воркера
railway service restart scraper-worker
```

### Добавление Telegram уведомлений

```bash
# Получите токен бота от @BotFather
railway variables set TELEGRAM_BOT_TOKEN="your-bot-token"

# Установите webhook URL
railway variables set TELEGRAM_WEBHOOK_URL="https://your-backend.railway.app/api/v1/telegram/webhook"
```

## 💰 Стоимость работы

### Railway (хостинг)

- **Developer план**: $5/месяц
- **Hobby план**: $20/месяц (рекомендуется)
- Включает PostgreSQL, 512MB RAM, автоскейлинг

### ScraperAPI (парсинг)

- **Free план**: 1,000 запросов/месяц (тестирование)
- **Startup план**: $29/месяц, 10,000 запросов
- **Professional план**: $99/месяц, 100,000 запросов

### Рекомендуемая конфигурация для старта

- Railway Hobby: $20/месяц
- ScraperAPI Startup: $29/месяц
- **Итого**: ~$50/месяц

## 📈 Статистика и метрики

### Производительность парсинга

- **Скорость**: ~50-100 объявлений за цикл парсинга
- **Частота**: каждые 6 часов (4 цикла в день)
- **Объем данных**: ~200-400 новых объявлений в день
- **Время цикла**: 2-5 минут

### Использование ресурсов

- **Backend**: ~100-200MB RAM
- **Scraper Worker**: ~50-100MB RAM
- **PostgreSQL**: ~50-100MB RAM
- **Frontend**: ~20-50MB RAM

## 🔧 Troubleshooting

### Проблема: Воркер парсинга не работает

```bash
# Проверить логи
railway logs --service scraper-worker

# Проверить переменные окружения
railway variables --service scraper-worker

# Проверить ScraperAPI ключ
railway run --service scraper-worker python -c "
from src.core.config import settings
print('ScraperAPI:', 'OK' if settings.SCRAPERAPI_KEY else 'НЕ НАСТРОЕН')
"

# Перезапустить воркер
railway service restart scraper-worker
```

### Проблема: База данных не подключается

```bash
# Проверить статус PostgreSQL
railway status

# Проверить подключение из backend
railway run --service backend python -c "
from src.db.database import test_database_connection
print('БД:', 'OK' if test_database_connection() else 'ОШИБКА')
"

# Применить миграции вручную
railway run --service backend alembic upgrade head
```

### Проблема: Frontend не загружается

```bash
# Проверить логи frontend
railway logs --service frontend

# Проверить переменные окружения
railway variables --service frontend

# Убедиться что VITE_API_URL правильный
railway variables set VITE_API_URL="https://your-backend.railway.app"
```

## 🚀 Следующие шаги развития

### Краткосрочные улучшения (1-2 недели)

1. **Добавить новые источники**: Idealista.it, Subito.it
2. **Telegram уведомления**: Полная интеграция с ботом
3. **Фильтры поиска**: Сохранение пользовательских фильтров
4. **Email уведомления**: Альтернатива Telegram

### Среднесрочные улучшения (1-2 месяца)

1. **Платная подписка**: Stripe интеграция
2. **Мобильное приложение**: React Native
3. **AI рекомендации**: Машинное обучение
4. **Аналитика**: Dashboards и отчеты

### Долгосрочные цели (3-6 месяцев)

1. **Масштабирование**: Kubernetes, микросервисы
2. **Международное расширение**: Другие страны
3. **B2B продукт**: API для агентств недвижимости
4. **Мобильная экосистема**: iOS/Android приложения

## 📞 Поддержка

- **Документация**: [docs/](docs/)
- **GitHub Issues**: [Issues](https://github.com/YourJeisus/ITA_RENT_02/issues)
- **Railway Help**: [railway.app/help](https://railway.app/help)
- **ScraperAPI Support**: [scraperapi.com/support](https://scraperapi.com/support)

---

**🎉 Поздравляем! Ваша система парсинга недвижимости готова к работе!**

_Создано: Январь 2025 | Версия: 1.0 Production_
