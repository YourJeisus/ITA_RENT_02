"""
Pydantic схемы для пользователей
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator
from pydantic import EmailStr


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    first_name: str
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return v


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telegram_username: Optional[str] = None
    email_notifications_enabled: Optional[bool] = None
    telegram_notifications_enabled: Optional[bool] = None


class UserInDBBase(UserBase):
    """Базовая схема пользователя в БД"""
    id: int
    is_active: bool
    is_superuser: bool
    subscription_type: str
    telegram_chat_id: Optional[str] = None
    telegram_username: Optional[str] = None
    whatsapp_phone: Optional[str] = None
    whatsapp_enabled: bool = False
    email_notifications_enabled: bool = True
    telegram_notifications_enabled: bool = True
    email_verified_at: Optional[datetime] = None
    email_last_sent_at: Optional[datetime] = None
    subscription_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """Схема пользователя для API ответов"""
    pass


class UserResponse(BaseModel):
    """Схема ответа с информацией о пользователе"""
    id: int
    email: EmailStr
    first_name: str
    last_name: Optional[str] = None
    subscription_type: str
    is_active: bool
    telegram_chat_id: Optional[str] = None
    telegram_username: Optional[str] = None
    whatsapp_phone: Optional[str] = None
    whatsapp_enabled: bool = False
    email_notifications_enabled: bool = True
    telegram_notifications_enabled: bool = True
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(UserInDBBase):
    """Схема пользователя в БД с хешированным паролем"""
    hashed_password: str


class UserTelegramLink(BaseModel):
    """Схема для привязки Telegram"""
    telegram_chat_id: str
    telegram_username: Optional[str] = None


class UserSubscription(BaseModel):
    """Схема информации о подписке"""
    subscription_type: str
    subscription_expires_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True 