#!/usr/bin/env python3
"""
🚀 СКРИПТ ДЛЯ МАССОВОГО СКРАПИРОВАНИЯ В RAILWAY БД

Соскрапывает 20 страниц из каждого источника:
- Casa.it
- Subito.it  
- Idealista.it
- Immobiliare.it

И сохраняет все в базу данных на Railway

Использование:
    python scripts/bulk_scrape_railway.py --pages 20

Или для локальной БД:
    python scripts/bulk_scrape_railway.py --pages 20 --local
"""
import sys
import asyncio
import logging
import argparse
import os
import time
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

from src.parsers import CasaScraper, SubitoScraper, IdealistaScraper, ImmobiliareScraper
from src.services.scraping_service import ScrapingService
from src.db.database import SessionLocal
from src.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bulk_scrape.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BulkScraper:
    """Класс для массового скрапирования"""
    
    def __init__(self, max_pages: int = 20):
        """
        Инициализация скрапера
        
        Args:
            max_pages: Количество страниц для скрапирования из каждого источника
        """
        self.max_pages = max_pages
        self.scraping_service = ScrapingService()
        
        logger.info(f"📊 BulkScraper инициализирован для скрапирования {max_pages} страниц")
        logger.info(f"🔌 Используется БД: {settings.DATABASE_URL[:50]}...")
    
    async def scrape_all_sources(self) -> dict:
        """
        Скрапит все 4 источника параллельно
        
        Returns:
            dict: Словарь с результатами парсинга по источникам
        """
        logger.info("🚀 Начинаем параллельный скрапинг всех 4 источников")
        
        results = {
            "casa_it": [],
            "subito": [],
            "idealista": [],
            "immobiliare": []
        }
        
        try:
            # Запускаем парсинг всех источников параллельно
            raw_results = await asyncio.gather(
                self.scraping_service.scrape_casa_async({}, self.max_pages),
                self.scraping_service.scrape_subito_async({}, self.max_pages),
                self.scraping_service.scrape_idealista_async({}, self.max_pages),
                self.scraping_service.scrape_immobiliare_async({}, self.max_pages),
                return_exceptions=True
            )
            
            # Обрабатываем результаты
            source_names = ["casa_it", "subito", "idealista", "immobiliare"]
            
            for i, result in enumerate(raw_results):
                source_name = source_names[i]
                
                if isinstance(result, Exception):
                    logger.error(f"❌ Ошибка парсинга {source_name}: {result}")
                    results[source_name] = []
                elif isinstance(result, list):
                    results[source_name] = result
                    logger.info(f"✅ {source_name}: получено {len(result)} объявлений")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка при параллельном скрапинге: {e}")
            return results
    
    def save_to_database(self, results: dict) -> dict:
        """
        Сохраняет результаты в базу данных
        
        Args:
            results: Словарь результатов парсинга по источникам
            
        Returns:
            dict: Статистика сохранения
        """
        db = SessionLocal()
        try:
            logger.info("💾 Начинаем сохранение объявлений в базу данных...")
            
            # Объединяем все объявления
            all_listings = []
            for source, listings in results.items():
                # Убеждаемся, что source указан правильно
                for listing in listings:
                    if 'source' not in listing or not listing.get('source'):
                        listing['source'] = source
                all_listings.extend(listings)
            
            if not all_listings:
                logger.warning("⚠️ Нет объявлений для сохранения")
                return {
                    "total_listings": 0,
                    "created": 0,
                    "updated": 0,
                    "errors": 0,
                    "skipped_duplicates": 0
                }
            
            # Сохраняем в БД
            stats = self.scraping_service.save_listings_to_db(all_listings, db)
            
            logger.info(f"💾 Сохранение завершено!")
            logger.info(f"   📊 Новых: {stats.get('created', 0)}")
            logger.info(f"   🔄 Обновлено: {stats.get('updated', 0)}")
            logger.info(f"   ⏭️ Дубликатов пропущено: {stats.get('skipped_duplicates', 0)}")
            logger.info(f"   ❌ Ошибок: {stats.get('errors', 0)}")
            
            return stats
            
        finally:
            db.close()
    
    async def run(self) -> dict:
        """
        Основной метод: скрапирование + сохранение
        
        Returns:
            dict: Полная статистика операции
        """
        start_time = datetime.now()
        
        try:
            logger.info("=" * 80)
            logger.info(f"🎯 МАССОВОЕ СКРАПИРОВАНИЕ НАЧАТО")
            logger.info(f"📅 Время начала: {start_time.strftime('%d.%m.%Y %H:%M:%S')}")
            logger.info(f"📄 Страниц на источник: {self.max_pages}")
            logger.info(f"🌐 Источники: Casa.it, Subito.it, Idealista.it, Immobiliare.it")
            logger.info("=" * 80)
            
            # Шаг 1: Скрапирование
            logger.info("\n📍 ШАГ 1: Скрапирование всех источников...")
            scrape_results = await self.scrape_all_sources()
            
            total_scraped = sum(len(listings) for listings in scrape_results.values())
            logger.info(f"\n✅ Скрапирование завершено: {total_scraped} объявлений всего")
            
            # Шаг 2: Сохранение
            logger.info("\n📍 ШАГ 2: Сохранение в базу данных...")
            save_stats = self.save_to_database(scrape_results)
            
            # Финальная статистика
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()
            
            final_stats = {
                "success": True,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "elapsed_seconds": elapsed,
                "elapsed_formatted": f"{int(elapsed // 60)} мин {int(elapsed % 60)} сек",
                "scraped_by_source": {
                    source: len(listings) 
                    for source, listings in scrape_results.items()
                },
                "total_scraped": total_scraped,
                "database_stats": save_stats
            }
            
            # Вывод финальной статистики
            logger.info("\n" + "=" * 80)
            logger.info("🎉 ОПЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            logger.info("=" * 80)
            
            logger.info(f"\n⏱️ Время выполнения: {final_stats['elapsed_formatted']}")
            
            logger.info(f"\n📊 СТАТИСТИКА ПО ИСТОЧНИКАМ:")
            for source, count in final_stats['scraped_by_source'].items():
                logger.info(f"   {source.upper():15} → {count} объявлений")
            
            logger.info(f"\n💾 СТАТИСТИКА СОХРАНЕНИЯ:")
            logger.info(f"   Всего скрапено   → {total_scraped}")
            logger.info(f"   Создано новых    → {save_stats.get('created', 0)}")
            logger.info(f"   Обновлено        → {save_stats.get('updated', 0)}")
            logger.info(f"   Дубликаты        → {save_stats.get('skipped_duplicates', 0)}")
            logger.info(f"   Ошибки           → {save_stats.get('errors', 0)}")
            
            if 'by_source' in save_stats:
                logger.info(f"\n📈 ПОДРОБНАЯ СТАТИСТИКА ПО ИСТОЧНИКАМ:")
                for source, stats in save_stats['by_source'].items():
                    logger.info(f"   {source.upper()}:")
                    logger.info(f"      Всего     → {stats.get('total', 0)}")
                    logger.info(f"      Новые     → {stats.get('created', 0)}")
                    logger.info(f"      Обновлено → {stats.get('updated', 0)}")
                    logger.info(f"      Пропущено → {stats.get('skipped', 0)}")
                    logger.info(f"      Ошибки    → {stats.get('errors', 0)}")
            
            logger.info("\n" + "=" * 80)
            
            return final_stats
            
        except Exception as e:
            logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            return {
                "success": False,
                "error": str(e),
                "elapsed_seconds": (datetime.now() - start_time).total_seconds()
            }


async def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='Массовое скрапирование недвижимости в Railway БД'
    )
    parser.add_argument(
        '--pages', 
        type=int, 
        default=20, 
        help='Количество страниц для парсинга из каждого источника (default: 20)'
    )
    parser.add_argument(
        '--local', 
        action='store_true',
        help='Использовать локальную БД вместо Railway (для тестирования)'
    )
    
    args = parser.parse_args()
    
    logger.info(f"\n🔧 ПАРАМЕТРЫ ЗАПУСКА:")
    logger.info(f"   Страниц на источник: {args.pages}")
    logger.info(f"   БД: {'Локальная' if args.local else 'Railway'}")
    logger.info(f"   DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    
    # Создаем и запускаем скрапер
    scraper = BulkScraper(max_pages=args.pages)
    stats = await scraper.run()
    
    # Возвращаем код выхода
    return 0 if stats.get('success', False) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
