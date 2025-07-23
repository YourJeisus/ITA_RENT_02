"""
API endpoints для авторизации
"""
import logging
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.api.deps import get_current_active_user, get_db
from src.core.config import settings
from src.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    validate_password_strength
)
from src.crud.crud_user import create_user, get_user_by_email, authenticate_user
from src.db.models import User
from src.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    Token
)
from src.schemas.user import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Регистрация нового пользователя
    """
    # Проверяем, что пользователь с таким email не существует
    existing_user = get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Валидируем силу пароля
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Создаем нового пользователя
    user_create_data = {
        "email": user_data.email,
        "hashed_password": get_password_hash(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "is_active": True
    }
    
    try:
        user = create_user(db, **user_create_data)
        logger.info(f"New user registered: {user.email}")
        
        return RegisterResponse(
            message="Пользователь успешно зарегистрирован",
            user={
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active
            }
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании пользователя"
        )


@router.post("/login", response_model=LoginResponse)
def login(
    user_data: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Вход в систему по email и паролю
    """
    # Аутентификация пользователя
    user = authenticate_user(db, email=user_data.email, password=user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем активность пользователя
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт деактивирован"
        )
    
    # Создаем JWT токен
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.email}")
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "subscription_type": user.subscription_type,
            "is_active": user.is_active
        }
    )


@router.post("/login/form", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Вход в систему через OAuth2 форму (для совместимости)
    """
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт деактивирован"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получение информации о текущем пользователе
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        subscription_type=current_user.subscription_type,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Выход из системы
    Примечание: При использовании JWT токенов выход происходит на клиенте
    путем удаления токена. Этот endpoint для совместимости.
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Успешный выход из системы"}


@router.post("/test-token", response_model=UserResponse)
def test_token(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Тестирование JWT токена
    """
    return current_user 