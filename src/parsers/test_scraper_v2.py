#!/usr/bin/env python3
"""
🧪 ТЕСТОВЫЙ СКРИПТ ДЛЯ НОВОГО АСИНХРОННОГО СКРАПЕРА V2
Проверяет правильность работы с разными страницами и дедупликацией

Использование:
    python src/parsers/test_scraper_v2.py [количество_страниц]
"""
import sys
import os
import asyncio
import logging
import json
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.parsers.immobiliare_async_scraper_v2 import ImmobiliareAsyncScraperV2
from src.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'scraper_v2_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


async def test_scraper_v2():
    """Тестирует новый асинхронный скрапер V2"""
    logger.info("🚀 ТЕСТИРОВАНИЕ НОВОГО АСИНХРОННОГО СКРАПЕРА V2")
    logger.info(f"🔑 SCRAPERAPI_KEY настроен: {'✅' if settings.SCRAPERAPI_KEY else '❌'}")
    
    if not settings.SCRAPERAPI_KEY:
        logger.error("❌ SCRAPERAPI_KEY не настроен! Установите в .env файле")
        return False
    
    # Получаем количество страниц из аргументов
    max_pages = 5
    if len(sys.argv) > 1:
        try:
            max_pages = int(sys.argv[1])
        except ValueError:
            logger.warning("⚠️ Неверный аргумент, используем 5 страниц по умолчанию")
    
    logger.info(f"📄 Тестируем на {max_pages} страницах...")
    
    # Создаем скрапер с геокодированием
    scraper = ImmobiliareAsyncScraperV2(enable_geocoding=True)
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Запускаем скрапинг
        listings = await scraper.scrape_multiple_pages(max_pages=max_pages)
        
        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time
        
        if not listings:
            logger.error("❌ Не найдено ни одного объявления")
            return False
        
        # Подробный анализ результатов
        logger.info("📊 ПОДРОБНЫЙ АНАЛИЗ РЕЗУЛЬТАТОВ:")
        logger.info(f"   ⏱️ Общее время: {elapsed_time:.1f}с")
        logger.info(f"   📋 Найдено объявлений: {len(listings)}")
        logger.info(f"   ⚡ Скорость: {len(listings)/elapsed_time:.2f} объявлений/сек")
        
        # Проверяем уникальность по external_id
        external_ids = [listing.get('external_id') for listing in listings if listing.get('external_id')]
        unique_ids = set(external_ids)
        
        logger.info(f"   🔄 Проверка дедупликации:")
        logger.info(f"      Всего external_id: {len(external_ids)}")
        logger.info(f"      Уникальных external_id: {len(unique_ids)}")
        logger.info(f"      Дубликатов: {len(external_ids) - len(unique_ids)}")
        
        if len(external_ids) == len(unique_ids):
            logger.info("   ✅ Дедупликация работает идеально!")
        else:
            logger.warning("   ⚠️ Обнаружены дубликаты!")
        
        # Анализ фотографий
        photo_counts = [len(listing.get('images', [])) for listing in listings]
        if photo_counts:
            avg_photos = sum(photo_counts) / len(photo_counts)
            max_photos = max(photo_counts)
            min_photos = min(photo_counts)
            total_photos = sum(photo_counts)
            
            logger.info(f"   📸 Статистика фотографий:")
            logger.info(f"      📊 Среднее: {avg_photos:.1f} фото/объявление")
            logger.info(f"      📈 Максимум: {max_photos} фото")
            logger.info(f"      📉 Минимум: {min_photos} фото")
            logger.info(f"      🎯 Всего фото: {total_photos}")
        
        # Анализ координат
        with_coords = sum(1 for listing in listings if listing.get('latitude') and listing.get('longitude'))
        coord_percentage = (with_coords / len(listings)) * 100
        
        logger.info(f"   🗺️ Геолокация:")
        logger.info(f"      С координатами: {with_coords}/{len(listings)} ({coord_percentage:.1f}%)")
        
        # Анализ типов недвижимости
        property_types = {}
        for listing in listings:
            prop_type = listing.get('property_type', 'unknown')
            property_types[prop_type] = property_types.get(prop_type, 0) + 1
        
        logger.info(f"   🏠 Типы недвижимости:")
        for prop_type, count in sorted(property_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(listings)) * 100
            logger.info(f"      {prop_type}: {count} ({percentage:.1f}%)")
        
        # Анализ цен
        prices = [listing.get('price') for listing in listings if listing.get('price')]
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            logger.info(f"   💰 Статистика цен:")
            logger.info(f"      📊 Средняя: {avg_price:.0f}€")
            logger.info(f"      📉 Минимальная: {min_price}€")
            logger.info(f"      📈 Максимальная: {max_price}€")
        
        # Анализ площади
        areas = [listing.get('area') for listing in listings if listing.get('area')]
        if areas:
            avg_area = sum(areas) / len(areas)
            min_area = min(areas)
            max_area = max(areas)
            
            logger.info(f"   📐 Статистика площади:")
            logger.info(f"      📊 Средняя: {avg_area:.0f}м²")
            logger.info(f"      📉 Минимальная: {min_area}м²")
            logger.info(f"      📈 Максимальная: {max_area}м²")
        
        # Показываем примеры объявлений
        logger.info(f"   📝 Примеры объявлений:")
        for i, listing in enumerate(listings[:5], 1):
            title = listing.get('title', 'Без названия')[:60]
            price = listing.get('price', 'N/A')
            prop_type = listing.get('property_type', 'N/A')
            photos = len(listing.get('images', []))
            coords = '✅' if listing.get('latitude') and listing.get('longitude') else '❌'
            external_id = listing.get('external_id', 'N/A')
            
            logger.info(f"      {i}. {title}...")
            logger.info(f"         💰 {price}€ | 🏠 {prop_type} | 📸 {photos} фото | 🗺️ {coords} | 🆔 {external_id}")
        
        # Проверяем разнообразие external_id (что страницы действительно разные)
        if len(unique_ids) >= max_pages * 15:  # Ожидаем минимум 15 уникальных объявлений на страницу
            logger.info("   ✅ Страницы содержат разные объявления!")
        else:
            logger.warning(f"   ⚠️ Мало уникальных объявлений для {max_pages} страниц")
        
        # Сохраняем результаты в JSON файл
        output_file = f"scraper_v2_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "scraper_version": "ImmobiliareAsyncScraperV2",
                "total_listings": len(listings),
                "unique_listings": len(unique_ids),
                "pages_scraped": max_pages,
                "elapsed_time_seconds": elapsed_time,
                "statistics": {
                    "photos": {
                        "average": avg_photos if photo_counts else 0,
                        "total": sum(photo_counts) if photo_counts else 0,
                        "max": max(photo_counts) if photo_counts else 0,
                        "min": min(photo_counts) if photo_counts else 0
                    },
                    "coordinates": {
                        "with_coords": with_coords,
                        "percentage": coord_percentage
                    },
                    "property_types": property_types,
                    "prices": {
                        "average": avg_price if prices else 0,
                        "min": min_price if prices else 0,
                        "max": max_price if prices else 0,
                        "count": len(prices)
                    } if prices else None,
                    "areas": {
                        "average": avg_area if areas else 0,
                        "min": min_area if areas else 0,
                        "max": max_area if areas else 0,
                        "count": len(areas)
                    } if areas else None
                }
            },
            "listings": listings
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"💾 Результаты сохранены в файл: {output_file}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения файла: {e}")
        
        # Оценка успешности
        success_criteria = [
            len(listings) >= max_pages * 10,  # Минимум 10 объявлений на страницу
            len(unique_ids) == len(external_ids),  # Нет дубликатов
            coord_percentage >= 70,  # Минимум 70% с координатами
            avg_photos >= 10 if photo_counts else False,  # Минимум 10 фото в среднем
            len(property_types) >= 2,  # Минимум 2 типа недвижимости
            elapsed_time <= max_pages * 30  # Максимум 30 секунд на страницу
        ]
        
        passed_criteria = sum(success_criteria)
        logger.info(f"📈 Критерии успешности: {passed_criteria}/{len(success_criteria)}")
        
        if passed_criteria >= 5:
            logger.info("🎉 ТЕСТ УСПЕШНО ПРОЙДЕН! Скрапер V2 работает отлично.")
            return True
        elif passed_criteria >= 4:
            logger.info("✅ ТЕСТ В ОСНОВНОМ ПРОЙДЕН. Скрапер V2 работает хорошо.")
            return True
        else:
            logger.warning("⚠️ ТЕСТ НЕ ПРОЙДЕН. Требуется доработка.")
            return False
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в тесте: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Основная функция"""
    result = await test_scraper_v2()
    
    if result:
        logger.info("✅ Тестирование скрапера V2 завершено успешно!")
        sys.exit(0)
    else:
        logger.error("❌ Тестирование скрапера V2 провалено!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 