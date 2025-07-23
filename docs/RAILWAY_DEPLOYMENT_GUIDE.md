# 🚀 Руководство по деплою в Railway

## Обзор

Этот документ описывает процесс деплоя ITA_RENT_BOT в Railway. Система настроена для автоматического деплоя при push в main ветку.

## 📋 Предварительные требования

1. ✅ GitHub репозиторий подключен к Railway
2. ✅ Настроены два сервиса: `backend` и `frontend`
3. ✅ Код готов к деплою (проверено скриптом `check_deploy_ready.py`)

## 🔧 Настройка переменных окружения

### Backend Service

Войдите в Railway Dashboard → Выберите проект → Backend Service → Variables

#### 🔴 Обязательные переменные:

```bash
# Database (Railway PostgreSQL)
DATABASE_URL=postgresql://postgres:password@host:port/database

# Security
SECRET_KEY=your-super-secure-secret-key-minimum-32-characters
ENVIRONMENT=production

# ScraperAPI для парсинга
SCRAPERAPI_KEY=your_scraperapi_key_here
```

#### 🟡 Опциональные переменные:

```bash
# Telegram Bot (для уведомлений)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Error tracking
SENTRY_DSN=https://your-sentry-dsn

# Redis (если используется)
REDIS_URL=redis://redis:6379/0

# CORS (дополнительные домены)
BACKEND_CORS_ORIGINS=["https://your-custom-domain.com"]
```

### Frontend Service

```bash
# Environment
NODE_ENV=production

# API URL (должен указывать на ваш backend)
VITE_API_URL=https://your-backend-service.railway.app
```

## 🗄️ Настройка базы данных

### 1. Добавить PostgreSQL

В Railway Dashboard:

1. Нажмите "+ New" → "Database" → "Add PostgreSQL"
2. Railway автоматически создаст переменную `DATABASE_URL`
3. Скопируйте `DATABASE_URL` в переменные backend сервиса

### 2. Применить миграции

После первого деплоя backend, выполните миграции:

1. Перейдите в Backend Service → Deployments
2. Откройте последний деплой → View Logs
3. Если нужно, выполните миграции через Railway CLI:

```bash
railway run alembic upgrade head
```

## 🚀 Процесс деплоя

### Автоматический деплой

1. **Внесите изменения** в код
2. **Закоммитьте** изменения:
   ```bash
   git add .
   git commit -m "your commit message"
   ```
3. **Запушьте** в main:
   ```bash
   git push origin main
   ```
4. **Railway автоматически** начнет деплой обоих сервисов

### Мониторинг деплоя

1. Откройте Railway Dashboard
2. Выберите ваш проект
3. Следите за статусом в разделах:
   - **Backend Service** → Deployments
   - **Frontend Service** → Deployments

### Проверка статуса

После деплоя проверьте:

#### Backend Health Check:

```bash
curl https://your-backend.railway.app/health
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

#### Frontend:

```bash
curl https://your-frontend.railway.app/
```

Должен вернуть HTML страницу React приложения.

## 🔍 Отладка проблем

### Проверка логов

#### Backend логи:

1. Railway Dashboard → Backend Service → Deployments
2. Выберите последний деплой → View Logs
3. Ищите ошибки в логах запуска

#### Frontend логи:

1. Railway Dashboard → Frontend Service → Deployments
2. Проверьте логи сборки (`npm run build`)
3. Проверьте логи запуска (`serve`)

### Частые проблемы

#### 1. Backend не запускается

**Проблема**: `ModuleNotFoundError` или `ImportError`

**Решение**:

- Проверьте `requirements.txt`
- Убедитесь что `PYTHONPATH=/app` установлен
- Проверьте структуру папок в логах

#### 2. Database Connection Error

**Проблема**: `could not connect to server`

**Решение**:

- Проверьте `DATABASE_URL` в переменных окружения
- Убедитесь что PostgreSQL сервис запущен
- Проверьте сетевые настройки Railway

#### 3. CORS Errors

**Проблема**: `Access-Control-Allow-Origin` ошибки

**Решение**:

- Обновите `BACKEND_CORS_ORIGINS` в `src/core/config.py`
- Добавьте URL фронтенда в CORS настройки
- Проверьте что домены указаны правильно

#### 4. Frontend не загружается

**Проблема**: Белая страница или 404 ошибки

**Решение**:

- Проверьте `VITE_API_URL` указывает на backend
- Убедитесь что `serve --single` используется для SPA
- Проверьте логи сборки на ошибки

## 📊 Мониторинг в production

### Health Checks

Railway автоматически проверяет:

- **Backend**: `GET /health` каждые 30 секунд
- **Frontend**: `GET /` каждые 30 секунд

### Метрики

В Railway Dashboard доступны:

- CPU и Memory usage
- Request count и response times
- Error rates
- Deployment frequency

### Логирование

Все логи доступны в реальном времени:

- Application logs (stdout/stderr)
- Build logs
- Deployment logs

## 🔄 Обновление приложения

### Hotfix

Для срочных исправлений:

```bash
git add .
git commit -m "hotfix: description"
git push origin main
```

### Feature Updates

1. Создайте feature ветку:
   ```bash
   git checkout -b feature/new-feature
   ```
2. Внесите изменения и протестируйте локально
3. Создайте Pull Request
4. После ревью мержите в main:
   ```bash
   git checkout main
   git merge feature/new-feature
   git push origin main
   ```

## 🔐 Безопасность

### Переменные окружения

- ❌ **Никогда** не коммитьте секретные ключи в код
- ✅ Используйте Railway Variables для всех секретов
- ✅ Регулярно ротируйте API ключи
- ✅ Используйте сильные SECRET_KEY (минимум 32 символа)

### HTTPS

Railway автоматически предоставляет HTTPS для всех доменов.

### Database Security

- PostgreSQL в Railway защищен по умолчанию
- Доступ только через зашифрованные соединения
- Регулярные автоматические бэкапы

## 📈 Масштабирование

### Vertical Scaling

Railway автоматически масштабирует ресурсы по необходимости.

### Monitoring

Настройте алерты в Railway Dashboard для:

- High CPU usage (>80%)
- High memory usage (>90%)
- Error rate (>5%)
- Response time (>2s)

## 🆘 Поддержка

### Полезные команды

```bash
# Проверка готовности к деплою
python check_deploy_ready.py

# Тестирование API после деплоя
python test_api.py

# Локальный запуск для отладки
python start_dev.py
```

### Контакты

- Railway Documentation: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- GitHub Issues: [Ваш репозиторий]/issues

---

**Последнее обновление**: Январь 2025  
**Версия**: 1.0.0
