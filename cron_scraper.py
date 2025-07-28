#!/usr/bin/env python3
"""
🤖 Entry point для Railway Cron Schedule
Запускает парсинг Immobiliare.it
"""
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Запускаем парсинг
if __name__ == "__main__":
    from src.parsers.run_scraping import main
    import asyncio
    
    print("🚀 Запуск парсинга через Railway Cron...")
    print("⏰ Расписание: каждый час в :00 минут")
    asyncio.run(main()) 