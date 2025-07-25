#!/usr/bin/env python3
"""
🤖 ВОРКЕР АВТОМАТИЧЕСКОГО ПАРСИНГА

Автоматически запускает парсинг каждые 6 часов
Работает в фоновом режиме на Railway
"""
import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional
import os

# Добавляем корень проекта в путь
sys.path.insert(0, '/app')

from src.services.scraping_service import ScrapingService
from src.db.database import SessionLocal, engine
from src.db.models import Base
from src.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


class ScraperWorker:
    """Воркер для автоматического парсинга каждые 6 часов"""
    
    def __init__(self):
        self.scraping_service = ScrapingService()
        self.is_running = True
        # Читаем настройки из переменных окружения
        self.interval_hours = settings.SCRAPER_WORKER_INTERVAL_HOURS
        self.max_pages = settings.SCRAPER_WORKER_MAX_PAGES
        
        # Настройка обработчиков сигналов для graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        logger.info(f"🛑 Получен сигнал {signum}, завершаем работу...")
        self.is_running = False
        
    async def ensure_database_tables(self):
        """Создание таблиц БД если их нет"""
        try:
            logger.info("🗄️ Проверяем наличие таблиц в базе данных...")
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Таблицы БД готовы")
        except Exception as e:
            logger.error(f"❌ Ошибка создания таблиц БД: {e}")
            raise
            
    async def run_scraping_cycle(self) -> bool:
        """
        Запуск одного цикла парсинга
        
        Returns:
            bool: True если парсинг прошел успешно
        """
        try:
            logger.info("🚀 Начинаем цикл парсинга...")
            
            # Фильтры для парсинга (пока парсим Рим)
            filters = {
                "city": "roma",
                "property_type": "apartment"
            }
            
            # Создаем сессию БД
            db = SessionLocal()
            
            try:
                # Запускаем парсинг и сохранение
                result = await self.scraping_service.scrape_and_save(
                    filters=filters,
                    db=db,
                    max_pages=self.max_pages
                )
                
                if result["success"]:
                    logger.info(f"✅ Парсинг завершен успешно:")
                    logger.info(f"   📋 Спаршено: {result['scraped_count']} объявлений")
                    logger.info(f"   💾 Сохранено: {result['saved_count']} объявлений")
                    logger.info(f"   ⏱️ Время: {result['elapsed_time']:.2f} сек")
                    return True
                else:
                    logger.error(f"❌ Парсинг завершился с ошибкой: {result['message']}")
                    return False
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в цикле парсинга: {e}")
            return False
            
    async def run_worker(self):
        """Основной цикл воркера"""
        logger.info("🤖 Запуск воркера автоматического парсинга")
        logger.info(f"⏰ Интервал парсинга: каждые {self.interval_hours} часов")
        logger.info(f"📄 Максимум страниц за цикл: {self.max_pages}")
        logger.info(f"🔑 ScraperAPI: {'✅ настроен' if settings.SCRAPERAPI_KEY else '❌ НЕ настроен'}")
        logger.info(f"🗄️ База данных: {settings.DATABASE_URL[:50]}...")
        
        # Проверяем настройки
        if not settings.SCRAPERAPI_KEY:
            logger.error("❌ SCRAPERAPI_KEY не настроен! Воркер не может работать.")
            return
            
        # Создаем таблицы БД если нужно
        await self.ensure_database_tables()
        
        # Запускаем первый цикл сразу
        logger.info("🚀 Запускаем первый цикл парсинга сразу...")
        await self.run_scraping_cycle()
        
        # Основной цикл с таймером
        while self.is_running:
            try:
                # Ждем до следующего цикла
                next_run = datetime.now() + timedelta(hours=self.interval_hours)
                logger.info(f"😴 Следующий запуск: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Спим по частям, чтобы можно было прервать
                sleep_seconds = self.interval_hours * 3600
                for _ in range(sleep_seconds):
                    if not self.is_running:
                        break
                    await asyncio.sleep(1)
                
                # Если получили сигнал на остановку, выходим
                if not self.is_running:
                    break
                    
                # Запускаем очередной цикл парсинга
                logger.info(f"⏰ Время для нового цикла парсинга!")
                await self.run_scraping_cycle()
                
            except Exception as e:
                logger.error(f"❌ Ошибка в основном цикле воркера: {e}")
                # Ждем 5 минут перед повтором при ошибке
                await asyncio.sleep(300)
                
        logger.info("🛑 Воркер парсинга завершен")
        
    async def health_check(self):
        """Health check для Railway"""
        return {
            "status": "healthy",
            "worker_type": "scraper",
            "interval_hours": self.interval_hours,
            "is_running": self.is_running,
            "timestamp": datetime.now().isoformat()
        }


async def main():
    """Точка входа для воркера"""
    logger.info("🤖 Инициализация воркера парсинга...")
    
    worker = ScraperWorker()
    
    try:
        await worker.run_worker()
    except KeyboardInterrupt:
        logger.info("🛑 Получено прерывание, завершаем работу...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка воркера: {e}")
        sys.exit(1)
    finally:
        logger.info("👋 Воркер парсинга завершен")


if __name__ == "__main__":
    # Проверяем переменную окружения для типа воркера
    worker_type = os.getenv("WORKER_TYPE", "")
    
    if worker_type != "scraper":
        logger.error(f"❌ Неверный тип воркера: {worker_type}. Ожидается: scraper")
        sys.exit(1)
        
    # Запускаем воркер
    asyncio.run(main()) 