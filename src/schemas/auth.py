"""
Pydantic схемы для авторизации
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Схема данных токена"""
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Схема запроса на вход"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Схема ответа при входе"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class RegisterRequest(BaseModel):
    """Схема запроса на регистрацию"""
    email: EmailStr
    password: str
    first_name: str
    last_name: Optional[str] = None


class RegisterResponse(BaseModel):
    """Схема ответа при регистрации"""
    message: str
    user: dict


class PasswordReset(BaseModel):
    """Схема сброса пароля"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Схема подтверждения сброса пароля"""
    token: str
    new_password: str


class ChangePassword(BaseModel):
    """Схема смены пароля"""
    current_password: str
    new_password: str 