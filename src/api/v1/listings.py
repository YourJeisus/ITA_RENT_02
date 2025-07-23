"""
API endpoints для работы с объявлениями
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.crud.crud_listing import listing
from src.schemas.listing import ListingResponse, ListingSearch
from src.services.scraping_service import ScrapingService

router = APIRouter()


@router.get("/", response_model=dict)
async def search_listings(
    city: Optional[str] = Query(None, description="Город для поиска"),
    min_price: Optional[float] = Query(None, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, description="Максимальная цена"),
    property_type: Optional[str] = Query(None, description="Тип недвижимости"),
    min_rooms: Optional[int] = Query(None, description="Минимальное количество комнат"),
    max_rooms: Optional[int] = Query(None, description="Максимальное количество комнат"),
    min_area: Optional[float] = Query(None, description="Минимальная площадь"),
    max_area: Optional[float] = Query(None, description="Максимальная площадь"),
    source_site: Optional[str] = Query(None, description="Источник (idealista, immobiliare)"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Количество записей на странице"),
    db: Session = Depends(get_db)
):
    """
    Поиск объявлений с фильтрами
    """
    try:
        # Сначала ищем в базе данных
        filters = {
            "city": city,
            "min_price": min_price,
            "max_price": max_price,
            "property_type": property_type,
            "min_rooms": min_rooms,
            "max_rooms": max_rooms,
            "min_area": min_area,
            "max_area": max_area,
            "source_site": source_site
        }
        
        # Убираем None значения
        filters = {k: v for k, v in filters.items() if v is not None}
        
        listings_data = listing.search_with_filters(
            db=db,
            filters=filters,
            skip=skip,
            limit=limit
        )
        
        total_count = listing.count_with_filters(db=db, filters=filters)
        
        # Если в базе мало результатов и это первая страница, запускаем парсинг
        should_scrape = (
            total_count < 10 and 
            skip == 0 and 
            city  # Обязательно нужен город для парсинга
        )
        
        search_type = "database"
        search_message = f"Найдено {total_count} объявлений в базе данных"
        
        if should_scrape:
            try:
                scraping_service = ScrapingService()
                scraping_filters = {
                    "city": city,
                    "min_price": min_price,
                    "max_price": max_price,
                    "property_type": property_type,
                    "min_rooms": min_rooms
                }
                
                scraped_listings = await scraping_service.scrape_all_sources(
                    filters=scraping_filters,
                    max_pages=2
                )
                
                if scraped_listings:
                    # Обновляем результаты после парсинга
                    listings_data = listing.search_with_filters(
                        db=db,
                        filters=filters,
                        skip=skip,
                        limit=limit
                    )
                    total_count = listing.count_with_filters(db=db, filters=filters)
                    search_type = "scraping"
                    search_message = f"Найдено {len(scraped_listings)} новых объявлений через парсинг. Всего в базе: {total_count}"
                
            except Exception as e:
                # Если парсинг не удался, продолжаем с результатами из базы
                print(f"Scraping failed: {e}")
        
        return {
            "success": True,
            "listings": [
                {
                    "id": str(l.id),
                    "source_site": l.source,
                    "original_id": l.external_id,
                    "url": l.url,
                    "title": l.title,
                    "description": l.description,
                    "price": l.price,
                    "currency": l.price_currency,
                    "address_text": l.address,
                    "city": l.city,
                    "district": l.district,
                    "latitude": l.latitude,
                    "longitude": l.longitude,
                    "area_sqm": l.area,
                    "num_rooms": l.rooms,
                    "num_bedrooms": l.bedrooms,
                    "num_bathrooms": l.bathrooms,
                    "floor": l.floor,
                    "property_type": l.property_type,
                    "features": [],  # TODO: добавить поддержку features
                    "photos_urls": l.images if l.images else [],
                    "published_at": l.scraped_at.isoformat() if l.scraped_at else None,
                    "created_at": l.created_at.isoformat() if l.created_at else None,
                    "last_seen_at": l.updated_at.isoformat() if l.updated_at else None,
                    "is_available": l.is_active
                }
                for l in listings_data
            ],
            "total_count": total_count,
            "returned_count": len(listings_data),
            "search_type": search_type,
            "message": search_message,
            "filters_used": filters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


@router.get("/{listing_id}", response_model=dict)
async def get_listing(
    listing_id: int,
    db: Session = Depends(get_db)
):
    """
    Получение детальной информации об объявлении
    """
    listing_obj = listing.get(db=db, id=listing_id)
    if not listing_obj:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    
    return {
        "id": str(listing_obj.id),
        "source_site": listing_obj.source,
        "original_id": listing_obj.external_id,
        "url": listing_obj.url,
        "title": listing_obj.title,
        "description": listing_obj.description,
        "price": listing_obj.price,
        "currency": listing_obj.price_currency,
        "address_text": listing_obj.address,
        "city": listing_obj.city,
        "district": listing_obj.district,
        "latitude": listing_obj.latitude,
        "longitude": listing_obj.longitude,
        "area_sqm": listing_obj.area,
        "num_rooms": listing_obj.rooms,
        "num_bedrooms": listing_obj.bedrooms,
        "num_bathrooms": listing_obj.bathrooms,
        "floor": listing_obj.floor,
        "property_type": listing_obj.property_type,
        "features": [],
        "photos_urls": listing_obj.images if listing_obj.images else [],
        "published_at": listing_obj.scraped_at.isoformat() if listing_obj.scraped_at else None,
        "created_at": listing_obj.created_at.isoformat() if listing_obj.created_at else None,
        "last_seen_at": listing_obj.updated_at.isoformat() if listing_obj.updated_at else None,
        "is_available": listing_obj.is_active
    }


@router.get("/suggestions/cities", response_model=List[str])
async def get_cities(
    db: Session = Depends(get_db)
):
    """
    Получение списка доступных городов
    """
    cities = listing.get_available_cities(db=db)
    return cities


@router.get("/stats/database", response_model=dict)
async def get_database_stats(
    db: Session = Depends(get_db)
):
    """
    Статистика базы данных объявлений
    """
    stats = listing.get_database_stats(db=db)
    return {
        "success": True,
        "stats": stats
    } 