"""
Конфигурация базы данных для ITA_RENT_BOT
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.config import settings

logger = logging.getLogger(__name__)

logger.info(f"🔗 Настройка подключения к базе данных...")
logger.info(f"📊 URL: {settings.DATABASE_URL[:50]}...")

# Создание движка базы данных
def create_database_engine():
    try:
        if "sqlite" in settings.DATABASE_URL:
            logger.info("🗃️ Используется SQLite база данных")
            engine = create_engine(
                settings.DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=settings.DEBUG  # Логирование SQL запросов в debug режиме
            )
        elif "postgresql" in settings.DATABASE_URL or "postgres" in settings.DATABASE_URL:
            logger.info("🐘 Используется PostgreSQL база данных")
            engine = create_engine(
                settings.DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=settings.DEBUG
            )
        else:
            logger.warning("⚠️ Неизвестный тип базы данных, используем стандартные настройки")
            engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
        
        logger.info("✅ Движок базы данных создан успешно")
        return engine
        
    except Exception as e:
        logger.error(f"💥 Ошибка создания движка базы данных: {e}")
        raise

# Создаем движок
engine = create_database_engine()

# Создаем фабрику сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для моделей
Base = declarative_base()

# Зависимость для получения сессии БД
def get_db():
    """
    Dependency для получения сессии базы данных
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания всех таблиц
def create_tables():
    """
    Создание всех таблиц в базе данных
    """
    logger.info("🏗️ Создание таблиц базы данных...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы созданы успешно")
    except Exception as e:
        logger.error(f"💥 Ошибка создания таблиц: {e}")
        raise

# Функция для проверки подключения к БД
async def check_database_connection():
    """
    Проверка подключения к базе данных
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"💥 Ошибка подключения к базе данных: {e}")
        return False 