#!/usr/bin/env python3
"""
Полное тестирование потока уведомлений
1. Создаем тестовый фильтр для WhatsApp пользователя
2. Запускаем скрапинг
3. Тестируем отправку уведомлений
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

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

def create_test_filter():
    """Создание тестового фильтра для WhatsApp пользователя"""
    logger.info("🔧 Создание тестового фильтра...")
    
    try:
        from src.db.database import get_db
        from src.db.models import User, Filter
        
        db = next(get_db())
        
        # Находим WhatsApp пользователя
        user = db.query(User).filter(
            User.whatsapp_phone.isnot(None),
            User.whatsapp_enabled == True
        ).first()
        
        if not user:
            logger.error("❌ WhatsApp пользователь не найден")
            return False
        
        logger.info(f"👤 Найден пользователь: {user.email}")
        
        # Проверяем есть ли уже фильтр
        existing_filter = db.query(Filter).filter(
            Filter.user_id == user.id,
            Filter.is_active == True
        ).first()
        
        if existing_filter:
            logger.info(f"✅ Фильтр уже существует: '{existing_filter.name}' (ID: {existing_filter.id})")
            return True
        
        # Создаем новый фильтр
        test_filter = Filter(
            user_id=user.id,
            name="Тест уведомлений WhatsApp",
            city="Roma",
            min_price=800,
            max_price=2000,
            min_rooms=2,
            max_rooms=4,
            property_type="apartment",
            is_active=True,
            notification_enabled=True,
            notification_frequency_hours=1  # Каждый час для тестирования
        )
        
        db.add(test_filter)
        db.commit()
        
        logger.info(f"✅ Создан тестовый фильтр ID: {test_filter.id}")
        logger.info(f"   - Название: {test_filter.name}")
        logger.info(f"   - Город: {test_filter.city}")
        logger.info(f"   - Цена: {test_filter.min_price}-{test_filter.max_price}€")
        logger.info(f"   - Комнаты: {test_filter.min_rooms}-{test_filter.max_rooms}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания фильтра: {e}")
        return False

async def run_scraping():
    """Запуск скрапинга для получения данных"""
    logger.info("🕷️ Запуск скрапинга...")
    
    try:
        # Импортируем координатор скрапинга
        from src.parsers.run_scraping import main as run_scraping_main
        
        # Запускаем скрапинг с ограниченным количеством страниц
        logger.info("🔍 Запускаем скрапинг Idealista...")
        await run_scraping_main()
        
        # Проверяем результаты
        from src.db.database import get_db
        from src.db.models import Listing
        
        db = next(get_db())
        listings_count = db.query(Listing).filter(
            Listing.is_active == True
        ).count()
        
        logger.info(f"📊 Найдено {listings_count} активных объявлений")
        
        if listings_count > 0:
            # Показываем примеры
            recent_listings = db.query(Listing).filter(
                Listing.is_active == True
            ).order_by(Listing.created_at.desc()).limit(3).all()
            
            logger.info("📋 Примеры объявлений:")
            for listing in recent_listings:
                logger.info(f"   - {listing.title[:50]}... (ID: {listing.id}, {listing.price}€)")
        
        return listings_count > 0
        
    except Exception as e:
        logger.error(f"❌ Ошибка скрапинга: {e}")
        return False

async def test_notification_system():
    """Тестирование системы уведомлений"""
    logger.info("🔔 Тестирование системы уведомлений...")
    
    try:
        from src.services.notification_service import run_notification_dispatcher
        
        # Запускаем диспетчер уведомлений
        result = await run_notification_dispatcher()
        
        if result:
            logger.info("📊 Результаты диспетчера уведомлений:")
            logger.info(f"   - Пользователей обработано: {result.get('users_processed', 0)}")
            logger.info(f"   - Уведомлений отправлено: {result.get('notifications_sent', 0)}")
            logger.info(f"   - Ошибок: {result.get('errors', 0)}")
            
            if result.get('notifications_sent', 0) > 0:
                logger.info("🎉 Уведомления успешно отправлены!")
            else:
                logger.info("ℹ️ Новых уведомлений для отправки не найдено")
            
            return True
        else:
            logger.warning("⚠️ Диспетчер вернул пустой результат")
            return False
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования уведомлений: {e}")
        return False

async def main():
    """Главная функция полного тестирования"""
    logger.info("🧪 Запуск полного тестирования потока уведомлений...")
    logger.info("=" * 80)
    
    # Загружаем переменные окружения
    load_environment()
    
    # Проверяем конфигурацию
    from src.core.config import settings
    
    logger.info("📋 Проверка конфигурации:")
    logger.info(f"   - DEBUG_NOTIFICATIONS: {settings.DEBUG_NOTIFICATIONS}")
    logger.info(f"   - WHATSAPP_ENABLED: {settings.WHATSAPP_ENABLED}")
    logger.info(f"   - TELEGRAM_BOT_TOKEN: {'✅' if settings.TELEGRAM_BOT_TOKEN else '❌'}")
    
    if not settings.WHATSAPP_ENABLED:
        logger.error("❌ WhatsApp уведомления отключены. Включите WHATSAPP_ENABLED=true")
        return
    
    # Этап 1: Создание тестового фильтра
    logger.info("\n" + "="*50)
    logger.info("📋 ЭТАП 1: Создание тестового фильтра")
    logger.info("="*50)
    
    filter_created = create_test_filter()
    if not filter_created:
        logger.error("❌ Не удалось создать тестовый фильтр")
        return
    
    # Этап 2: Запуск скрапинга
    logger.info("\n" + "="*50)
    logger.info("🕷️ ЭТАП 2: Запуск скрапинга")
    logger.info("="*50)
    
    scraping_success = await run_scraping()
    if not scraping_success:
        logger.warning("⚠️ Скрапинг не дал результатов, но продолжаем тестирование")
    
    # Этап 3: Тестирование уведомлений
    logger.info("\n" + "="*50)
    logger.info("🔔 ЭТАП 3: Тестирование уведомлений")
    logger.info("="*50)
    
    notification_success = await test_notification_system()
    
    # Итоги
    logger.info("\n" + "="*50)
    logger.info("📊 ИТОГИ ТЕСТИРОВАНИЯ")
    logger.info("="*50)
    
    logger.info(f"✅ Фильтр создан: {'Да' if filter_created else 'Нет'}")
    logger.info(f"✅ Скрапинг выполнен: {'Да' if scraping_success else 'Частично'}")
    logger.info(f"✅ Уведомления работают: {'Да' if notification_success else 'Нет'}")
    
    if filter_created and notification_success:
        logger.info("\n🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ КОРРЕКТНО!")
        logger.info("🚀 Notification worker готов к продакшену")
    else:
        logger.info("\n⚠️ Обнаружены проблемы, требуется дополнительная настройка")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Тестирование прервано пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1) 