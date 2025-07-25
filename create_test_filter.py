#!/usr/bin/env python3
"""
Создание тестового фильтра для отладки уведомлений
"""
import sys
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

from src.db.database import get_db
from src.db.models import Filter
from datetime import datetime

def create_test_filter():
    """Создает тестовый фильтр для пользователя ID=1"""
    try:
        db = next(get_db())
        
        # Создаем тестовый фильтр
        test_filter = Filter(
            user_id=1,
            name="Тестовый фильтр - Рим",
            city="Roma",
            min_price=800,
            max_price=2000,
            min_rooms=2,
            max_rooms=4,
            property_type="apartment",
            is_active=True,
            notification_enabled=True,
            notification_frequency_hours=1,  # 1 час для тестирования
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(test_filter)
        db.commit()
        db.refresh(test_filter)
        
        print(f"✅ Создан тестовый фильтр:")
        print(f"   ID: {test_filter.id}")
        print(f"   Название: {test_filter.name}")
        print(f"   Город: {test_filter.city}")
        print(f"   Цена: {test_filter.min_price}-{test_filter.max_price} EUR")
        print(f"   Комнаты: {test_filter.min_rooms}-{test_filter.max_rooms}")
        print(f"   Активен: {test_filter.is_active}")
        print(f"   Уведомления: {test_filter.notification_enabled}")
        
        return test_filter.id
        
    except Exception as e:
        print(f"❌ Ошибка создания фильтра: {e}")
        return None
    finally:
        db.close()

def delete_test_filters():
    """Удаляет все тестовые фильтры"""
    try:
        db = next(get_db())
        
        # Удаляем все фильтры пользователя ID=1
        deleted_count = db.query(Filter).filter(Filter.user_id == 1).delete()
        db.commit()
        
        print(f"✅ Удалено {deleted_count} тестовых фильтров")
        
    except Exception as e:
        print(f"❌ Ошибка удаления фильтров: {e}")
    finally:
        db.close()

def list_filters():
    """Показывает все фильтры пользователя"""
    try:
        db = next(get_db())
        
        filters = db.query(Filter).filter(Filter.user_id == 1).all()
        
        if not filters:
            print("📋 У пользователя нет фильтров")
            return
        
        print(f"📋 Найдено {len(filters)} фильтров:")
        for f in filters:
            status = "✅ активен" if f.is_active else "❌ неактивен"
            notifications = "🔔 вкл" if f.notification_enabled else "🔕 выкл"
            print(f"   {f.id}: '{f.name}' ({f.city}, {f.min_price}-{f.max_price} EUR) - {status}, {notifications}")
        
    except Exception as e:
        print(f"❌ Ошибка получения фильтров: {e}")
    finally:
        db.close()

def main():
    """Главная функция"""
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        
        if action == "create":
            filter_id = create_test_filter()
            if filter_id:
                print(f"\n💡 Теперь запустите тест: python test_notification_worker_debug.py")
                
        elif action == "delete":
            delete_test_filters()
            
        elif action == "list":
            list_filters()
            
        else:
            print(f"❌ Неизвестное действие: {action}")
            print("Доступные действия: create, delete, list")
    else:
        print("🔧 Управление тестовыми фильтрами")
        print("\nДоступные команды:")
        print("  python create_test_filter.py create  - создать тестовый фильтр")
        print("  python create_test_filter.py list    - показать все фильтры")
        print("  python create_test_filter.py delete  - удалить все фильтры")

if __name__ == "__main__":
    main() 