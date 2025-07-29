#!/usr/bin/env python3
"""
🔍 Детальная проверка парсинга Idealista
Тестирует:
- property_type поле
- rooms парсинг
- качество данных
"""
import sys
import asyncio
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from src.parsers.idealista_scraper import IdealistaScraper
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_idealista_fields():
    """Тестирует поля объявлений Idealista"""
    print("🔍 ДЕТАЛЬНАЯ ПРОВЕРКА IDEALISTA")
    print("=" * 50)
    
    scraper = IdealistaScraper()
    
    try:
        # Парсим 1 страницу
        print("🚀 Парсинг 1 страницы...")
        listings = await scraper.scrape_multiple_pages(max_pages=1)
        
        print(f"📊 Найдено объявлений: {len(listings)}")
        
        # Анализируем качество данных
        property_type_count = 0
        rooms_count = 0
        price_count = 0
        
        print(f"\n📋 ДЕТАЛЬНЫЙ АНАЛИЗ {min(5, len(listings))} ОБЪЯВЛЕНИЙ:")
        
        for i, listing in enumerate(listings[:5], 1):
            print(f"\n{i}. {listing.get('title', 'Без названия')[:50]}...")
            print(f"   💰 Цена: {listing.get('price', 'НЕТ')}")
            print(f"   🏠 Тип: {listing.get('property_type', 'НЕТ')}")
            print(f"   🚪 Комнаты: {listing.get('rooms', 'НЕТ')}")
            print(f"   📍 Город: {listing.get('city', 'НЕТ')}")
            print(f"   🔗 URL: {listing.get('url', 'НЕТ')[:60]}...")
            
            # Подсчет статистики
            if listing.get('property_type'):
                property_type_count += 1
            if listing.get('rooms'):
                rooms_count += 1
            if listing.get('price'):
                price_count += 1
        
        # Общая статистика
        total = len(listings)
        print(f"\n📊 СТАТИСТИКА КАЧЕСТВА ДАННЫХ:")
        print(f"   🏠 property_type: {property_type_count}/{total} ({property_type_count/total*100:.1f}%)")
        print(f"   🚪 rooms: {rooms_count}/{total} ({rooms_count/total*100:.1f}%)")
        print(f"   💰 price: {price_count}/{total} ({price_count/total*100:.1f}%)")
        
        # Проверяем типы комнат из заголовков
        print(f"\n🔍 АНАЛИЗ ТИПОВ КОМНАТ ИЗ ЗАГОЛОВКОВ:")
        room_types = {}
        for listing in listings:
            title = listing.get('title', '').lower()
            if 'monolocale' in title:
                room_types['monolocale'] = room_types.get('monolocale', 0) + 1
            elif 'bilocale' in title:
                room_types['bilocale'] = room_types.get('bilocale', 0) + 1
            elif 'trilocale' in title:
                room_types['trilocale'] = room_types.get('trilocale', 0) + 1
            elif 'quadrilocale' in title:
                room_types['quadrilocale'] = room_types.get('quadrilocale', 0) + 1
        
        for room_type, count in room_types.items():
            print(f"   📌 {room_type}: {count} объявлений")
        
        return listings
        
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте: {e}")
        return []


async def main():
    """Главная функция теста"""
    print("🧪 ТЕСТ КАЧЕСТВА ДАННЫХ IDEALISTA")
    print("=" * 50)
    
    await test_idealista_fields()
    
    print("\n✅ ТЕСТ ЗАВЕРШЕН")


if __name__ == "__main__":
    asyncio.run(main()) 