#!/usr/bin/env python3
"""
🤖 Entry point для Railway Cron Schedule - IDEALISTA.IT
Запускает парсинг только Idealista.it
"""
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Запускаем парсинг Idealista.it
if __name__ == "__main__":
    from src.parsers.run_idealista_scraping import main
    import asyncio
    
    print("🚀 Запуск парсинга Idealista.it через Railway Cron...")
    print("📊 Источник: Idealista.it")
    print("⏰ Расписание: каждые 3 часа")
    asyncio.run(main()) 