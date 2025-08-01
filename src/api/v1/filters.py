"""
API endpoints для работы с фильтрами пользователей
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_current_user
from src.crud.crud_filter import filter as crud_filter
from src.schemas.filter import FilterCreate, FilterUpdate, FilterResponse, Filter
from src.db.models import User
from src.services.telegram_bot import send_filter_confirmation_message

router = APIRouter()


@router.get("/", response_model=List[Filter])
async def get_user_filters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение всех фильтров текущего пользователя
    """
    filters = crud_filter.get_by_user(db=db, user_id=current_user.id)
    return filters


@router.post("/", response_model=Filter)
async def create_filter(
    filter_data: FilterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового фильтра с автоматической перезаписью
    Максимум 1 фильтр на пользователя независимо от подписки
    """
    existing_filters = crud_filter.get_by_user(db=db, user_id=current_user.id)
    
    # ОГРАНИЧЕНИЕ: максимум 1 фильтр на пользователя
    if len(existing_filters) >= 1:
        # Обновляем существующий фильтр (перезаписываем)
        old_filter = existing_filters[0]
        filter_obj = crud_filter.update(
            db=db,
            db_obj=old_filter,
            obj_in=filter_data
        )
        
        # Отправляем подтверждение в Telegram (если привязан)
        if current_user.telegram_chat_id:
            try:
                await send_filter_confirmation_message(
                    current_user.telegram_chat_id,
                    filter_obj,
                    is_new=False
                )
            except Exception as e:
                # Логируем ошибку, но не прерываем обновление фильтра
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Ошибка отправки подтверждения в Telegram: {e}")
        
        return filter_obj
    
    # Создаем новый фильтр
    filter_obj = crud_filter.create_with_owner(
        db=db,
        obj_in=filter_data,
        user_id=current_user.id
    )
    
    # Отправляем подтверждение в Telegram (если привязан)
    if current_user.telegram_chat_id:
        try:
            await send_filter_confirmation_message(
                current_user.telegram_chat_id,
                filter_obj,
                is_new=True
            )
        except Exception as e:
            # Логируем ошибку, но не прерываем создание фильтра
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка отправки подтверждения в Telegram: {e}")
    
    return filter_obj


@router.get("/{filter_id}", response_model=Filter)
async def get_filter(
    filter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение конкретного фильтра
    """
    filter_obj = crud_filter.get(db=db, id=filter_id)
    if not filter_obj:
        raise HTTPException(status_code=404, detail="Фильтр не найден")
    
    if filter_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому фильтру")
    
    return filter_obj


@router.put("/{filter_id}", response_model=Filter)
async def update_filter(
    filter_id: int,
    filter_update: FilterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновление фильтра
    """
    filter_obj = crud_filter.get(db=db, id=filter_id)
    if not filter_obj:
        raise HTTPException(status_code=404, detail="Фильтр не найден")
    
    if filter_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому фильтру")
    
    filter_obj = crud_filter.update(db=db, db_obj=filter_obj, obj_in=filter_update)
    return filter_obj


@router.delete("/{filter_id}")
async def delete_filter(
    filter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаление фильтра
    """
    filter_obj = crud_filter.get(db=db, id=filter_id)
    if not filter_obj:
        raise HTTPException(status_code=404, detail="Фильтр не найден")
    
    if filter_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому фильтру")
    
    crud_filter.remove(db=db, id=filter_id)
    return {"message": "Фильтр успешно удален"}


@router.post("/{filter_id}/test", response_model=dict)
async def test_filter(
    filter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Тестирование фильтра - показывает сколько объявлений найдено
    """
    filter_obj = crud_filter.get(db=db, id=filter_id)
    if not filter_obj:
        raise HTTPException(status_code=404, detail="Фильтр не найден")
    
    if filter_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому фильтру")
    
    # Импортируем здесь чтобы избежать циклических импортов
    from src.crud.crud_listing import listing
    
    # Конвертируем фильтр в параметры поиска
    search_filters = {}
    if filter_obj.city:
        search_filters["city"] = filter_obj.city
    if filter_obj.min_price:
        search_filters["min_price"] = filter_obj.min_price
    if filter_obj.max_price:
        search_filters["max_price"] = filter_obj.max_price
    if filter_obj.min_rooms:
        search_filters["min_rooms"] = filter_obj.min_rooms
    if filter_obj.max_rooms:
        search_filters["max_rooms"] = filter_obj.max_rooms
    if filter_obj.property_type:
        search_filters["property_type"] = filter_obj.property_type
    if filter_obj.min_area:
        search_filters["min_area"] = filter_obj.min_area
    if filter_obj.max_area:
        search_filters["max_area"] = filter_obj.max_area
    
    # Подсчитываем количество найденных объявлений
    total_count = listing.count_with_filters(db=db, filters=search_filters)
    
    # Получаем несколько примеров
    sample_listings = listing.search_with_filters(
        db=db,
        filters=search_filters,
        skip=0,
        limit=3
    )
    
    return {
        "success": True,
        "filter_name": filter_obj.name,
        "total_matches": total_count,
        "sample_listings": [
            {
                "title": l.title,
                "price": l.price,
                "city": l.city,
                "address": l.address,
                "source": l.source
            }
            for l in sample_listings
        ],
        "message": f"По вашему фильтру '{filter_obj.name}' найдено {total_count} объявлений"
    } 