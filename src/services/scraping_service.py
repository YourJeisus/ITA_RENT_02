"""
Сервис для координации парсинга недвижимости
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from src.parsers import CasaScraper, SubitoScraper, IdealistaScraper, ImmobiliareScraper
from src.crud.crud_listing import listing as crud_listing
from src.schemas.listing import ListingCreate
from src.db.models import Listing

logger = logging.getLogger(__name__)


class ScrapingService:
    """
    Сервис для координации парсинга недвижимости
    Поддерживает все 4 источника: Casa.it, Subito, Idealista, Immobiliare
    """
    
    def __init__(self):
        # Инициализируем все скраперы
        self.casa_scraper = CasaScraper(max_concurrent=5, enable_geocoding=False)
        self.subito_scraper = SubitoScraper(enable_geocoding=False, fetch_coords=False)
        self.idealista_scraper = IdealistaScraper(max_concurrent=5, enable_geocoding=False)
        self.immobiliare_scraper = ImmobiliareScraper(enable_geocoding=False)
        
        # Настройки по умолчанию
        self.default_max_pages = 5
        
    def get_available_sources(self) -> List[str]:
        """Получить список доступных источников"""
        return ['casa_it', 'subito', 'idealista', 'immobiliare']
    
    async def scrape_casa_async(
        self,
        filters: Dict[str, Any],
        max_pages: int = None
    ) -> List[Dict[str, Any]]:
        """Асинхронный парсинг Casa.it"""
        if max_pages is None:
            max_pages = self.default_max_pages
            
        try:
            logger.info(f"🚀 Запускаем парсинг Casa.it на {max_pages} страниц")
            listings = await self.casa_scraper.scrape_multiple_pages(max_pages=max_pages)
            logger.info(f"✅ Получено {len(listings)} объявлений из Casa.it")
            return listings
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга Casa.it: {e}")
            return []
    
    async def scrape_subito_async(
        self,
        filters: Dict[str, Any],
        max_pages: int = None
    ) -> List[Dict[str, Any]]:
        """Асинхронный парсинг Subito"""
        if max_pages is None:
            max_pages = self.default_max_pages
            
        try:
            logger.info(f"🚀 Запускаем парсинг Subito.it на {max_pages} страниц")
            listings = await self.subito_scraper.scrape_multiple_pages(max_pages=max_pages)
            logger.info(f"✅ Получено {len(listings)} объявлений из Subito.it")
            return listings
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга Subito.it: {e}")
            return []
    
    async def scrape_idealista_async(
        self,
        filters: Dict[str, Any],
        max_pages: int = None
    ) -> List[Dict[str, Any]]:
        """Асинхронный парсинг Idealista"""
        if max_pages is None:
            max_pages = self.default_max_pages
            
        try:
            logger.info(f"🚀 Запускаем парсинг Idealista.it на {max_pages} страниц")
            listings = await self.idealista_scraper.scrape_multiple_pages(max_pages=max_pages)
            logger.info(f"✅ Получено {len(listings)} объявлений из Idealista.it")
            return listings
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга Idealista.it: {e}")
            return []
    
    async def scrape_immobiliare_async(
        self,
        filters: Dict[str, Any],
        max_pages: int = None
    ) -> List[Dict[str, Any]]:
        """Асинхронный парсинг Immobiliare.it"""
        if max_pages is None:
            max_pages = self.default_max_pages
            
        try:
            logger.info(f"🚀 Запускаем парсинг Immobiliare.it на {max_pages} страниц")
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
        
        # Запускаем парсинг всех источников параллельно
        results = await asyncio.gather(
            self.scrape_casa_async(filters, max_pages),
            self.scrape_subito_async(filters, max_pages),
            self.scrape_idealista_async(filters, max_pages),
            self.scrape_immobiliare_async(filters, max_pages),
            return_exceptions=True
        )
        
        # Объединяем результаты
        all_listings = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Ошибка парсинга: {result}")
            elif isinstance(result, list):
                all_listings.extend(result)
        
        logger.info(f"📊 Всего получено {len(all_listings)} объявлений из всех источников")
        return all_listings
    
    def save_listings_to_db(
        self,
        listings: List[Dict[str, Any]],
        db: Session
    ) -> Dict[str, int]:
        """
        Сохраняет объявления в базу данных с дедупликацией
        
        Args:
            listings: Список объявлений для сохранения
            db: Сессия базы данных
            
        Returns:
            Dict[str, int]: Статистика сохранения
        """
        if not listings:
            return {"created": 0, "updated": 0, "errors": 0, "skipped_duplicates": 0}
            
        stats = {
            "created": 0, 
            "updated": 0, 
            "errors": 0, 
            "skipped_duplicates": 0,
            "by_source": {}
        }
        
        logger.info(f"💾 Сохраняем {len(listings)} объявлений в базу данных...")
        
        # Группируем по источникам для статистики
        for listing_data in listings:
            source = listing_data.get('source', 'unknown')
            if source not in stats["by_source"]:
                stats["by_source"][source] = {
                    "total": 0, "created": 0, "updated": 0, "errors": 0, "skipped": 0
                }
            stats["by_source"][source]["total"] += 1
        
        for listing_data in listings:
            try:
                external_id = listing_data.get('external_id')
                source = listing_data.get('source', 'unknown')
                url = listing_data.get('url', '')
                
                if not external_id:
                    logger.warning("⚠️ Объявление без external_id, пропускаем")
                    stats["errors"] += 1
                    stats["by_source"][source]["errors"] += 1
                    continue
                
                # Сначала проверяем по external_id + source (основной способ)
                existing = crud_listing.get_by_external_id(
                    db=db,
                    external_id=external_id,
                    source=source
                )
                
                # Если не найдено по external_id, проверяем по URL
                if not existing and url:
                    existing = crud_listing.get_by_url(db=db, url=url)
                    
                    if existing and existing.source != source:
                        # Объявление с таким URL уже есть, но из другого источника
                        # Обновляем external_id и source в существующем объявлении
                        logger.info(f"🔗 Найдено существующее объявление с URL {url[:50]}... из источника {existing.source}, обновляем на {source}")
                        listing_update = ListingCreate(**listing_data)
                        crud_listing.update(db=db, db_obj=existing, obj_in=listing_update)
                        stats["updated"] += 1
                        stats["by_source"][source]["updated"] += 1
                        continue
                    elif existing:
                        # То же самое объявление, пропускаем
                        logger.debug(f"🔄 Объявление с URL уже существует: {url[:50]}...")
                        stats["skipped_duplicates"] += 1
                        stats["by_source"][source]["skipped"] += 1
                        continue
                
                if existing:
                    # Обновляем существующее объявление
                    listing_update = ListingCreate(**listing_data)
                    crud_listing.update(db=db, db_obj=existing, obj_in=listing_update)
                    stats["updated"] += 1
                    stats["by_source"][source]["updated"] += 1
                    logger.debug(f"🔄 Обновлено объявление {external_id}")
                else:
                    # Создаем новое объявление
                    listing_create = ListingCreate(**listing_data)
                    crud_listing.create(db=db, obj_in=listing_create)
                    stats["created"] += 1
                    stats["by_source"][source]["created"] += 1
                    logger.debug(f"✅ Создано объявление {external_id}")
                    
            except Exception as e:
                error_msg = str(e)
                source = listing_data.get('source', 'unknown')
                
                # Обработка дубликатов URL
                if "duplicate key value violates unique constraint" in error_msg and "url" in error_msg:
                    logger.warning(f"⚠️ Дубликат URL для {external_id}, пропускаем")
                    stats["skipped_duplicates"] += 1
                    stats["by_source"][source]["skipped"] += 1
                    
                    # НЕ делаем rollback для дубликатов URL - это нормально
                    continue
                else:
                    logger.error(f"❌ Ошибка сохранения объявления {external_id}: {e}")
                    
                    # Принудительный rollback сессии при ошибках
                    try:
                        db.rollback()
                        logger.debug("🔄 Сессия БД откатана")
                    except Exception as rollback_error:
                        logger.error(f"❌ Ошибка rollback: {rollback_error}")
                    
                    # Детальное логирование для диагностики
                    if "value too long" in error_msg:
                        logger.error(f"🔍 Слишком длинное значение в объявлении {external_id}")
                        for field, value in listing_data.items():
                            if isinstance(value, str) and len(value) > 100:
                                logger.error(f"   📏 Поле '{field}': {len(value)} символов (первые 100: {value[:100]}...)")
                    
                    stats["errors"] += 1
                    stats["by_source"][source]["errors"] += 1
                    continue
        
        # Подробная статистика
        logger.info(f"💾 Статистика сохранения:")
        logger.info(f"   📊 Общая: {stats['created']} новых, {stats['updated']} обновлено, {stats['skipped_duplicates']} дубликатов, {stats['errors']} ошибок")
        
        for source, source_stats in stats["by_source"].items():
            logger.info(f"   📌 {source}: {source_stats['created']} новых, {source_stats['updated']} обновлено, {source_stats['skipped']} пропущено, {source_stats['errors']} ошибок из {source_stats['total']} всего")
        
        return stats
    
    def save_listing(self, db: Session, listing_data: Dict[str, Any]) -> str:
        """
        Сохраняет одно объявление в базу данных
        
        Args:
            db: Сессия базы данных
            listing_data: Данные объявления
            
        Returns:
            str: "created", "updated" или "error"
        """
        try:
            # Проверяем, существует ли уже такое объявление
            external_id = listing_data.get('external_id')
            source = listing_data.get('source', 'immobiliare')
            
            if not external_id:
                logger.warning("⚠️ Объявление без external_id, пропускаем")
                return "error"
            
            existing = crud_listing.get_by_external_id(
                db=db,
                external_id=external_id,
                source=source
            )
            
            if existing:
                # Обновляем существующее объявление
                listing_update = ListingCreate(**listing_data)
                crud_listing.update(db=db, db_obj=existing, obj_in=listing_update)
                logger.debug(f"🔄 Обновлено объявление {external_id}")
                return "updated"
            else:
                # Создаем новое объявление
                listing_create = ListingCreate(**listing_data)
                crud_listing.create(db=db, obj_in=listing_create)
                logger.debug(f"✅ Создано объявление {external_id}")
                return "created"
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения объявления {external_id}: {e}")
            
            # Принудительный rollback сессии при ошибках
            try:
                db.rollback()
                logger.debug("🔄 Сессия БД откатана")
            except Exception as rollback_error:
                logger.error(f"❌ Ошибка rollback: {rollback_error}")
            
            return "error"
    
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
            saved_stats = self.save_listings_to_db(listings, db)
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "message": f"Успешно обработано {len(listings)} объявлений",
                "scraped_count": len(listings),
                "saved_count": saved_stats["created"],
                "updated_count": saved_stats["updated"],
                "error_count": saved_stats["errors"],
                "sources": ["casa_it", "subito", "idealista", "immobiliare"],
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

    def get_database_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Получение статистики базы данных по источникам и общих метрик
        """
        try:
            from src.db.models import Listing
            from sqlalchemy import func, desc
            from datetime import datetime, timedelta
            
            # Общая статистика
            total_listings = db.query(func.count(Listing.id)).scalar()
            active_listings = db.query(func.count(Listing.id)).filter(Listing.is_active == True).scalar()
            
            # Статистика по источникам
            source_stats = db.query(
                Listing.source,
                func.count(Listing.id).label('total'),
                func.count(func.nullif(Listing.is_active, False)).label('active')
            ).group_by(Listing.source).all()
            
            # Статистика за последние 24 часа
            since_24h = datetime.utcnow() - timedelta(hours=24)
            recent_stats = db.query(
                Listing.source,
                func.count(Listing.id).label('recent_24h')
            ).filter(
                Listing.created_at >= since_24h
            ).group_by(Listing.source).all()
            
            # Статистика за последнюю неделю
            since_week = datetime.utcnow() - timedelta(days=7)
            week_stats = db.query(
                Listing.source,
                func.count(Listing.id).label('recent_week')
            ).filter(
                Listing.created_at >= since_week
            ).group_by(Listing.source).all()
            
            # Собираем результат
            result = {
                "total_listings": total_listings,
                "active_listings": active_listings,
                "inactive_listings": total_listings - active_listings,
                "by_source": {},
                "recent_24h": {},
                "recent_week": {}
            }
            
            # Заполняем статистику по источникам
            for source, total, active in source_stats:
                result["by_source"][source] = {
                    "total": total,
                    "active": active,
                    "inactive": total - active
                }
            
            # Заполняем недавние статистики
            for source, count in recent_stats:
                result["recent_24h"][source] = count
                
            for source, count in week_stats:
                result["recent_week"][source] = count
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики БД: {e}")
            return {
                "error": str(e),
                "total_listings": 0,
                "active_listings": 0,
                "by_source": {}
            } 