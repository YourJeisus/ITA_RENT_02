#!/usr/bin/env python3
"""
Скрипт запуска диспетчера уведомлений для ITA_RENT_BOT
MVP версия для автоматической отправки уведомлений пользователям
"""
import asyncio
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Добавляем корневую папку в Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.services.notification_service import run_notification_dispatcher

# Загружаем переменные окружения
load_dotenv(dotenv_path=ROOT_DIR / '.env')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('notification_dispatcher.log') if os.path.exists('/') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска диспетчера уведомлений"""
    logger.info("🔔 Запуск диспетчера уведомлений ITA_RENT_BOT...")
    
    # Проверяем наличие необходимых настроек
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    database_url = os.getenv("DATABASE_URL")
    
    if not telegram_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
        sys.exit(1)
    
    if not database_url:
        logger.error("❌ DATABASE_URL не установлен!")
        sys.exit(1)
    
    try:
        # Запускаем диспетчер уведомлений
        stats = await run_notification_dispatcher()
        
        logger.info("📊 Статистика выполнения:")
        logger.info(f"   👥 Обработано пользователей: {stats['users_processed']}")
        logger.info(f"   📨 Отправлено уведомлений: {stats['notifications_sent']}")
        logger.info(f"   ❌ Ошибок: {stats['errors']}")
        
        if stats['notifications_sent'] > 0:
            logger.info("✅ Диспетчер уведомлений завершен успешно")
        else:
            logger.info("ℹ️  Новых уведомлений для отправки не найдено")
        
        return 0  # Успешное завершение
        
    except KeyboardInterrupt:
        logger.info("⏹️  Диспетчер остановлен пользователем")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка диспетчера: {e}")
        logger.exception("Детали ошибки:")
        return 1  # Ошибка


if __name__ == "__main__":
    # Запускаем диспетчер
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 