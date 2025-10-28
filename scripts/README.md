# Utility Scripts

Все вспомогательные скрипты проекта перенесены в эту директорию, чтобы корень репозитория оставался чистым. Каждый скрипт можно запускать из корня репозитория командой `python scripts/<имя>.py`.

## Основные скрипты

| Скрипт | Назначение |
| --- | --- |
| `run_telegram_bot.py` | Запуск Telegram-бота в режиме polling. Используется в development и на Railway. |
| `run_notification_worker.py` | Фоновый воркер, который периодически отправляет уведомления пользователям. |
| `run_notification_dispatcher.py` | Одноразовый запуск диспетчера уведомлений (ручная диагностика). |
| `run_whatsapp_worker.py` | Фоновый воркер WhatsApp-уведомлений. |
| `cron_notifications.py` | Cron-задача для проверки новых объявлений каждые N минут. |
| `cron_scraper.py` | Cron-задача для запуска парсера Immobiliare. |
| `cron_subito_scraper.py` | Cron-задача для запуска парсера Subito. |
| `cron_idealista_scraper.py` | Cron-задача для запуска парсера Idealista. |
| `cron_all_scrapers.py` | Совмещенный cron для всех источников. |
| `debug_system_status.py` | Быстрая диагностика состояния БД и системы уведомлений. |
| `debug_notifications.py` | Ручная проверка логики уведомлений (режим разработчика). |
| `check_db_content.py` | Подробный отчёт по содержимому БД. |
| `reset_telegram_webhook.py` | Сброс Telegram webhook и очистка pending updates. |
| `send_simple_whatsapp.py` | Ручная отправка тестового WhatsApp сообщения. |
| `send_real_listing_whatsapp.py` | Отправка реального объявления в WhatsApp (ручные тесты). |
| `send_whatsapp_with_images.py` | Тест отправки WhatsApp с изображениями. |

## Запуск

```bash
# Пример запуска Telegram-бота
python scripts/run_telegram_bot.py

# Пример cron-задачи в Railway
railway run python scripts/cron_all_scrapers.py

# Диагностика системы
python scripts/debug_system_status.py
```

> ⚠️ Скрипты используют настройки из `.env`. Перед запуском убедитесь, что файл `.env` существует в корне проекта или переменные среды установлены через Railway.
