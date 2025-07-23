from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv

from src.api.v1.api import api_router
from src.core.config import settings

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Telegram бот для поиска недвижимости в Италии",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 🗄️ Автоматическое создание таблиц при запуске
@app.on_event("startup")
async def startup_event():
    """Инициализация базы данных при запуске приложения"""
    try:
        # ВРЕМЕННО: Принудительное пересоздание таблиц для обновления схемы
        logger.info("🔄 ПРИНУДИТЕЛЬНОЕ пересоздание таблиц для обновления схемы...")
        
        from src.db.database import init_database
        init_success = init_database()
        
        if init_success:
            logger.info("✅ База данных инициализирована успешно!")
        else:
            logger.error("❌ Ошибка инициализации базы данных!")
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка startup: {e}")
        # Не останавливаем приложение, продолжаем работу

# CORS настройки - используем настройки из config
origins = settings.BACKEND_CORS_ORIGINS.copy()

# Добавляем дополнительные origins из переменных окружения
cors_origins = os.getenv("BACKEND_CORS_ORIGINS")
if cors_origins:
    try:
        import json
        additional_origins = json.loads(cors_origins)
        origins.extend(additional_origins)
        logger.info(f"Добавлены дополнительные CORS origins: {additional_origins}")
    except json.JSONDecodeError:
        logger.warning("Неверный формат BACKEND_CORS_ORIGINS в переменных окружения")

logger.info(f"CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.railway\.app",  # Railway domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем API роутеры
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Простой health check endpoint для проверки работоспособности API
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    )

# Корневой endpoint
@app.get("/")
async def root():
    """
    Корневой endpoint
    """
    return {
        "message": "Welcome to ITA Rent Bot! Visit /docs for API documentation.",
        "docs": "/docs",
        "health": "/health"
    }

# Обработчик ошибок
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint не найден"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Внутренняя ошибка сервера: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )

if __name__ == "__main__":
    import uvicorn
    
    # Запуск сервера
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("DEBUG", "False").lower() == "true" else False,
        log_level="info"
    ) 