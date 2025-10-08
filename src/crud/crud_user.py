"""
CRUD операции для пользователей
"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.crud.base import CRUDBase
from src.db.models import User
from src.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD операции для пользователей"""
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_by_telegram_chat_id(self, db: Session, *, telegram_chat_id: str) -> Optional[User]:
        """Получить пользователя по Telegram chat ID"""
        try:
            return db.query(User).filter(User.telegram_chat_id == telegram_chat_id).first()
        except Exception as e:
            logger.error(f"Ошибка при поиске пользователя по telegram_chat_id {telegram_chat_id}: {e}")
            return None
    
    def get_by_whatsapp_phone(self, db: Session, *, whatsapp_phone: str) -> Optional[User]:
        """Получить пользователя по WhatsApp номеру телефона"""
        try:
            return db.query(User).filter(User.whatsapp_phone == whatsapp_phone).first()
        except Exception as e:
            logger.error(f"Ошибка при поиске пользователя по whatsapp_phone {whatsapp_phone}: {e}")
            return None
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Создать пользователя с хешированным паролем"""
        from src.core.security import get_password_hash
        
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_active=True,
            subscription_type="free"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        from src.core.security import verify_password
        
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """Проверить активность пользователя"""
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """Проверить права суперпользователя"""
        return user.is_superuser
    
    def get_active_users(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить активных пользователей"""
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def get_premium_users(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить пользователей с Premium подпиской"""
        return db.query(User).filter(
            and_(
                User.is_active == True,
                User.subscription_type == "premium"
            )
        ).offset(skip).limit(limit).all()
    
    def link_telegram(self, db: Session, *, user_id: int, telegram_chat_id: str, telegram_username: str = None) -> User:
        """Привязать Telegram к аккаунту пользователя"""
        user = self.get(db, id=user_id)
        if user:
            user.telegram_chat_id = telegram_chat_id
            if telegram_username:
                user.telegram_username = telegram_username
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    def unlink_telegram(self, db: Session, *, user_id: int) -> User:
        """Отвязать Telegram от аккаунта пользователя"""
        user = self.get(db, id=user_id)
        if user:
            user.telegram_chat_id = None
            user.telegram_username = None
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    def link_whatsapp(self, db: Session, *, user_id: int, whatsapp_phone: str, 
                      whatsapp_instance_id: str = None, enabled: bool = True) -> User:
        """Привязать WhatsApp к аккаунту пользователя"""
        user = self.get(db, id=user_id)
        if user:
            user.whatsapp_phone = whatsapp_phone
            user.whatsapp_instance_id = whatsapp_instance_id
            user.whatsapp_enabled = enabled
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    def unlink_whatsapp(self, db: Session, *, user_id: int) -> User:
        """Отвязать WhatsApp от аккаунта пользователя"""
        user = self.get(db, id=user_id)
        if user:
            user.whatsapp_phone = None
            user.whatsapp_instance_id = None
            user.whatsapp_enabled = False
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    def toggle_whatsapp(self, db: Session, *, user_id: int, enabled: bool) -> User:
        """Включить/выключить WhatsApp уведомления"""
        user = self.get(db, id=user_id)
        if user:
            user.whatsapp_enabled = enabled
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    def update_subscription(self, db: Session, *, user_id: int, subscription_type: str, expires_at=None) -> User:
        """Обновить подписку пользователя"""
        user = self.get(db, id=user_id)
        if user:
            user.subscription_type = subscription_type
            user.subscription_expires_at = expires_at
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    def update_last_login(self, db: Session, *, user_id: int) -> User:
        """Обновить время последнего входа"""
        from datetime import datetime
        
        user = self.get(db, id=user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            db.add(user)
            db.commit()
            db.refresh(user)
        return user


# Создаем экземпляр CRUD для использования
user = CRUDUser(User)

# Функции-обертки для совместимости с API
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получить пользователя по email"""
    return user.get_by_email(db, email=email)

def get_by_telegram_chat_id(db: Session, telegram_chat_id: str) -> Optional[User]:
    """Получить пользователя по Telegram chat ID"""
    return user.get_by_telegram_chat_id(db, telegram_chat_id=telegram_chat_id)

def link_telegram(db: Session, user_id: int, telegram_chat_id: str, telegram_username: str = None) -> User:
    """Привязать Telegram к аккаунту пользователя"""
    return user.link_telegram(db, user_id=user_id, telegram_chat_id=telegram_chat_id, telegram_username=telegram_username)

def unlink_telegram(db: Session, user_id: int) -> User:
    """Отвязать Telegram от аккаунта пользователя"""
    return user.unlink_telegram(db, user_id=user_id)

def create_user(db: Session, **kwargs) -> User:
    """Создать пользователя"""
    db_obj = User(**kwargs)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Аутентификация пользователя"""
    return user.authenticate(db, email=email, password=password)

# WhatsApp функции-обертки
def get_by_whatsapp_phone(db: Session, whatsapp_phone: str) -> Optional[User]:
    """Получить пользователя по WhatsApp номеру"""
    return user.get_by_whatsapp_phone(db, whatsapp_phone=whatsapp_phone)

def get_user_by_whatsapp_phone(db: Session, whatsapp_phone: str) -> Optional[User]:
    """Получить пользователя по WhatsApp номеру (альтернативное название)"""
    return user.get_by_whatsapp_phone(db, whatsapp_phone=whatsapp_phone)

def link_whatsapp(db: Session, user_id: int, whatsapp_phone: str, 
                  whatsapp_instance_id: str = None, enabled: bool = True) -> User:
    """Привязать WhatsApp к аккаунту пользователя"""
    return user.link_whatsapp(db, user_id=user_id, whatsapp_phone=whatsapp_phone, 
                              whatsapp_instance_id=whatsapp_instance_id, enabled=enabled)

def unlink_whatsapp(db: Session, user_id: int) -> User:
    """Отвязать WhatsApp от аккаунта пользователя"""
    return user.unlink_whatsapp(db, user_id=user_id)

def toggle_whatsapp_notifications(db: Session, user_id: int, enabled: bool) -> User:
    """Включить/выключить WhatsApp уведомления"""
    return user.toggle_whatsapp(db, user_id=user_id, enabled=enabled) 