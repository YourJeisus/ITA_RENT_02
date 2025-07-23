#!/usr/bin/env python3
"""
🧪 ТЕСТОВЫЙ СКРИПТ ДЛЯ УЛУЧШЕННОГО АСИНХРОННОГО ПАРСЕРА
Проверяет все новые функции:
- ✅ Правильную асинхронную логику ScraperAPI
- ✅ Извлечение всех фотографий (~20+ на объявление)
- ✅ Унаследованную логику типов жилья из старого парсера
- ✅ Геокодирование через OpenStreetMap API

Использование:
    python src/parsers/test_enhanced_async_scraper.py [количество_страниц]
    
Примеры:
    python src/parsers/test_enhanced_async_scraper.py 1    # Тест 1 страницы с геокодированием
    python src/parsers/test_enhanced_async_scraper.py 2    # Тест 2 страниц
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'enhanced_async_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


async def test_photo_extraction():
    """Тестирует извлечение всех фотографий"""
    logger.info("🧪 ТЕСТ 1: Извлечение всех фотографий")
    
    parser = ImmobiliareAsyncParser(enable_geocoding=False)  # Без геокодирования для скорости
    
    try:
        # Получаем одну страницу для тестирования фотографий
        listings = await parser.scrape_listings(max_pages=1)
        
        if not listings:
            logger.error("❌ Не найдено объявлений для тестирования фотографий")
            return False
        
        logger.info(f"📊 Анализ фотографий для {len(listings)} объявлений:")
        
        photo_counts = []
        property_types = {}
        
        for i, listing in enumerate(listings[:5], 1):  # Показываем первые 5
            photos = listing.get('images', [])
            photo_count = len(photos)
            photo_counts.append(photo_count)
            
            prop_type = listing.get('property_type', 'unknown')
            property_types[prop_type] = property_types.get(prop_type, 0) + 1
            
            logger.info(f"   {i}. {listing.get('title', 'Без названия')[:50]}...")
            logger.info(f"      📸 Фотографий: {photo_count}")
            logger.info(f"      🏠 Тип: {prop_type}")
            logger.info(f"      💰 Цена: {listing.get('price', 'N/A')}€")
            
            # Показываем несколько URL фотографий
            if photos:
                logger.info(f"      🔗 Примеры фото:")
                for j, photo_url in enumerate(photos[:3], 1):
                    logger.info(f"         {j}. {photo_url}")
        
        if photo_counts:
            avg_photos = sum(photo_counts) / len(photo_counts)
            max_photos = max(photo_counts)
            min_photos = min(photo_counts)
            
            logger.info(f"📈 Статистика фотографий:")
            logger.info(f"   📊 Среднее: {avg_photos:.1f} фото/объявление")
            logger.info(f"   📈 Максимум: {max_photos} фото")
            logger.info(f"   📉 Минимум: {min_photos} фото")
            
            # Проверяем, что в среднем получаем много фотографий
            if avg_photos >= 15:
                logger.info("✅ Извлечение фотографий работает отлично!")
                return True
            else:
                logger.warning(f"⚠️ Среднее количество фотографий ({avg_photos:.1f}) меньше ожидаемого (15+)")
                return False
        
        logger.info(f"🏠 Типы недвижимости:")
        for prop_type, count in property_types.items():
            logger.info(f"   {prop_type}: {count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте фотографий: {e}")
        return False


async def test_property_type_classification():
    """Тестирует классификацию типов недвижимости"""
    logger.info("🧪 ТЕСТ 2: Классификация типов недвижимости")
    
    parser = ImmobiliareAsyncParser(enable_geocoding=False)
    
    try:
        listings = await parser.scrape_listings(max_pages=2)
        
        if not listings:
            logger.error("❌ Не найдено объявлений для тестирования типов")
            return False
        
        # Анализируем типы недвижимости
        property_types = {}
        type_examples = {}
        
        for listing in listings:
            prop_type = listing.get('property_type', 'unknown')
            title = listing.get('title', '')
            
            property_types[prop_type] = property_types.get(prop_type, 0) + 1
            
            if prop_type not in type_examples:
                type_examples[prop_type] = []
            if len(type_examples[prop_type]) < 2:  # Сохраняем по 2 примера каждого типа
                type_examples[prop_type].append(title[:60])
        
        logger.info(f"🏠 Найдено типов недвижимости: {len(property_types)}")
        
        expected_types = ['apartment', 'house', 'studio', 'room']
        found_expected_types = 0
        
        for prop_type, count in property_types.items():
            logger.info(f"   {prop_type}: {count} объявлений")
            
            # Показываем примеры
            if prop_type in type_examples:
                logger.info(f"      Примеры:")
                for example in type_examples[prop_type]:
                    logger.info(f"        • {example}...")
            
            if prop_type in expected_types:
                found_expected_types += 1
        
        logger.info(f"📊 Найдено ожидаемых типов: {found_expected_types}/{len(expected_types)}")
        
        # Проверяем, что классификация работает
        if found_expected_types >= 2:  # Должно быть минимум 2 разных типа
            logger.info("✅ Классификация типов недвижимости работает!")
            return True
        else:
            logger.warning("⚠️ Найдено мало различных типов недвижимости")
            return False
        
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте классификации: {e}")
        return False


async def test_geocoding():
    """Тестирует геокодирование через OpenStreetMap"""
    logger.info("🧪 ТЕСТ 3: Геокодирование через OpenStreetMap")
    
    parser = ImmobiliareAsyncParser(enable_geocoding=True)
    
    try:
        # Тестируем прямое геокодирование
        logger.info("🗺️ Тестируем прямое геокодирование адресов...")
        
        test_addresses = [
            "Via del Corso 123",
            "Piazza di Spagna 1", 
            "Via Nazionale 50"
        ]
        
        geocoding_results = []
        for address in test_addresses:
            logger.info(f"   Геокодируем: {address}")
            lat, lon = await parser._geocode_address(address, "Roma, Italy")
            
            if lat and lon:
                logger.info(f"   ✅ Результат: {lat:.6f}, {lon:.6f}")
                geocoding_results.append(True)
            else:
                logger.info(f"   ❌ Не удалось геокодировать")
                geocoding_results.append(False)
        
        geocoding_success_rate = sum(geocoding_results) / len(geocoding_results) * 100
        logger.info(f"📊 Успешность геокодирования: {geocoding_success_rate:.1f}%")
        
        # Теперь тестируем на реальных объявлениях
        logger.info("🏠 Тестируем геокодирование на реальных объявлениях...")
        
        listings = await parser.scrape_listings(max_pages=1)
        
        if not listings:
            logger.error("❌ Не найдено объявлений для тестирования геокодирования")
            return geocoding_success_rate >= 50  # Возвращаем результат прямого геокодирования
        
        coords_from_json = 0
        coords_from_geocoding = 0
        no_coords = 0
        
        for listing in listings[:10]:  # Тестируем первые 10
            lat = listing.get('latitude')
            lon = listing.get('longitude')
            address = listing.get('address', '')
            
            if lat and lon:
                if address and len(address) > 10:
                    coords_from_geocoding += 1
                    logger.debug(f"🗺️ Геокодирование: {address} -> {lat:.6f}, {lon:.6f}")
                else:
                    coords_from_json += 1
                    logger.debug(f"📍 Из JSON: {lat:.6f}, {lon:.6f}")
            else:
                no_coords += 1
                logger.debug(f"❌ Без координат: {listing.get('title', 'N/A')[:50]}")
        
        total_tested = coords_from_json + coords_from_geocoding + no_coords
        coords_success_rate = (coords_from_json + coords_from_geocoding) / total_tested * 100
        
        logger.info(f"📊 Результаты геолокации для {total_tested} объявлений:")
        logger.info(f"   📍 Координаты из JSON: {coords_from_json}")
        logger.info(f"   🗺️ Координаты через геокодирование: {coords_from_geocoding}")
        logger.info(f"   ❌ Без координат: {no_coords}")
        logger.info(f"   📈 Общая успешность: {coords_success_rate:.1f}%")
        
        # Считаем тест успешным, если >= 70% объявлений имеют координаты
        if coords_success_rate >= 70:
            logger.info("✅ Геокодирование работает отлично!")
            return True
        else:
            logger.warning(f"⚠️ Низкая успешность геокодирования: {coords_success_rate:.1f}%")
            return False
        
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте геокодирования: {e}")
        return False


async def test_full_integration(max_pages: int = 1):
    """Интеграционный тест всех функций"""
    logger.info(f"🧪 ТЕСТ 4: Полная интеграция ({max_pages} страниц)")
    
    parser = ImmobiliareAsyncParser(enable_geocoding=True)
    
    try:
        start_time = asyncio.get_event_loop().time()
        listings = await parser.scrape_listings(max_pages=max_pages)
        end_time = asyncio.get_event_loop().time()
        
        elapsed_time = end_time - start_time
        
        if not listings:
            logger.error("❌ Не найдено объявлений в интеграционном тесте")
            return False
        
        # Анализируем результаты
        photo_counts = [len(listing.get('images', [])) for listing in listings]
        coords_count = sum(1 for listing in listings if listing.get('latitude') and listing.get('longitude'))
        property_types = {}
        
        for listing in listings:
            prop_type = listing.get('property_type', 'unknown')
            property_types[prop_type] = property_types.get(prop_type, 0) + 1
        
        avg_photos = sum(photo_counts) / len(photo_counts) if photo_counts else 0
        coords_percentage = (coords_count / len(listings)) * 100
        
        logger.info(f"🎉 РЕЗУЛЬТАТЫ ИНТЕГРАЦИОННОГО ТЕСТА:")
        logger.info(f"   ⏱️ Время выполнения: {elapsed_time:.1f}с")
        logger.info(f"   📋 Найдено объявлений: {len(listings)}")
        logger.info(f"   📸 Среднее фото/объявление: {avg_photos:.1f}")
        logger.info(f"   🗺️ Объявлений с координатами: {coords_count}/{len(listings)} ({coords_percentage:.1f}%)")
        logger.info(f"   🏠 Типов недвижимости: {len(property_types)}")
        
        for prop_type, count in property_types.items():
            logger.info(f"      {prop_type}: {count}")
        
        # Показываем несколько примеров
        logger.info(f"   📝 Примеры объявлений:")
        for i, listing in enumerate(listings[:3], 1):
            logger.info(f"      {i}. {listing.get('title', 'Без названия')[:50]}...")
            logger.info(f"         💰 {listing.get('price', 'N/A')}€ | 🏠 {listing.get('property_type', 'N/A')}")
            logger.info(f"         📸 {len(listing.get('images', []))} фото | 🗺️ {'✅' if listing.get('latitude') else '❌'} координаты")
        
        # Критерии успешности
        success_criteria = [
            avg_photos >= 10,  # В среднем >= 10 фото
            coords_percentage >= 50,  # >= 50% с координатами
            len(property_types) >= 2,  # >= 2 типов недвижимости
            len(listings) >= 5  # >= 5 объявлений найдено
        ]
        
        passed_criteria = sum(success_criteria)
        logger.info(f"📊 Критерии успешности: {passed_criteria}/{len(success_criteria)}")
        
        if passed_criteria >= 3:
            logger.info("✅ Интеграционный тест ПРОЙДЕН!")
            return True
        else:
            logger.warning("⚠️ Интеграционный тест НЕ ПРОЙДЕН")
            return False
        
    except Exception as e:
        logger.error(f"❌ Ошибка в интеграционном тесте: {e}")
        return False


async def main():
    """Основная функция тестирования"""
    logger.info("🚀 НАЧИНАЕМ ТЕСТИРОВАНИЕ УЛУЧШЕННОГО АСИНХРОННОГО ПАРСЕРА")
    logger.info(f"🔑 SCRAPERAPI_KEY настроен: {'✅' if settings.SCRAPERAPI_KEY else '❌'}")
    
    if not settings.SCRAPERAPI_KEY:
        logger.error("❌ SCRAPERAPI_KEY не настроен! Установите в .env файле")
        return
    
    # Получаем количество страниц из аргументов
    max_pages = 1
    if len(sys.argv) > 1:
        try:
            max_pages = int(sys.argv[1])
        except ValueError:
            logger.warning("⚠️ Неверный аргумент, используем 1 страницу по умолчанию")
    
    logger.info(f"📄 Тестируем с {max_pages} страницами")
    
    tests_results = []
    
    # Тест 1: Извлечение фотографий
    try:
        result1 = await test_photo_extraction()
        tests_results.append(("Извлечение фотографий", result1))
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте 1: {e}")
        tests_results.append(("Извлечение фотографий", False))
    
    # Тест 2: Классификация типов
    try:
        result2 = await test_property_type_classification()
        tests_results.append(("Классификация типов", result2))
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте 2: {e}")
        tests_results.append(("Классификация типов", False))
    
    # Тест 3: Геокодирование
    try:
        result3 = await test_geocoding()
        tests_results.append(("Геокодирование", result3))
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте 3: {e}")
        tests_results.append(("Геокодирование", False))
    
    # Тест 4: Полная интеграция
    try:
        result4 = await test_full_integration(max_pages)
        tests_results.append(("Полная интеграция", result4))
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте 4: {e}")
        tests_results.append(("Полная интеграция", False))
    
    # Итоговый отчет
    logger.info("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ:")
    passed = 0
    for test_name, result in tests_results:
        status = "✅ ПРОШЕЛ" if result else "❌ ПРОВАЛЕН"
        logger.info(f"   {status}: {test_name}")
        if result:
            passed += 1
    
    total_tests = len(tests_results)
    logger.info(f"📈 Результат: {passed}/{total_tests} тестов прошли ({(passed/total_tests)*100:.1f}%)")
    
    if passed == total_tests:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОШЛИ! Улучшенный парсер готов к использованию.")
    elif passed >= total_tests * 0.75:
        logger.info("✅ БОЛЬШИНСТВО ТЕСТОВ ПРОШЛИ! Парсер работает хорошо.")
    else:
        logger.warning("⚠️ МНОГИЕ ТЕСТЫ ПРОВАЛИЛИСЬ. Требуется доработка.")


if __name__ == "__main__":
    asyncio.run(main()) 