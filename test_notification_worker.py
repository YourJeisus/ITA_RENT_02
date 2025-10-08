#!/usr/bin/env python3
"""
Тестирование notification worker
Проверяем работу с Telegram и WhatsApp уведомлениями
"""
import os
import sys
import asyncio
import logging
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

async def test_notification_worker():
    """Тестирование notification worker"""
    logger.info("🧪 Запуск тестирования notification worker...")
    
    try:
        # Импортируем и тестируем конфигурацию
        from src.core.config import settings
        
        logger.info("📋 Проверка конфигурации:")
        logger.info(f"   - DEBUG_NOTIFICATIONS: {settings.DEBUG_NOTIFICATIONS}")
        logger.info(f"   - TELEGRAM_BOT_TOKEN: {'✅ установлен' if settings.TELEGRAM_BOT_TOKEN else '❌ отсутствует'}")
        logger.info(f"   - WHATSAPP_ENABLED: {settings.WHATSAPP_ENABLED}")
        
        if settings.WHATSAPP_ENABLED:
            logger.info("📱 Конфигурация WhatsApp:")
            logger.info(f"   - WHATSAPP_API_TOKEN: {'✅ установлен' if settings.WHATSAPP_API_TOKEN else '❌ отсутствует'}")
            logger.info(f"   - WHATSAPP_PHONE_NUMBER_ID: {'✅ установлен' if settings.WHATSAPP_PHONE_NUMBER_ID else '❌ отсутствует'}")
            logger.info(f"   - WHATSAPP_BUSINESS_ACCOUNT_ID: {'✅ установлен' if settings.WHATSAPP_BUSINESS_ACCOUNT_ID else '❌ отсутствует'}")
        
        # Проверяем подключение к базе данных
        logger.info("🗄️ Проверка подключения к базе данных...")
        from src.db.database import get_db
        from src.db.models import User
        
        db = next(get_db())
        users_count = db.query(User).count()
        active_users_count = db.query(User).filter(User.is_active == True).count()
        telegram_users_count = db.query(User).filter(
            User.is_active == True, 
            User.telegram_chat_id.isnot(None)
        ).count()
        
        whatsapp_users_count = 0
        if settings.WHATSAPP_ENABLED:
            whatsapp_users_count = db.query(User).filter(
                User.is_active == True,
                User.whatsapp_phone.isnot(None),
                User.whatsapp_enabled == True
            ).count()
        
        logger.info(f"   - Всего пользователей: {users_count}")
        logger.info(f"   - Активных пользователей: {active_users_count}")
        logger.info(f"   - С Telegram: {telegram_users_count}")
        logger.info(f"   - С WhatsApp: {whatsapp_users_count}")
        
        # Запускаем диспетчер уведомлений
        logger.info("🔔 Запуск диспетчера уведомлений...")
        from src.services.notification_service import run_notification_dispatcher
        
        result = await run_notification_dispatcher()
        
        if result:
            logger.info("📊 Результаты работы диспетчера:")
            logger.info(f"   - Пользователей обработано: {result.get('users_processed', 0)}")
            logger.info(f"   - Уведомлений отправлено: {result.get('notifications_sent', 0)}")
            logger.info(f"   - Ошибок: {result.get('errors', 0)}")
            
            if result.get('notifications_sent', 0) > 0:
                logger.info("🎉 Уведомления успешно отправлены!")
            elif result.get('users_processed', 0) > 0:
                logger.info("ℹ️ Новых уведомлений для отправки не найдено")
            else:
                logger.info("⚠️ Пользователей для обработки не найдено")
        else:
            logger.warning("⚠️ Диспетчер вернул пустой результат")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования: {e}")
        return False

async def test_individual_services():
    """Тестирование отдельных сервисов"""
    logger.info("🔧 Тестирование отдельных сервисов...")
    
    try:
        # Тестируем Telegram сервис
        logger.info("📱 Тестирование Telegram сервиса...")
        try:
            from src.services.telegram_bot import TelegramBotService
            telegram_bot = TelegramBotService()
            logger.info("   ✅ Telegram сервис инициализирован")
        except Exception as e:
            logger.error(f"   ❌ Ошибка инициализации Telegram сервиса: {e}")
        
        # Тестируем WhatsApp сервис
        from src.core.config import settings
        if settings.WHATSAPP_ENABLED:
            logger.info("📱 Тестирование WhatsApp сервиса...")
            from src.services.whatsapp_service import WhatsAppService
            
            try:
                whatsapp_service = WhatsAppService()
                logger.info("   ✅ WhatsApp сервис инициализирован")
            except Exception as e:
                logger.error(f"   ❌ Ошибка инициализации WhatsApp сервиса: {e}")
        else:
            logger.info("📱 WhatsApp сервис отключен в конфигурации")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования сервисов: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    logger.info("🧪 Начинаем тестирование notification worker...")
    
    # Загружаем переменные окружения
    load_environment()
    
    # Тестируем отдельные сервисы
    services_ok = await test_individual_services()
    
    if not services_ok:
        logger.error("❌ Тестирование сервисов провалено")
        return
    
    # Тестируем notification worker
    worker_ok = await test_notification_worker()
    
    if worker_ok:
        logger.info("✅ Все тесты прошли успешно!")
        logger.info("🚀 Notification worker готов к работе")
    else:
        logger.error("❌ Тестирование notification worker провалено")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Тестирование прервано пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1) 