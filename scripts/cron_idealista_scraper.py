#!/usr/bin/env python3
"""
🤖 Entry point для Railway Cron Schedule - IDEALISTA.IT
Запускает парсинг только Idealista.it
"""
import sys
from pathlib import Path

# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Запускаем парсинг Idealista.it
if __name__ == "__main__":
    from src.parsers.run_idealista_scraping import main
    import asyncio
    
    print("🚀 Запуск парсинга Idealista.it через Railway Cron...")
    print("📊 Источник: Idealista.it")
    print("⏰ Расписание: каждые 3 часа")
    asyncio.run(main()) 