#!/usr/bin/env python3
"""
Скрипт для обновления пользователя до Premium статуса
"""
import sys
import os
import asyncio
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.db.database import SessionLocal
from src.crud.crud_user import CRUDUser

def update_user_to_premium(email: str):
    """Обновляет пользователя до Premium статуса"""
    db: Session = SessionLocal()
    
    try:
        # Находим пользователя
        user_crud = CRUDUser(User)
        user = user_crud.get_by_email(db, email=email)
        
        if not user:
            print(f"❌ Пользователь с email {email} не найден!")
            return False
        
        print(f"👤 Найден пользователь: {user.email}")
        print(f"📊 Текущий статус: {user.subscription_type}")
        
        # Обновляем до Premium
        user.subscription_type = "premium"
        db.commit()
        db.refresh(user)
        
        print(f"✅ Пользователь {user.email} обновлен до Premium!")
        print(f"🎉 Новый статус: {user.subscription_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении пользователя: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    # Импортируем модель здесь, чтобы избежать circular imports
    from src.db.models import User
    
    email = "Your@jeisus.ru"
    
    print(f"🔄 Обновление пользователя {email} до Premium статуса...")
    
    if update_user_to_premium(email):
        print("🎉 Успешно!")
    else:
        print("❌ Ошибка!")
        sys.exit(1) 