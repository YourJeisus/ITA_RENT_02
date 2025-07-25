# 🤖 Настройка Telegram бота - ITA_RENT_BOT

## 📋 Обзор

Telegram бот для ITA_RENT_BOT предоставляет пользователям возможность:

- Связывать свой аккаунт с Telegram для получения уведомлений
- Управлять фильтрами поиска через команды бота
- Получать автоматические уведомления о новых объявлениях
- Приостанавливать и возобновлять уведомления

## 🛠️ Настройка бота

### 1. Создание бота в Telegram

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Введите имя бота: `ITA Rent Bot`
4. Введите username бота: `ita_rent_bot` (или другой доступный)
5. Сохраните токен бота (например: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Настройка переменных окружения

Добавьте в файл `.env`:

```bash
# Telegram Bot настройки
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhook
```

### 3. Настройка команд бота (опционально)

Отправьте @BotFather команду `/setcommands` и добавьте:

```
start - Начало работы с ботом
help - Справка по командам
register - Связать аккаунт с email
status - Информация о подписке и фильтрах
filters - Список ваших фильтров поиска
```

## 🚀 Запуск бота

### Локальная разработка

```bash
# Запуск бота в polling режиме
python run_telegram_bot.py

# Запуск диспетчера уведомлений (тестирование)
python run_notification_dispatcher.py
```

### Production (Railway)

Бот автоматически запускается как отдельный сервис в Railway. См. `railway.toml`.

## 📱 Команды бота

### Основные команды

| Команда     | Описание                   | Пример                       |
| ----------- | -------------------------- | ---------------------------- |
| `/start`    | Приветствие и инструкция   | `/start`                     |
| `/help`     | Справка по всем командам   | `/help`                      |
| `/register` | Связывание аккаунта        | `/register user@example.com` |
| `/status`   | Статус аккаунта и подписки | `/status`                    |
| `/filters`  | Список фильтров поиска     | `/filters`                   |

### Команды управления фильтрами

| Команда      | Описание                      | Пример       |
| ------------ | ----------------------------- | ------------ |
| `/pause_123` | Приостановить фильтр с ID 123 | `/pause_123` |

## 🔄 Пользовательский сценарий

### 1. Первое использование

1. Пользователь открывает бота в Telegram
2. Отправляет `/start`
3. Получает приветствие и инструкции
4. Регистрируется на сайте (если ещё не зарегистрирован)
5. Использует команду `/register email@example.com`
6. Получает подтверждение о связывании аккаунта

### 2. Настройка фильтров

1. Пользователь создает фильтры на веб-сайте
2. Использует команду `/filters` для просмотра
3. Может приостанавливать фильтры командами `/pause_ID`

### 3. Получение уведомлений

1. Система автоматически проверяет новые объявления каждые 30 минут
2. Если найдены объявления по фильтрам пользователя, отправляется уведомление
3. Частота зависит от подписки:
   - **Free**: раз в день
   - **Premium**: каждые 30 минут

## 🔔 Система уведомлений

### Формат уведомления

```
🏠 Новые объявления по фильтру 'Квартира в Риме'

1. Уютная квартира в центре Рима
📍 Via del Corso, 123, Roma
💰 1,800€/мес
🚪 3 комн. • 📐 85 м² • 🏠 apartment
🔗 Посмотреть объявление

2. Современная студия рядом с Колизеем
📍 Via dei Fori Imperiali, 45, Roma
💰 1,200€/мес
🚪 1 комн. • 📐 40 м² • 🏠 studio
🔗 Посмотреть объявление

🔍 Фильтр: Квартира в Риме
📍 Город: Roma

/pause_123 - приостановить этот фильтр
/filters - все ваши фильтры
```

### Логика отправки

- Проверка выполняется каждые 30 минут
- Учитывается тип подписки пользователя
- Максимум 5 объявлений в одном уведомлении
- Дедупликация уже отправленных объявлений

## 🛠️ API интеграция

### Endpoints для работы с Telegram

```bash
# Связывание аккаунта
POST /api/v1/telegram/link
{
    "telegram_chat_id": "123456789",
    "telegram_username": "username"
}

# Отвязка аккаунта
DELETE /api/v1/telegram/unlink

# Статус интеграции
GET /api/v1/telegram/status

# Тестовое уведомление
POST /api/v1/telegram/test-notification

# Webhook (для production)
POST /api/v1/telegram/webhook
```

## 🧪 Тестирование

### 1. Тестирование основных команд

```bash
# Запустите бота локально
python run_telegram_bot.py

# В Telegram:
/start
/help
/register test@example.com
/status
/filters
```

### 2. Тестирование уведомлений

```bash
# Запустите диспетчер уведомлений
python run_notification_dispatcher.py

# Или через API (если аккаунт привязан)
curl -X POST "http://localhost:8000/api/v1/telegram/test-notification" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. Тестирование cron задач

```bash
# Однократный запуск cron задачи
python cron_notifications.py

# Настройка реального cron (в production)
# Добавьте в crontab:
# */30 * * * * cd /path/to/project && python cron_notifications.py
```

## 🐛 Диагностика проблем

### Частые проблемы

1. **Бот не отвечает**

   ```bash
   # Проверьте токен
   echo $TELEGRAM_BOT_TOKEN

   # Проверьте логи
   tail -f telegram_bot.log
   ```

2. **Уведомления не приходят**

   ```bash
   # Проверьте диспетчер
   python run_notification_dispatcher.py

   # Проверьте привязку аккаунта
   curl -X GET "http://localhost:8000/api/v1/telegram/status" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **Ошибки авторизации**
   ```bash
   # Проверьте базу данных
   # Убедитесь, что telegram_chat_id сохраняется корректно
   ```

### Логи

- `telegram_bot.log` - логи бота
- `notification_dispatcher.log` - логи диспетчера уведомлений
- `cron_notifications.log` - логи cron задач

## 📊 Мониторинг

### Метрики для отслеживания

- Количество активных пользователей бота
- Процент успешных уведомлений
- Среднее время ответа бота
- Количество ошибок в день

### Алерты

- Бот не отвечает более 5 минут
- Диспетчер уведомлений упал
- Превышен лимит ошибок Telegram API

## 🔄 Обновления и деплой

### Обновление бота

1. Обновите код
2. Перезапустите сервисы:

   ```bash
   # На Railway автоматически
   git push origin main

   # Локально
   pkill -f run_telegram_bot.py
   python run_telegram_bot.py
   ```

### Миграция данных

При изменении структуры БД убедитесь, что:

- Поле `telegram_chat_id` сохраняется
- Связи между пользователями и фильтрами работают
- Запускайте `alembic upgrade head`

## 🚀 Планы развития

### Краткосрочные улучшения

- [ ] Inline кнопки для управления фильтрами
- [ ] Поддержка геолокации для поиска
- [ ] Уведомления об изменении цены
- [ ] Групповые чаты для районов

### Долгосрочные планы

- [ ] AI ассистент для консультаций
- [ ] Интеграция с календарем просмотров
- [ ] Система рейтингов арендодателей
- [ ] Мультиязычная поддержка

---

**Создано**: Январь 2025  
**Версия**: MVP 1.0  
**Статус**: Готов к использованию ✅
