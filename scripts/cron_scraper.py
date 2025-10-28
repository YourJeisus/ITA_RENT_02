#!/usr/bin/env python3
"""
🤖 Entry point для Railway Cron Schedule
Запускает парсинг Immobiliare.it
"""
import sys
from pathlib import Path

# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Запускаем парсинг
if __name__ == "__main__":
    from src.parsers.run_scraping import main
    import asyncio
    
    print("🚀 Запуск парсинга через Railway Cron...")
    print("⏰ Расписание: каждый час в :00 минут")
    asyncio.run(main()) 