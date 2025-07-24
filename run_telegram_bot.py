#!/usr/bin/env python3
"""
Скрипт запуска Telegram бота для ITA_RENT_BOT
MVP версия
"""
import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Добавляем корневую папку в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.telegram_bot import TelegramBotService

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('telegram_bot.log') if os.path.exists('/') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    logger.info("🤖 Запуск ITA_RENT_BOT Telegram Bot...")
    
    # Проверяем наличие токена
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
        logger.error("Создайте .env файл и добавьте:")
        logger.error("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        sys.exit(1)
    
    # Создаем и запускаем бота
    try:
        bot = TelegramBotService()
        logger.info("✅ Бот инициализирован успешно")
        
        # Запускаем в polling режиме
        await bot.start_polling()
        
    except KeyboardInterrupt:
        logger.info("⏹️  Бот остановлен пользователем")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
        logger.exception("Детали ошибки:")
        sys.exit(1)


if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main()) 