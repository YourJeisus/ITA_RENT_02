#!/usr/bin/env python3
"""
🤖 Entry point для Railway Cron Schedule - Subito.it
Запускает парсинг Subito.it
"""
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Запускаем парсинг Subito.it
if __name__ == "__main__":
    from src.parsers.run_subito_scraping import main
    import asyncio
    
    print("🚀 Запуск парсинга Subito.it через Railway Cron...")
    print("⏰ Расписание: каждый час в :30 минут")
    asyncio.run(main()) 