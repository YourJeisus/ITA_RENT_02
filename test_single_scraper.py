#!/usr/bin/env python3
"""
🧪 ТЕСТ ОТДЕЛЬНЫХ СКРАПЕРОВ

Позволяет протестировать работу каждого скрапера отдельно
для диагностики проблем

Использование:
    python test_single_scraper.py idealista
    python test_single_scraper.py immobiliare  
    python test_single_scraper.py subito
    python test_single_scraper.py all
"""
import sys
import asyncio
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from src.parsers.idealista_scraper import IdealistaScraper
from src.parsers.immobiliare_scraper import ImmobiliareScraper
from src.parsers.subito_scraper import SubitoScraper
from src.services.scraping_service import ScrapingService
from src.db.database import SessionLocal
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_idealista():
    """Тест Idealista scraper"""
    print("\n" + "="*50)
    print("🏠 ТЕСТ IDEALISTA SCRAPER")
    print("="*50)
    
    try:
        scraper = IdealistaScraper(enable_geocoding=False)  # Отключаем геокодирование для быстроты
        
        print("🚀 Запуск парсинга Idealista (2 страницы)...")
        start_time = datetime.now()
        
        listings = await scraper.scrape_multiple_pages(max_pages=2)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Парсинг Idealista завершен за {duration:.1f}с")
        print(f"📊 Найдено объявлений: {len(listings)}")
        
        if listings:
            print(f"\n📋 Примеры объявлений:")
            for i, listing in enumerate(listings[:3], 1):
                title = listing.get('title', 'Без названия')[:50]
                price = listing.get('price', 'Цена не указана')
                city = listing.get('city', 'Город не указан')
                external_id = listing.get('external_id', 'ID отсутствует')
                
                print(f"   {i}. {title}...")
                print(f"      💰 {price} | 📍 {city} | ID: {external_id}")
        
        return len(listings)
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Idealista: {e}")
        return 0


async def test_immobiliare():
    """Тест Immobiliare scraper"""
    print("\n" + "="*50)
    print("🏠 ТЕСТ IMMOBILIARE SCRAPER")
    print("="*50)
    
    try:
        scraper = ImmobiliareScraper(enable_geocoding=False)
        
        print("🚀 Запуск парсинга Immobiliare (2 страницы)...")
        start_time = datetime.now()
        
        listings = await scraper.scrape_multiple_pages(max_pages=2)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Парсинг Immobiliare завершен за {duration:.1f}с")
        print(f"📊 Найдено объявлений: {len(listings)}")
        
        if listings:
            print(f"\n📋 Примеры объявлений:")
            for i, listing in enumerate(listings[:3], 1):
                title = listing.get('title', 'Без названия')[:50]
                price = listing.get('price', 'Цена не указана')
                city = listing.get('city', 'Город не указан')
                external_id = listing.get('external_id', 'ID отсутствует')
                
                print(f"   {i}. {title}...")
                print(f"      💰 {price} | 📍 {city} | ID: {external_id}")
        
        return len(listings)
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Immobiliare: {e}")
        return 0


async def test_subito():
    """Тест Subito scraper"""
    print("\n" + "="*50)
    print("🏠 ТЕСТ SUBITO SCRAPER")
    print("="*50)
    
    try:
        scraper = SubitoScraper(enable_geocoding=False)
        
        print("🚀 Запуск парсинга Subito (2 страницы)...")
        start_time = datetime.now()
        
        listings = await scraper.scrape_multiple_pages(max_pages=2)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Парсинг Subito завершен за {duration:.1f}с")
        print(f"📊 Найдено объявлений: {len(listings)}")
        
        if listings:
            print(f"\n📋 Примеры объявлений:")
            for i, listing in enumerate(listings[:3], 1):
                title = listing.get('title', 'Без названия')[:50]
                price = listing.get('price', 'Цена не указана')
                city = listing.get('city', 'Город не указан')
                external_id = listing.get('external_id', 'ID отсутствует')
                
                print(f"   {i}. {title}...")
                print(f"      💰 {price} | 📍 {city} | ID: {external_id}")
        
        return len(listings)
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Subito: {e}")
        return 0


async def test_all_scrapers():
    """Тест всех скраперов"""
    print("\n" + "="*50)
    print("🚀 ТЕСТ ВСЕХ СКРАПЕРОВ")
    print("="*50)
    
    results = {}
    
    # Тестируем каждый скрапер
    results['idealista'] = await test_idealista()
    results['immobiliare'] = await test_immobiliare()
    results['subito'] = await test_subito()
    
    # Итоговая статистика
    print("\n" + "="*50)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("="*50)
    
    total_listings = sum(results.values())
    
    for source, count in results.items():
        status = "✅" if count > 0 else "❌"
        print(f"   {status} {source.upper()}: {count} объявлений")
    
    print(f"\n🎯 Общий итог: {total_listings} объявлений")
    
    if total_listings == 0:
        print("⚠️ ВНИМАНИЕ: Ни один скрапер не вернул объявления!")
        print("   Проверьте:")
        print("   • SCRAPERAPI_KEY в переменных окружения")
        print("   • Интернет соединение")
        print("   • Работоспособность сайтов")
    else:
        print("✅ Система скрапинга работает корректно")


async def save_test_results(all_listings: list):
    """Сохраняет результаты тестирования в БД"""
    if not all_listings:
        print("❌ Нет объявлений для сохранения")
        return
    
    print(f"\n💾 Сохранение {len(all_listings)} объявлений в БД...")
    
    db = SessionLocal()
    try:
        scraping_service = ScrapingService()
        saved_stats = scraping_service.save_listings_to_db(all_listings, db)
        
        print(f"✅ Сохранение завершено:")
        print(f"   • Новых: {saved_stats['created']}")
        print(f"   • Обновлено: {saved_stats['updated']}")
        print(f"   • Дубликатов пропущено: {saved_stats.get('skipped_duplicates', 0)}")
        print(f"   • Ошибок: {saved_stats['errors']}")
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
    finally:
        db.close()


async def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("❌ Использование: python test_single_scraper.py <scraper>")
        print("   Доступные варианты: idealista, immobiliare, subito, all")
        return
    
    scraper_name = sys.argv[1].lower()
    
    print("🧪 ТЕСТИРОВАНИЕ СКРАПЕРОВ ITA_RENT_BOT")
    print("=" * 50)
    print(f"⏰ Время запуска: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    
    # Проверяем настройки
    try:
        from src.core.config import settings
        if not settings.SCRAPERAPI_KEY:
            print("❌ ОШИБКА: SCRAPERAPI_KEY не настроен!")
            return
        print(f"✅ SCRAPERAPI_KEY настроен")
    except Exception as e:
        print(f"❌ Ошибка настроек: {e}")
        return
    
    all_listings = []
    
    # Запускаем нужный тест
    if scraper_name == "idealista":
        count = await test_idealista()
    elif scraper_name == "immobiliare":
        count = await test_immobiliare()
    elif scraper_name == "subito":
        count = await test_subito()
    elif scraper_name == "all":
        await test_all_scrapers()
    else:
        print(f"❌ Неизвестный скрапер: {scraper_name}")
        print("   Доступные: idealista, immobiliare, subito, all")
        return
    
    print("\n" + "="*50)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main()) 