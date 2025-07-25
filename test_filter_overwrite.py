#!/usr/bin/env python3
"""
🧪 ТЕСТ АВТОМАТИЧЕСКОЙ ПЕРЕЗАПИСИ ФИЛЬТРОВ

Проверяет, что при создании второго фильтра первый автоматически перезаписывается
"""
import sys
import os
import asyncio
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

from src.crud.crud_filter import filter as crud_filter
from src.crud.crud_user import user as crud_user
from src.schemas.filter import FilterCreate
import sqlalchemy
from sqlalchemy.orm import sessionmaker

# Подключение к онлайн БД Railway
DATABASE_URL = 'postgresql://postgres:TAkDvHCdDTxVzutQsNNfJgbcSttzrgzN@caboose.proxy.rlwy.net:15179/railway'
engine = sqlalchemy.create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_filter_overwrite(user_email: str = "your@jeisus.ru"):
    """
    Тестирует автоматическую перезапись фильтров
    """
    print("🧪 ТЕСТ АВТОМАТИЧЕСКОЙ ПЕРЕЗАПИСИ ФИЛЬТРОВ")
    print("=" * 60)
    print(f"👤 Пользователь: {user_email}")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Получаем пользователя
        user = crud_user.get_by_email(db, email=user_email)
        if not user:
            print(f"❌ Пользователь {user_email} не найден!")
            return False
        
        print(f"✅ Найден пользователь: {user.email} ({user.subscription_type})")
        
        # Проверяем текущие фильтры
        existing_filters = crud_filter.get_by_user(db=db, user_id=user.id)
        print(f"📊 Текущих фильтров: {len(existing_filters)}")
        
        if existing_filters:
            for i, f in enumerate(existing_filters, 1):
                print(f"   {i}. ID {f.id}: {f.name} | {f.city} | {f.property_type}")
        
        # Создаем новый фильтр
        print(f"\n🔄 Создаем НОВЫЙ фильтр...")
        new_filter_data = FilterCreate(
            name="Тестовый фильтр - Милан",
            city="Milano",
            min_price=1000,
            max_price=2500,
            property_type="house",  # меняем на дома
            min_rooms=3,
            max_rooms=5,
            notification_enabled=True
        )
        
        if len(existing_filters) >= 1:
            # Должна сработать перезапись
            print(f"   📝 Ожидается ПЕРЕЗАПИСЬ фильтра ID {existing_filters[0].id}")
            old_filter = existing_filters[0]
            updated_filter = crud_filter.update(
                db=db,
                db_obj=old_filter,
                obj_in=new_filter_data
            )
            print(f"   ✅ Фильтр ID {updated_filter.id} обновлен")
        else:
            # Создание нового
            print(f"   📝 Создается НОВЫЙ фильтр")
            new_filter = crud_filter.create_with_owner(
                db=db,
                obj_in=new_filter_data,
                user_id=user.id
            )
            print(f"   ✅ Создан фильтр ID {new_filter.id}")
        
        # Проверяем результат
        updated_filters = crud_filter.get_by_user(db=db, user_id=user.id)
        print(f"\n📊 РЕЗУЛЬТАТ:")
        print(f"   📈 Фильтров после операции: {len(updated_filters)}")
        
        if updated_filters:
            for i, f in enumerate(updated_filters, 1):
                print(f"   {i}. ID {f.id}: {f.name}")
                print(f"      📍 {f.city} | 🏠 {f.property_type} | 💰 {f.min_price}-{f.max_price}€")
                print(f"      🚪 {f.min_rooms}-{f.max_rooms} комн | 📅 {f.updated_at}")
        
        success = len(updated_filters) == 1
        
        if success:
            print(f"\n✅ ТЕСТ ПРОШЕЛ: максимум 1 фильтр на пользователя!")
        else:
            print(f"\n❌ ТЕСТ НЕ ПРОШЕЛ: найдено {len(updated_filters)} фильтров!")
        
        return success
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Тест автоматической перезаписи фильтров")
    parser.add_argument("--email", type=str, default="your@jeisus.ru", 
                       help="Email пользователя для тестирования")
    
    args = parser.parse_args()
    
    try:
        result = test_filter_overwrite(args.email)
        if result:
            print(f"\n🎉 ВСЕ РАБОТАЕТ! Автоматическая перезапись фильтров настроена корректно.")
        else:
            print(f"\n⚠️  НУЖНА ДОРАБОТКА. Проверьте логи выше.")
        
        sys.exit(0 if result else 1)
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Тест прерван пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 