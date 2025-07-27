#!/usr/bin/env python3
"""
🚀 СКРИПТ ДЛЯ ЗАПУСКА ПАРСИНГА IMMOBILIARE.IT

Парсит главную страницу https://www.immobiliare.it/affitto-case/roma/
Извлекает все объявления и все фотографии, сохраняет в БД

Использование:
    cd src/parsers
    python run_scraping.py
    
Или из корня проекта:
    python src/parsers/run_scraping.py
"""
import sys
import asyncio
import logging
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.parsers.immobiliare_scraper import ImmobiliareScraper
from src.services.scraping_service import ScrapingService
from src.db.database import SessionLocal

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """
    Основная функция запуска парсинга
    """
    print("🚀 Парсинг Immobiliare.it (Рим)")
    
    # Геокодирование включено по умолчанию
    import sys
    enable_geocoding = True
    
    if len(sys.argv) > 1 and sys.argv[1] == "--no-geo":
        enable_geocoding = False
    
    # Инициализируем скрапер с выбранными настройками
    scraper = ImmobiliareScraper(enable_geocoding=enable_geocoding)
    scraping_service = ScrapingService()
    
    # Проверяем ScraperAPI ключ
    from src.core.config import settings
    if not settings.SCRAPERAPI_KEY:
        print("❌ ОШИБКА: SCRAPERAPI_KEY не настроен!")
        return
    
    try:
        
        import time
        start_time = time.time()
        
        listings = await scraper.scrape_multiple_pages(max_pages=10)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if not listings:
            print("❌ Объявления не найдены!")
            return
        
        # Сохраняем в базу данных
        db = SessionLocal()
        try:
            saved_stats = scraping_service.save_listings_to_db(listings, db)
            
            # Краткая сводка с таймером
            from datetime import datetime, timedelta
            next_run = datetime.now() + timedelta(hours=1)
            
            print(f"✅ Парсинг завершен: {len(listings)} объявлений за {execution_time:.1f}с")
            print(f"💾 Сохранено: {saved_stats['created']} новых, {saved_stats['updated']} обновлено")
            print(f"⏰ Следующий запуск: {next_run.strftime('%H:%M %d.%m.%Y')} (через 1ч)")
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге: {e}")
        print(f"❌ ОШИБКА: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 