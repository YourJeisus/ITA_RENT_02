#!/usr/bin/env python3
"""
Тестовый запуск notification worker в режиме отладки
Запускает одну итерацию и останавливается
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

def setup_debug_environment():
    """Принудительно устанавливает режим отладки"""
    os.environ["DEBUG_NOTIFICATIONS"] = "true"
    
    # Загружаем переменные окружения из .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("✅ Переменные окружения загружены")
    except ImportError:
        logger.info("📝 python-dotenv не установлен, используем системные переменные")
    
    # Принудительно устанавливаем режим отладки
    os.environ["DEBUG_NOTIFICATIONS"] = "true"
    logger.info("🐛 Принудительно установлен режим отладки")

async def run_single_iteration():
    """Запуск одной итерации диспетчера уведомлений"""
    try:
        logger.info("🧪 Тестовый запуск notification worker в режиме отладки...")
        
        # Импортируем и запускаем диспетчер
        from src.services.notification_service import run_notification_dispatcher
        
        result = await run_notification_dispatcher()
        logger.info(f"✅ Тест завершен. Результат: {result}")
        
        # Выводим детальную статистику
        print("\n" + "="*60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("="*60)
        print(f"👥 Обработано пользователей: {result.get('users_processed', 0)}")
        print(f"📧 Отправлено уведомлений: {result.get('notifications_sent', 0)}")
        print(f"❌ Ошибок: {result.get('errors', 0)}")
        print("="*60)
        
        if result.get('notifications_sent', 0) > 0:
            print("✅ УСПЕХ: Уведомления отправлены!")
        elif result.get('users_processed', 0) > 0:
            print("⚠️  Пользователи обработаны, но уведомления не отправлены")
            print("   (возможно, нет новых объявлений или все уже отправлены)")
        else:
            print("❌ Пользователи не найдены или произошла ошибка")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в тестовом запуске: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Главная функция теста"""
    print("🧪 ТЕСТОВЫЙ ЗАПУСК NOTIFICATION WORKER")
    print("🐛 Режим отладки включен автоматически")
    print("⚡ Одна итерация и выход\n")
    
    # Настраиваем окружение
    setup_debug_environment()
    
    # Запускаем тест
    success = await run_single_iteration()
    
    if success:
        print("\n✅ Тест завершен успешно!")
        print("💡 Для постоянного запуска используйте: python run_notification_worker.py")
    else:
        print("\n❌ Тест завершен с ошибками!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Тест прерван пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в тесте: {e}")
        sys.exit(1) 