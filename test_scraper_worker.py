#!/usr/bin/env python3
"""
🧪 Тест scraper worker локально
"""
import os
import sys
import asyncio

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем переменные окружения для теста
os.environ["WORKER_TYPE"] = "scraper"
os.environ["SCRAPER_WORKER_INTERVAL_HOURS"] = "1"  # 1 час для теста
os.environ["SCRAPER_WORKER_MAX_PAGES"] = "2"

async def test_worker():
    """Тест запуска воркера"""
    print("🧪 Тестируем scraper worker...")
    
    from src.workers.scraper_worker import ScraperWorker
    
    worker = ScraperWorker()
    
    # Запускаем только один цикл
    print("🚀 Запускаем один цикл парсинга...")
    success = await worker.run_scraping_cycle()
    
    if success:
        print("✅ Воркер работает корректно!")
    else:
        print("❌ Воркер не работает!")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(test_worker())
    sys.exit(0 if result else 1) 