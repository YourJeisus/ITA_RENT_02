"""
Зависимости для API endpoints
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.core.security import verify_token
from src.crud.crud_user import get_user_by_email
from src.db.database import get_db
from src.db.models import User

# Схема авторизации
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Получение текущего пользователя по JWT токену
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Проверяем токен
    email = verify_token(credentials.credentials)
    if email is None:
        raise credentials_exception
    
    # Получаем пользователя из БД
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    # Проверяем активность пользователя
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Получение текущего активного пользователя
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Получение текущего пользователя (опционально)
    Используется для endpoints, которые работают как с авторизованными,
    так и с неавторизованными пользователями
    """
    if credentials is None:
        return None
    
    email = verify_token(credentials.credentials)
    if email is None:
        return None
    
    user = get_user_by_email(db, email=email)
    if user is None or not user.is_active:
        return None
    
    return user 