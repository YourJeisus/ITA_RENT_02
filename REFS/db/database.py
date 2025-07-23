import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

logger = logging.getLogger(__name__)

logger.info(f"🔗 Настройка подключения к базе данных...")
logger.info(f"📊 URL: {settings.DATABASE_URL[:50]}...")

try:
    engine = create_engine(
        settings.DATABASE_URL, 
        # connect_args={"check_same_thread": False} # Необходимо только для SQLite
    )

    # Для SQLite, раскомментируйте и используйте connect_args
    if "sqlite" in settings.DATABASE_URL:
        logger.info("🗃️ Используется SQLite база данных")
        engine = create_engine(
            settings.DATABASE_URL, 
            connect_args={"check_same_thread": False}
        )
    elif "postgres" in settings.DATABASE_URL:
        logger.info("🐘 Используется PostgreSQL база данных")
    
    logger.info("✅ Движок базы данных создан успешно")
    
except Exception as e:
    logger.error(f"💥 Ошибка создания движка базы данных: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 