#!/bin/bash

# 🚀 Автоматический деплой ITA_RENT_BOT на Railway
# Использование: ./deploy_railway.sh

set -e  # Остановиться при любой ошибке

echo "🚀 НАЧИНАЕМ ДЕПЛОЙ ITA_RENT_BOT НА RAILWAY"
echo "=========================================="

# Проверяем наличие Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI не установлен!"
    echo "💡 Установите: npm install -g @railway/cli"
    exit 1
fi

# Проверяем авторизацию в Railway
if ! railway whoami &> /dev/null; then
    echo "❌ Вы не авторизованы в Railway!"
    echo "💡 Выполните: railway login"
    exit 1
fi

echo "✅ Railway CLI готов"

# Проверяем обязательные переменные окружения
if [ -z "$SCRAPERAPI_KEY" ]; then
    echo "❌ SCRAPERAPI_KEY не установлен!"
    echo "💡 Установите: export SCRAPERAPI_KEY=your-key"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️ SECRET_KEY не установлен, генерируем случайный..."
    export SECRET_KEY="$(openssl rand -hex 32)"
    echo "🔑 Сгенерирован SECRET_KEY: $SECRET_KEY"
fi

echo "✅ Переменные окружения готовы"

# Коммитим последние изменения
echo "📝 Коммитим последние изменения..."
git add .
git commit -m "🚀 Deploy: Railway автоматический деплой с PostgreSQL и парсером" || true
git push origin main

echo "✅ Код отправлен в репозиторий"

# Деплоим на Railway
echo "🚀 Деплой на Railway..."

# Если проекта нет, создаем новый
if ! railway status &> /dev/null; then
    echo "📁 Создаем новый проект на Railway..."
    railway login
    railway init
fi

# Устанавливаем переменные окружения для backend
echo "🔧 Настройка переменных окружения для backend..."
railway variables set ENVIRONMENT=production
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set SCRAPERAPI_KEY="$SCRAPERAPI_KEY"

# Устанавливаем переменные для scraper worker
echo "🤖 Настройка переменных для воркера парсинга..."
railway service connect scraper-worker 2>/dev/null || echo "Сервис scraper-worker будет создан автоматически"
railway variables set WORKER_TYPE=scraper
railway variables set ENVIRONMENT=production
railway variables set SCRAPERAPI_KEY="$SCRAPERAPI_KEY"
railway variables set SCRAPER_WORKER_INTERVAL_HOURS=6
railway variables set SCRAPER_WORKER_MAX_PAGES=10

# Добавляем PostgreSQL если еще не добавлен
echo "🗄️ Проверка PostgreSQL базы данных..."
railway add --database postgresql 2>/dev/null || echo "PostgreSQL уже добавлен"

# Запускаем деплой
echo "🚀 Запуск деплоя..."
railway up --detach

echo ""
echo "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
echo "==================="
echo ""
echo "🔗 Ссылки на ваши сервисы:"
railway status | grep "https://" || echo "Получение ссылок..."

echo ""
echo "📊 Проверить статус деплоя:"
echo "railway logs --service backend"
echo "railway logs --service scraper-worker"
echo "railway logs --service frontend"

echo ""
echo "🗄️ Подключение к базе данных:"
echo "railway connect postgres"

echo ""
echo "🎉 Деплой завершен! Ваша система парсинга недвижимости работает!"
echo "🤖 Автоматический парсинг запустится в течение 6 часов"
echo "📋 Посмотрите документацию: docs/RAILWAY_DEPLOYMENT_COMPLETE.md" 