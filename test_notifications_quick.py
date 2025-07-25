#!/usr/bin/env python3
"""
🧪 БЫСТРЫЙ ТЕСТ УВЕДОМЛЕНИЙ

Запускает notification service одноразово для быстрого тестирования
"""
import sys
import os
import asyncio
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

# Импорты
from src.services.notification_service import NotificationService
from src.crud.crud_user import user as crud_user
import sqlalchemy
from sqlalchemy.orm import sessionmaker

# Подключение к онлайн БД Railway
DATABASE_URL = 'postgresql://postgres:TAkDvHCdDTxVzutQsNNfJgbcSttzrgzN@caboose.proxy.rlwy.net:15179/railway'
engine = sqlalchemy.create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def test_notifications_now(user_email: str = "your@jeisus.ru"):
    """
    Тестирует уведомления прямо сейчас для указанного пользователя
    """
    print("🧪 БЫСТРЫЙ ТЕСТ УВЕДОМЛЕНИЙ")
    print("=" * 60)
    print(f"👤 Пользователь: {user_email}")
    print("=" * 60)
    
    # Инициализируем сервис уведомлений
    notification_service = NotificationService()
    
    try:
        # Получаем пользователя
        db = SessionLocal()
        user = crud_user.get_by_email(db, email=user_email)
        
        if not user:
            print(f"❌ Пользователь {user_email} не найден!")
            return False
            
        print(f"✅ Найден пользователь: {user.email} ({user.subscription_type})")
        print(f"📱 Telegram chat_id: {user.telegram_chat_id}")
        
        if not user.telegram_chat_id:
            print(f"❌ У пользователя нет привязанного Telegram!")
            return False
        
        # Включаем режим отладки принудительно
        print(f"\n🐛 ВКЛЮЧАЕМ РЕЖИМ ОТЛАДКИ для теста...")
        os.environ["DEBUG_NOTIFICATIONS"] = "true"
        
        # Перезагружаем конфигурацию
        from src.core.config import settings
        from importlib import reload
        import src.core.config
        reload(src.core.config)
        
        print(f"🔧 DEBUG_NOTIFICATIONS = {settings.DEBUG_NOTIFICATIONS}")
        
        # Запускаем обработку уведомлений для этого пользователя
        print(f"\n🔔 Запускаем обработку уведомлений...")
        sent_count = await notification_service.process_user_notifications(user)
        
        print(f"\n📊 РЕЗУЛЬТАТ:")
        print(f"   📱 Отправлено уведомлений: {sent_count}")
        
        if sent_count > 0:
            print(f"   ✅ Уведомления отправлены в Telegram!")
            print(f"   📱 Проверьте чат с ботом")
        else:
            print(f"   ⚠️  Уведомления не отправлены")
            print(f"   🔍 Возможные причины:")
            print(f"      - Нет новых объявлений")
            print(f"      - Все объявления уже отправлены")
            print(f"      - Проблемы с фильтром")
        
        db.close()
        return sent_count > 0
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Быстрый тест уведомлений")
    parser.add_argument("--email", type=str, default="your@jeisus.ru", 
                       help="Email пользователя для тестирования")
    
    args = parser.parse_args()
    
    try:
        result = asyncio.run(test_notifications_now(args.email))
        if result:
            print(f"\n🎉 ТЕСТ УСПЕШЕН! Проверьте Telegram бота.")
        else:
            print(f"\n⚠️  ТЕСТ НЕ ПРОШЕЛ. Проверьте логи выше.")
        
        sys.exit(0 if result else 1)
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Тест прерван пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 