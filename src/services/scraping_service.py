"""
Сервис для координации парсинга недвижимости
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from src.parsers import ImmobiliareParser
from src.crud.crud_listing import listing as crud_listing
from src.schemas.listing import ListingCreate
from src.db.models import Listing

logger = logging.getLogger(__name__)


class ScrapingService:
    """
    Сервис для координации парсинга недвижимости
    Управляет всеми парсерами и обеспечивает единый интерфейс
    """
    
    def __init__(self):
        # Инициализируем доступные парсеры
        self.parsers = {
            'immobiliare': ImmobiliareParser(),
            # Можно добавить другие парсеры:
            # 'idealista': IdealistaParser(),
            # 'subito': SubitoParser(),
        }
        
        # Настройки по умолчанию
        self.default_max_pages = 5
        self.default_use_scraperapi = True
        
    def get_available_parsers(self) -> List[str]:
        """Получить список доступных парсеров"""
        return list(self.parsers.keys())
    
    def scrape_single_source(
        self,
        source: str,
        filters: Dict[str, Any],
        max_pages: int = None,
        use_scraperapi: bool = None
    ) -> List[Dict[str, Any]]:
        """
        Запустить парсинг для одного источника
        
        Args:
            source: Название источника (immobiliare, idealista, etc.)
            filters: Фильтры поиска
            max_pages: Максимальное количество страниц
            use_scraperapi: Использовать ScraperAPI
            
        Returns:
            Список нормализованных объявлений
        """
        if source not in self.parsers:
            raise ValueError(f"Парсер '{source}' не найден. Доступные: {list(self.parsers.keys())}")
        
        parser = self.parsers[source]
        max_pages = max_pages or self.default_max_pages
        use_scraperapi = use_scraperapi if use_scraperapi is not None else self.default_use_scraperapi
        
        logger.info(f"🚀 Запуск парсинга для источника '{source}' с фильтрами: {filters}")
        
        try:
            # Валидируем фильтры для конкретного парсера
            if hasattr(parser, 'validate_filters'):
                cleaned_filters = parser.validate_filters(filters)
                logger.info(f"✅ Фильтры очищены: {cleaned_filters}")
            else:
                cleaned_filters = filters
            
            # Запускаем парсинг
            listings = parser.scrape_listings(
                filters=cleaned_filters,
                max_pages=max_pages,
                use_scraperapi=use_scraperapi
            )
            
            logger.info(f"✅ Парсинг завершен для '{source}': найдено {len(listings)} объявлений")
            return listings
            
        except Exception as e:
            logger.error(f"❌ Ошибка при парсинге источника '{source}': {e}")
            raise
    
    def scrape_all_sources(
        self,
        filters: Dict[str, Any],
        sources: List[str] = None,
        max_pages: int = None,
        use_scraperapi: bool = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Запустить парсинг для всех или выбранных источников
        
        Args:
            filters: Фильтры поиска
            sources: Список источников (None = все доступные)
            max_pages: Максимальное количество страниц
            use_scraperapi: Использовать ScraperAPI
            
        Returns:
            Словарь с результатами по каждому источнику
        """
        if sources is None:
            sources = list(self.parsers.keys())
        
        results = {}
        
        for source in sources:
            if source not in self.parsers:
                logger.warning(f"⚠️ Парсер '{source}' не найден, пропускаем")
                continue
            
            try:
                listings = self.scrape_single_source(
                    source=source,
                    filters=filters,
                    max_pages=max_pages,
                    use_scraperapi=use_scraperapi
                )
                results[source] = listings
                
            except Exception as e:
                logger.error(f"❌ Ошибка при парсинге '{source}': {e}")
                results[source] = []
        
        total_listings = sum(len(listings) for listings in results.values())
        logger.info(f"🎉 Парсинг всех источников завершен: {total_listings} объявлений")
        
        return results
    
    def save_listings_to_db(
        self,
        listings: List[Dict[str, Any]],
        db: Session,
        update_existing: bool = True
    ) -> Dict[str, int]:
        """
        Сохранить объявления в базу данных
        
        Args:
            listings: Список объявлений для сохранения
            db: Сессия базы данных
            update_existing: Обновлять существующие объявления
            
        Returns:
            Статистика сохранения (created, updated, skipped)
        """
        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        logger.info(f"💾 Начинаем сохранение {len(listings)} объявлений в БД")
        
        for listing_data in listings:
            try:
                # Проверяем существование объявления
                existing_listing = crud_listing.get_by_external_id(
                    db=db,
                    source=listing_data['source'],
                    external_id=listing_data['external_id']
                )
                
                if existing_listing:
                    if update_existing:
                        # Обновляем существующее объявление
                        updated_data = listing_data.copy()
                        updated_data['scraped_at'] = datetime.utcnow()
                        
                        updated_listing = crud_listing.update(
                            db=db,
                            db_obj=existing_listing,
                            obj_in=updated_data
                        )
                        stats['updated'] += 1
                        logger.debug(f"🔄 Обновлено объявление: {updated_listing.external_id}")
                    else:
                        stats['skipped'] += 1
                        logger.debug(f"⏭️ Пропущено существующее объявление: {listing_data['external_id']}")
                else:
                    # Создаем новое объявление
                    listing_data['scraped_at'] = datetime.utcnow()
                    
                    # Создаем схему для валидации
                    listing_create = ListingCreate(**listing_data)
                    
                    # Сохраняем в БД
                    new_listing = crud_listing.create(db=db, obj_in=listing_create)
                    stats['created'] += 1
                    logger.debug(f"✅ Создано новое объявление: {new_listing.external_id}")
                
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"❌ Ошибка при сохранении объявления {listing_data.get('external_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"💾 Сохранение завершено: создано {stats['created']}, обновлено {stats['updated']}, пропущено {stats['skipped']}, ошибок {stats['errors']}")
        return stats
    
    def scrape_and_save(
        self,
        filters: Dict[str, Any],
        db: Session,
        sources: List[str] = None,
        max_pages: int = None,
        use_scraperapi: bool = None,
        update_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Полный цикл: парсинг + сохранение в БД
        
        Args:
            filters: Фильтры поиска
            db: Сессия базы данных
            sources: Список источников (None = все)
            max_pages: Максимальное количество страниц
            use_scraperapi: Использовать ScraperAPI
            update_existing: Обновлять существующие объявления
            
        Returns:
            Полная статистика операции
        """
        start_time = datetime.utcnow()
        
        logger.info(f"🚀 Запуск полного цикла парсинга и сохранения")
        logger.info(f"📋 Фильтры: {filters}")
        logger.info(f"🌐 Источники: {sources or 'все доступные'}")
        
        try:
            # Этап 1: Парсинг
            scraping_results = self.scrape_all_sources(
                filters=filters,
                sources=sources,
                max_pages=max_pages,
                use_scraperapi=use_scraperapi
            )
            
            # Этап 2: Объединение результатов
            all_listings = []
            for source, listings in scraping_results.items():
                all_listings.extend(listings)
            
            # Этап 3: Дедупликация
            unique_listings = self._deduplicate_listings(all_listings)
            
            # Этап 4: Сохранение в БД
            save_stats = self.save_listings_to_db(
                listings=unique_listings,
                db=db,
                update_existing=update_existing
            )
            
            # Финальная статистика
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            final_stats = {
                'duration_seconds': duration,
                'sources_processed': len(scraping_results),
                'total_scraped': len(all_listings),
                'unique_listings': len(unique_listings),
                'database_stats': save_stats,
                'scraping_results': {
                    source: len(listings) 
                    for source, listings in scraping_results.items()
                }
            }
            
            logger.info(f"🎉 Полный цикл завершен за {duration:.1f} секунд")
            logger.info(f"📊 Итоговая статистика: {final_stats}")
            
            return final_stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка в полном цикле парсинга: {e}")
            raise
    
    def _deduplicate_listings(self, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Удалить дубликаты объявлений
        
        Args:
            listings: Список объявлений
            
        Returns:
            Список уникальных объявлений
        """
        seen = set()
        unique_listings = []
        
        for listing in listings:
            # Создаем уникальный ключ из источника и external_id
            key = f"{listing['source']}_{listing['external_id']}"
            
            if key not in seen:
                seen.add(key)
                unique_listings.append(listing)
            else:
                logger.debug(f"🔄 Удален дубликат: {key}")
        
        duplicates_count = len(listings) - len(unique_listings)
        if duplicates_count > 0:
            logger.info(f"🧹 Удалено {duplicates_count} дубликатов, осталось {len(unique_listings)} уникальных объявлений")
        
        return unique_listings
    
    def get_parser_info(self, source: str) -> Dict[str, Any]:
        """
        Получить информацию о парсере
        
        Args:
            source: Название источника
            
        Returns:
            Информация о парсере
        """
        if source not in self.parsers:
            return None
        
        parser = self.parsers[source]
        
        info = {
            'name': parser.name,
            'base_url': parser.base_url,
            'has_scraperapi': bool(parser.scraperapi_key),
        }
        
        # Дополнительная информация, если доступна
        if hasattr(parser, 'get_supported_cities'):
            info['supported_cities'] = parser.get_supported_cities()
        
        return info
    
    def get_all_parsers_info(self) -> Dict[str, Dict[str, Any]]:
        """Получить информацию о всех парсерах"""
        return {
            source: self.get_parser_info(source)
            for source in self.parsers.keys()
        }
    
    def test_parser(
        self,
        source: str,
        test_filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Протестировать парсер с минимальными настройками
        
        Args:
            source: Название источника
            test_filters: Тестовые фильтры (по умолчанию Roma)
            
        Returns:
            Результаты тестирования
        """
        if source not in self.parsers:
            return {'error': f"Парсер '{source}' не найден"}
        
        # Тестовые фильтры по умолчанию
        if test_filters is None:
            test_filters = {'city': 'roma'}
        
        try:
            start_time = datetime.utcnow()
            
            listings = self.scrape_single_source(
                source=source,
                filters=test_filters,
                max_pages=1,  # Только одна страница для теста
                use_scraperapi=False  # Без ScraperAPI для быстроты
            )
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'source': source,
                'filters_used': test_filters,
                'listings_found': len(listings),
                'duration_seconds': duration,
                'sample_listing': listings[0] if listings else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'source': source,
                'error': str(e)
            } 