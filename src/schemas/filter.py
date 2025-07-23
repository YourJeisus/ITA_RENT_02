"""
Pydantic схемы для фильтров
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, validator


class FilterBase(BaseModel):
    """Базовая схема фильтра"""
    name: str
    city: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_rooms: Optional[int] = None
    max_rooms: Optional[int] = None
    property_type: Optional[str] = None
    min_area: Optional[int] = None
    max_area: Optional[int] = None
    furnished: Optional[bool] = None
    pets_allowed: Optional[bool] = None
    notification_enabled: bool = True
    notification_frequency_hours: int = 24


class FilterCreate(FilterBase):
    """Схема для создания фильтра"""
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Название фильтра не может быть пустым')
        if len(v) > 255:
            raise ValueError('Название фильтра не может быть длиннее 255 символов')
        return v.strip()
    
    @validator('min_price', 'max_price')
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('Цена не может быть отрицательной')
        return v
    
    @validator('max_price')
    def validate_price_range(cls, v, values):
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v <= values['min_price']:
                raise ValueError('Максимальная цена должна быть больше минимальной')
        return v
    
    @validator('min_rooms', 'max_rooms')
    def validate_rooms(cls, v):
        if v is not None and v < 0:
            raise ValueError('Количество комнат не может быть отрицательным')
        return v
    
    @validator('max_rooms')
    def validate_rooms_range(cls, v, values):
        if v is not None and 'min_rooms' in values and values['min_rooms'] is not None:
            if v < values['min_rooms']:
                raise ValueError('Максимальное количество комнат должно быть больше или равно минимальному')
        return v
    
    @validator('min_area', 'max_area')
    def validate_area(cls, v):
        if v is not None and v < 0:
            raise ValueError('Площадь не может быть отрицательной')
        return v
    
    @validator('max_area')
    def validate_area_range(cls, v, values):
        if v is not None and 'min_area' in values and values['min_area'] is not None:
            if v <= values['min_area']:
                raise ValueError('Максимальная площадь должна быть больше минимальной')
        return v
    
    @validator('property_type')
    def validate_property_type(cls, v):
        if v is not None:
            allowed_types = ['apartment', 'house', 'room', 'studio']
            if v not in allowed_types:
                raise ValueError(f'Тип недвижимости должен быть одним из: {", ".join(allowed_types)}')
        return v
    
    @validator('notification_frequency_hours')
    def validate_notification_frequency(cls, v):
        if v < 1:
            raise ValueError('Частота уведомлений должна быть минимум 1 час')
        if v > 168:  # 7 дней
            raise ValueError('Частота уведомлений не может быть больше 168 часов (7 дней)')
        return v


class FilterUpdate(BaseModel):
    """Схема для обновления фильтра"""
    name: Optional[str] = None
    city: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_rooms: Optional[int] = None
    max_rooms: Optional[int] = None
    property_type: Optional[str] = None
    min_area: Optional[int] = None
    max_area: Optional[int] = None
    furnished: Optional[bool] = None
    pets_allowed: Optional[bool] = None
    is_active: Optional[bool] = None
    notification_enabled: Optional[bool] = None
    notification_frequency_hours: Optional[int] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) < 1:
                raise ValueError('Название фильтра не может быть пустым')
            if len(v) > 255:
                raise ValueError('Название фильтра не может быть длиннее 255 символов')
            return v.strip()
        return v


class FilterInDBBase(FilterBase):
    """Базовая схема фильтра в БД"""
    id: int
    user_id: int
    is_active: bool
    last_notification_sent: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Filter(FilterInDBBase):
    """Схема фильтра для API ответов"""
    pass


class FilterInDB(FilterInDBBase):
    """Схема фильтра в БД"""
    pass


class FilterResponse(BaseModel):
    """Схема ответа со списком фильтров"""
    filters: List[Filter]
    total: int


class FilterToggle(BaseModel):
    """Схема для переключения состояния фильтра"""
    is_active: Optional[bool] = None
    notification_enabled: Optional[bool] = None


class FilterTest(BaseModel):
    """Схема для тестирования фильтра"""
    sample_listings_count: int = 10
    
    class Config:
        from_attributes = True


class FilterTestResult(BaseModel):
    """Схема результата тестирования фильтра"""
    filter_id: int
    matching_listings: List[dict]
    total_matches: int
    test_performed_at: datetime 