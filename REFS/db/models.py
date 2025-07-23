from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON, Text, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from src.db.database import Base
from datetime import datetime
from typing import Optional, List, Dict

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)
    telegram_verification_code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)
    telegram_verification_code_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    whatsapp_number = Column(String, nullable=True, unique=True, index=True)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    filters: Mapped[List["Filter"]] = relationship(back_populates="owner")
    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates="user")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")

class Filter(Base):
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    name: Mapped[str] = mapped_column(String(255), index=True, default="Мой фильтр")
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Детализированные поля фильтра
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    min_price: Mapped[Optional[int]] = mapped_column(Integer)
    max_price: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    min_rooms: Mapped[Optional[int]] = mapped_column(Integer)
    max_rooms: Mapped[Optional[int]] = mapped_column(Integer)
    property_type: Mapped[Optional[str]] = mapped_column(String(100)) # apartment, room, house
    min_area: Mapped[Optional[int]] = mapped_column(Integer)
    max_area: Mapped[Optional[int]] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    owner: Mapped["User"] = relationship(back_populates="filters")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="filter_criteria", cascade="all, delete-orphan")


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_site: Mapped[str] = mapped_column(String(100), index=True)
    original_id: Mapped[str] = mapped_column(String(255), index=True)
    
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    title: Mapped[str] = mapped_column(String(512))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    price: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    
    address_text: Mapped[Optional[str]] = mapped_column(String(512))
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    district: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    
    area_sqm: Mapped[Optional[float]] = mapped_column(Float)
    num_rooms: Mapped[Optional[int]] = mapped_column(Integer)
    num_bedrooms: Mapped[Optional[int]] = mapped_column(Integer)
    num_bathrooms: Mapped[Optional[int]] = mapped_column(Integer)
    floor: Mapped[Optional[str]] = mapped_column(String(50))
    
    property_type: Mapped[Optional[str]] = mapped_column(String(100), index=True) # Тип недвижимости (apartment, house)
    listing_type: Mapped[Optional[str]] = mapped_column(String(50), default="rent") # rent, sale - в основном rent

    features: Mapped[Optional[List[str]]] = mapped_column(JSON) # Список фич
    photos_urls: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    agency_name: Mapped[Optional[str]] = mapped_column(String(255)) # Название агентства
    additional_info: Mapped[Optional[Dict]] = mapped_column(JSON) # Дополнительная информация
    
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    is_available: Mapped[bool] = mapped_column(default=True, index=True)

    __table_args__ = (UniqueConstraint("source_site", "original_id", name="_source_original_id_uc"),)
    
    notifications: Mapped[List["Notification"]] = relationship(back_populates="listing_info")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    subscription_type: Mapped[str] = mapped_column(String(50), default="free") # free, premium_monthly, premium_annual
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    is_active: Mapped[bool] = mapped_column(default=True)
    
    user: Mapped["User"] = relationship(back_populates="subscriptions")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    filter_id: Mapped[int] = mapped_column(ForeignKey("filters.id"))
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, sent, failed, error
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(String(512))

    user: Mapped["User"] = relationship(back_populates="notifications")
    filter_criteria: Mapped["Filter"] = relationship(back_populates="notifications")
    listing_info: Mapped["Listing"] = relationship(back_populates="notifications") 