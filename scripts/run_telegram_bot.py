#!/usr/bin/env python3
"""
Скрипт запуска Telegram бота для ITA_RENT_BOT
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Добавляем корневую папку в путь
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_environment():
    """Загрузка переменных окружения"""
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=ROOT_DIR / '.env')
        logger.info("✅ Переменные окружения загружены")
    except ImportError:
        logger.info("📝 python-dotenv не установлен, используем системные переменные")

def check_required_env_vars():
    """Проверка обязательных переменных окружения"""
    required_vars = {
        "TELEGRAM_BOT_TOKEN": "Токен Telegram бота",
        "DATABASE_URL": "URL базы данных",
        "SECRET_KEY": "Секретный ключ"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.error("❌ Отсутствуют обязательные переменные окружения:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        return False
    
    logger.info("✅ Все обязательные переменные окружения установлены")
    return True

async def check_database_connection():
    """Проверка подключения к базе данных с ретраями"""
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            from src.db.database import get_db
            from src.db.models import User
            
            # Получаем сессию БД
            db = next(get_db())
            
            # Пробуем выполнить простой запрос
            count = db.query(User).count()
            logger.info(f"✅ База данных доступна. Пользователей: {count}")
            db.close()
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Попытка {attempt + 1}/{max_retries} подключения к БД неуспешна: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"⏳ Ожидание {retry_delay} секунд перед повторной попыткой...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("❌ Не удалось подключиться к базе данных")
                return False
    
    return False

async def main():
    """Главная функция"""
    logger.info("🤖 Запуск ITA_RENT_BOT Telegram Bot...")
    
    # Загружаем переменные окружения
    load_environment()
    
    # Проверяем переменные окружения
    if not check_required_env_vars():
        sys.exit(1)
    
    # Проверяем подключение к базе данных
    logger.info("🔍 Проверка подключения к базе данных...")
    if not await check_database_connection():
        logger.error("❌ Критическая ошибка: Нет подключения к базе данных")
        sys.exit(1)
    
    # Запускаем Telegram бота
    try:
        from src.services.telegram_bot import TelegramBotService
        
        bot_service = TelegramBotService()
        logger.info("✅ Бот инициализирован успешно")
        
        # Запуск в режиме polling
        await bot_service.start_polling()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 