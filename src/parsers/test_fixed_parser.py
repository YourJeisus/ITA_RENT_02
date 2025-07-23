#!/usr/bin/env python3
"""
🧪 ТЕСТОВЫЙ СКРИПТ ДЛЯ ИСПРАВЛЕННОГО АСИНХРОННОГО ПАРСЕРА
Простой тест на 10 страниц с подробной статистикой

Использование:
    python src/parsers/test_fixed_parser.py
"""
import sys
import os
import asyncio
import logging
import json
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
        logging.FileHandler(f'fixed_parser_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


async def test_fixed_parser():
    """Тестирует исправленный парсер на 10 страницах"""
    logger.info("🚀 ТЕСТИРОВАНИЕ ИСПРАВЛЕННОГО АСИНХРОННОГО ПАРСЕРА")
    logger.info(f"🔑 SCRAPERAPI_KEY настроен: {'✅' if settings.SCRAPERAPI_KEY else '❌'}")
    
    if not settings.SCRAPERAPI_KEY:
        logger.error("❌ SCRAPERAPI_KEY не настроен! Установите в .env файле")
        return False
    
    # Создаем парсер с геокодированием
    parser = ImmobiliareAsyncParser(enable_geocoding=True)
    
    # Запускаем парсинг 10 страниц
    max_pages = 10
    logger.info(f"📄 Парсим {max_pages} страниц...")
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        listings = await parser.scrape_listings(max_pages=max_pages)
        
        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time
        
        if not listings:
            logger.error("❌ Не найдено ни одного объявления")
            return False
        
        # Подробная статистика
        logger.info("📊 ПОДРОБНАЯ СТАТИСТИКА:")
        logger.info(f"   ⏱️ Общее время: {elapsed_time:.1f}с")
        logger.info(f"   📋 Найдено объявлений: {len(listings)}")
        logger.info(f"   ⚡ Скорость: {len(listings)/elapsed_time:.1f} объявлений/сек")
        
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
        
        # Показываем несколько примеров
        logger.info(f"   📝 Примеры объявлений:")
        for i, listing in enumerate(listings[:5], 1):
            title = listing.get('title', 'Без названия')[:60]
            price = listing.get('price', 'N/A')
            prop_type = listing.get('property_type', 'N/A')
            photos = len(listing.get('images', []))
            coords = '✅' if listing.get('latitude') and listing.get('longitude') else '❌'
            
            logger.info(f"      {i}. {title}...")
            logger.info(f"         💰 {price}€ | 🏠 {prop_type} | 📸 {photos} фото | 🗺️ {coords}")
        
        # Сохраняем результаты в JSON файл
        output_file = f"parsed_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Подготавливаем данные для сохранения
        output_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_listings": len(listings),
                "pages_parsed": max_pages,
                "elapsed_time_seconds": elapsed_time,
                "parser_version": "ImmobiliareAsyncParser (Fixed)",
                "statistics": {
                    "photos": {
                        "average": avg_photos if photo_counts else 0,
                        "total": sum(photo_counts) if photo_counts else 0
                    },
                    "coordinates": {
                        "with_coords": with_coords,
                        "percentage": coord_percentage
                    },
                    "property_types": property_types,
                    "prices": {
                        "average": avg_price if prices else 0,
                        "min": min_price if prices else 0,
                        "max": max_price if prices else 0
                    } if prices else None
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
            len(listings) >= 50,  # Минимум 50 объявлений
            coord_percentage >= 70,  # Минимум 70% с координатами
            avg_photos >= 10 if photo_counts else False,  # Минимум 10 фото в среднем
            len(property_types) >= 2,  # Минимум 2 типа недвижимости
            elapsed_time <= 300  # Максимум 5 минут
        ]
        
        passed_criteria = sum(success_criteria)
        logger.info(f"📈 Критерии успешности: {passed_criteria}/{len(success_criteria)}")
        
        if passed_criteria >= 4:
            logger.info("🎉 ТЕСТ УСПЕШНО ПРОЙДЕН! Парсер работает отлично.")
            return True
        elif passed_criteria >= 3:
            logger.info("✅ ТЕСТ В ОСНОВНОМ ПРОЙДЕН. Парсер работает хорошо.")
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
    result = await test_fixed_parser()
    
    if result:
        logger.info("✅ Тестирование завершено успешно!")
        sys.exit(0)
    else:
        logger.error("❌ Тестирование провалено!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 