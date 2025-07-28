#!/usr/bin/env python3
"""
🚀 СКРИПТ ДЛЯ ЗАПУСКА ПАРСИНГА IDEALISTA.IT

Парсит объявления с Idealista.it и сохраняет в базу данных

Использование:
    cd src/parsers
    python run_idealista_scraping.py
    
Или из корня проекта:
    python src/parsers/run_idealista_scraping.py
    
Опции:
    --no-geo    Отключить геокодирование (быстрее)
"""
import sys
import asyncio
import logging
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.parsers.idealista_scraper import IdealistaScraper
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
    Основная функция запуска парсинга Idealista.it
    """
    print("🚀 Запуск парсинга Idealista.it")
    
    # Геокодирование включено по умолчанию
    enable_geocoding = True
    
    if len(sys.argv) > 1 and sys.argv[1] == "--no-geo":
        enable_geocoding = False
        print("ℹ️ Геокодирование отключено для максимальной скорости")
    
    # Проверяем ScraperAPI ключ
    from src.core.config import settings
    if not settings.SCRAPERAPI_KEY:
        print("❌ ОШИБКА: SCRAPERAPI_KEY не настроен!")
        print("Добавьте SCRAPERAPI_KEY в .env файл")
        return
    
    # Инициализируем сервисы
    scraper = IdealistaScraper(enable_geocoding=enable_geocoding)
    scraping_service = ScrapingService()
    
    try:
        import time
        start_time = time.time()
        
        # Запускаем парсинг
        logger.info("🔍 Начинаем парсинг Idealista.it...")
        listings = await scraper.scrape_multiple_pages(max_pages=10)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n📊 Результаты парсинга Idealista.it:")
        print(f"   • Найдено объявлений: {len(listings)}")
        print(f"   • Время выполнения: {execution_time:.1f} сек")
        print(f"   • Скорость: {len(listings)/execution_time:.1f} объявлений/сек")
        
        if not listings:
            print("⚠️ Объявления не найдены. Проверьте настройки ScraperAPI или структуру сайта.")
            return
        
        # Сохраняем в базу данных
        print(f"\n💾 Сохраняем {len(listings)} объявлений в базу данных...")
        
        db = SessionLocal()
        try:
            saved_count = 0
            updated_count = 0
            
            for listing in listings:
                try:
                    result = scraping_service.save_listing(db, listing)
                    if result == "created":
                        saved_count += 1
                    elif result == "updated":
                        updated_count += 1
                except Exception as e:
                    logger.error(f"❌ Ошибка сохранения объявления {listing.get('external_id', 'unknown')}: {e}")
                    continue
            
            db.commit()
            
            print(f"✅ Успешно сохранено:")
            print(f"   • Новых объявлений: {saved_count}")
            print(f"   • Обновленных объявлений: {updated_count}")
            print(f"   • Общий прогресс: {saved_count + updated_count}/{len(listings)}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при работе с базой данных: {e}")
            db.rollback()
        finally:
            db.close()
        
        # Примеры объявлений
        if listings:
            print(f"\n📋 Первые 3 объявления:")
            for i, listing in enumerate(listings[:3], 1):
                print(f"\n{i}. {listing.get('title', 'Без названия')[:60]}...")
                print(f"   💰 Цена: {listing.get('price', 0)}€/месяц")
                if listing.get('area'):
                    print(f"   📐 Площадь: {listing.get('area')} м²")
                if listing.get('rooms'):
                    print(f"   🚪 Комнаты: {listing.get('rooms')}")
                print(f"   📍 Адрес: {listing.get('address', 'N/A')}")
                if listing.get('latitude') and listing.get('longitude'):
                    print(f"   🗺️ Координаты: {listing.get('latitude'):.4f}, {listing.get('longitude'):.4f}")
                print(f"   🔗 URL: {listing.get('url', 'N/A')[:80]}...")
        
    except KeyboardInterrupt:
        print("\n⏹️ Парсинг прерван пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 