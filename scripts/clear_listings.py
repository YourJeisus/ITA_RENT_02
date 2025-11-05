"""
Скрипт для очистки объявлений из БД
"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Подключение к БД
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ita_rent.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def clear_listings():
    """Удаляет все объявления из БД"""
    session = SessionLocal()
    try:
        # Получаем текущее количество
        result = session.execute(text("SELECT COUNT(*) FROM listings"))
        total_before = result.scalar()
        
        print(f"\n📊 Объявлений в БД сейчас: {total_before}")
        
        if total_before == 0:
            print("✅ База данных уже пуста")
            return
        
        # Подтверждение
        confirm = input(f"\n⚠️  Вы уверены, что хотите удалить ВСЕ {total_before} объявлений? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Операция отменена")
            return
        
        # Удаляем все объявления
        print("\n🗑️  Удаление объявлений...")
        session.execute(text("DELETE FROM listings"))
        session.commit()
        
        # Проверяем результат
        result = session.execute(text("SELECT COUNT(*) FROM listings"))
        total_after = result.scalar()
        
        print(f"✅ Удалено объявлений: {total_before - total_after}")
        print(f"📊 Осталось объявлений: {total_after}")
        
        # Также очищаем таблицу sent_notifications
        print("\n🗑️  Очистка истории уведомлений...")
        session.execute(text("DELETE FROM sent_notifications"))
        session.commit()
        print("✅ История уведомлений очищена")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    clear_listings()

