# 🚂 Полная инструкция по деплою на Railway

## 📋 Обзор

Railway будет хостить оба сервиса:

- **Backend**: FastAPI приложение (Python)
- **Frontend**: React приложение (Node.js + serve)

Оба сервиса будут автоматически деплоиться из одного GitHub репозитория.

## 🚀 Пошаговая инструкция деплоя

### Шаг 1: Подготовка репозитория

1. **Убедитесь, что все изменения закоммичены:**

```bash
git add .
git commit -m "feat: добавлена конфигурация Railway для полного деплоя"
git push origin main
```

2. **Проверьте структуру файлов:**

```
ITA_RENT_02/
├── railway.toml                    # Конфигурация Railway
├── Dockerfile.prod                 # Backend Dockerfile
├── frontend/
│   ├── Dockerfile.railway         # Frontend Dockerfile для Railway
│   └── ...
└── ...
```

### Шаг 2: Создание проекта на Railway

1. **Зайдите на Railway:**

   - Откройте [railway.app](https://railway.app)
   - Нажмите "Login" и войдите через GitHub

2. **Создайте новый проект:**

   - Нажмите "New Project"
   - Выберите "Deploy from GitHub repo"
   - Найдите и выберите ваш репозиторий `YourJeisus/ITA_RENT_02`

3. **Railway автоматически обнаружит конфигурацию:**
   - Railway прочитает `railway.toml`
   - Создаст два сервиса: `backend` и `frontend`

### Шаг 3: Настройка Backend сервиса

1. **Откройте проект в Railway Dashboard**

2. **Перейдите в сервис "backend":**

   - Кликните на карточку "backend"

3. **Настройте переменные окружения:**
   - Перейдите в раздел "Variables"
   - Добавьте следующие переменные:

```env
# Обязательные переменные
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key-change-this-in-production
APP_NAME=ITA_RENT_BOT
APP_VERSION=1.0.0

# База данных (Railway автоматически создаст PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Опциональные переменные
DEBUG=False
PYTHONPATH=/app
```

4. **Добавьте PostgreSQL базу данных:**

   - В проекте нажмите "New"
   - Выберите "Database" → "Add PostgreSQL"
   - Railway автоматически создаст переменную `DATABASE_URL`

5. **Проверьте деплой:**
   - Railway автоматически начнет сборку
   - Следите за логами в разделе "Deployments"

### Шаг 4: Настройка Frontend сервиса

1. **Перейдите в сервис "frontend":**

   - Кликните на карточку "frontend"

2. **Настройте переменные окружения:**
   - Перейдите в раздел "Variables"
   - Добавьте переменную для подключения к backend:

```env
# URL вашего backend сервиса
VITE_API_URL=https://your-backend-service.railway.app

# Другие переменные
NODE_ENV=production
```

**Важно:** URL backend сервиса можно найти в разделе "Settings" → "Domains" backend сервиса.

3. **Проверьте деплой:**
   - Railway автоматически начнет сборку frontend
   - Следите за логами в разделе "Deployments"

### Шаг 5: Настройка доменов

1. **Backend домен:**

   - В сервисе "backend" → "Settings" → "Domains"
   - Railway автоматически создаст домен типа `your-app-backend.railway.app`
   - Можете добавить кастомный домен

2. **Frontend домен:**

   - В сервисе "frontend" → "Settings" → "Domains"
   - Railway автоматически создаст домен типа `your-app-frontend.railway.app`
   - Можете добавить кастомный домен

3. **Обновите VITE_API_URL:**
   - Скопируйте URL backend сервиса
   - Обновите переменную `VITE_API_URL` в frontend сервисе
   - Frontend автоматически пересоберется

### Шаг 6: Проверка работоспособности

1. **Проверьте backend:**

```bash
curl https://your-backend-service.railway.app/health
```

Ожидаемый ответ:

```json
{
  "status": "ok",
  "app_name": "ITA_RENT_BOT",
  "version": "1.0.0",
  "environment": "production"
}
```

2. **Проверьте frontend:**

   - Откройте `https://your-frontend-service.railway.app`
   - Убедитесь, что страница загружается
   - Проверьте, что frontend подключается к backend

3. **Проверьте базу данных:**
   - В PostgreSQL сервисе → "Data" → "Query"
   - Выполните тестовый запрос: `SELECT version();`

## 🔧 Настройка автоматического деплоя

Railway автоматически деплоит при каждом push в main ветку:

1. **Webhook уже настроен:**

   - Railway автоматически настроил webhook в вашем GitHub репозитории

2. **Проверка автоматического деплоя:**

```bash
# Сделайте небольшое изменение
echo "# Test deployment" >> README.md
git add README.md
git commit -m "test: проверка автоматического деплоя"
git push origin main
```

3. **Отслеживание деплоя:**
   - Зайдите в Railway Dashboard
   - Следите за новыми деплоями в разделе "Deployments"

## 🐛 Отладка и мониторинг

### Просмотр логов

1. **Backend логи:**

   - Railway Dashboard → backend сервис → "Deployments"
   - Кликните на последний деплой → "View Logs"

2. **Frontend логи:**

   - Railway Dashboard → frontend сервис → "Deployments"
   - Кликните на последний деплой → "View Logs"

3. **База данных логи:**
   - Railway Dashboard → PostgreSQL сервис → "Metrics"

### Типичные проблемы и решения

1. **Backend не запускается:**

```bash
# Проверьте логи сервиса
# Убедитесь, что все переменные окружения установлены
# Проверьте, что DATABASE_URL правильно настроен
```

2. **Frontend не подключается к backend:**

```bash
# Проверьте переменную VITE_API_URL
# Убедитесь, что backend сервис доступен
# Проверьте CORS настройки в backend
```

3. **Ошибки базы данных:**

```bash
# Проверьте, что PostgreSQL сервис запущен
# Убедитесь, что DATABASE_URL корректный
# Проверьте подключение к базе данных
```

### Мониторинг

1. **Метрики Railway:**

   - CPU и память использование
   - Количество запросов
   - Время ответа

2. **Health checks:**
   - Backend: `/health` endpoint
   - Frontend: корневая страница
   - Автоматические проверки каждые 5 минут

## 💰 Стоимость

Railway предоставляет:

- **$5 бесплатно** каждый месяц
- **$0.000463 за GB-час** для compute
- **$0.25 за GB в месяц** для storage

Примерная стоимость для MVP:

- Backend: ~$3-5/месяц
- Frontend: ~$1-2/месяц
- PostgreSQL: ~$1-2/месяц
- **Итого: ~$5-9/месяц**

## 🔄 Следующие шаги

После успешного деплоя:

1. **Настройте мониторинг:**

   - Добавьте Sentry для отслеживания ошибок
   - Настройте уведомления о проблемах

2. **Безопасность:**

   - Смените SECRET_KEY на production значение
   - Настройте CORS правильно
   - Добавьте rate limiting

3. **Производительность:**

   - Настройте кеширование
   - Оптимизируйте запросы к базе данных
   - Добавьте CDN для статических файлов

4. **Кастомные домены:**
   - Настройте собственный домен
   - Добавьте SSL сертификаты

---

## 📞 Поддержка

Если возникнут проблемы:

1. **Документация Railway:** [docs.railway.app](https://docs.railway.app)
2. **Community Discord:** [discord.gg/railway](https://discord.gg/railway)
3. **GitHub Issues:** создайте issue в вашем репозитории

---

**Статус**: 🚀 Готово к деплою на Railway  
**Время деплоя**: ~15-20 минут  
**Автоматический деплой**: ✅ Настроен
