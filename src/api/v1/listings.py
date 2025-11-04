"""
API endpoints для работы с объявлениями
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.crud.crud_listing import listing
from src.schemas.listing import ListingResponse, ListingSearch
from src.services.scraping_service import ScrapingService
from src.services.telegram_bot import telegram_bot
import logging

router = APIRouter()


# Добавляем функцию очистки изображений
def _clean_images(images: Optional[List[str]]) -> List[str]:
    """
    Очищает список изображений от пустых значений и дубликатов
    
    Args:
        images: Список URL изображений
        
    Returns:
        Очищенный список уникальных валидных URL
    """
    if not images:
        return []
    
    # Фильтруем пустые значения и приводим к нижнему регистру для сравнения
    valid_images = []
    seen = set()
    
    for img_url in images:
        if img_url and isinstance(img_url, str):
            cleaned_url = img_url.strip()
            # Проверяем валидность URL
            if cleaned_url and (cleaned_url.startswith('http://') or cleaned_url.startswith('https://')):
                # Нормализуем для дедупликации (игнорируем параметры запроса)
                base_url = cleaned_url.split('?')[0].split('#')[0].lower()
                if base_url not in seen:
                    seen.add(base_url)
                    valid_images.append(cleaned_url)
    
    return valid_images


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
    force_scraping: bool = Query(False, description="Принудительно запустить парсинг"),
    max_pages: int = Query(5, ge=1, le=20, description="Максимальное количество страниц для парсинга"),
    db: Session = Depends(get_db)
):
    """
    Поиск объявлений с фильтрами и автоматическим парсингом
    """
    try:
        # Формируем фильтры
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
        
        # Сначала ищем в базе данных
        listings_data = listing.search_with_filters(
            db=db,
            filters=filters,
            skip=skip,
            limit=limit
        )
        
        total_count = listing.count_with_filters(db=db, filters=filters)
        
        # Определяем, нужен ли парсинг (только по явному запросу)
        should_scrape = force_scraping
        
        search_type = "database"
        search_message = f"Найдено {total_count} объявлений в базе данных"
        scraping_stats = None
        
        if should_scrape:
            try:
                # Создаем новый асинхронный сервис парсинга
                scraping_service = ScrapingService()
                
                # Формируем фильтры для парсинга
                scraping_filters = {
                    "city": city or "roma",  # По умолчанию Рим
                    "min_price": min_price,
                    "max_price": max_price,
                    "property_type": property_type,
                    "min_rooms": min_rooms
                }
                
                # Запускаем асинхронный парсинг с сохранением в БД
                scraping_result = await scraping_service.scrape_and_save(
                    filters=scraping_filters,
                    db=db,
                    max_pages=max_pages
                )
                
                if scraping_result.get("success"):
                    # Обновляем результаты после парсинга
                    listings_data = listing.search_with_filters(
                        db=db,
                        filters=filters,
                        skip=skip,
                        limit=limit
                    )
                    total_count = listing.count_with_filters(db=db, filters=filters)
                    
                    search_type = "scraping"
                    search_message = (
                        f"Найдено {scraping_result['scraped_count']} новых объявлений через парсинг. "
                        f"Сохранено: {scraping_result['saved_count']}. Всего в базе: {total_count}"
                    )
                    
                    scraping_stats = {
                        "scraped_count": scraping_result["scraped_count"],
                        "saved_count": scraping_result["saved_count"],
                        "sources": scraping_result["sources"],
                        "elapsed_time": scraping_result["elapsed_time"]
                    }
                else:
                    search_message += f". Парсинг не удался: {scraping_result.get('message', 'Неизвестная ошибка')}"
                
            except Exception as e:
                # Если парсинг не удался, продолжаем с результатами из базы
                search_message += f". Ошибка парсинга: {str(e)}"
                print(f"Scraping failed: {e}")
        
        # Формируем ответ
        response_data = {
            "success": True,
            "search_type": search_type,
            "message": search_message,
            "total_count": total_count,
            "returned_count": len(listings_data),
            "page_info": {
                "skip": skip,
                "limit": limit,
                "has_more": total_count > skip + limit
            },
            "results": [
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
                    "num_bathrooms": l.bathrooms,
                    "property_type": l.property_type,
                    "floor": l.floor,
                    "is_furnished": l.furnished,
                    "pets_allowed": l.pets_allowed,
                    "features": l.features if hasattr(l, 'features') else [],
                    "images": _clean_images(l.images),
                    "virtual_tour_url": l.virtual_tour_url,
                    "agency_name": l.agency_name if hasattr(l, 'agency_name') else None,
                    "is_active": l.is_active,
                    "published_at": l.published_at.isoformat() if l.published_at else None,
                    "scraped_at": l.scraped_at.isoformat() if l.scraped_at else None,
                    "created_at": l.created_at.isoformat() if l.created_at else None,
                    "updated_at": l.updated_at.isoformat() if l.updated_at else None
                }
                for l in listings_data
            ]
        }
        
        # Добавляем статистику парсинга, если она есть
        if scraping_stats:
            response_data["scraping_stats"] = scraping_stats
        
        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при поиске объявлений: {str(e)}"
        )


@router.get("/map", response_model=dict)
async def get_listings_for_map(
    city: Optional[str] = Query(None, description="Город для поиска"),
    min_price: Optional[float] = Query(None, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, description="Максимальная цена"),
    property_type: Optional[str] = Query(None, description="Тип недвижимости"),
    source_site: Optional[str] = Query(None, description="Источник (casa_it, subito, idealista, immobiliare)"),
    limit: int = Query(500, ge=1, le=1000, description="Максимальное количество объявлений"),
    db: Session = Depends(get_db)
):
    """
    Получить объявления с координатами для отображения на карте
    Возвращает только объявления с координатами
    """
    try:
        # Формируем фильтры
        filters = {
            "city": city or "Roma",
            "min_price": min_price,
            "max_price": max_price,
            "property_type": property_type,
            "source_site": source_site
        }
        
        # Убираем None значения
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Получаем объявления с координатами
        listings_data = listing.search_with_filters(
            db=db,
            filters=filters,
            skip=0,
            limit=limit
        )
        
        # Фильтруем только объявления с координатами
        listings_with_coords = [l for l in listings_data if l.latitude and l.longitude]
        
        total_count = len(listings_with_coords)
        
        # Формируем ответ
        response_data = {
            "success": True,
            "total": total_count,
            "listings": [
                {
                    "id": str(l.id),
                    "source_site": l.source,
                    "original_id": l.external_id,
                    "url": l.url,
                    "title": l.title,
                    "price": l.price,
                    "address_text": l.address,
                    "latitude": l.latitude,
                    "longitude": l.longitude,
                    "area_sqm": l.area,
                    "num_rooms": l.rooms,
                    "images": l.images if l.images else []
                }
                for l in listings_with_coords
            ]
        }
        
        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении объявлений для карты: {str(e)}"
        ) 


@router.get("/{listing_id}", response_model=dict)
async def get_listing(
    listing_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить детали конкретного объявления
    """
    try:
        listing_obj = listing.get(db=db, id=listing_id)
        
        if not listing_obj:
            raise HTTPException(
                status_code=404,
                detail="Объявление не найдено"
            )
        
        return {
            "success": True,
            "listing": {
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
                "num_bathrooms": listing_obj.bathrooms,
                "property_type": listing_obj.property_type,
                "floor": listing_obj.floor,
                "is_furnished": listing_obj.furnished,
                "pets_allowed": listing_obj.pets_allowed,
                "features": listing_obj.features if hasattr(listing_obj, 'features') else [],
                "images": listing_obj.images if listing_obj.images else [],
                "virtual_tour_url": listing_obj.virtual_tour_url,
                "agency_name": listing_obj.agency_name if hasattr(listing_obj, 'agency_name') else None,
                "is_active": listing_obj.is_active,
                "published_at": listing_obj.published_at.isoformat() if listing_obj.published_at else None,
                "scraped_at": listing_obj.scraped_at.isoformat() if listing_obj.scraped_at else None,
                "created_at": listing_obj.created_at.isoformat() if listing_obj.created_at else None,
                "updated_at": listing_obj.updated_at.isoformat() if listing_obj.updated_at else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении объявления: {str(e)}"
        )


@router.post("/scrape", response_model=dict)
async def manual_scraping(
    city: str = Query("roma", description="Город для парсинга"),
    max_pages: int = Query(5, ge=1, le=20, description="Максимальное количество страниц"),
    save_to_db: bool = Query(True, description="Сохранять результаты в базу данных"),
    db: Session = Depends(get_db)
):
    """
    Ручной запуск парсинга объявлений
    """
    try:
        scraping_service = ScrapingService()
        
        scraping_filters = {
            "city": city
        }
        
        if save_to_db:
            # Парсинг с сохранением в БД
            result = await scraping_service.scrape_and_save(
                filters=scraping_filters,
                db=db,
                max_pages=max_pages
            )
            
            return {
                "success": result["success"],
                "message": result["message"],
                "scraped_count": result["scraped_count"],
                "saved_count": result["saved_count"],
                "sources": result["sources"],
                "elapsed_time": result["elapsed_time"]
            }
        else:
            # Только парсинг без сохранения
            listings = await scraping_service.scrape_all_sources(
                filters=scraping_filters,
                max_pages=max_pages
            )
            
            return {
                "success": True,
                "message": f"Найдено {len(listings)} объявлений",
                "scraped_count": len(listings),
                "sources": ["immobiliare"],
                "listings": listings[:10]  # Возвращаем первые 10 для примера
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при парсинге: {str(e)}"
        ) 