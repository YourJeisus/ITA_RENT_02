#!/usr/bin/env python3
"""
🤖 Entry point для Railway Cron Schedule - ВСЕ ИСТОЧНИКИ
Запускает параллельный парсинг всех источников:
- Immobiliare.it
- Subito.it
- Idealista.it
"""
import sys
from pathlib import Path

# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Запускаем парсинг всех источников
if __name__ == "__main__":
    from src.parsers.run_all_scraping import main
    import asyncio
    
    print("🚀 Запуск парсинга ВСЕХ источников через Railway Cron...")
    print("📊 Источники: Immobiliare.it + Subito.it + Idealista.it + Casa.it")
    print("⏰ Расписание: каждые 2 часа")
    asyncio.run(main()) 