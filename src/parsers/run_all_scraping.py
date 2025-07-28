#!/usr/bin/env python3
"""
🚀 СКРИПТ ДЛЯ ЗАПУСКА ПАРСИНГА ВСЕХ ИСТОЧНИКОВ

Парсит объявления с:
- Immobiliare.it
- Subito.it  
- Idealista.it

Запускает парсинг параллельно для максимальной скорости

Использование:
    cd src/parsers
    python run_all_scraping.py
    
Или из корня проекта:
    python src/parsers/run_all_scraping.py
"""
import sys
import asyncio
import logging
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.parsers.immobiliare_scraper import ImmobiliareScraper
from src.parsers.subito_scraper import SubitoScraper
from src.parsers.idealista_scraper import IdealistaScraper
from src.services.scraping_service import ScrapingService
from src.db.database import SessionLocal

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def scrape_source(scraper, source_name: str):
    """Парсит один источник и возвращает результаты"""
    try:
        logger.info(f"🚀 Запуск парсинга: {source_name}")
        listings = await scraper.scrape_multiple_pages(max_pages=10)
        logger.info(f"✅ {source_name}: получено {len(listings)} объявлений")
        return source_name, listings
    except Exception as e:
        logger.error(f"❌ Ошибка парсинга {source_name}: {e}")
        return source_name, []


async def main():
    """
    Основная функция запуска парсинга всех источников
    """
    print("🚀 Параллельный парсинг всех источников")
    
    # Геокодирование включено по умолчанию
    enable_geocoding = True
    
    if len(sys.argv) > 1 and sys.argv[1] == "--no-geo":
        enable_geocoding = False
    
    # Проверяем ScraperAPI ключ
    from src.core.config import settings
    if not settings.SCRAPERAPI_KEY:
        print("❌ ОШИБКА: SCRAPERAPI_KEY не настроен!")
        return
    
    # Инициализируем скраперы
    immobiliare_scraper = ImmobiliareScraper(enable_geocoding=enable_geocoding)
    subito_scraper = SubitoScraper(enable_geocoding=enable_geocoding)
    idealista_scraper = IdealistaScraper(enable_geocoding=enable_geocoding)
    scraping_service = ScrapingService()
    
    try:
        import time
        start_time = time.time()
        
        # Запускаем парсинг всех источников параллельно
        results = await asyncio.gather(
            scrape_source(immobiliare_scraper, "Immobiliare.it"),
            scrape_source(subito_scraper, "Subito.it"),
            scrape_source(idealista_scraper, "Idealista.it"),
            return_exceptions=True
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Обрабатываем результаты
        all_listings = []
        stats_by_source = {}
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Ошибка при парсинге: {result}")
                continue
                
            source_name, listings = result
            stats_by_source[source_name] = len(listings)
            all_listings.extend(listings)
        
        if not all_listings:
            print("❌ Объявления не найдены ни в одном источнике!")
            return
        
        # Сохраняем в базу данных
        db = SessionLocal()
        try:
            saved_stats = scraping_service.save_listings_to_db(all_listings, db)
            
            # Подробная сводка
            from datetime import datetime, timedelta
            next_run = datetime.now() + timedelta(hours=1)
            
            print(f"\n✅ Парсинг всех источников завершен за {execution_time:.1f}с")
            print(f"📊 Статистика по источникам:")
            for source, count in stats_by_source.items():
                print(f"   • {source}: {count} объявлений")
            
            print(f"\n💾 Сохранено в БД:")
            print(f"   • Новых: {saved_stats['created']}")
            print(f"   • Обновлено: {saved_stats['updated']}")
            print(f"   • Общий итог: {len(all_listings)} объявлений")
            
            print(f"\n⏰ Следующий запуск: {next_run.strftime('%H:%M %d.%m.%Y')} (через 1ч)")
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 