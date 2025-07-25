"""
CRUD операции для фильтров
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta

from src.crud.base import CRUDBase
from src.db.models import Filter
from src.schemas.filter import FilterCreate, FilterUpdate


class CRUDFilter(CRUDBase[Filter, FilterCreate, FilterUpdate]):
    """CRUD операции для фильтров"""
    
    def get_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[Filter]:
        """Получить фильтры пользователя"""
        return db.query(Filter).filter(Filter.user_id == user_id).order_by(desc(Filter.created_at)).offset(skip).limit(limit).all()
    
    def get_active_by_user(self, db: Session, *, user_id: int) -> List[Filter]:
        """Получить активные фильтры пользователя"""
        return db.query(Filter).filter(
            and_(
                Filter.user_id == user_id,
                Filter.is_active == True
            )
        ).order_by(desc(Filter.created_at)).all()
    
    def get_user_filter(self, db: Session, *, user_id: int, filter_id: int) -> Optional[Filter]:
        """Получить конкретный фильтр пользователя"""
        return db.query(Filter).filter(
            and_(
                Filter.id == filter_id,
                Filter.user_id == user_id
            )
        ).first()
    
    def create_with_user(self, db: Session, *, obj_in: FilterCreate, user_id: int) -> Filter:
        """Создать фильтр для пользователя"""
        obj_in_data = obj_in.dict()
        obj_in_data['user_id'] = user_id
        db_obj = Filter(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_with_owner(self, db: Session, *, obj_in: FilterCreate, user_id: int) -> Filter:
        """Создать фильтр для пользователя (алиас для create_with_user)"""
        return self.create_with_user(db=db, obj_in=obj_in, user_id=user_id)
    
    def get_filters_for_notification(self, db: Session) -> List[Filter]:
        """Получить фильтры, готовые для отправки уведомлений"""
        # Получаем фильтры, которые:
        # 1. Активны
        # 2. Уведомления включены
        # 3. Прошло достаточно времени с последнего уведомления
        now = datetime.utcnow()
        
        return db.query(Filter).filter(
            and_(
                Filter.is_active == True,
                Filter.notification_enabled == True,
                or_(
                    Filter.last_notification_sent.is_(None),
                    Filter.last_notification_sent <= now - timedelta(hours=Filter.notification_frequency_hours)
                )
            )
        ).all()
    
    def update_notification_sent(self, db: Session, *, filter_id: int) -> Optional[Filter]:
        """Обновить время отправки последнего уведомления"""
        filter_obj = self.get(db, id=filter_id)
        if filter_obj:
            filter_obj.last_notification_sent = datetime.utcnow()
            db.add(filter_obj)
            db.commit()
            db.refresh(filter_obj)
        return filter_obj
    
    def toggle_active(self, db: Session, *, filter_id: int, user_id: int) -> Optional[Filter]:
        """Переключить активность фильтра"""
        filter_obj = self.get_user_filter(db, user_id=user_id, filter_id=filter_id)
        if filter_obj:
            filter_obj.is_active = not filter_obj.is_active
            db.add(filter_obj)
            db.commit()
            db.refresh(filter_obj)
        return filter_obj
    
    def toggle_notifications(self, db: Session, *, filter_id: int, user_id: int) -> Optional[Filter]:
        """Переключить уведомления для фильтра"""
        filter_obj = self.get_user_filter(db, user_id=user_id, filter_id=filter_id)
        if filter_obj:
            filter_obj.notification_enabled = not filter_obj.notification_enabled
            db.add(filter_obj)
            db.commit()
            db.refresh(filter_obj)
        return filter_obj
    
    def count_user_filters(self, db: Session, *, user_id: int, active_only: bool = False) -> int:
        """Подсчитать количество фильтров пользователя"""
        query = db.query(Filter).filter(Filter.user_id == user_id)
        if active_only:
            query = query.filter(Filter.is_active == True)
        return query.count()
    
    def get_popular_cities(self, db: Session, *, limit: int = 10) -> List[tuple]:
        """Получить популярные города из фильтров"""
        from sqlalchemy import func
        
        return db.query(
            Filter.city,
            func.count(Filter.id).label('count')
        ).filter(
            and_(
                Filter.city.isnot(None),
                Filter.is_active == True
            )
        ).group_by(Filter.city).order_by(desc('count')).limit(limit).all()
    
    def get_filters_by_criteria(
        self,
        db: Session,
        *,
        city: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        property_type: Optional[str] = None
    ) -> List[Filter]:
        """Найти фильтры по критериям (для поиска подходящих пользователей)"""
        query = db.query(Filter).filter(
            and_(
                Filter.is_active == True,
                Filter.notification_enabled == True
            )
        )
        
        if city:
            query = query.filter(
                or_(
                    Filter.city.is_(None),
                    Filter.city.ilike(f"%{city}%")
                )
            )
        
        if min_price is not None:
            query = query.filter(
                or_(
                    Filter.min_price.is_(None),
                    Filter.min_price <= min_price
                )
            )
        
        if max_price is not None:
            query = query.filter(
                or_(
                    Filter.max_price.is_(None),
                    Filter.max_price >= max_price
                )
            )
        
        if property_type:
            query = query.filter(
                or_(
                    Filter.property_type.is_(None),
                    Filter.property_type == property_type
                )
            )
        
        return query.all()
    
    def check_listing_matches_filter(self, filter_obj: Filter, listing_data: dict) -> bool:
        """Проверить, соответствует ли объявление фильтру"""
        # Проверяем город
        if filter_obj.city and listing_data.get('city'):
            if filter_obj.city.lower() not in listing_data['city'].lower():
                return False
        
        # Проверяем цену
        listing_price = listing_data.get('price')
        if listing_price:
            if filter_obj.min_price and listing_price < filter_obj.min_price:
                return False
            if filter_obj.max_price and listing_price > filter_obj.max_price:
                return False
        
        # Проверяем количество комнат
        listing_rooms = listing_data.get('rooms')
        if listing_rooms:
            if filter_obj.min_rooms and listing_rooms < filter_obj.min_rooms:
                return False
            if filter_obj.max_rooms and listing_rooms > filter_obj.max_rooms:
                return False
        
        # Проверяем площадь
        listing_area = listing_data.get('area')
        if listing_area:
            if filter_obj.min_area and listing_area < filter_obj.min_area:
                return False
            if filter_obj.max_area and listing_area > filter_obj.max_area:
                return False
        
        # Проверяем тип недвижимости
        if filter_obj.property_type and listing_data.get('property_type'):
            if filter_obj.property_type != listing_data['property_type']:
                return False
        
        # Проверяем меблированность
        if filter_obj.furnished is not None and listing_data.get('furnished') is not None:
            if filter_obj.furnished != listing_data['furnished']:
                return False
        
        # Проверяем разрешение животных
        if filter_obj.pets_allowed is not None and listing_data.get('pets_allowed') is not None:
            if filter_obj.pets_allowed != listing_data['pets_allowed']:
                return False
        
        return True


# Создаем экземпляр CRUD для использования
filter = CRUDFilter(Filter)

# Функции-обертки для совместимости с API
def get_user_filters(db: Session, user_id: int) -> List[Filter]:
    """Получить все фильтры пользователя"""
    return filter.get_user_filters(db, user_id=user_id)

def get_filter_by_id(db: Session, filter_id: int) -> Optional[Filter]:
    """Получить фильтр по ID"""
    return filter.get(db, id=filter_id)

def create_filter(db: Session, filter_data: dict, user_id: int) -> Filter:
    """Создать новый фильтр"""
    return filter.create_with_owner(db, obj_in=filter_data, user_id=user_id)

def update_filter(db: Session, filter_id: int, filter_data: dict) -> Optional[Filter]:
    """Обновить фильтр"""
    filter_obj = filter.get(db, id=filter_id)
    if filter_obj:
        return filter.update(db, db_obj=filter_obj, obj_in=filter_data)
    return None

def delete_filter(db: Session, filter_id: int) -> bool:
    """Удалить фильтр"""
    filter_obj = filter.get(db, id=filter_id)
    if filter_obj:
        filter.remove(db, id=filter_id)
        return True
    return False 