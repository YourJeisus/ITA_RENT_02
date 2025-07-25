#!/usr/bin/env python3
"""
Запуск notification worker в бесконечном цикле
Замена для shell команды while true в Docker
"""
import os
import sys
import time
import asyncio
import logging
import subprocess
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

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
        load_dotenv()
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

async def run_notification_dispatcher():
    """Запуск диспетчера уведомлений"""
    try:
        logger.info("🔔 Запуск диспетчера уведомлений...")
        
        # Импортируем и запускаем диспетчер
        from src.services.notification_service import run_notification_dispatcher
        
        result = await run_notification_dispatcher()
        logger.info(f"✅ Диспетчер завершен. Результат: {result}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в диспетчере уведомлений: {e}")
        return False

async def main():
    """Главный цикл notification worker"""
    logger.info("🔔 Запуск Notification Worker...")
    
    # Загружаем переменные окружения
    load_environment()
    
    # Проверяем переменные окружения
    if not check_required_env_vars():
        sys.exit(1)
    
    # Интервал между запусками (30 минут = 1800 секунд)
    interval_seconds = int(os.getenv("NOTIFICATION_INTERVAL_SECONDS", "1800"))
    logger.info(f"⏰ Интервал уведомлений: {interval_seconds} секунд ({interval_seconds//60} минут)")
    
    # Бесконечный цикл
    iteration = 0
    while True:
        iteration += 1
        logger.info(f"🔄 Итерация #{iteration} - запуск диспетчера уведомлений")
        
        try:
            # Запускаем диспетчер уведомлений
            success = await run_notification_dispatcher()
            
            if success:
                logger.info(f"✅ Итерация #{iteration} завершена успешно")
            else:
                logger.warning(f"⚠️ Итерация #{iteration} завершена с ошибками")
                
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в итерации #{iteration}: {e}")
        
        # Ожидание до следующего запуска
        logger.info(f"⏳ Ожидание {interval_seconds} секунд до следующего запуска...")
        await asyncio.sleep(interval_seconds)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1) 