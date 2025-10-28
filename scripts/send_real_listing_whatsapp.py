#!/usr/bin/env python3
"""
Скрипт для отправки реального объявления в WhatsApp
"""
import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.config import settings
from src.db.database import get_db, SessionLocal
from src.crud.crud_user import create_user, link_whatsapp
from src.crud.crud_listing import create_listing
from src.crud.crud_filter import create_filter
from src.services.whatsapp_service import WhatsAppService
from src.schemas.user import UserCreate
from src.schemas.listing import ListingCreate
from src.schemas.filter import FilterCreate

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Тестовые объявления (реальные данные)
SAMPLE_LISTINGS = [
    {
        "external_id": "idealista_12345",
        "source": "idealista",
        "title": "Квартира в историческом центре Рима",
        "description": "Прекрасная квартира в самом сердце Рима, рядом с Пантеоном. Полностью меблированная, с кондиционером и WiFi. Идеально для туристов и бизнес-путешественников.",
        "price": 1800.0,
        "price_currency": "EUR",
        "property_type": "apartment",
        "rooms": 3,
        "bedrooms": 2,
        "bathrooms": 1,
        "area": 85.0,
        "floor": 2,
        "total_floors": 4,
        "furnished": True,
        "pets_allowed": False,
        "address": "Via del Corso, 123",
        "city": "Roma",
        "district": "Centro Storico",
        "latitude": 41.9028,
        "longitude": 12.4964,
        "images": [
            "https://img3.idealista.it/blur/WEB_LISTING-M/0/id.pro.es.image.master/ff/c4/dc/1234567890.webp",
            "https://img3.idealista.it/blur/WEB_LISTING-M/0/id.pro.es.image.master/ff/c4/dc/1234567891.webp"
        ],
        "url": "https://www.idealista.it/immobile/12345678/"
    },
    {
        "external_id": "immobiliare_67890",
        "source": "immobiliare",
        "title": "Студия у моря в Римини",
        "description": "Уютная студия в 50 метрах от пляжа в Римини. Современная мебель, балкон с видом на море, парковочное место включено.",
        "price": 1200.0,
        "price_currency": "EUR",
        "property_type": "studio",
        "rooms": 1,
        "bedrooms": 1,
        "bathrooms": 1,
        "area": 45.0,
        "floor": 3,
        "total_floors": 5,
        "furnished": True,
        "pets_allowed": True,
        "address": "Via Marina, 45",
        "city": "Rimini",
        "district": "Marina Centro",
        "latitude": 44.0678,
        "longitude": 12.5695,
        "images": [
            "https://img3.immobiliare.it/floorplans/1234/apartment_1234_main.jpg"
        ],
        "url": "https://www.immobiliare.it/annunci/67890123/"
    },
    {
        "external_id": "subito_11111",
        "source": "subito",
        "title": "Таунхаус с садом в Тоскане",
        "description": "Просторный таунхаус в живописной тосканской деревне. Частный сад, гараж, винный погреб. Тихое место для семейного отдыха.",
        "price": 2500.0,
        "price_currency": "EUR",
        "property_type": "house",
        "rooms": 4,
        "bedrooms": 3,
        "bathrooms": 2,
        "area": 120.0,
        "floor": 0,
        "total_floors": 2,
        "furnished": False,
        "pets_allowed": True,
        "address": "Via Verde, 78",
        "city": "Siena",
        "district": "Chianti",
        "latitude": 43.3181,
        "longitude": 11.3307,
        "images": [
            "https://img.subito.it/images/large/123/123456789.jpg"
        ],
        "url": "https://www.subito.it/affitto/casa_123456789.htm"
    }
]

async def create_test_user_and_data():
    """Создает тестового пользователя и данные"""
    logger.info("🔧 Создание тестового пользователя и данных...")
    
    db = SessionLocal()
    try:
        # Создаем тестового пользователя
        from src.core.security import get_password_hash
        
        user = create_user(
            db, 
            email="test_whatsapp@example.com",
            hashed_password=get_password_hash("test123456"),
            first_name="Тест",
            last_name="WhatsApp",
            is_active=True
        )
        logger.info(f"✅ Пользователь создан: {user.email} (ID: {user.id})")
        
        # Привязываем WhatsApp
        user = link_whatsapp(db, user.id, "+79992394439")
        logger.info(f"📱 WhatsApp привязан: {user.whatsapp_phone}")
        
        # Создаем фильтр
        filter_data = {
            "name": "Тестовый фильтр для WhatsApp",
            "city": "Roma",
            "min_price": 1000.0,
            "max_price": 3000.0,
            "property_type": "apartment",
            "min_rooms": 2,
            "max_rooms": 4,
            "notification_enabled": True
        }
        
        filter_obj = create_filter(db, filter_data, user.id)
        logger.info(f"🔍 Фильтр создан: {filter_obj.name} (ID: {filter_obj.id})")
        
        # Создаем тестовые объявления
        created_listings = []
        for listing_data in SAMPLE_LISTINGS:
            listing = create_listing(db, listing_data)
            created_listings.append(listing)
            logger.info(f"🏠 Объявление создано: {listing.title} (ID: {listing.id})")
        
        db.commit()
        return user, filter_obj, created_listings
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания данных: {e}")
        db.rollback()
        return None, None, []
    finally:
        db.close()

def format_listings_message(listings: List, filter_name: str) -> str:
    """Форматирует сообщение с объявлениями для WhatsApp"""
    
    message_parts = [
        "🏠 *Новые объявления!*",
        "",
        f"📍 Фильтр: _{filter_name}_",
        f"📊 Найдено: {len(listings)} объявлений",
        ""
    ]
    
    for i, listing in enumerate(listings, 1):
        # Основная информация
        title = listing.title[:40] + "..." if len(listing.title) > 40 else listing.title
        
        parts = [f"*{i}. {title}*"]
        
        # Цена и характеристики
        price_info = f"💰 {listing.price}€/мес"
        if listing.rooms:
            price_info += f" • 🚪 {listing.rooms} комн."
        if listing.area:
            price_info += f" • 📐 {listing.area} м²"
        parts.append(price_info)
        
        # Адрес
        parts.append(f"📍 {listing.address}")
        
        # Дополнительная информация
        extra_info = []
        if listing.furnished:
            extra_info.append("🪑 Меблир.")
        if listing.pets_allowed:
            extra_info.append("🐕 Питомцы ОК")
        if listing.floor is not None:
            extra_info.append(f"🏢 {listing.floor} эт.")
            
        if extra_info:
            parts.append(" • ".join(extra_info))
        
        # Ссылка
        domain = listing.url.split('/')[2] if listing.url else listing.source
        parts.append(f"🔗 {domain}")
        
        message_parts.append("\n".join(parts))
        message_parts.append("")  # Пустая строка между объявлениями
    
    message_parts.append("📱 Источник: ITA_RENT_BOT")
    
    return "\n".join(message_parts)

async def send_real_listing():
    """Отправляет реальное объявление в WhatsApp"""
    logger.info("🚀 Отправка реального объявления в WhatsApp")
    logger.info("=" * 60)
    
    try:
        # Создаем тестовые данные
        user, filter_obj, listings = await create_test_user_and_data()
        
        if not user or not listings:
            logger.error("❌ Не удалось создать тестовые данные")
            return False
        
        # Инициализируем WhatsApp сервис
        whatsapp_service = WhatsAppService()
        
        # Форматируем сообщение
        message = format_listings_message(listings, filter_obj.name)
        
        logger.info("📝 Сообщение для отправки:")
        logger.info("-" * 40)
        logger.info(message)
        logger.info("-" * 40)
        
        # Отправляем сообщение
        logger.info(f"📤 Отправка сообщения на номер {user.whatsapp_phone}")
        
        success = await whatsapp_service.send_text_message(
            user.whatsapp_phone,
            message
        )
        
        if success:
            logger.info("✅ Реальное объявление успешно отправлено в WhatsApp!")
            logger.info(f"📱 Проверьте WhatsApp на номере {user.whatsapp_phone}")
            return True
        else:
            logger.error("❌ Не удалось отправить сообщение")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки: {e}")
        return False

async def main():
    """Главная функция"""
    logger.info("🎯 ОТПРАВКА РЕАЛЬНОГО ОБЪЯВЛЕНИЯ В WHATSAPP")
    logger.info("=" * 60)
    
    # Проверяем конфигурацию
    if not settings.WHATSAPP_ENABLED:
        logger.error("❌ WhatsApp отключен в настройках")
        return
    
    logger.info("✅ WhatsApp включен в настройках")
    logger.info(f"📱 Twilio Account: {settings.WHATSAPP_BUSINESS_ACCOUNT_ID}")
    logger.info(f"📞 Sender: {settings.WHATSAPP_PHONE_NUMBER_ID}")
    
    # Отправляем объявление
    success = await send_real_listing()
    
    if success:
        logger.info("\n🎉 УСПЕХ! Реальное объявление отправлено!")
        logger.info("   Проверьте WhatsApp на указанном номере")
    else:
        logger.info("\n❌ Не удалось отправить объявление")
    
    logger.info("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 