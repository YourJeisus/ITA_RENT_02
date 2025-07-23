from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Настройки приложения
    """
    # Основные настройки
    APP_NAME: str = "ITA_RENT_BOT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API настройки
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    # База данных - автоматическое определение типа БД
    DATABASE_URL: str = "sqlite:///./ita_rent.db"
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Синхронная версия DATABASE_URL для SQLAlchemy"""
        if self.DATABASE_URL.startswith("postgresql://"):
            # Railway PostgreSQL использует postgresql://, но SQLAlchemy 2.0+ требует postgresql+psycopg2://
            return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
        return self.DATABASE_URL
    
    @property 
    def DATABASE_URL_ASYNC(self) -> str:
        """Асинхронная версия DATABASE_URL для SQLAlchemy"""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
    
    # Redis (опционально)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    
    # Stripe платежи
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # Парсинг
    SCRAPERAPI_KEY: str = ""
    SCRAPER_API_KEY: str = ""  # Для обратной совместимости 
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Настройки парсинга
    SCRAPING_MAX_PAGES: int = 10
    SCRAPING_DELAY_SECONDS: int = 1
    SCRAPING_TIMEOUT_SECONDS: int = 30
    
    # Воркер настройки
    SCRAPER_WORKER_INTERVAL_HOURS: int = 6
    SCRAPER_WORKER_MAX_PAGES: int = 10
    
    # Мониторинг
    SENTRY_DSN: str = ""
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    
    # CORS - обновленные домены Railway + Vercel
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        # Railway production URLs (обновленные)
        "https://itarent02front-production.up.railway.app",
        "https://itarent02back-production.up.railway.app",
        # Vercel domains
        "https://ita-rent-02.vercel.app",
        "https://ita-rent-02-*.vercel.app",
        "https://*.vercel.app",
        # Возможные новые домены Railway
        "https://*.railway.app",
        "https://*.up.railway.app"
    ]
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 часа
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48  # 48 часов
    
    # Production настройки
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_echo(self) -> bool:
        """Включать ли SQL логи"""
        return self.DEBUG and not self.is_production
    
    # Railway специфичные настройки
    PORT: int = int(os.getenv("PORT", "8000"))
    RAILWAY_ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "")
    RAILWAY_PROJECT_ID: str = os.getenv("RAILWAY_PROJECT_ID", "")
    RAILWAY_SERVICE_ID: str = os.getenv("RAILWAY_SERVICE_ID", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Создаем глобальный экземпляр настроек
settings = Settings()

# Автоматическая настройка для Railway
if settings.RAILWAY_ENVIRONMENT:
    # Мы в Railway, обновляем настройки
    settings.ENVIRONMENT = "production"
    settings.DEBUG = False 