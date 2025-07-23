"""
Сервис для координации парсинга недвижимости
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from src.parsers.immobiliare_async_scraper_v2 import ImmobiliareAsyncScraperV2
from src.crud.crud_listing import listing as crud_listing
from src.schemas.listing import ListingCreate
from src.db.models import Listing

logger = logging.getLogger(__name__)


class ScrapingService:
    """
    Сервис для координации парсинга недвижимости V2
    Использует новый асинхронный скрапер для максимальной производительности
    """
    
    def __init__(self):
        # Инициализируем новый асинхронный скрапер
        self.immobiliare_scraper = ImmobiliareAsyncScraperV2(enable_geocoding=True)
        
        # Настройки по умолчанию
        self.default_max_pages = 5
        
    def get_available_sources(self) -> List[str]:
        """Получить список доступных источников"""
        return ['immobiliare']
    
    async def scrape_immobiliare_async(
        self,
        filters: Dict[str, Any],
        max_pages: int = None
    ) -> List[Dict[str, Any]]:
        """
        Асинхронный парсинг Immobiliare.it
        
        Args:
            filters: Фильтры поиска (пока не используются, парсим Рим)
            max_pages: Максимальное количество страниц
            
        Returns:
            List[Dict]: Список объявлений
        """
        if max_pages is None:
            max_pages = self.default_max_pages
            
        try:
            logger.info(f"🚀 Запускаем асинхронный парсинг Immobiliare.it на {max_pages} страниц")
            
            # Запускаем новый асинхронный скрапер
            listings = await self.immobiliare_scraper.scrape_multiple_pages(max_pages=max_pages)
            
            logger.info(f"✅ Получено {len(listings)} объявлений из Immobiliare.it")
            return listings
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга Immobiliare.it: {e}")
            return []
    
    async def scrape_all_sources(
        self,
        filters: Dict[str, Any],
        max_pages: int = None
    ) -> List[Dict[str, Any]]:
        """
        ОСНОВНОЙ МЕТОД: Асинхронный парсинг всех источников
        
        Args:
            filters: Фильтры поиска
            max_pages: Максимальное количество страниц на источник
            
        Returns:
            List[Dict]: Объединенный список объявлений из всех источников
        """
        if max_pages is None:
            max_pages = self.default_max_pages
            
        logger.info(f"🔍 Начинаем парсинг всех источников (max_pages={max_pages})")
        
        all_listings = []
        
        # Пока у нас только Immobiliare.it, но можно легко добавить другие источники
        try:
            immobiliare_listings = await self.scrape_immobiliare_async(filters, max_pages)
            all_listings.extend(immobiliare_listings)
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга Immobiliare.it: {e}")
        
        # В будущем можно добавить другие источники:
        # try:
        #     idealista_listings = await self.scrape_idealista_async(filters, max_pages)
        #     all_listings.extend(idealista_listings)
        # except Exception as e:
        #     logger.error(f"❌ Ошибка парсинга Idealista.it: {e}")
        
        logger.info(f"📊 Всего получено {len(all_listings)} объявлений из всех источников")
        return all_listings
    
    async def save_listings_to_db(
        self,
        listings: List[Dict[str, Any]],
        db: Session
    ) -> int:
        """
        Сохраняет объявления в базу данных с дедупликацией
        
        Args:
            listings: Список объявлений для сохранения
            db: Сессия базы данных
            
        Returns:
            int: Количество сохраненных объявлений
        """
        if not listings:
            return 0
            
        saved_count = 0
        duplicate_count = 0
        error_count = 0
        
        logger.info(f"💾 Сохраняем {len(listings)} объявлений в базу данных...")
        
        for listing_data in listings:
            try:
                # Проверяем, существует ли уже такое объявление
                external_id = listing_data.get('external_id')
                source = listing_data.get('source', 'immobiliare')
                
                if not external_id:
                    logger.warning("⚠️ Объявление без external_id, пропускаем")
                    error_count += 1
                    continue
                
                existing = crud_listing.get_by_external_id(
                    db=db,
                    external_id=external_id,
                    source=source
                )
                
                if existing:
                    # Обновляем существующее объявление
                    listing_update = ListingCreate(**listing_data)
                    crud_listing.update(db=db, db_obj=existing, obj_in=listing_update)
                    duplicate_count += 1
                    logger.debug(f"🔄 Обновлено объявление {external_id}")
                else:
                    # Создаем новое объявление
                    listing_create = ListingCreate(**listing_data)
                    crud_listing.create(db=db, obj_in=listing_create)
                    saved_count += 1
                    logger.debug(f"✅ Создано объявление {external_id}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка сохранения объявления: {e}")
                logger.debug(f"Данные объявления: {listing_data}")
                error_count += 1
                continue
        
        logger.info(f"📊 Результаты сохранения:")
        logger.info(f"   ✅ Новых объявлений: {saved_count}")
        logger.info(f"   🔄 Обновленных: {duplicate_count}")
        logger.info(f"   ❌ Ошибок: {error_count}")
        
        return saved_count
    
    async def scrape_and_save(
        self,
        filters: Dict[str, Any],
        db: Session,
        max_pages: int = None
    ) -> Dict[str, Any]:
        """
        Полный цикл: парсинг + сохранение в БД
        
        Args:
            filters: Фильтры поиска
            db: Сессия базы данных
            max_pages: Максимальное количество страниц
            
        Returns:
            Dict: Результаты операции
        """
        start_time = datetime.now()
        
        try:
            # Шаг 1: Парсинг
            listings = await self.scrape_all_sources(filters, max_pages)
            
            if not listings:
                return {
                    "success": False,
                    "message": "Не найдено объявлений для сохранения",
                    "scraped_count": 0,
                    "saved_count": 0,
                    "elapsed_time": (datetime.now() - start_time).total_seconds()
                }
            
            # Шаг 2: Сохранение в БД
            saved_count = await self.save_listings_to_db(listings, db)
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "message": f"Успешно обработано {len(listings)} объявлений",
                "scraped_count": len(listings),
                "saved_count": saved_count,
                "sources": ["immobiliare"],
                "elapsed_time": elapsed_time
            }
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в scrape_and_save: {e}")
            return {
                "success": False,
                "message": f"Критическая ошибка: {str(e)}",
                "scraped_count": 0,
                "saved_count": 0,
                "elapsed_time": (datetime.now() - start_time).total_seconds()
            }

    # Методы для обратной совместимости со старым API
    def scrape_single_source(
        self,
        source: str,
        filters: Dict[str, Any],
        max_pages: int = None,
        use_scraperapi: bool = None
    ) -> List[Dict[str, Any]]:
        """
        УСТАРЕВШИЙ МЕТОД: Синхронная обертка для асинхронного парсинга
        Используется для обратной совместимости
        """
        logger.warning("⚠️ Используется устаревший синхронный метод scrape_single_source")
        
        # Запускаем асинхронный метод в новом event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if source == 'immobiliare':
                result = loop.run_until_complete(
                    self.scrape_immobiliare_async(filters, max_pages)
                )
            else:
                logger.error(f"❌ Неподдерживаемый источник: {source}")
                result = []
                
            loop.close()
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка в синхронной обертке: {e}")
            return [] 