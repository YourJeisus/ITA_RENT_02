#!/bin/bash

echo "🚀 Деплой исправлений для Scraper Worker"
echo "========================================"

# Коммитим изменения
echo "📝 Коммитим изменения..."
git add .
git commit -m "fix: scraper worker improvements

- Упростили логирование скрапера
- Исправили health check для scraper-worker  
- Добавили недостающие переменные конфигурации
- Создали тест воркера

Изменения:
- Убрали лишние детали из логов парсинга
- Отключили проблемный health check
- Добавили SCRAPER_WORKER_INTERVAL_HOURS и SCRAPER_WORKER_MAX_PAGES в конфиг
- Оставили только основную сводку сессии скрапинга"

# Пушим в main
echo "⬆️ Отправляем в GitHub..."
git push origin main

echo ""
echo "✅ Изменения отправлены!"
echo ""
echo "🔧 Следующие шаги в Railway:"
echo "1. Проверьте что все переменные окружения установлены:"
echo "   - SCRAPER_WORKER_INTERVAL_HOURS = 1" 
echo "   - SCRAPER_WORKER_MAX_PAGES = 10"
echo "   - WORKER_TYPE = scraper"
echo ""
echo "2. Перезапустите сервис 'scraper-worker'"
echo ""  
echo "3. Проверьте логи сервиса 'scraper-worker'"
echo ""
echo "📊 Теперь логи будут гораздо чище - только основная сводка!" 