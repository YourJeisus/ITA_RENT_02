"""
CRUD операции для объявлений
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta

from src.crud.base import CRUDBase
from src.db.models import Listing
from src.schemas.listing import ListingCreate, ListingUpdate


class CRUDListing(CRUDBase[Listing, ListingCreate, ListingUpdate]):
    """CRUD операции для объявлений"""
    
    def get_by_external_id(self, db: Session, *, source: str, external_id: str) -> Optional[Listing]:
        """Получить объявление по внешнему ID и источнику"""
        return db.query(Listing).filter(
            and_(
                Listing.source == source,
                Listing.external_id == external_id
            )
        ).first()
    
    def get_by_url(self, db: Session, *, url: str) -> Optional[Listing]:
        """Получить объявление по URL"""
        return db.query(Listing).filter(Listing.url == url).first()
    
    def search(
        self,
        db: Session,
        *,
        city: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        property_type: Optional[str] = None,
        min_rooms: Optional[int] = None,
        max_rooms: Optional[int] = None,
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        furnished: Optional[bool] = None,
        pets_allowed: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Listing]:
        """Поиск объявлений с фильтрами"""
        query = db.query(Listing).filter(Listing.is_active == True)
        
        # Применяем фильтры
        if city:
            query = query.filter(Listing.city.ilike(f"%{city}%"))
        
        if min_price is not None:
            query = query.filter(Listing.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Listing.price <= max_price)
        
        if property_type:
            query = query.filter(Listing.property_type == property_type)
        
        if min_rooms is not None:
            query = query.filter(Listing.rooms >= min_rooms)
        
        if max_rooms is not None:
            query = query.filter(Listing.rooms <= max_rooms)
        
        if min_area is not None:
            query = query.filter(Listing.area >= min_area)
        
        if max_area is not None:
            query = query.filter(Listing.area <= max_area)
        
        if furnished is not None:
            query = query.filter(Listing.furnished == furnished)
        
        if pets_allowed is not None:
            query = query.filter(Listing.pets_allowed == pets_allowed)
        
        # Сортировка по дате добавления (новые первыми)
        query = query.order_by(desc(Listing.scraped_at))
        
        return query.offset(skip).limit(limit).all()
    
    def get_recent(self, db: Session, *, hours: int = 24, limit: int = 100) -> List[Listing]:
        """Получить недавние объявления"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(Listing).filter(
            and_(
                Listing.is_active == True,
                Listing.scraped_at >= cutoff_time
            )
        ).order_by(desc(Listing.scraped_at)).limit(limit).all()
    
    def get_by_source(self, db: Session, *, source: str, skip: int = 0, limit: int = 100) -> List[Listing]:
        """Получить объявления по источнику"""
        return db.query(Listing).filter(
            and_(
                Listing.source == source,
                Listing.is_active == True
            )
        ).order_by(desc(Listing.scraped_at)).offset(skip).limit(limit).all()
    
    def get_cities(self, db: Session) -> List[str]:
        """Получить список всех городов"""
        result = db.query(Listing.city).filter(
            and_(
                Listing.city.isnot(None),
                Listing.is_active == True
            )
        ).distinct().all()
        return [city[0] for city in result if city[0]]
    
    def get_price_range(self, db: Session, *, city: Optional[str] = None) -> Dict[str, float]:
        """Получить диапазон цен"""
        query = db.query(
            func.min(Listing.price).label('min_price'),
            func.max(Listing.price).label('max_price'),
            func.avg(Listing.price).label('avg_price')
        ).filter(
            and_(
                Listing.is_active == True,
                Listing.price.isnot(None)
            )
        )
        
        if city:
            query = query.filter(Listing.city.ilike(f"%{city}%"))
        
        result = query.first()
        return {
            "min_price": float(result.min_price) if result.min_price else 0,
            "max_price": float(result.max_price) if result.max_price else 0,
            "avg_price": float(result.avg_price) if result.avg_price else 0
        }
    
    def create_or_update(self, db: Session, *, obj_in: ListingCreate) -> Listing:
        """Создать или обновить объявление (для парсинга)"""
        existing = self.get_by_external_id(
            db, 
            source=obj_in.source, 
            external_id=obj_in.external_id
        )
        
        if existing:
            # Обновляем существующее объявление
            update_data = obj_in.dict(exclude_unset=True)
            update_data['updated_at'] = datetime.utcnow()
            
            for field, value in update_data.items():
                setattr(existing, field, value)
            
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Создаем новое объявление
            return self.create(db, obj_in=obj_in)
    
    def deactivate_old_listings(self, db: Session, *, source: str, days: int = 30) -> int:
        """Деактивировать старые объявления"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        updated_count = db.query(Listing).filter(
            and_(
                Listing.source == source,
                Listing.is_active == True,
                Listing.scraped_at < cutoff_time
            )
        ).update({"is_active": False})
        
        db.commit()
        return updated_count
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Получить статистику объявлений"""
        total = db.query(Listing).count()
        active = db.query(Listing).filter(Listing.is_active == True).count()
        
        by_source = db.query(
            Listing.source,
            func.count(Listing.id).label('count')
        ).filter(Listing.is_active == True).group_by(Listing.source).all()
        
        by_city = db.query(
            Listing.city,
            func.count(Listing.id).label('count')
        ).filter(
            and_(
                Listing.is_active == True,
                Listing.city.isnot(None)
            )
        ).group_by(Listing.city).order_by(desc('count')).limit(10).all()
        
        return {
            "total_listings": total,
            "active_listings": active,
            "by_source": {source: count for source, count in by_source},
            "top_cities": {city: count for city, count in by_city}
        }
    
    def bulk_create(self, db: Session, *, listings: List[ListingCreate]) -> List[Listing]:
        """Массовое создание объявлений (для парсинга)"""
        db_objs = []
        for listing_data in listings:
            # Проверяем, не существует ли уже такое объявление
            if not self.get_by_external_id(
                db, 
                source=listing_data.source, 
                external_id=listing_data.external_id
            ):
                obj_in_data = listing_data.dict()
                db_obj = Listing(**obj_in_data)
                db_objs.append(db_obj)
        
        if db_objs:
            db.add_all(db_objs)
            db.commit()
            for obj in db_objs:
                db.refresh(obj)
        
        return db_objs
    
    def search_with_filters(
        self,
        db: Session,
        *,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 50
    ) -> List[Listing]:
        """Поиск объявлений с фильтрами (новая версия)"""
        query = db.query(Listing).filter(Listing.is_active == True)
        
        # Применяем фильтры
        if "city" in filters and filters["city"]:
            query = query.filter(Listing.city.ilike(f"%{filters['city']}%"))
        
        if "min_price" in filters and filters["min_price"] is not None:
            query = query.filter(Listing.price >= filters["min_price"])
        
        if "max_price" in filters and filters["max_price"] is not None:
            query = query.filter(Listing.price <= filters["max_price"])
        
        if "property_type" in filters and filters["property_type"]:
            query = query.filter(Listing.property_type == filters["property_type"])
        
        if "min_rooms" in filters and filters["min_rooms"] is not None:
            query = query.filter(Listing.rooms >= filters["min_rooms"])
        
        if "max_rooms" in filters and filters["max_rooms"] is not None:
            query = query.filter(Listing.rooms <= filters["max_rooms"])
        
        if "min_area" in filters and filters["min_area"] is not None:
            query = query.filter(Listing.area >= filters["min_area"])
        
        if "max_area" in filters and filters["max_area"] is not None:
            query = query.filter(Listing.area <= filters["max_area"])
        
        if "source_site" in filters and filters["source_site"]:
            query = query.filter(Listing.source == filters["source_site"])
        
        # Сортировка по дате добавления (новые первыми)
        query = query.order_by(desc(Listing.scraped_at))
        
        return query.offset(skip).limit(limit).all()
    
    def count_with_filters(
        self,
        db: Session,
        *,
        filters: Dict[str, Any]
    ) -> int:
        """Подсчет объявлений с фильтрами"""
        query = db.query(Listing).filter(Listing.is_active == True)
        
        # Применяем те же фильтры что и в search_with_filters
        if "city" in filters and filters["city"]:
            query = query.filter(Listing.city.ilike(f"%{filters['city']}%"))
        
        if "min_price" in filters and filters["min_price"] is not None:
            query = query.filter(Listing.price >= filters["min_price"])
        
        if "max_price" in filters and filters["max_price"] is not None:
            query = query.filter(Listing.price <= filters["max_price"])
        
        if "property_type" in filters and filters["property_type"]:
            query = query.filter(Listing.property_type == filters["property_type"])
        
        if "min_rooms" in filters and filters["min_rooms"] is not None:
            query = query.filter(Listing.rooms >= filters["min_rooms"])
        
        if "max_rooms" in filters and filters["max_rooms"] is not None:
            query = query.filter(Listing.rooms <= filters["max_rooms"])
        
        if "min_area" in filters and filters["min_area"] is not None:
            query = query.filter(Listing.area >= filters["min_area"])
        
        if "max_area" in filters and filters["max_area"] is not None:
            query = query.filter(Listing.area <= filters["max_area"])
        
        if "source_site" in filters and filters["source_site"]:
            query = query.filter(Listing.source == filters["source_site"])
        
        return query.count()
    
    def get_available_cities(self, db: Session) -> List[str]:
        """Получить список доступных городов"""
        result = db.query(Listing.city).filter(
            and_(
                Listing.city.isnot(None),
                Listing.is_active == True
            )
        ).distinct().order_by(Listing.city).all()
        return [city[0] for city in result if city[0]]
    
    def get_database_stats(self, db: Session) -> Dict[str, Any]:
        """Получить подробную статистику базы данных"""
        total = db.query(Listing).count()
        active = db.query(Listing).filter(Listing.is_active == True).count()
        inactive = total - active
        
        # Статистика по источникам
        by_source = db.query(
            Listing.source,
            func.count(Listing.id).label('count')
        ).filter(Listing.is_active == True).group_by(Listing.source).all()
        
        # Топ городов
        by_city = db.query(
            Listing.city,
            func.count(Listing.id).label('count')
        ).filter(
            and_(
                Listing.is_active == True,
                Listing.city.isnot(None)
            )
        ).group_by(Listing.city).order_by(desc('count')).limit(10).all()
        
        # Средняя цена
        avg_price_result = db.query(
            func.avg(Listing.price).label('avg_price')
        ).filter(
            and_(
                Listing.is_active == True,
                Listing.price.isnot(None)
            )
        ).first()
        
        # Диапазон дат
        date_range = db.query(
            func.min(Listing.scraped_at).label('oldest'),
            func.max(Listing.scraped_at).label('newest')
        ).filter(Listing.is_active == True).first()
        
        # Свежие объявления за 24 часа
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        recent_24h = db.query(Listing).filter(
            and_(
                Listing.is_active == True,
                Listing.scraped_at >= cutoff_time
            )
        ).count()
        
        return {
            "total_listings": total,
            "active_listings": active,
            "inactive_listings": inactive,
            "sites": {source: count for source, count in by_source},
            "top_cities": {city: count for city, count in by_city},
            "average_price": float(avg_price_result.avg_price) if avg_price_result.avg_price else 0,
            "date_range": {
                "oldest": date_range.oldest.isoformat() if date_range.oldest else None,
                "newest": date_range.newest.isoformat() if date_range.newest else None
            },
            "recent_listings_24h": recent_24h,
            "data_freshness": {
                "total_active": active,
                "recent_24h": recent_24h,
                "freshness_ratio": round(recent_24h / active * 100, 2) if active > 0 else 0
            }
        }


# Создаем экземпляр CRUD для использования
listing = CRUDListing(Listing)

# Функции-обертки для совместимости с API
def search_listings(db: Session, **filters) -> Dict[str, Any]:
    """Поиск объявлений с фильтрами"""
    # Получаем основные параметры
    page = filters.pop('page', 1)
    limit = filters.pop('limit', 50)
    
    # Конвертируем page в skip
    skip = (page - 1) * limit
    
    # Выполняем поиск
    listings = listing.search(db, skip=skip, limit=limit, **filters)
    
    # Получаем общее количество для расчета страниц
    total_count = listing.count_with_filters(db, filters=filters)
    
    return {
        "listings": listings,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit
    }

def get_listing_by_id(db: Session, listing_id: int) -> Optional[Listing]:
    """Получить объявление по ID"""
    return listing.get(db, id=listing_id)

def create_listing(db: Session, listing_data: dict) -> Listing:
    """Создать новое объявление"""
    return listing.create(db, obj_in=listing_data)

def update_listing(db: Session, listing_id: int, listing_data: dict) -> Optional[Listing]:
    """Обновить объявление"""
    listing_obj = listing.get(db, id=listing_id)
    if listing_obj:
        return listing.update(db, db_obj=listing_obj, obj_in=listing_data)
    return None

def get_database_stats(db: Session) -> Dict[str, Any]:
    """Получить статистику базы данных"""
    return listing.get_database_stats(db) 