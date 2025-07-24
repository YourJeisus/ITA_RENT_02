#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы всей системы Telegram бота
MVP версия для этапа 6
"""
import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Добавляем корневую папку в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_telegram_bot_service():
    """Тест инициализации Telegram бота"""
    print("\n🤖 Тестирование Telegram бота...")
    
    try:
        from src.services.telegram_bot import TelegramBotService
        
        # Проверяем наличие токена
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            print("❌ TELEGRAM_BOT_TOKEN не настроен")
            return False
        
        # Создаем бота
        bot = TelegramBotService()
        await bot.initialize()
        
        print("✅ Telegram бот инициализирован успешно")
        print(f"📱 Токен: {token[:10]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации бота: {e}")
        return False


async def test_notification_service():
    """Тест сервиса уведомлений"""
    print("\n🔔 Тестирование сервиса уведомлений...")
    
    try:
        from src.services.notification_service import NotificationService
        
        # Создаем сервис
        notification_service = NotificationService()
        
        # Проверяем подключение к базе данных
        db = notification_service.get_db()
        
        print("✅ Сервис уведомлений инициализирован")
        print("✅ Подключение к базе данных работает")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка сервиса уведомлений: {e}")
        return False


async def test_database_models():
    """Тест моделей базы данных"""
    print("\n💾 Тестирование моделей базы данных...")
    
    try:
        from src.db.database import get_db
        from src.db.models import User, Filter, Listing, Notification
        from src.crud.crud_user import get_user_by_email
        
        # Тестируем подключение к БД
        db = next(get_db())
        
        # Пробуем выполнить простой запрос
        users_count = db.query(User).count()
        filters_count = db.query(Filter).count()
        listings_count = db.query(Listing).count()
        
        print(f"✅ База данных подключена")
        print(f"📊 Пользователей: {users_count}")
        print(f"🔍 Фильтров: {filters_count}")
        print(f"🏠 Объявлений: {listings_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False


async def test_api_endpoints():
    """Тест API endpoints"""
    print("\n🌐 Тестирование API endpoints...")
    
    try:
        import httpx
        
        # Проверяем основной API
        api_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            # Тест health endpoint
            response = await client.get(f"{api_url}/health")
            if response.status_code == 200:
                print("✅ Health endpoint работает")
            else:
                print("⚠️ Health endpoint недоступен (API не запущен?)")
                return False
            
            # Тест Telegram endpoints (без авторизации)
            response = await client.get(f"{api_url}/api/v1/telegram/webhook")
            print(f"📱 Telegram webhook endpoint: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        print("💡 Убедитесь, что API сервер запущен: python -m uvicorn src.main:app")
        return False


def test_environment_variables():
    """Тест переменных окружения"""
    print("\n⚙️ Проверка переменных окружения...")
    
    required_vars = {
        "DATABASE_URL": "Подключение к базе данных",
        "SECRET_KEY": "Секретный ключ для JWT",
        "TELEGRAM_BOT_TOKEN": "Токен Telegram бота"
    }
    
    optional_vars = {
        "SCRAPERAPI_KEY": "Ключ для парсинга",
        "REDIS_URL": "Кеширование (опционально)",
        "STRIPE_SECRET_KEY": "Платежи (опционально)"
    }
    
    all_good = True
    
    print("📋 Обязательные переменные:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✅ {var}: {masked_value} ({description})")
        else:
            print(f"  ❌ {var}: НЕ НАСТРОЕН ({description})")
            all_good = False
    
    print("\n📋 Опциональные переменные:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✅ {var}: {masked_value} ({description})")
        else:
            print(f"  ⚪ {var}: не настроен ({description})")
    
    return all_good


def test_file_structure():
    """Тест структуры файлов"""
    print("\n📁 Проверка структуры файлов...")
    
    required_files = [
        "src/services/telegram_bot.py",
        "src/services/notification_service.py",
        "src/api/v1/telegram.py",
        "run_telegram_bot.py",
        "run_notification_dispatcher.py",
        "cron_notifications.py"
    ]
    
    all_good = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - НЕ НАЙДЕН")
            all_good = False
    
    return all_good


async def run_full_test():
    """Запуск полного теста всей системы"""
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ TELEGRAM БОТА")
    print("=" * 50)
    
    tests = [
        ("Переменные окружения", test_environment_variables),
        ("Структура файлов", test_file_structure),
        ("Модели базы данных", test_database_models),
        ("Telegram бот", test_telegram_bot_service),
        ("Сервис уведомлений", test_notification_service),
        ("API endpoints", test_api_endpoints)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 30}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            results[test_name] = result
            
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
            results[test_name] = False
    
    # Результаты
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ ПРОШЕЛ" if result else "❌ НЕ ПРОШЕЛ"
        print(f"  {status:12} {test_name}")
    
    print(f"\n📈 Общий результат: {passed}/{total} тестов прошло")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ! Система готова к использованию.")
        print("\n🚀 Следующие шаги:")
        print("1. Запустите API: python -m uvicorn src.main:app")
        print("2. Запустите бота: python run_telegram_bot.py")
        print("3. Протестируйте в Telegram: /start")
        return 0
    else:
        print("⚠️ ЕСТЬ ПРОБЛЕМЫ. Исправьте ошибки перед использованием.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_full_test())
    sys.exit(exit_code) 