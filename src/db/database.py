"""
Конфигурация базы данных для ITA_RENT_BOT
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

logger = logging.getLogger(__name__)

# Создаем движок базы данных с правильными настройками
def create_database_engine():
    """Создание движка БД с учетом типа базы данных"""
    database_url = settings.DATABASE_URL_SYNC
    
    if database_url.startswith("postgresql"):
        # PostgreSQL настройки для production
        engine = create_engine(
            database_url,
            echo=settings.database_echo,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,  # Переподключение каждый час
            connect_args={
                "options": "-c timezone=UTC"
            }
        )
        logger.info("🐘 Используется PostgreSQL база данных")
    else:
        # SQLite настройки для разработки
        engine = create_engine(
            database_url,
            echo=settings.database_echo,
            connect_args={"check_same_thread": False}
        )
        logger.info("📁 Используется SQLite база данных")
    
    return engine

# Создаем движок
engine = create_database_engine()

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

def get_db():
    """
    Dependency для получения сессии базы данных
    Используется в FastAPI эндпоинтах
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection():
    """Тест подключения к базе данных"""
    try:
        db = SessionLocal()
        # Простой запрос для проверки соединения
        db.execute("SELECT 1")
        db.close()
        logger.info("✅ Подключение к базе данных успешно")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к базе данных: {e}")
        return False

def init_database():
    """Инициализация базы данных и создание таблиц"""
    try:
        from src.db.models import Base
        logger.info("🗄️ Принудительное пересоздание таблиц базы данных...")
        
        # ВРЕМЕННО: Удаляем и пересоздаем все таблицы для обновления схемы
        Base.metadata.drop_all(bind=engine)
        logger.info("🗑️ Старые таблицы удалены")
        
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы базы данных созданы с новой схемой")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка создания таблиц БД: {e}")
        return False 