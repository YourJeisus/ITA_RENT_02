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

from src.parsers.immobiliare_parser import ImmobiliareParser
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
    
    # Инициализируем парсер с выбранными настройками
    parser = ImmobiliareParser(enable_geocoding=enable_geocoding)
    scraping_service = ScrapingService()
    
    # Проверяем ScraperAPI ключ
    if not parser.scraperapi_key:
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
        
        listings = await parser.scrape_all_listings(max_pages=10)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if not listings:
            print("❌ Объявления не найдены!")
            return
        
        print(f"\n📊 РЕЗУЛЬТАТЫ АСИНХРОННОГО ПАРСИНГА:")
        print(f"   📋 Всего объявлений: {len(listings)}")
        print(f"   ⏱️  Время выполнения: {execution_time:.2f} секунд")
        print(f"   ⚡ Скорость: {len(listings)/execution_time:.2f} объявлений/сек")
        
        # Статистика по фотографиям
        total_photos = sum(len(listing.get('images', [])) for listing in listings)
        listings_with_photos = sum(1 for listing in listings if listing.get('images'))
        
        print(f"   📸 Всего фотографий: {total_photos}")
        print(f"   🖼️  Объявлений с фото: {listings_with_photos}/{len(listings)}")
        print(f"   📷 Среднее фото на объявление: {total_photos/len(listings):.1f}")
        
        # Статистика по координатам
        with_coords = sum(1 for listing in listings if listing.get('latitude') and listing.get('longitude'))
        print(f"   🗺️  С координатами: {with_coords}/{len(listings)}")
        
        # Сохраняем в базу данных
        print(f"\n💾 СОХРАНЕНИЕ В БАЗУ ДАННЫХ...")
        
        db = SessionLocal()
        try:
            saved_stats = scraping_service.save_listings_to_db(listings, db)
            
            print(f"✅ СОХРАНЕНИЕ ЗАВЕРШЕНО:")
            print(f"   ➕ Создано новых: {saved_stats['created']}")
            print(f"   🔄 Обновлено: {saved_stats['updated']}")
            print(f"   ❌ Ошибок: {saved_stats['errors']}")
            
        finally:
            db.close()
        
        # Показываем примеры объявлений
        print(f"\n🏠 ПРИМЕРЫ ОБЪЯВЛЕНИЙ:")
        print("-" * 60)
        
        for i, listing in enumerate(listings[:3], 1):
            print(f"{i}. {listing.get('title', 'Без названия')[:50]}...")
            print(f"   🆔 ID: {listing.get('external_id', 'N/A')}")
            print(f"   💰 Цена: {listing.get('price', 'N/A')}€/месяц")
            print(f"   📐 Площадь: {listing.get('area', 'N/A')} м²")
            print(f"   🚪 Комнат: {listing.get('rooms', 'N/A')}")
            print(f"   📸 Фото: {len(listing.get('images', []))} шт.")
            print(f"   🗺️  Координаты: {'✅' if listing.get('latitude') else '❌'}")
            print(f"   🔗 URL: {listing.get('url', 'N/A')}")
            print()
        
        print("🎉 ПАРСИНГ УСПЕШНО ЗАВЕРШЕН!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге: {e}")
        print(f"❌ ОШИБКА: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 