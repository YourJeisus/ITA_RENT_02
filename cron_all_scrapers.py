#!/usr/bin/env python3
"""
🤖 Entry point для Railway Cron Schedule - ВСЕ ИСТОЧНИКИ
Запускает параллельный парсинг всех источников:
- Immobiliare.it
- Subito.it
- Idealista.it
"""
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Запускаем парсинг всех источников
if __name__ == "__main__":
    from src.parsers.run_all_scraping import main
    import asyncio
    
    print("🚀 Запуск парсинга ВСЕХ источников через Railway Cron...")
    print("📊 Источники: Immobiliare.it + Subito.it + Idealista.it")
    print("⏰ Расписание: каждые 2 часа")
    asyncio.run(main()) 