"""
Модели базы данных для ITA_RENT_BOT
Оптимизированы для MVP с возможностью масштабирования
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float, 
    ForeignKey, JSON, Text, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict

from src.db.database import Base


class User(Base):
    """
    Модель пользователя системы
    MVP: базовая авторизация + Telegram интеграция
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Базовая информация
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Статус аккаунта
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    
    # Telegram интеграция
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, unique=True, index=True
    )
    telegram_username: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Подписка (упрощенная модель для MVP)
    subscription_type: Mapped[str] = mapped_column(
        String(50), default="free", index=True
    )  # free, premium
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    
    # Временные метки
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Связи
    filters: Mapped[List["Filter"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # Индексы для оптимизации
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_subscription', 'subscription_type', 'subscription_expires_at'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Filter(Base):
    """
    Фильтр поиска пользователя
    MVP: базовые фильтры с возможностью расширения
    """
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    
    # Основная информация о фильтре
    name: Mapped[str] = mapped_column(String(255), default="Мой фильтр")
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    
    # Параметры поиска
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    min_price: Mapped[Optional[int]] = mapped_column(Integer)
    max_price: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    min_rooms: Mapped[Optional[int]] = mapped_column(Integer)
    max_rooms: Mapped[Optional[int]] = mapped_column(Integer)
    property_type: Mapped[Optional[str]] = mapped_column(
        String(50), index=True
    )  # apartment, house, room, studio
    min_area: Mapped[Optional[int]] = mapped_column(Integer)
    max_area: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Дополнительные фильтры (для будущего расширения)
    furnished: Mapped[Optional[bool]] = mapped_column(Boolean)
    pets_allowed: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    # Настройки уведомлений
    notification_enabled: Mapped[bool] = mapped_column(default=True)
    notification_frequency_hours: Mapped[int] = mapped_column(default=24)  # Частота в часах
    last_notification_sent: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Связи
    user: Mapped["User"] = relationship(back_populates="filters")
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="filter", cascade="all, delete-orphan"
    )

    # Индексы для оптимизации поиска
    __table_args__ = (
        Index('idx_filter_user_active', 'user_id', 'is_active'),
        Index('idx_filter_city_price', 'city', 'min_price', 'max_price'),
        Index('idx_filter_notifications', 'notification_enabled', 'last_notification_sent'),
    )

    def __repr__(self):
        return f"<Filter(id={self.id}, name={self.name}, user_id={self.user_id})>"


class Listing(Base):
    """
    Объявление о недвижимости
    MVP: основная информация с возможностью расширения
    """
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Идентификация источника
    external_id: Mapped[str] = mapped_column(String(255), index=True)  # ID на сайте-источнике
    source: Mapped[str] = mapped_column(String(50), index=True)  # idealista, immobiliare, subito
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    
    # Основная информация
    title: Mapped[str] = mapped_column(String(512))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Цена
    price: Mapped[Optional[float]] = mapped_column(Float, index=True)
    price_currency: Mapped[str] = mapped_column(String(10), default="EUR")
    
    # Характеристики недвижимости
    property_type: Mapped[Optional[str]] = mapped_column(
        String(50), index=True
    )  # apartment, house, room, studio
    rooms: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    bedrooms: Mapped[Optional[int]] = mapped_column(Integer)
    bathrooms: Mapped[Optional[int]] = mapped_column(Integer)
    area: Mapped[Optional[float]] = mapped_column(Float, index=True)  # площадь в м²
    floor: Mapped[Optional[str]] = mapped_column(String(20))
    total_floors: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Дополнительные характеристики
    furnished: Mapped[Optional[bool]] = mapped_column(Boolean)
    pets_allowed: Mapped[Optional[bool]] = mapped_column(Boolean)
    features: Mapped[Optional[List[str]]] = mapped_column(JSON)  # балкон, лифт, парковка и т.д.
    
    # Местоположение
    address: Mapped[Optional[str]] = mapped_column(String(512))
    city: Mapped[str] = mapped_column(String(100), index=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    
    # Медиа
    images: Mapped[Optional[List[str]]] = mapped_column(JSON)  # список URL изображений
    virtual_tour_url: Mapped[Optional[str]] = mapped_column(String(1024))
    
    # Информация об агентстве/владельце
    agency_name: Mapped[Optional[str]] = mapped_column(String(255))
    contact_info: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    # Статус и временные метки
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Связи
    notifications: Mapped[List["Notification"]] = relationship(back_populates="listing")

    # Уникальное ограничение для предотвращения дубликатов
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
        Index('idx_listing_city_price', 'city', 'price'),
        Index('idx_listing_rooms_area', 'rooms', 'area'),
        Index('idx_listing_coordinates', 'latitude', 'longitude'),
        Index('idx_listing_source_active', 'source', 'is_active'),
        Index('idx_listing_scraped_at', 'scraped_at'),
    )

    def __repr__(self):
        return f"<Listing(id={self.id}, title={self.title[:50]}, source={self.source})>"


class Notification(Base):
    """
    Уведомление пользователю
    MVP: простая система уведомлений через Telegram
    """
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    filter_id: Mapped[int] = mapped_column(ForeignKey("filters.id"), index=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    
    # Тип и статус уведомления
    notification_type: Mapped[str] = mapped_column(
        String(50), default="new_listing", index=True
    )  # new_listing, price_change, listing_updated
    status: Mapped[str] = mapped_column(
        String(50), default="pending", index=True
    )  # pending, sent, failed, error
    
    # Сообщение и ошибки
    message: Mapped[Optional[str]] = mapped_column(Text)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Попытки отправки
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)

    # Связи
    user: Mapped["User"] = relationship(back_populates="notifications")
    filter: Mapped["Filter"] = relationship(back_populates="notifications")
    listing: Mapped["Listing"] = relationship(back_populates="notifications")

    # Индексы для оптимизации
    __table_args__ = (
        Index('idx_notification_status_created', 'status', 'created_at'),
        Index('idx_notification_user_filter', 'user_id', 'filter_id'),
        Index('idx_notification_pending', 'status', 'attempts', 'max_attempts'),
    )

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, status={self.status})>"


# Модель для хранения статистики парсинга (опционально для MVP)
class ScrapingSession(Base):
    """
    Сессия парсинга для отслеживания процесса
    MVP: базовая статистика
    """
    __tablename__ = "scraping_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Информация о сессии
    source: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(
        String(50), default="running", index=True
    )  # running, completed, failed
    
    # Статистика
    total_listings_found: Mapped[int] = mapped_column(Integer, default=0)
    new_listings_added: Mapped[int] = mapped_column(Integer, default=0)
    updated_listings: Mapped[int] = mapped_column(Integer, default=0)
    errors_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Дополнительная информация
    filters_used: Mapped[Optional[Dict]] = mapped_column(JSON)
    error_details: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Временные метки
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    # Индексы
    __table_args__ = (
        Index('idx_scraping_source_status', 'source', 'status'),
        Index('idx_scraping_started_at', 'started_at'),
    )

    def __repr__(self):
        return f"<ScrapingSession(id={self.id}, source={self.source}, status={self.status})>" 