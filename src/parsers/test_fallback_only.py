#!/usr/bin/env python3
"""
🧪 ТЕСТОВЫЙ СКРИПТ ТОЛЬКО ДЛЯ FALLBACK МЕТОДА
Тестирует обычный ScraperAPI без async функций

Использование:
    python src/parsers/test_fallback_only.py
"""
import sys
import os
import asyncio
import logging
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.parsers.immobiliare_parser_async import ImmobiliareAsyncParser
from src.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'fallback_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


async def test_fallback_only():
    """Тестирует только fallback метод на 3 страницах"""
    logger.info("🚀 ТЕСТИРОВАНИЕ ТОЛЬКО FALLBACK МЕТОДА")
    logger.info(f"🔑 SCRAPERAPI_KEY настроен: {'✅' if settings.SCRAPERAPI_KEY else '❌'}")
    
    if not settings.SCRAPERAPI_KEY:
        logger.error("❌ SCRAPERAPI_KEY не настроен! Установите в .env файле")
        return False
    
    # Создаем парсер без геокодирования для скорости
    parser = ImmobiliareAsyncParser(enable_geocoding=False)
    
    # Тестируем fallback на 3 страницах
    max_pages = 3
    logger.info(f"📄 Тестируем fallback на {max_pages} страницах...")
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        all_listings = []
        successful_pages = 0
        
        # Парсим каждую страницу последовательно через fallback
        for page_num in range(1, max_pages + 1):
            logger.info(f"📄 Обрабатываем страницу {page_num}...")
            
            page_listings = await parser.scrape_page_fallback(page_num)
            
            if page_listings:
                all_listings.extend(page_listings)
                successful_pages += 1
                logger.info(f"✅ Страница {page_num}: найдено {len(page_listings)} объявлений")
            else:
                logger.warning(f"⚠️ Страница {page_num}: объявления не найдены")
        
        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time
        
        # Дедупликация
        unique_listings = []
        seen_ids = set()
        
        for listing in all_listings:
            listing_id = listing.get('external_id')
            if listing_id and listing_id not in seen_ids:
                seen_ids.add(listing_id)
                unique_listings.append(listing)
        
        logger.info("📊 РЕЗУЛЬТАТЫ FALLBACK ТЕСТА:")
        logger.info(f"   ⏱️ Общее время: {elapsed_time:.1f}с")
        logger.info(f"   ✅ Успешных страниц: {successful_pages}/{max_pages}")
        logger.info(f"   📋 Всего объявлений: {len(all_listings)}")
        logger.info(f"   🔄 Уникальных объявлений: {len(unique_listings)}")
        
        if unique_listings:
            # Анализ результатов
            photo_counts = [len(listing.get('images', [])) for listing in unique_listings]
            avg_photos = sum(photo_counts) / len(photo_counts) if photo_counts else 0
            
            property_types = {}
            for listing in unique_listings:
                prop_type = listing.get('property_type', 'unknown')
                property_types[prop_type] = property_types.get(prop_type, 0) + 1
            
            logger.info(f"   📸 Среднее фото/объявление: {avg_photos:.1f}")
            logger.info(f"   🏠 Типы недвижимости: {list(property_types.keys())}")
            
            # Показываем примеры
            logger.info(f"   📝 Примеры объявлений:")
            for i, listing in enumerate(unique_listings[:3], 1):
                title = listing.get('title', 'Без названия')[:50]
                price = listing.get('price', 'N/A')
                prop_type = listing.get('property_type', 'N/A')
                photos = len(listing.get('images', []))
                
                logger.info(f"      {i}. {title}...")
                logger.info(f"         💰 {price}€ | 🏠 {prop_type} | 📸 {photos} фото")
            
            # Оценка успешности
            if len(unique_listings) >= 5 and successful_pages >= 1:
                logger.info("🎉 FALLBACK ТЕСТ УСПЕШЕН! Метод работает.")
                return True
            else:
                logger.warning("⚠️ FALLBACK ТЕСТ ЧАСТИЧНО УСПЕШЕН.")
                return len(unique_listings) > 0
        else:
            logger.error("❌ FALLBACK ТЕСТ ПРОВАЛЕН. Объявления не найдены.")
            return False
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в fallback тесте: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Основная функция"""
    result = await test_fallback_only()
    
    if result:
        logger.info("✅ Fallback тестирование завершено успешно!")
        sys.exit(0)
    else:
        logger.error("❌ Fallback тестирование провалено!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 