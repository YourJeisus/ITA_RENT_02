"""
Скрипт инициализации базы данных
"""
import logging
from sqlalchemy.orm import Session

from src.db.database import SessionLocal, create_tables
from src.crud.crud_user import user as crud_user
from src.schemas.user import UserCreate
from src.core.config import settings

logger = logging.getLogger(__name__)


def init_db(db: Session = None) -> None:
    """
    Инициализация базы данных
    Создает таблицы и суперпользователя
    """
    logger.info("🚀 Инициализация базы данных...")
    
    # Создаем таблицы
    create_tables()
    
    if db is None:
        db = SessionLocal()
    
    try:
        # Проверяем, есть ли суперпользователь
        superuser = crud_user.get_by_email(db, email="admin@itarent.com")
        
        if not superuser:
            logger.info("👤 Создание суперпользователя...")
            user_in = UserCreate(
                email="admin@itarent.com",
                password="admin123456",  # В production должен быть изменен
                first_name="Admin",
                last_name="User"
            )
            superuser = crud_user.create(db, obj_in=user_in)
            
            # Делаем его суперпользователем
            superuser.is_superuser = True
            superuser.subscription_type = "premium"
            db.add(superuser)
            db.commit()
            db.refresh(superuser)
            
            logger.info(f"✅ Суперпользователь создан: {superuser.email}")
        else:
            logger.info("👤 Суперпользователь уже существует")
        
        logger.info("✅ База данных инициализирована успешно")
        
    except Exception as e:
        logger.error(f"💥 Ошибка инициализации базы данных: {e}")
        raise
    finally:
        db.close()


def create_sample_data(db: Session = None) -> None:
    """
    Создание тестовых данных для разработки
    """
    if settings.ENVIRONMENT != "development":
        logger.warning("⚠️ Создание тестовых данных разрешено только в development окружении")
        return
    
    logger.info("📊 Создание тестовых данных...")
    
    if db is None:
        db = SessionLocal()
    
    try:
        from src.crud.crud_listing import listing as crud_listing
        from src.schemas.listing import ListingCreate
        from datetime import datetime
        
        # Создаем несколько тестовых объявлений
        sample_listings = [
            {
                "external_id": "test_1",
                "source": "idealista",
                "url": "https://www.idealista.it/test/1",
                "title": "Уютная квартира в центре Рима",
                "description": "Прекрасная квартира в историческом центре",
                "price": 1500.0,
                "property_type": "apartment",
                "rooms": 2,
                "area": 80.0,
                "city": "Roma",
                "address": "Via del Corso, 123",
                "images": ["https://example.com/image1.jpg"],
                "is_active": True
            },
            {
                "external_id": "test_2", 
                "source": "idealista",
                "url": "https://www.idealista.it/test/2",
                "title": "Современная студия в Милане",
                "description": "Стильная студия в деловом районе",
                "price": 1200.0,
                "property_type": "studio",
                "rooms": 1,
                "area": 45.0,
                "city": "Milano",
                "address": "Via Brera, 456",
                "images": ["https://example.com/image2.jpg"],
                "is_active": True
            },
            {
                "external_id": "test_3",
                "source": "immobiliare",
                "url": "https://www.immobiliare.it/test/3",
                "title": "Дом с садом во Флоренции",
                "description": "Красивый дом с частным садом",
                "price": 2200.0,
                "property_type": "house",
                "rooms": 4,
                "area": 150.0,
                "city": "Firenze",
                "address": "Via dei Giardini, 789",
                "images": ["https://example.com/image3.jpg"],
                "furnished": True,
                "pets_allowed": True,
                "is_active": True
            }
        ]
        
        for listing_data in sample_listings:
            # Проверяем, не существует ли уже такое объявление
            existing = crud_listing.get_by_external_id(
                db, 
                source=listing_data["source"], 
                external_id=listing_data["external_id"]
            )
            
            if not existing:
                listing_in = ListingCreate(**listing_data)
                crud_listing.create(db, obj_in=listing_in)
                logger.info(f"📝 Создано тестовое объявление: {listing_data['title']}")
        
        logger.info("✅ Тестовые данные созданы успешно")
        
    except Exception as e:
        logger.error(f"💥 Ошибка создания тестовых данных: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    """
    Запуск инициализации из командной строки
    """
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Инициализация базы данных ITA_RENT_BOT...")
    init_db()
    
    if settings.ENVIRONMENT == "development":
        print("📊 Создание тестовых данных...")
        create_sample_data()
    
    print("✅ Готово!") 