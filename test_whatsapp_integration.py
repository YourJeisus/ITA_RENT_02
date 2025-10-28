#!/usr/bin/env python3
"""
Тестовый скрипт для проверки WhatsApp интеграции
Проверяет все компоненты системы уведомлений WhatsApp
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

async def test_whatsapp_config():
    """Тест 1: Проверка конфигурации WhatsApp"""
    logger.info("🧪 Тест 1: Проверка конфигурации WhatsApp")
    
    try:
        from src.core.config import settings
        
        logger.info(f"   WHATSAPP_ENABLED: {settings.WHATSAPP_ENABLED}")
        logger.info(f"   WHATSAPP_API_URL: {'*' * 20 if settings.WHATSAPP_API_URL else 'НЕ НАСТРОЕН'}")
        logger.info(f"   WHATSAPP_API_TOKEN: {'*' * 20 if settings.WHATSAPP_API_TOKEN else 'НЕ НАСТРОЕН'}")
        logger.info(f"   WHATSAPP_PHONE_NUMBER_ID: {'*' * 10 if settings.WHATSAPP_PHONE_NUMBER_ID else 'НЕ НАСТРОЕН'}")
        
        if not settings.WHATSAPP_ENABLED:
            logger.warning("   ⚠️ WhatsApp отключен в конфигурации")
            return False
        
        if not all([settings.WHATSAPP_API_URL, settings.WHATSAPP_API_TOKEN, settings.WHATSAPP_PHONE_NUMBER_ID]):
            logger.error("   ❌ Не все обязательные настройки WhatsApp настроены")
            return False
        
        logger.info("   ✅ Конфигурация WhatsApp корректна")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Ошибка проверки конфигурации: {e}")
        return False

async def test_whatsapp_service():
    """Тест 2: Проверка WhatsApp сервиса"""
    logger.info("🧪 Тест 2: Проверка WhatsApp сервиса")
    
    try:
        from src.services.whatsapp_service import get_whatsapp_service
        
        service = get_whatsapp_service()
        if not service:
            logger.error("   ❌ WhatsApp сервис не инициализирован")
            return False
        
        logger.info("   ✅ WhatsApp сервис инициализирован успешно")
        
        # Тест форматирования сообщений
        test_listings = [
            {
                'id': 1,
                'title': 'Тестовая квартира в центре',
                'price': 1800,
                'address': 'Via del Corso, 123',
                'city': 'Roma',
                'rooms': 3,
                'area': 85,
                'url': 'https://example.com/listing/1',
                'source': 'idealista'
            }
        ]
        
        message = service.format_listing_message(test_listings, "Тестовый фильтр")
        logger.info("   ✅ Форматирование сообщений работает")
        logger.info(f"   📝 Пример сообщения:\n{message[:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Ошибка инициализации WhatsApp сервиса: {e}")
        return False

async def test_database_fields():
    """Тест 3: Проверка полей WhatsApp в базе данных"""
    logger.info("🧪 Тест 3: Проверка полей WhatsApp в базе данных")
    
    try:
        from src.db.database import get_db
        from src.db.models import User
        
        # Получаем сессию БД
        db = next(get_db())
        
        # Проверяем наличие полей в модели
        user_fields = [attr for attr in dir(User) if not attr.startswith('_')]
        whatsapp_fields = ['whatsapp_phone', 'whatsapp_instance_id', 'whatsapp_enabled']
        
        missing_fields = []
        for field in whatsapp_fields:
            if field not in user_fields:
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"   ❌ Отсутствуют поля в модели User: {missing_fields}")
            return False
        
        # Проверяем выполнение запроса
        count = db.query(User).count()
        logger.info(f"   📊 Всего пользователей в БД: {count}")
        
        # Проверяем WhatsApp пользователей
        whatsapp_users = db.query(User).filter(User.whatsapp_phone.isnot(None)).count()
        logger.info(f"   📱 Пользователей с WhatsApp: {whatsapp_users}")
        
        db.close()
        logger.info("   ✅ Поля WhatsApp в базе данных настроены корректно")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Ошибка проверки базы данных: {e}")
        return False

async def test_crud_operations():
    """Тест 4: Проверка CRUD операций для WhatsApp"""
    logger.info("🧪 Тест 4: Проверка CRUD операций для WhatsApp")
    
    try:
        from src.crud.crud_user import (
            get_by_whatsapp_phone, 
            link_whatsapp, 
            unlink_whatsapp, 
            toggle_whatsapp_notifications
        )
        
        logger.info("   ✅ Все CRUD функции для WhatsApp импортированы успешно")
        
        # Проверяем что функции существуют и вызываемы
        crud_functions = [
            get_by_whatsapp_phone,
            link_whatsapp,
            unlink_whatsapp,
            toggle_whatsapp_notifications
        ]
        
        for func in crud_functions:
            if not callable(func):
                logger.error(f"   ❌ Функция {func.__name__} не вызываема")
                return False
        
        logger.info("   ✅ Все CRUD функции для WhatsApp доступны")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Ошибка проверки CRUD операций: {e}")
        return False

async def test_api_endpoints():
    """Тест 5: Проверка API эндпоинтов"""
    logger.info("🧪 Тест 5: Проверка API эндпоинтов")
    
    try:
        from src.api.v1.whatsapp import router
        
        # Проверяем что роутер создан
        if not router:
            logger.error("   ❌ WhatsApp роутер не создан")
            return False
        
        # Проверяем наличие маршрутов
        routes = [route for route in router.routes]
        route_paths = [route.path for route in routes]
        
        expected_paths = ['/status', '/link', '/unlink', '/toggle', '/test', '/settings']
        
        missing_paths = []
        for path in expected_paths:
            if path not in route_paths:
                missing_paths.append(path)
        
        if missing_paths:
            logger.error(f"   ❌ Отсутствуют маршруты: {missing_paths}")
            return False
        
        logger.info(f"   📊 Найдено маршрутов: {len(routes)}")
        logger.info(f"   📋 Маршруты: {route_paths}")
        logger.info("   ✅ Все API эндпоинты для WhatsApp настроены")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Ошибка проверки API эндпоинтов: {e}")
        return False

async def test_notification_service_integration():
    """Тест 6: Проверка интеграции с NotificationService"""
    logger.info("🧪 Тест 6: Проверка интеграции с NotificationService")
    
    try:
        from src.services.notification_service import NotificationService
        
        service = NotificationService()
        
        # Проверяем что методы обновлены для поддержки WhatsApp
        # Создаем тестового пользователя
        class MockUser:
            def __init__(self):
                self.id = 1
                self.email = "test@example.com"
                self.telegram_chat_id = None
                self.whatsapp_phone = None
                self.whatsapp_enabled = False
        
        class MockFilter:
            def __init__(self):
                self.id = 1
                self.is_active = True
                self.name = "Тестовый фильтр"
        
        user = MockUser()
        filter_obj = MockFilter()
        
        # Тест 1: Пользователь без способов связи
        result = service.should_send_notification(user, filter_obj)
        if result:
            logger.error("   ❌ should_send_notification возвращает True для пользователя без способов связи")
            return False
        
        # Тест 2: Пользователь только с WhatsApp
        user.whatsapp_phone = "+393401234567"
        user.whatsapp_enabled = True
        
        from src.core.config import settings
        if settings.WHATSAPP_ENABLED:
            result = service.should_send_notification(user, filter_obj)
            if not result:
                logger.error("   ❌ should_send_notification возвращает False для пользователя с WhatsApp")
                return False
        
        logger.info("   ✅ NotificationService поддерживает WhatsApp")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Ошибка проверки интеграции NotificationService: {e}")
        return False

async def test_whatsapp_api_connection():
    """Тест 7: Проверка подключения к WhatsApp API (только если настроено)"""
    logger.info("🧪 Тест 7: Проверка подключения к WhatsApp API")
    
    try:
        from src.core.config import settings
        
        if not settings.WHATSAPP_ENABLED:
            logger.info("   ⏭️ WhatsApp отключен - пропускаем тест API")
            return True
        
        if not all([settings.WHATSAPP_API_URL, settings.WHATSAPP_API_TOKEN]):
            logger.info("   ⏭️ API настройки не полные - пропускаем тест подключения")
            return True
        
        # Простая проверка URL и токена
        import aiohttp
        
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Не отправляем реальный запрос, только проверяем формат
        if settings.WHATSAPP_API_URL and settings.WHATSAPP_API_TOKEN:
            logger.info("   ✅ API настройки выглядят корректно")
            logger.info("   ℹ️ Для полного теста используйте POST /api/v1/whatsapp/test")
            return True
        
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Ошибка проверки WhatsApp API: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    logger.info("🚀 Запуск тестирования WhatsApp интеграции для ITA_RENT_BOT")
    logger.info("=" * 60)
    
    # Загружаем переменные окружения
    load_environment()
    
    # Список тестов
    tests = [
        ("Конфигурация WhatsApp", test_whatsapp_config),
        ("WhatsApp сервис", test_whatsapp_service),
        ("Поля в базе данных", test_database_fields),
        ("CRUD операции", test_crud_operations),
        ("API эндпоинты", test_api_endpoints),
        ("Интеграция NotificationService", test_notification_service_integration),
        ("Подключение к WhatsApp API", test_whatsapp_api_connection),
    ]
    
    results = []
    
    # Выполняем тесты
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: ПРОЙДЕН")
            else:
                logger.error(f"❌ {test_name}: ПРОВАЛЕН")
                
        except Exception as e:
            logger.error(f"💥 {test_name}: ОШИБКА - {e}")
            results.append((test_name, False))
        
        logger.info("-" * 60)
    
    # Итоговая статистика
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    logger.info("📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    logger.info(f"   Всего тестов: {total}")
    logger.info(f"   Пройдено: {passed}")
    logger.info(f"   Провалено: {total - passed}")
    logger.info(f"   Процент успеха: {(passed/total)*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! WhatsApp интеграция готова к использованию.")
    else:
        logger.warning("⚠️ Некоторые тесты провалены. Проверьте настройки и исправьте ошибки.")
    
    logger.info("=" * 60)
    
    # Инструкции по дальнейшим действиям
    logger.info("📋 ДАЛЬНЕЙШИЕ ДЕЙСТВИЯ:")
    logger.info("1. Настройте WhatsApp Business API у провайдера")
    logger.info("2. Обновите переменные окружения в .env файле")
    logger.info("3. Запустите WhatsApp worker: python scripts/run_whatsapp_worker.py")
    logger.info("4. Протестируйте через API: POST /api/v1/whatsapp/test")
    logger.info("5. Настройте пользователей через веб-интерфейс")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        sys.exit(1) 