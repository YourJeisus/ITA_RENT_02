#!/usr/bin/env python3
"""
Запуск WhatsApp notification worker в бесконечном цикле
Аналогично Telegram worker, но для WhatsApp уведомлений
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
    """Проверка обязательных переменных окружения для WhatsApp"""
    required_vars = {
        "DATABASE_URL": "URL базы данных",
        "SECRET_KEY": "Секретный ключ"
    }
    
    # WhatsApp переменные (опциональные, но если включен WHATSAPP_ENABLED)
    whatsapp_vars = {
        "WHATSAPP_API_URL": "URL WhatsApp API",
        "WHATSAPP_API_TOKEN": "Токен WhatsApp API",
        "WHATSAPP_PHONE_NUMBER_ID": "ID номера телефона WhatsApp"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    # Проверяем WhatsApp настройки если включен
    whatsapp_enabled = os.getenv("WHATSAPP_ENABLED", "false").lower() == "true"
    
    if whatsapp_enabled:
        for var, description in whatsapp_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.error("❌ Отсутствуют обязательные переменные окружения:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        return False
    
    if not whatsapp_enabled:
        logger.warning("⚠️ WhatsApp уведомления отключены (WHATSAPP_ENABLED=false)")
        logger.info("   Worker будет работать в режиме мониторинга без отправки уведомлений")
    
    logger.info("✅ Все обязательные переменные окружения установлены")
    return True

async def run_whatsapp_notification_dispatcher():
    """Запуск диспетчера WhatsApp уведомлений"""
    try:
        from src.core.config import settings
        
        if not settings.WHATSAPP_ENABLED:
            logger.info("📱 WhatsApp уведомления отключены - пропускаем обработку")
            return {
                'users_processed': 0,
                'notifications_sent': 0,
                'errors': 0,
                'status': 'disabled'
            }
        
        logger.info("📱 Запуск диспетчера WhatsApp уведомлений...")
        
        # Импортируем и запускаем диспетчер уведомлений
        # Используем тот же NotificationService, но он уже поддерживает WhatsApp
        from src.services.notification_service import run_notification_dispatcher
        
        result = await run_notification_dispatcher()
        
        if result:
            # Подробная статистика
            users_processed = result.get('users_processed', 0)
            notifications_sent = result.get('notifications_sent', 0)
            errors = result.get('errors', 0)
            
            logger.info(f"✅ WhatsApp диспетчер завершен успешно:")
            logger.info(f"   👥 Пользователей обработано: {users_processed}")
            logger.info(f"   📱 WhatsApp уведомлений отправлено: {notifications_sent}")
            logger.info(f"   ❌ Ошибок: {errors}")
            
            if notifications_sent == 0 and users_processed > 0:
                logger.info("   ℹ️ Новых WhatsApp уведомлений для отправки не найдено")
            elif notifications_sent > 0:
                logger.info(f"   🎉 Успешно отправлено {notifications_sent} WhatsApp уведомлений!")
        else:
            logger.warning("⚠️ WhatsApp диспетчер вернул пустой результат")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в диспетчере WhatsApp уведомлений: {e}")
        return False

async def main():
    """Главный цикл WhatsApp notification worker"""
    logger.info("📱 Запуск WhatsApp Notification Worker...")
    
    # Загружаем переменные окружения
    load_environment()
    
    # Проверяем переменные окружения
    if not check_required_env_vars():
        sys.exit(1)
    
    # Проверяем режим отладки  
    from src.core.config import settings
    debug_mode = settings.DEBUG_NOTIFICATIONS
    whatsapp_enabled = settings.WHATSAPP_ENABLED
    
    # Получаем интервал из переменной окружения
    if debug_mode:
        # В режиме отладки используем переменную или 300 секунд (5 минут) по умолчанию
        default_interval = 300
        interval_seconds = int(os.getenv("WHATSAPP_NOTIFICATION_INTERVAL_SECONDS", str(default_interval)))
        logger.info("🐛 РЕЖИМ ОТЛАДКИ ВКЛЮЧЕН!")
        logger.info("   - Временные ограничения отключены")
        logger.info("   - WhatsApp уведомления при каждом запуске")
        logger.info(f"   - Интервал: {interval_seconds} секунд")
    else:
        # Обычный режим - интервал между запусками (30 минут = 1800 секунд)
        interval_seconds = int(os.getenv("WHATSAPP_NOTIFICATION_INTERVAL_SECONDS", "1800"))
    
    logger.info(f"⏰ Интервал WhatsApp уведомлений: {interval_seconds} секунд ({interval_seconds//60} минут)")
    
    if not whatsapp_enabled:
        logger.info("📱 WhatsApp отключен - работаем в режиме мониторинга")
    
    # Бесконечный цикл
    iteration = 0
    while True:
        iteration += 1
        
        if debug_mode:
            logger.info(f"🐛 [DEBUG] Итерация #{iteration} - запуск WhatsApp диспетчера уведомлений")
        else:
            logger.info(f"🔄 Итерация #{iteration} - запуск WhatsApp диспетчера уведомлений")
        
        try:
            # Запускаем диспетчер WhatsApp уведомлений
            success = await run_whatsapp_notification_dispatcher()
            
            if success:
                if debug_mode:
                    logger.info(f"🐛 [DEBUG] WhatsApp итерация #{iteration} завершена успешно")
                else:
                    logger.info(f"✅ WhatsApp итерация #{iteration} завершена успешно")
            else:
                logger.warning(f"⚠️ WhatsApp итерация #{iteration} завершена с ошибками")
                
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в WhatsApp итерации #{iteration}: {e}")
        
        # Ожидание до следующего запуска
        if debug_mode:
            logger.info(f"🐛 [DEBUG] Ожидание {interval_seconds} секунд до следующего WhatsApp запуска...")
        else:
            logger.info(f"⏳ Ожидание {interval_seconds} секунд до следующего WhatsApp запуска...")
        
        await asyncio.sleep(interval_seconds)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки WhatsApp worker")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка WhatsApp worker: {e}")
        sys.exit(1) 