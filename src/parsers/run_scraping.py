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
    print("🚀 ЗАПУСК ПАРСИНГА IMMOBILIARE.IT")
    print("=" * 60)
    print("🎯 Цель: https://www.immobiliare.it/affitto-case/roma/")
    print("📋 Задача: Спарсить ВСЕ объявления и ВСЕ фотографии")
    print("💾 Результат: Сохранить в базу данных")
    print("=" * 60)
    
    # Геокодирование включено по умолчанию
    import sys
    enable_geocoding = True
    
    if len(sys.argv) > 1 and sys.argv[1] == "--no-geo":
        enable_geocoding = False
        print("🚀 РЕЖИМ: БЕЗ ГЕОКОДИРОВАНИЯ (ускорение ~4%)")
    else:
        print("🗺️  РЕЖИМ: С ГЕОКОДИРОВАНИЕМ (полные данные, рекомендуется)")
    
    print("💡 Для ускорения на 4%: python run_scraping.py --no-geo")
    print("=" * 60)
    
    # Инициализируем скрапер с выбранными настройками
    scraper = ImmobiliareScraper(enable_geocoding=enable_geocoding)
    scraping_service = ScrapingService()
    
    # Проверяем ScraperAPI ключ
    from src.core.config import settings
    if not settings.SCRAPERAPI_KEY:
        print("❌ ОШИБКА: SCRAPERAPI_KEY не настроен!")
        print("💡 Добавьте SCRAPERAPI_KEY в файл .env")
        return
    
    print(f"✅ ScraperAPI ключ настроен")
    
    try:
        # Запускаем парсинг (максимум 10 страниц)
        print(f"\n🔄 НАЧИНАЕМ АСИНХРОННЫЙ ПАРСИНГ...")
        print(f"⚡ Все {10} страниц будут обрабатываться параллельно!")
        
        import time
        start_time = time.time()
        
        listings = await scraper.scrape_multiple_pages(max_pages=10)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if not listings:
            print("❌ Объявления не найдены!")
            return
        
        print(f"\n🎉 Парсинг завершен за {execution_time:.1f}с: {len(listings)} объявлений")
        
        # Сохраняем в базу данных
        db = SessionLocal()
        try:
            saved_stats = scraping_service.save_listings_to_db(listings, db)
            print(f"💾 Сохранено: {saved_stats['created']} новых, {saved_stats['updated']} обновлено")
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге: {e}")
        print(f"❌ ОШИБКА: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 