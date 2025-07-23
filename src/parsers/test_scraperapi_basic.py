#!/usr/bin/env python3
"""
🧪 БАЗОВЫЙ ТЕСТ SCRAPERAPI
Проверяет работоспособность ScraperAPI на простых сайтах

Использование:
    python src/parsers/test_scraperapi_basic.py
"""
import sys
import os
import asyncio
import aiohttp
import logging
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'scraperapi_basic_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


async def test_scraperapi_basic():
    """Тестирует ScraperAPI на простых сайтах"""
    logger.info("🚀 БАЗОВЫЙ ТЕСТ SCRAPERAPI")
    logger.info(f"🔑 SCRAPERAPI_KEY настроен: {'✅' if settings.SCRAPERAPI_KEY else '❌'}")
    
    if not settings.SCRAPERAPI_KEY:
        logger.error("❌ SCRAPERAPI_KEY не настроен!")
        return False
    
    # Тестовые сайты
    test_sites = [
        {
            "name": "HTTPBin (простой тест)",
            "url": "https://httpbin.org/html",
            "expected_content": "<h1>Herman Melville - Moby-Dick</h1>"
        },
        {
            "name": "Example.com",
            "url": "https://example.com",
            "expected_content": "Example Domain"
        },
        {
            "name": "Google (главная)",
            "url": "https://google.com",
            "expected_content": "google"
        }
    ]
    
    sync_api_url = "https://api.scraperapi.com"
    timeout = aiohttp.ClientTimeout(total=30)
    
    successful_tests = 0
    
    for i, test_site in enumerate(test_sites, 1):
        logger.info(f"🧪 Тест {i}/{len(test_sites)}: {test_site['name']}")
        
        params = {
            'api_key': settings.SCRAPERAPI_KEY,
            'url': test_site['url'],
            'render': 'false'  # Без JS для скорости
        }
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(sync_api_url, params=params) as response:
                    logger.info(f"   📊 Статус: {response.status}")
                    
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"   📄 Размер ответа: {len(content)} символов")
                        
                        if test_site['expected_content'].lower() in content.lower():
                            logger.info(f"   ✅ Контент найден: {test_site['expected_content'][:30]}...")
                            successful_tests += 1
                        else:
                            logger.warning(f"   ⚠️ Ожидаемый контент не найден")
                            logger.debug(f"   Первые 200 символов: {content[:200]}")
                    else:
                        logger.error(f"   ❌ HTTP ошибка: {response.status}")
                        content = await response.text()
                        logger.debug(f"   Ответ: {content[:200]}")
                        
        except Exception as e:
            logger.error(f"   ❌ Исключение: {e}")
        
        # Пауза между тестами
        if i < len(test_sites):
            await asyncio.sleep(2)
    
    logger.info(f"📊 РЕЗУЛЬТАТЫ БАЗОВОГО ТЕСТА:")
    logger.info(f"   ✅ Успешных тестов: {successful_tests}/{len(test_sites)}")
    
    if successful_tests >= 2:
        logger.info("🎉 ScraperAPI работает нормально!")
        return True
    elif successful_tests >= 1:
        logger.warning("⚠️ ScraperAPI работает частично")
        return True
    else:
        logger.error("❌ ScraperAPI не работает!")
        return False


async def test_immobiliare_alternatives():
    """Тестирует альтернативные параметры для Immobiliare.it"""
    logger.info("🏠 ТЕСТ АЛЬТЕРНАТИВНЫХ ПАРАМЕТРОВ ДЛЯ IMMOBILIARE.IT")
    
    base_url = "https://www.immobiliare.it/affitto-case/roma/"
    sync_api_url = "https://api.scraperapi.com"
    timeout = aiohttp.ClientTimeout(total=60)
    
    # Различные комбинации параметров
    param_sets = [
        {
            "name": "Базовые параметры",
            "params": {
                'api_key': settings.SCRAPERAPI_KEY,
                'url': base_url,
                'render': 'false'
            }
        },
        {
            "name": "С рендерингом JS",
            "params": {
                'api_key': settings.SCRAPERAPI_KEY,
                'url': base_url,
                'render': 'true'
            }
        },
        {
            "name": "С премиум прокси",
            "params": {
                'api_key': settings.SCRAPERAPI_KEY,
                'url': base_url,
                'render': 'true',
                'premium': 'true'
            }
        },
        {
            "name": "Мобильная версия",
            "params": {
                'api_key': settings.SCRAPERAPI_KEY,
                'url': base_url,
                'render': 'true',
                'device_type': 'mobile'
            }
        },
        {
            "name": "Без геотаргетинга",
            "params": {
                'api_key': settings.SCRAPERAPI_KEY,
                'url': base_url,
                'render': 'true',
                'premium': 'true'
            }
        },
        {
            "name": "С пользовательскими заголовками",
            "params": {
                'api_key': settings.SCRAPERAPI_KEY,
                'url': base_url,
                'render': 'true',
                'premium': 'true',
                'keep_headers': 'true'
            }
        }
    ]
    
    successful_attempts = 0
    
    for i, param_set in enumerate(param_sets, 1):
        logger.info(f"🧪 Попытка {i}/{len(param_sets)}: {param_set['name']}")
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(sync_api_url, params=param_set['params']) as response:
                    logger.info(f"   📊 Статус: {response.status}")
                    
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"   📄 Размер ответа: {len(content)} символов")
                        
                        # Проверяем признаки успешного парсинга
                        success_indicators = [
                            'immobiliare' in content.lower(),
                            'affitto' in content.lower(),
                            'roma' in content.lower(),
                            '__NEXT_DATA__' in content,
                            'annunci' in content.lower()
                        ]
                        
                        found_indicators = sum(success_indicators)
                        logger.info(f"   🎯 Найдено индикаторов: {found_indicators}/5")
                        
                        if found_indicators >= 3:
                            logger.info(f"   ✅ Успешный парсинг!")
                            successful_attempts += 1
                            
                            # Сохраняем успешный результат для анализа
                            with open(f'immobiliare_success_{i}.html', 'w', encoding='utf-8') as f:
                                f.write(content)
                            logger.info(f"   💾 Результат сохранен в immobiliare_success_{i}.html")
                        else:
                            logger.warning(f"   ⚠️ Недостаточно индикаторов успеха")
                            logger.debug(f"   Первые 300 символов: {content[:300]}")
                    else:
                        logger.error(f"   ❌ HTTP ошибка: {response.status}")
                        content = await response.text()
                        logger.debug(f"   Ответ: {content[:200]}")
                        
        except Exception as e:
            logger.error(f"   ❌ Исключение: {e}")
        
        # Пауза между попытками
        if i < len(param_sets):
            await asyncio.sleep(5)
    
    logger.info(f"📊 РЕЗУЛЬТАТЫ ТЕСТА IMMOBILIARE:")
    logger.info(f"   ✅ Успешных попыток: {successful_attempts}/{len(param_sets)}")
    
    return successful_attempts > 0


async def main():
    """Основная функция"""
    logger.info("🚀 КОМПЛЕКСНЫЙ ТЕСТ SCRAPERAPI")
    
    # Тест 1: Базовая проверка ScraperAPI
    basic_result = await test_scraperapi_basic()
    
    if not basic_result:
        logger.error("❌ Базовый тест ScraperAPI провален! Проверьте ключ API.")
        sys.exit(1)
    
    # Тест 2: Альтернативные параметры для Immobiliare
    immobiliare_result = await test_immobiliare_alternatives()
    
    if immobiliare_result:
        logger.info("🎉 Найдены рабочие параметры для Immobiliare.it!")
        sys.exit(0)
    else:
        logger.error("❌ Все попытки доступа к Immobiliare.it провалились.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 