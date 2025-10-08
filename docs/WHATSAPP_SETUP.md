# 📱 Настройка WhatsApp уведомлений для ITA_RENT_BOT

Это руководство поможет настроить систему WhatsApp уведомлений в дополнение к существующим Telegram уведомлениям.

## 🎯 Обзор

WhatsApp интеграция позволяет пользователям получать уведомления о новых объявлениях недвижимости через WhatsApp в дополнение к Telegram. Система поддерживает:

- ✅ Текстовые уведомления с деталями объявлений
- ✅ Автоматическое форматирование сообщений
- ✅ Поддержка международных номеров
- ✅ Отдельное управление через API
- ✅ Совместимость с Telegram уведомлениями

## 🔧 Настройка WhatsApp Business API

### 1. Получение доступа к WhatsApp Business API

Для работы с WhatsApp требуется доступ к **WhatsApp Business API**. Есть несколько вариантов:

#### Вариант 1: Meta Business (официальный)

1. Зарегистрируйтесь в [Meta Business](https://business.facebook.com/)
2. Создайте WhatsApp Business аккаунт
3. Получите API токены и настройки

#### Вариант 2: Сторонние провайдеры (рекомендуется)

- **Twilio** - [https://www.twilio.com/whatsapp](https://www.twilio.com/whatsapp)
- **MessageBird** - [https://messagebird.com/whatsapp](https://messagebird.com/whatsapp)
- **360Dialog** - [https://www.360dialog.com/](https://www.360dialog.com/)
- **ChatAPI** - [https://chat-api.com/](https://chat-api.com/)

### 2. Настройка переменных окружения

Добавьте следующие переменные в ваш `.env` файл:

```bash
# WhatsApp API настройки
WHATSAPP_ENABLED=true
WHATSAPP_API_URL=https://your-whatsapp-provider.com/v1
WHATSAPP_API_TOKEN=your_whatsapp_api_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token

# Интервалы уведомлений (в секундах)
WHATSAPP_NOTIFICATION_INTERVAL_SECONDS=1800  # 30 минут
```

### 3. Примеры настройки для разных провайдеров

#### Twilio настройка

```bash
WHATSAPP_API_URL=https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json
WHATSAPP_API_TOKEN=your_twilio_auth_token
WHATSAPP_PHONE_NUMBER_ID=whatsapp:+14155238886
```

#### 360Dialog настройка

```bash
WHATSAPP_API_URL=https://waba.360dialog.io
WHATSAPP_API_TOKEN=your_360dialog_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

## 🚀 Запуск системы

### 1. Применение миграций базы данных

```bash
# Применить миграции для добавления WhatsApp полей
alembic upgrade head
```

### 2. Запуск WhatsApp worker

```bash
# Запуск в production
python run_whatsapp_worker.py

# Запуск в режиме отладки
DEBUG_NOTIFICATIONS=true python run_whatsapp_worker.py
```

### 3. Запуск в Docker

Обновите ваш `docker-compose.yml`:

```yaml
services:
  # ... существующие сервисы ...

  whatsapp-worker:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - WHATSAPP_ENABLED=${WHATSAPP_ENABLED}
      - WHATSAPP_API_URL=${WHATSAPP_API_URL}
      - WHATSAPP_API_TOKEN=${WHATSAPP_API_TOKEN}
      - WHATSAPP_PHONE_NUMBER_ID=${WHATSAPP_PHONE_NUMBER_ID}
    command: python run_whatsapp_worker.py
    depends_on:
      - api
    restart: unless-stopped
```

## 📋 API Эндпоинты

### Получение статуса WhatsApp

```http
GET /api/v1/whatsapp/status
Authorization: Bearer your_jwt_token
```

### Привязка WhatsApp номера

```http
POST /api/v1/whatsapp/link
Authorization: Bearer your_jwt_token
Content-Type: application/json

{
  "phone_number": "+393401234567",
  "instance_id": "optional_instance_id"
}
```

### Отвязка WhatsApp номера

```http
DELETE /api/v1/whatsapp/unlink
Authorization: Bearer your_jwt_token
```

### Включение/выключение уведомлений

```http
POST /api/v1/whatsapp/toggle
Authorization: Bearer your_jwt_token
Content-Type: application/json

{
  "enabled": true
}
```

### Тестовое сообщение

```http
POST /api/v1/whatsapp/test
Authorization: Bearer your_jwt_token
Content-Type: application/json

{
  "phone_number": "+393401234567"
}
```

### Настройки WhatsApp

```http
GET /api/v1/whatsapp/settings
```

## 🎨 Формат уведомлений

### Пример WhatsApp сообщения

```
🏠 *Новые объявления!*

📍 Фильтр: _Квартира в центре Рима_
📊 Найдено: 3 объявления

*1. Прекрасная квартира в историческом центре*
💰 1800€/мес • 🚪 3 комн. • 📐 85 м²
📍 Via del Corso, 123, Roma
🔗 https://www.idealista.it/...
📱 Источник: IDEALISTA

*2. Уютная студия рядом с Колизеем*
💰 1200€/мес • 🚪 1 комн. • 📐 45 м²
📍 Via dei Fori Imperiali, Roma
🔗 https://www.immobiliare.it/...
📱 Источник: IMMOBILIARE

*3. Современная двушка в Трастевере*
💰 1600€/мес • 🚪 2 комн. • 📐 70 м²
📍 Trastevere, Roma
🔗 https://www.idealista.it/...
📱 Источник: IDEALISTA

💡 _Уведомления можно настроить в личном кабинете_
```

## ⚙️ Технические особенности

### Различия между Telegram и WhatsApp

| Функция                          | Telegram       | WhatsApp      |
| -------------------------------- | -------------- | ------------- |
| Максимум объявлений за сообщение | 5              | 3             |
| Поддержка Markdown               | Полная         | Базовая       |
| Изображения                      | Поддерживается | Пока нет      |
| Кнопки/клавиатура                | Поддерживается | Пока нет      |
| Длина сообщения                  | 4096 символов  | 4096 символов |

### Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                   Notification Service                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  process_user_notifications()                                   │
│           │                                                     │
│           ├─── send_notification_for_filter()                   │
│           │            │                                        │
│           │            ├─── Telegram: send_listing_notification │
│           │            └─── WhatsApp: send_whatsapp_listing     │
│           │                                                     │
│           └─── Обновление БД и статистики                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Логика отправки

1. **Проверка пользователей**: Система находит пользователей с активными фильтрами
2. **Проверка каналов**: Для каждого пользователя проверяется наличие Telegram и/или WhatsApp
3. **Параллельная отправка**: Уведомления отправляются одновременно в оба канала (если настроены)
4. **Обновление статистики**: Результат считается успешным если хотя бы один канал сработал

## 🔍 Мониторинг и отладка

### Логи WhatsApp worker

```bash
# Просмотр логов в реальном времени
tail -f logs/whatsapp_worker.log

# Поиск ошибок
grep "ERROR" logs/whatsapp_worker.log

# Статистика отправки
grep "WhatsApp.*отправлено" logs/whatsapp_worker.log
```

### Режим отладки

```bash
# Включить подробные логи
export DEBUG_NOTIFICATIONS=true
export WHATSAPP_NOTIFICATION_INTERVAL_SECONDS=60

# Запустить worker в режиме отладки
python run_whatsapp_worker.py
```

### Проверка статуса через API

```bash
# Проверить настройки WhatsApp
curl -X GET "http://localhost:8000/api/v1/whatsapp/settings"

# Проверить статус пользователя
curl -X GET "http://localhost:8000/api/v1/whatsapp/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🛠️ Устранение неполадок

### Частые проблемы

#### 1. "WhatsApp уведомления отключены"

```bash
# Проверьте переменную окружения
echo $WHATSAPP_ENABLED

# Должна быть true
export WHATSAPP_ENABLED=true
```

#### 2. "Не все обязательные настройки WhatsApp API настроены"

```bash
# Проверьте все переменные
echo $WHATSAPP_API_URL
echo $WHATSAPP_API_TOKEN
echo $WHATSAPP_PHONE_NUMBER_ID
```

#### 3. "Cannot add a NOT NULL column with default value NULL"

```bash
# Примените миграции вручную
sqlite3 ita_rent.db "ALTER TABLE users ADD COLUMN whatsapp_enabled BOOLEAN NOT NULL DEFAULT 0;"
alembic stamp head
```

#### 4. Сообщения не отправляются

- Проверьте правильность API токена
- Убедитесь что номер телефона WhatsApp Business подтвержден
- Проверьте лимиты API провайдера

### Тестирование

```bash
# Тест подключения к WhatsApp API
curl -X POST "${WHATSAPP_API_URL}/${WHATSAPP_PHONE_NUMBER_ID}/messages" \
  -H "Authorization: Bearer ${WHATSAPP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "393401234567",
    "type": "text",
    "text": {"body": "Тест подключения"}
  }'
```

## 🔐 Безопасность

### Рекомендации

1. **Храните токены в секрете**: Никогда не коммитьте API токены в Git
2. **Используйте HTTPS**: Всегда используйте защищенные соединения
3. **Ограничьте доступ**: Настройте IP ограничения для webhook'ов
4. **Мониторинг**: Отслеживайте необычную активность API

### Ротация токенов

```bash
# Обновление токена без перезапуска
export WHATSAPP_API_TOKEN=new_token
# Перезапустите worker
```

## 📈 Масштабирование

### Production рекомендации

1. **Используйте очереди**: Для больших объемов рассмотрите Redis/RabbitMQ
2. **Мониторинг**: Настройте алерты на ошибки отправки
3. **Резервирование**: Настройте fallback на другой провайдер
4. **Лимиты**: Отслеживайте лимиты API провайдера

### Метрики для мониторинга

- Количество отправленных сообщений в час
- Процент успешных отправок
- Время отклика API
- Количество ошибок по типам

## 🚀 Развертывание

### Railway.app

Добавьте переменные окружения в Railway:

```bash
WHATSAPP_ENABLED=true
WHATSAPP_API_URL=your_api_url
WHATSAPP_API_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
```

### Vercel + Backend

WhatsApp worker нужно запускать на backend сервере (Railway, DigitalOcean и т.д.), так как Vercel не поддерживает долгоживущие процессы.

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи worker'а
2. Убедитесь в правильности настроек API
3. Протестируйте API провайдера напрямую
4. Проверьте статус пользователя через API

Для получения помощи создайте issue с подробным описанием проблемы и логами.
