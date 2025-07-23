"""
Pydantic схемы для объявлений
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl, field_validator


class ListingBase(BaseModel):
    """Базовая схема объявления"""
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    price_currency: str = "EUR"
    property_type: Optional[str] = None
    rooms: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    floor: Optional[str] = None
    total_floors: Optional[int] = None
    furnished: Optional[bool] = None
    pets_allowed: Optional[bool] = None
    features: Optional[List[str]] = None
    city: str
    district: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: Optional[List[str]] = None
    virtual_tour_url: Optional[str] = None
    agency_name: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None


class ListingCreate(ListingBase):
    """Схема для создания объявления"""
    external_id: str
    source: str
    url: str
    
    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        allowed_sources = ['idealista', 'immobiliare', 'subito']
        if v not in allowed_sources:
            raise ValueError(f'Источник должен быть одним из: {", ".join(allowed_sources)}')
        return v
    
    @field_validator('property_type')
    @classmethod
    def validate_property_type(cls, v):
        if v is not None:
            allowed_types = ['apartment', 'house', 'room', 'studio']
            if v not in allowed_types:
                raise ValueError(f'Тип недвижимости должен быть одним из: {", ".join(allowed_types)}')
        return v


class ListingUpdate(BaseModel):
    """Схема для обновления объявления"""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    property_type: Optional[str] = None
    rooms: Optional[int] = None
    area: Optional[float] = None
    furnished: Optional[bool] = None
    pets_allowed: Optional[bool] = None
    features: Optional[List[str]] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ListingInDBBase(ListingBase):
    """Базовая схема объявления в БД"""
    id: int
    external_id: str
    source: str
    url: str
    is_active: bool
    published_at: Optional[datetime] = None
    scraped_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Listing(ListingInDBBase):
    """Схема объявления для API ответов"""
    pass


class ListingInDB(ListingInDBBase):
    """Схема объявления в БД"""
    pass


class ListingSearch(BaseModel):
    """Схема для поиска объявлений"""
    city: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    property_type: Optional[str] = None
    min_rooms: Optional[int] = None
    max_rooms: Optional[int] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    furnished: Optional[bool] = None
    pets_allowed: Optional[bool] = None
    page: int = 1
    limit: int = 50
    
    @field_validator('page')
    @classmethod
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Номер страницы должен быть больше 0')
        return v
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Лимит должен быть от 1 до 100')
        return v


class ListingResponse(BaseModel):
    """Схема ответа со списком объявлений"""
    listings: List[Listing]
    total: int
    page: int
    limit: int
    pages: int


class ListingStatistics(BaseModel):
    """Схема статистики объявлений"""
    total_listings: int
    active_listings: int
    by_source: Dict[str, int]
    top_cities: Dict[str, int]


class ListingPriceRange(BaseModel):
    """Схема диапазона цен"""
    min_price: float
    max_price: float
    avg_price: float
    city: Optional[str] = None 