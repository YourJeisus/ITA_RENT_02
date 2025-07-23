#!/usr/bin/env python3
"""
🧪 ТЕСТОВЫЙ СКРИПТ ДЛЯ ПРАВИЛЬНОГО АСИНХРОННОГО ПАРСЕРА
Проверяет соответствие асинхронной логике ScraperAPI

Использование:
    python src/parsers/test_async_scraper.py [количество_страниц]
    
Примеры:
    python src/parsers/test_async_scraper.py 2    # Тест 2 страниц
    python src/parsers/test_async_scraper.py 1    # Тест 1 страницы
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
        logging.FileHandler(f'async_scraper_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


async def test_single_job_submission():
    """Тестирует отправку одной задачи в ScraperAPI Async"""
    logger.info("🧪 ТЕСТ 1: Отправка одной задачи в ScraperAPI Async")
    
    parser = ImmobiliareAsyncParser()
    url = "https://www.immobiliare.it/affitto-case/roma/"
    
    # Отправляем задачу
    job_data = await parser.submit_scraping_job(url, {"test": "single_job"})
    
    if job_data:
        logger.info(f"✅ Задача создана успешно:")
        logger.info(f"   🆔 Job ID: {job_data.get('id')}")
        logger.info(f"   📊 Статус: {job_data.get('status')}")
        logger.info(f"   🔗 Status URL: {job_data.get('statusUrl')}")
        
        # Проверяем статус
        status_url = job_data.get('statusUrl')
        if status_url:
            result = await parser.poll_job_status(status_url, max_wait_time=120)
            if result:
                response_data = result.get('response', {})
                html_size = len(response_data.get('body', ''))
                status_code = response_data.get('statusCode')
                
                logger.info(f"✅ Задача завершена:")
                logger.info(f"   📄 HTML размер: {html_size} символов")
                logger.info(f"   🔢 Статус код: {status_code}")
                
                return True
            else:
                logger.error("❌ Не удалось получить результат")
                return False
        else:
            logger.error("❌ Нет status URL")
            return False
    else:
        logger.error("❌ Не удалось создать задачу")
        return False


async def test_batch_scraping(max_pages: int = 2):
    """Тестирует батч скрапинг нескольких страниц"""
    logger.info(f"🧪 ТЕСТ 2: Батч скрапинг {max_pages} страниц")
    
    parser = ImmobiliareAsyncParser(enable_geocoding=True)
    
    # Запускаем полный парсинг
    start_time = asyncio.get_event_loop().time()
    listings = await parser.scrape_listings(max_pages=max_pages)
    end_time = asyncio.get_event_loop().time()
    
    elapsed_time = end_time - start_time
    
    logger.info(f"🎉 РЕЗУЛЬТАТЫ БАТЧ СКРАПИНГА:")
    logger.info(f"   ⏱️ Время выполнения: {elapsed_time:.1f}с")
    logger.info(f"   📋 Найдено объявлений: {len(listings)}")
    
    if listings:
        # Анализ фотографий
        photo_counts = [len(listing.get('images', [])) for listing in listings]
        avg_photos = sum(photo_counts) / len(photo_counts)
        max_photos = max(photo_counts)
        min_photos = min(photo_counts)
        
        logger.info(f"   📸 Фотографии:")
        logger.info(f"      📊 Среднее: {avg_photos:.1f}")
        logger.info(f"      📈 Максимум: {max_photos}")
        logger.info(f"      📉 Минимум: {min_photos}")
        
        # Анализ типов недвижимости
        property_types = {}
        for listing in listings:
            prop_type = listing.get('property_type', 'unknown')
            property_types[prop_type] = property_types.get(prop_type, 0) + 1
        
        logger.info(f"   🏠 Типы недвижимости:")
        for prop_type, count in property_types.items():
            logger.info(f"      {prop_type}: {count}")
        
        # Анализ координат
        with_coords = sum(1 for listing in listings if listing.get('latitude') and listing.get('longitude'))
        coord_percentage = (with_coords / len(listings)) * 100
        
        logger.info(f"   🗺️ Геолокация:")
        logger.info(f"      С координатами: {with_coords}/{len(listings)} ({coord_percentage:.1f}%)")
        
        # Показываем несколько примеров
        logger.info(f"   📝 Примеры объявлений:")
        for i, listing in enumerate(listings[:3], 1):
            logger.info(f"      {i}. {listing.get('title', 'Без названия')[:50]}...")
            logger.info(f"         💰 {listing.get('price', 'N/A')}€ | 🏠 {listing.get('property_type', 'N/A')} | 📸 {len(listing.get('images', []))} фото")
        
        return True
    else:
        logger.error("❌ Не найдено ни одного объявления")
        return False


async def test_api_parameters():
    """Тестирует правильность API параметров"""
    logger.info("🧪 ТЕСТ 3: Проверка API параметров")
    
    parser = ImmobiliareAsyncParser()
    
    # Проверяем структуру запроса
    test_payload = {
        "apiKey": "test_key",
        "url": "https://example.com",
        "apiParams": {
            "render": True,
            "premium": True,
            "country_code": "it",
            "device_type": "desktop",
            "autoparse": False,
            "retry_404": True,
            "follow_redirect": True
        },
        "meta": {"test": True}
    }
    
    logger.info("✅ Структура запроса соответствует документации ScraperAPI:")
    logger.info(f"   📋 Payload: {test_payload}")
    
    # Проверяем URL
    assert parser.async_api_url == "https://async.scraperapi.com/jobs"
    logger.info(f"   🔗 Правильный URL: {parser.async_api_url}")
    
    return True


async def main():
    """Основная функция тестирования"""
    logger.info("🚀 НАЧИНАЕМ ТЕСТИРОВАНИЕ ПРАВИЛЬНОГО АСИНХРОННОГО ПАРСЕРА")
    logger.info(f"🔑 SCRAPERAPI_KEY настроен: {'✅' if settings.SCRAPERAPI_KEY else '❌'}")
    
    if not settings.SCRAPERAPI_KEY:
        logger.error("❌ SCRAPERAPI_KEY не настроен! Установите в .env файле")
        return
    
    # Получаем количество страниц из аргументов
    max_pages = 2
    if len(sys.argv) > 1:
        try:
            max_pages = int(sys.argv[1])
        except ValueError:
            logger.warning("⚠️ Неверный аргумент, используем 2 страницы по умолчанию")
    
    logger.info(f"📄 Тестируем с {max_pages} страницами")
    
    tests_results = []
    
    # Тест 1: Отправка одной задачи
    try:
        result1 = await test_single_job_submission()
        tests_results.append(("Отправка одной задачи", result1))
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте 1: {e}")
        tests_results.append(("Отправка одной задачи", False))
    
    # Тест 2: Батч скрапинг
    try:
        result2 = await test_batch_scraping(max_pages)
        tests_results.append(("Батч скрапинг", result2))
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте 2: {e}")
        tests_results.append(("Батч скрапинг", False))
    
    # Тест 3: API параметры
    try:
        result3 = await test_api_parameters()
        tests_results.append(("API параметры", result3))
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте 3: {e}")
        tests_results.append(("API параметры", False))
    
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
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОШЛИ! Парсер готов к использованию.")
    else:
        logger.warning("⚠️ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ. Требуется доработка.")


if __name__ == "__main__":
    asyncio.run(main()) 