#!/usr/bin/env python3
"""
⚡ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ПАРСЕРА

Сравнивает скорость работы с включенным и выключенным геокодированием
"""
import sys
import asyncio
import time
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.parsers.immobiliare_parser import ImmobiliareParser


async def test_performance_comparison():
    """
    Сравнение производительности с геокодированием и без
    """
    print("⚡ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ПАРСЕРА IMMOBILIARE.IT")
    print("=" * 70)
    print("🎯 Цель: Сравнить скорость с геокодированием и без")
    print("📄 Тестируем: 10 страниц для полного сравнения")
    print("=" * 70)
    
    test_pages = 10
    
    # ТЕСТ 1: БЕЗ ГЕОКОДИРОВАНИЯ
    print(f"\n🚀 ТЕСТ 1: БЕЗ ГЕОКОДИРОВАНИЯ")
    print("-" * 50)
    
    parser_no_geo = ImmobiliareParser(enable_geocoding=False)
    
    start_time = time.time()
    listings_no_geo = await parser_no_geo.scrape_all_listings(max_pages=test_pages)
    end_time = time.time()
    
    time_no_geo = end_time - start_time
    
    print(f"✅ Результат БЕЗ геокодирования:")
    print(f"   📋 Объявлений: {len(listings_no_geo)}")
    print(f"   ⏱️  Время: {time_no_geo:.2f} секунд")
    print(f"   ⚡ Скорость: {len(listings_no_geo)/time_no_geo:.2f} объявлений/сек")
    
    # Статистика по координатам
    with_coords_no_geo = sum(1 for listing in listings_no_geo if listing.get('latitude'))
    print(f"   🗺️  С координатами: {with_coords_no_geo}/{len(listings_no_geo)}")
    
    # ТЕСТ 2: С ГЕОКОДИРОВАНИЕМ
    print(f"\n🗺️  ТЕСТ 2: С ГЕОКОДИРОВАНИЕМ")
    print("-" * 50)
    
    parser_with_geo = ImmobiliareParser(enable_geocoding=True)
    
    start_time = time.time()
    listings_with_geo = await parser_with_geo.scrape_all_listings(max_pages=test_pages)
    end_time = time.time()
    
    time_with_geo = end_time - start_time
    
    print(f"✅ Результат С геокодированием:")
    print(f"   📋 Объявлений: {len(listings_with_geo)}")
    print(f"   ⏱️  Время: {time_with_geo:.2f} секунд")
    print(f"   ⚡ Скорость: {len(listings_with_geo)/time_with_geo:.2f} объявлений/сек")
    
    # Статистика по координатам
    with_coords_with_geo = sum(1 for listing in listings_with_geo if listing.get('latitude'))
    print(f"   🗺️  С координатами: {with_coords_with_geo}/{len(listings_with_geo)}")
    
    # СРАВНЕНИЕ
    print(f"\n📊 СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ:")
    print("=" * 70)
    
    speed_improvement = ((time_with_geo - time_no_geo) / time_with_geo) * 100
    
    print(f"⏱️  БЕЗ геокодирования: {time_no_geo:.2f} сек")
    print(f"⏱️  С геокодированием:  {time_with_geo:.2f} сек")
    print(f"📈 Разница во времени:  {abs(time_with_geo - time_no_geo):.2f} сек")
    
    if time_no_geo < time_with_geo:
        print(f"🚀 Ускорение БЕЗ геокодирования: {speed_improvement:.1f}%")
    else:
        print(f"🐌 Замедление БЕЗ геокодирования: {abs(speed_improvement):.1f}%")
    
    # Скорость объявлений в секунду
    speed_no_geo = len(listings_no_geo) / time_no_geo
    speed_with_geo = len(listings_with_geo) / time_with_geo
    
    print(f"⚡ Скорость БЕЗ геокодирования: {speed_no_geo:.2f} объявлений/сек")
    print(f"⚡ Скорость С геокодированием:  {speed_with_geo:.2f} объявлений/сек")
    
    # Статистика по фотографиям
    photos_no_geo = sum(len(listing.get('images', [])) for listing in listings_no_geo)
    photos_with_geo = sum(len(listing.get('images', [])) for listing in listings_with_geo)
    
    print(f"\n📸 СТАТИСТИКА ПО ФОТОГРАФИЯМ:")
    print(f"   БЕЗ геокодирования: {photos_no_geo} фото")
    print(f"   С геокодированием:  {photos_with_geo} фото")
    
    print(f"\n🎯 РЕКОМЕНДАЦИЯ:")
    if time_no_geo < time_with_geo:
        print("   ✅ Для максимальной скорости используйте enable_geocoding=False")
        print("   📍 Координаты можно добавить позже отдельным процессом")
    else:
        print("   ✅ Геокодирование не влияет значительно на производительность")
        print("   🗺️  Можно безопасно использовать enable_geocoding=True")


if __name__ == "__main__":
    asyncio.run(test_performance_comparison()) 