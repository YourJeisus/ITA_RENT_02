"""
API endpoints для управления парсингом недвижимости
"""
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from sqlalchemy import text

from src.api.deps import get_current_user, get_db
from src.db.models import User
from src.services.scraping_service import ScrapingService

logger = logging.getLogger(__name__)

router = APIRouter()

# Инициализируем сервис парсинга
scraping_service = ScrapingService()


class ScrapingRequest(BaseModel):
    """Схема запроса на парсинг"""
    filters: Dict[str, Any]
    sources: Optional[List[str]] = None
    max_pages: int = 5
    use_scraperapi: bool = True
    update_existing: bool = True
    
    @validator('max_pages')
    def validate_max_pages(cls, v):
        if v < 1 or v > 20:
            raise ValueError('max_pages должно быть от 1 до 20')
        return v
    
    @validator('sources')
    def validate_sources(cls, v):
        if v is not None:
            available_sources = scraping_service.get_available_parsers()
            for source in v:
                if source not in available_sources:
                    raise ValueError(f'Неизвестный источник: {source}. Доступные: {available_sources}')
        return v


class ScrapingResponse(BaseModel):
    """Схема ответа парсинга"""
    success: bool
    message: str
    stats: Dict[str, Any]


class ParserTestRequest(BaseModel):
    """Схема запроса тестирования парсера"""
    source: str
    test_filters: Optional[Dict[str, Any]] = None


@router.get("/parsers", response_model=Dict[str, Dict[str, Any]])
async def get_available_parsers():
    """
    Получить информацию о всех доступных парсерах
    """
    try:
        parsers_info = scraping_service.get_all_parsers_info()
        return parsers_info
    except Exception as e:
        logger.error(f"Ошибка при получении информации о парсерах: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении информации о парсерах"
        )


@router.get("/parsers/{source}", response_model=Dict[str, Any])
async def get_parser_info(source: str):
    """
    Получить информацию о конкретном парсере
    """
    try:
        parser_info = scraping_service.get_parser_info(source)
        if not parser_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Парсер '{source}' не найден"
            )
        return parser_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении информации о парсере {source}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении информации о парсере"
        )


@router.post("/test", response_model=Dict[str, Any])
async def test_parser(
    request: ParserTestRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Протестировать парсер с минимальными настройками
    Доступно только авторизованным пользователям
    """
    try:
        logger.info(f"Пользователь {current_user.email} тестирует парсер {request.source}")
        
        result = scraping_service.test_parser(
            source=request.source,
            test_filters=request.test_filters
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании парсера {request.source}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при тестировании парсера: {str(e)}"
        )


@router.post("/run", response_model=ScrapingResponse)
async def run_scraping(
    request: ScrapingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Запустить парсинг недвижимости
    Доступно только авторизованным пользователям
    """
    try:
        logger.info(f"Пользователь {current_user.email} запускает парсинг с параметрами: {request.dict()}")
        
        # Проверяем, что пользователь может запускать парсинг
        # В MVP версии - любой авторизованный пользователь
        # В будущем можно добавить проверку подписки или роли
        
        # Запускаем парсинг синхронно для простоты
        # В production версии можно сделать асинхронно через background_tasks
        stats = scraping_service.scrape_and_save(
            filters=request.filters,
            db=db,
            sources=request.sources,
            max_pages=request.max_pages,
            use_scraperapi=request.use_scraperapi,
            update_existing=request.update_existing
        )
        
        logger.info(f"Парсинг завершен для пользователя {current_user.email}: {stats}")
        
        return ScrapingResponse(
            success=True,
            message=f"Парсинг завершен успешно. Обработано {stats['total_scraped']} объявлений.",
            stats=stats
        )
        
    except ValueError as e:
        logger.warning(f"Неверные параметры парсинга от пользователя {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Ошибка при парсинге для пользователя {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при выполнении парсинга: {str(e)}"
        )


@router.post("/run-async", response_model=Dict[str, str])
async def run_scraping_async(
    request: ScrapingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Запустить парсинг в фоновом режиме
    Возвращает немедленно, парсинг выполняется асинхронно
    """
    try:
        logger.info(f"Пользователь {current_user.email} запускает асинхронный парсинг")
        
        # Добавляем задачу в фоновые процессы
        background_tasks.add_task(
            _run_background_scraping,
            request=request,
            user_id=current_user.id,
            user_email=current_user.email
        )
        
        return {
            "message": "Парсинг запущен в фоновом режиме",
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Ошибка при запуске асинхронного парсинга: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при запуске асинхронного парсинга"
        )


async def _run_background_scraping(
    request: ScrapingRequest,
    user_id: int,
    user_email: str
):
    """
    Фоновая функция для выполнения парсинга
    """
    try:
        logger.info(f"Начинаем фоновый парсинг для пользователя {user_email}")
        
        # Получаем новую сессию БД для фонового процесса
        from src.db.database import SessionLocal
        db = SessionLocal()
        
        try:
            stats = scraping_service.scrape_and_save(
                filters=request.filters,
                db=db,
                sources=request.sources,
                max_pages=request.max_pages,
                use_scraperapi=request.use_scraperapi,
                update_existing=request.update_existing
            )
            
            logger.info(f"Фоновый парсинг завершен для пользователя {user_email}: {stats}")
            
            # Здесь можно добавить уведомление пользователю о завершении
            # Например, через Telegram или email
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в фоновом парсинге для пользователя {user_email}: {e}")


@router.get("/status")
async def get_scraping_status():
    """
    Получить статус системы парсинга
    """
    try:
        # Базовая информация о статусе
        status_info = {
            "available_parsers": scraping_service.get_available_parsers(),
            "total_parsers": len(scraping_service.parsers),
            "system_status": "operational"
        }
        
        # Дополнительная информация о каждом парсере
        parsers_status = {}
        for source in scraping_service.get_available_parsers():
            parser_info = scraping_service.get_parser_info(source)
            parsers_status[source] = {
                "name": parser_info.get("name"),
                "has_scraperapi": parser_info.get("has_scraperapi", False),
                "status": "ready"
            }
        
        status_info["parsers_status"] = parsers_status
        
        return status_info
        
    except Exception as e:
        logger.error(f"Ошибка при получении статуса парсинга: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении статуса системы"
        ) 


@router.post("/run-public", response_model=ScrapingResponse)
async def run_scraping_public(
    city: str = "Roma",
    max_pages: int = 10,
    db: Session = Depends(get_db)
):
    """
    ВРЕМЕННЫЙ публичный endpoint для запуска парсинга без авторизации
    Только для тестирования и первичного заполнения БД
    """
    try:
        logger.info(f"Публичный запуск парсинга для города {city}, страниц: {max_pages}")
        
        # Базовые фильтры для Рима
        filters = {
            "city": city,
            "min_price": 500,
            "max_price": 3000,
            "property_type": "apartment"
        }
        
        # Запускаем парсинг с правильными параметрами
        stats = await scraping_service.scrape_and_save(
            filters=filters,
            db=db,
            max_pages=max_pages
        )
        
        logger.info(f"Публичный парсинг завершен: {stats}")
        
        return ScrapingResponse(
            success=True,
            message=f"Парсинг завершен успешно. Обработано {stats.get('scraped_count', 0)} объявлений.",
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Ошибка при публичном парсинге: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при выполнении парсинга: {str(e)}"
        ) 


@router.get("/test-db")
async def test_database_connection(db: Session = Depends(get_db)):
    """
    Тестирование подключения к базе данных
    """
    try:
        # Простой запрос для проверки БД
        result = db.execute(text("SELECT 1 as test"))
        test_value = result.scalar()
        
        # Проверяем количество таблиц
        tables_result = db.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in tables_result.fetchall()]
        
        return {
            "success": True,
            "database_connection": "OK",
            "test_query": test_value,
            "tables_count": len(tables),
            "tables": tables
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к БД: {e}")
        return {
            "success": False,
            "error": str(e),
            "database_connection": "FAILED"
        } 


@router.post("/test-create-listing")
async def test_create_listing(db: Session = Depends(get_db)):
    """
    Тестирование создания простого объявления
    """
    try:
        from src.schemas.listing import ListingCreate
        from src.crud.crud_listing import listing as crud_listing
        from datetime import datetime
        
        # Простое тестовое объявление
        test_listing_data = {
            "external_id": "TEST123",
            "source": "immobiliare",
            "url": "https://test.com/listing/123",
            "title": "Test Apartment",
            "description": "Test description",
            "price": 1500.0,
            "price_currency": "EUR",
            "property_type": "apartment",
            "rooms": 3,
            "city": "Roma",
            "images": ["https://example.com/image1.jpg"],
            "is_active": True,
            "scraped_at": datetime.utcnow()
        }
        
        # Создаем через Pydantic схему
        listing_create = ListingCreate(**test_listing_data)
        
        # Сохраняем в БД
        new_listing = crud_listing.create(db=db, obj_in=listing_create)
        
        return {
            "success": True,
            "message": "Тестовое объявление создано",
            "listing_id": new_listing.id,
            "external_id": new_listing.external_id
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания тестового объявления: {e}")
        return {
            "success": False,
            "error": str(e)
        } 