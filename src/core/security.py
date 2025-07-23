"""
Модуль безопасности для работы с паролями и JWT токенами
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings

logger = logging.getLogger(__name__)

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Создание JWT токена доступа
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Проверка JWT токена и извлечение subject (email)
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError as e:
        logger.warning(f"JWT token verification failed: {e}")
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хеширование пароля
    """
    return pwd_context.hash(password)


def generate_password_reset_token(email: str) -> str:
    """
    Генерация токена для сброса пароля
    """
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, 
        settings.SECRET_KEY, 
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Проверка токена сброса пароля
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token["sub"]
    except JWTError:
        return None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Валидация силы пароля
    Возвращает (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Пароль должен содержать минимум 8 символов"
    
    if not any(c.isupper() for c in password):
        return False, "Пароль должен содержать минимум одну заглавную букву"
    
    if not any(c.islower() for c in password):
        return False, "Пароль должен содержать минимум одну строчную букву"
    
    if not any(c.isdigit() for c in password):
        return False, "Пароль должен содержать минимум одну цифру"
    
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in password):
        return False, f"Пароль должен содержать минимум один специальный символ: {special_chars}"
    
    return True, ""


def create_telegram_auth_token(telegram_data: dict) -> str:
    """
    Создание токена для авторизации через Telegram
    """
    expire = datetime.utcnow() + timedelta(minutes=10)  # Короткий срок жизни
    to_encode = {
        "exp": expire,
        "telegram_data": telegram_data,
        "type": "telegram_auth"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_telegram_auth_token(token: str) -> Optional[dict]:
    """
    Проверка токена авторизации через Telegram
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "telegram_auth":
            return None
        return payload.get("telegram_data")
    except JWTError:
        return None 