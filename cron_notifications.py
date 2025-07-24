#!/usr/bin/env python3
"""
CRON задача для автоматической отправки уведомлений
Запускается каждые 30 минут для проверки новых объявлений
"""
import asyncio
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Добавляем корневую папку в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.notification_service import run_notification_dispatcher

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования для cron (краткий формат)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('cron_notifications.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Cron задача для отправки уведомлений"""
    start_time = datetime.now()
    logger.info(f"CRON: Запуск проверки уведомлений {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Запускаем диспетчер уведомлений
        stats = await run_notification_dispatcher()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Краткий лог результата
        if stats['notifications_sent'] > 0:
            logger.info(
                f"CRON: ✅ Успешно. Пользователей: {stats['users_processed']}, "
                f"Уведомлений: {stats['notifications_sent']}, "
                f"Время: {duration:.1f}с"
            )
        else:
            logger.info(f"CRON: ℹ️  Новых уведомлений нет. Время: {duration:.1f}с")
        
        if stats['errors'] > 0:
            logger.warning(f"CRON: ⚠️  Ошибок: {stats['errors']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"CRON: ❌ Ошибка: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 