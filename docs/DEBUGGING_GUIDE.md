# 🔍 Руководство по диагностике ITA_RENT_BOT

## Проблемы и их решения

### 1. Дубликаты URL в базе данных

**Симптомы:**

```
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "listings_url_key"
```

**Решение:**

1. Запустить миграцию для удаления constraint:

```bash
alembic upgrade head
```

2. Проверить что constraint удален:

```bash
python debug_system_status.py
```

### 2. Мало объявлений с некоторых источников

**Диагностика:**

```bash
# Проверить работу отдельных скраперов
python test_single_scraper.py idealista
python test_single_scraper.py immobiliare
python test_single_scraper.py subito

# Или все сразу
python test_single_scraper.py all
```

**Проверить статистику БД:**

```bash
python debug_system_status.py
```

### 3. Уведомления не приходят

**Диагностика:**

```bash
# Полная диагностика системы
python debug_system_status.py

# Тест уведомлений отдельно
python run_notification_worker.py
```

**Проверить:**

1. У пользователя привязан Telegram (`telegram_chat_id`)
2. У пользователя есть активные фильтры
3. Есть ли новые объявления подходящие под фильтры
4. Настроен ли `TELEGRAM_BOT_TOKEN`

### 4. Скраперы не находят объявления

**Проверить:**

1. Настроен ли `SCRAPERAPI_KEY`
2. Работает ли интернет соединение
3. Не заблокированы ли IP адреса

## Диагностические скрипты

### `debug_system_status.py`

Полная диагностика системы:

- Статистика БД по источникам
- Состояние пользователей и фильтров
- Последние объявления
- Тест системы уведомлений

```bash
python debug_system_status.py
```

### `test_single_scraper.py`

Тест отдельных скраперов:

```bash
# Тест конкретного скрапера
python test_single_scraper.py idealista
python test_single_scraper.py immobiliare
python test_single_scraper.py subito

# Тест всех скраперов
python test_single_scraper.py all
```

### `run_notification_worker.py`

Запуск worker уведомлений с диагностикой:

```bash
python run_notification_worker.py
```

## Режим отладки

Для включения подробного логирования установите:

```bash
export DEBUG_NOTIFICATIONS=true
```

В этом режиме:

- Отключены временные ограничения на уведомления
- Разрешены дубликаты уведомлений
- Включено подробное логирование

## Логи

Важные логи для диагностики:

### Скрапинг

```
📊 Статистика по источникам: {'idealista': 15, 'subito': 8, 'immobiliare': 3}
💾 Сохранено: 12 новых, 8 обновлено, 6 дубликатов, 2 ошибки
```

### Уведомления

```
🔔 Диспетчер завершен: 3 пользователя, 5 уведомлений, 0 ошибок
📊 К отправке по источникам: {'subito': 3, 'idealista': 2}
```

## Частые ошибки

### 1. `SCRAPERAPI_KEY не настроен`

Добавьте в `.env`:

```
SCRAPERAPI_KEY=your_key_here
```

### 2. `TELEGRAM_BOT_TOKEN не настроен`

Добавьте в `.env`:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 3. `UniqueViolation на URL`

Запустите миграцию:

```bash
alembic upgrade head
```

### 4. Нет новых объявлений для уведомлений

Проверьте:

- Фильтры пользователей (слишком жесткие?)
- Время последнего уведомления
- Есть ли вообще новые объявления в БД

## Мониторинг в production

### Railway логи

```bash
railway logs
```

### Метрики

- Количество объявлений по источникам
- Частота отправки уведомлений
- Ошибки скрапинга

### Алерты

Настройте алерты на:

- Отсутствие новых объявлений > 2 часов
- Ошибки скрапинга > 50%
- Отсутствие уведомлений > 24 часа
