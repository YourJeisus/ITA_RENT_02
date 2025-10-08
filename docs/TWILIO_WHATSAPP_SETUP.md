# 📱 Настройка Twilio WhatsApp для ITA_RENT_BOT

Пошаговая инструкция по настройке WhatsApp уведомлений через Twilio - рекомендуемый провайдер для начинающих.

## 🌟 Почему Twilio?

### ✅ Преимущества Twilio:

- **Простота настройки** - регистрация и настройка за 10 минут
- **Бесплатный Sandbox** - можно тестировать без затрат
- **Отличная документация** - множество примеров и гайдов
- **Надежность** - один из крупнейших провайдеров связи в мире
- **Техподдержка** - качественная поддержка на русском языке
- **Гибкие тарифы** - платите только за отправленные сообщения
- **Официальное партнерство** - с Meta для WhatsApp Business API

### 💰 Стоимость:

- **Sandbox режим**: Бесплатно для тестирования
- **Production**: ~$0.005 за сообщение (зависит от страны)
- **Без абонплаты** - платите только за использование

## 📋 Пошаговая настройка

### Шаг 1: Регистрация в Twilio (5 минут)

1. **Откройте сайт Twilio**:

   ```
   https://www.twilio.com/
   ```

2. **Нажмите "Sign up free"** (красная кнопка в правом верхнем углу)

3. **Заполните форму регистрации**:

   - **Email**: ваш рабочий email
   - **Password**: надежный пароль
   - **First Name**: ваше имя
   - **Last Name**: ваша фамилия
   - **Company**: можете указать свое имя или название проекта

4. **Согласитесь с условиями** и нажмите "Start your free trial"

5. **Подтвердите номер телефона**:

   - Введите ваш номер телефона
   - Получите и введите код из SMS
   - Нажмите "Verify"

6. **Выберите продукты**:
   - Отметьте **"Messaging"** ✅
   - Отметьте **"WhatsApp"** ✅
   - Нажмите "Get started"

### Шаг 2: Настройка WhatsApp Sandbox (3 минуты)

1. **В консоли Twilio найдите раздел Messaging**:

   ```
   Левое меню → Messaging → Try it out → Send a WhatsApp message
   ```

2. **Перейдите в WhatsApp Sandbox**:

   - Найдите раздел "WhatsApp Sandbox"
   - Увидите номер типа: **+1 415 523 8886**
   - Увидите код типа: **join select-thumb**

3. **Активируйте Sandbox**:
   - Откройте WhatsApp на телефоне
   - Создайте новый чат с номером **+1 415 523 8886**
   - Отправьте сообщение: **join select-thumb** (ваш код может отличаться!)
   - Получите подтверждение активации

### Шаг 3: Получение API ключей (2 минуты)

1. **Перейдите в настройки аккаунта**:

   ```
   Левое меню → Account → API keys & tokens
   ```

2. **Найдите основные данные**:

   - **Account SID**: строка типа `AC1234567890abcdef1234567890abcdef`
   - **Auth Token**: нажмите "Show" чтобы увидеть

3. **Скопируйте данные**:
   - Account SID → сохраните в блокнот
   - Auth Token → сохраните в блокнот

### Шаг 4: Настройка .env файла

1. **Откройте ваш .env файл** или создайте новый

2. **Добавьте Twilio настройки**:

   ```bash
   # WhatsApp Twilio настройки
   WHATSAPP_ENABLED=true
   WHATSAPP_API_URL=https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json
   WHATSAPP_API_TOKEN=ваш_auth_token
   WHATSAPP_PHONE_NUMBER_ID=whatsapp:+14155238886
   WHATSAPP_BUSINESS_ACCOUNT_ID=ваш_account_sid
   ```

3. **Замените значения**:

   - `YOUR_ACCOUNT_SID` → ваш Account SID
   - `ваш_auth_token` → ваш Auth Token
   - `ваш_account_sid` → тот же Account SID

4. **Пример заполненного .env**:
   ```bash
   WHATSAPP_ENABLED=true
   WHATSAPP_API_URL=https://api.twilio.com/2010-04-01/Accounts/AC1234567890abcdef1234567890abcdef/Messages.json
   WHATSAPP_API_TOKEN=abcdef1234567890abcdef1234567890
   WHATSAPP_PHONE_NUMBER_ID=whatsapp:+14155238886
   WHATSAPP_BUSINESS_ACCOUNT_ID=AC1234567890abcdef1234567890abcdef
   ```

## 🧪 Тестирование настройки

### Быстрый тест через наш скрипт:

```bash
# Запустите тестовый скрипт
python test_twilio_whatsapp.py
```

Скрипт проверит:

- ✅ Настройки переменных окружения
- ✅ Подключение к Twilio API
- ✅ Отправку тестового сообщения
- ✅ Работу через наш WhatsApp сервис

### Ручное тестирование через cURL:

```bash
# Замените YOUR_ACCOUNT_SID и YOUR_AUTH_TOKEN на ваши данные
curl -X POST "https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json" \
--data-urlencode "From=whatsapp:+14155238886" \
--data-urlencode "To=whatsapp:+393401234567" \
--data-urlencode "Body=Тест WhatsApp от ITA_RENT_BOT!" \
-u YOUR_ACCOUNT_SID:YOUR_AUTH_TOKEN
```

## 🚀 Запуск системы

### 1. Проверка системы:

```bash
# Проверить общую интеграцию
python test_whatsapp_integration.py

# Проверить только Twilio
python test_twilio_whatsapp.py
```

### 2. Запуск worker'а:

```bash
# В режиме отладки
DEBUG_NOTIFICATIONS=true python run_whatsapp_worker.py

# В обычном режиме
python run_whatsapp_worker.py
```

### 3. Запуск API сервера:

```bash
# В режиме разработки
python -m uvicorn src.main:app --reload

# В production
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 📱 Использование через API

### Привязка WhatsApp номера:

```bash
curl -X POST "http://localhost:8000/api/v1/whatsapp/link" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+393401234567"
  }'
```

### Тестовое сообщение:

```bash
curl -X POST "http://localhost:8000/api/v1/whatsapp/test" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+393401234567"
  }'
```

### Проверка статуса:

```bash
curl -X GET "http://localhost:8000/api/v1/whatsapp/status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔧 Настройка Production

### Переход с Sandbox на Production:

1. **В консоли Twilio перейдите в**:

   ```
   Messaging → Senders → WhatsApp senders
   ```

2. **Нажмите "Request Access"** для production доступа

3. **Заполните заявку**:

   - Название бизнеса
   - Описание использования
   - Ожидаемый объем сообщений

4. **Дождитесь одобрения** (обычно 1-3 дня)

5. **Обновите настройки**:
   - Получите production номер телефона
   - Обновите `WHATSAPP_PHONE_NUMBER_ID` в .env

### Production настройки безопасности:

```bash
# Добавьте в .env для production
WHATSAPP_WEBHOOK_VERIFY_TOKEN=ваш_случайный_токен_32_символа
DEBUG_NOTIFICATIONS=false
WHATSAPP_NOTIFICATION_INTERVAL_SECONDS=1800
```

## 📊 Мониторинг и отладка

### Логи Twilio:

1. **В консоли Twilio**:

   ```
   Monitor → Logs → Programmable Messaging
   ```

2. **Фильтры для поиска**:
   - По времени отправки
   - По статусу доставки
   - По номеру получателя

### Статусы сообщений Twilio:

- **queued** - сообщение в очереди
- **sending** - отправляется
- **sent** - отправлено
- **delivered** - доставлено
- **undelivered** - не доставлено
- **failed** - ошибка отправки

### Отладка через логи:

```bash
# Запуск с подробными логами
DEBUG_NOTIFICATIONS=true python run_whatsapp_worker.py

# Поиск ошибок в логах
grep "ERROR" logs/whatsapp_worker.log

# Мониторинг в реальном времени
tail -f logs/whatsapp_worker.log | grep "Twilio"
```

## 💸 Управление расходами

### Настройка лимитов в Twilio:

1. **Billing → Notifications & Limits**
2. **Установите Monthly Spending Limit**
3. **Настройте уведомления при превышении**

### Оптимизация расходов:

- **Группируйте уведомления** - отправляйте не чаще чем раз в час
- **Фильтруйте дубликаты** - не отправляйте одинаковые объявления
- **Используйте интервалы** - настройте разумные интервалы уведомлений

## 🛠️ Решение проблем

### Частые ошибки:

#### 1. "Authenticate" error (401)

```bash
# Проверьте правильность Account SID и Auth Token
echo $WHATSAPP_BUSINESS_ACCOUNT_ID
echo $WHATSAPP_API_TOKEN
```

#### 2. "From number not verified" error

- Убедитесь что используете Sandbox номер: `whatsapp:+14155238886`
- Или настройте production номер

#### 3. "To number not in sandbox" error

- Добавьте получателя в Sandbox через join код
- Или используйте production версию

#### 4. "Message body too long" error

- WhatsApp лимит: 4096 символов
- Сократите сообщение или разбейте на части

### Проверка подключения:

```bash
# Тест подключения к API
curl -u YOUR_ACCOUNT_SID:YOUR_AUTH_TOKEN \
  "https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID.json"
```

## 📞 Поддержка

### Контакты Twilio:

- **Документация**: https://www.twilio.com/docs/whatsapp
- **Поддержка**: https://support.twilio.com/
- **Статусы**: https://status.twilio.com/

### Полезные ссылки:

- **Console**: https://console.twilio.com/
- **WhatsApp Sandbox**: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
- **Billing**: https://console.twilio.com/us1/billing

## 🎉 Следующие шаги

После успешной настройки Twilio:

1. ✅ **Протестируйте отправку** через `test_twilio_whatsapp.py`
2. ✅ **Запустите worker** `python run_whatsapp_worker.py`
3. ✅ **Настройте пользователей** через веб-интерфейс
4. ✅ **Мониторьте логи** и статистику
5. ✅ **Планируйте переход** на production при необходимости

**Поздравляем! WhatsApp уведомления через Twilio готовы к работе! 🎯**
