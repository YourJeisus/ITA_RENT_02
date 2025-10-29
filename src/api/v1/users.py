"""
API endpoints для управления пользователями
"""
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_active_user, get_db
from src.crud.crud_user import user as crud_user
from src.db.models import User
from src.schemas.user import UserResponse, UserUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получение профиля текущего пользователя
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        notification_email=current_user.notification_email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        subscription_type=current_user.subscription_type,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        telegram_chat_id=current_user.telegram_chat_id,
        telegram_username=current_user.telegram_username,
        email_notifications_enabled=current_user.email_notifications_enabled,
        telegram_notifications_enabled=current_user.telegram_notifications_enabled
    )


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Обновление профиля текущего пользователя
    """
    try:
        updated_user = crud_user.update(db, db_obj=current_user, obj_in=user_update)
        logger.info(f"User profile updated: {updated_user.email}")
        
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            subscription_type=updated_user.subscription_type,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении профиля"
        )


@router.get("/subscription")
def get_user_subscription(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получение информации о подписке пользователя
    """
    return {
        "subscription_type": current_user.subscription_type,
        "subscription_expires_at": current_user.subscription_expires_at,
        "is_active": current_user.is_active,
        "limits": get_subscription_limits(current_user.subscription_type)
    }


def get_subscription_limits(subscription_type: str) -> dict:
    """
    Получение лимитов для типа подписки
    """
    limits = {
        "free": {
            "max_filters": 1,
            "max_notifications_per_day": 10,
            "notification_interval_hours": 24
        },
        "premium": {
            "max_filters": 10,
            "max_notifications_per_day": 100,
            "notification_interval_hours": 1
        }
    }
    return limits.get(subscription_type, limits["free"])


@router.get("/notifications/settings")
def get_notification_settings(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Получение настроек уведомлений пользователя
    """
    return {
        "email_notifications_enabled": current_user.email_notifications_enabled,
        "telegram_notifications_enabled": current_user.telegram_notifications_enabled,
        "has_telegram": bool(current_user.telegram_chat_id),
        "has_whatsapp": bool(current_user.whatsapp_phone),
        "whatsapp_enabled": current_user.whatsapp_enabled,
        "email_verified_at": current_user.email_verified_at,
        "email_last_sent_at": current_user.email_last_sent_at
    }


@router.put("/notifications/settings")
def update_notification_settings(
    settings_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Обновление настроек уведомлений пользователя
    """
    try:
        # Обновляем только переданные поля
        if "email_notifications_enabled" in settings_update:
            current_user.email_notifications_enabled = settings_update["email_notifications_enabled"]
        
        if "telegram_notifications_enabled" in settings_update:
            current_user.telegram_notifications_enabled = settings_update["telegram_notifications_enabled"]
        
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Notification settings updated for user: {current_user.email}")
        
        return {
            "success": True,
            "email_notifications_enabled": current_user.email_notifications_enabled,
            "telegram_notifications_enabled": current_user.telegram_notifications_enabled
        }
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении настроек уведомлений"
        )


@router.post("/notifications/test-email")
async def send_test_email_notification(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Отправка тестового email уведомления
    """
    # Используем notification_email если он установлен, иначе основной email
    notification_email = current_user.notification_email or current_user.email
    
    if not notification_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email не указан для рассылки"
        )
    
    if not current_user.email_notifications_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уведомления отключены"
        )
    
    try:
        from src.services.email_service import email_service
        
        if not email_service.is_enabled():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Email сервис не настроен"
            )
        
        success = await email_service.send_test_email(notification_email)
        
        if success:
            return {"status": "sent", "message": "Тестовое email уведомление отправлено"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить email"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отправке тестового email"
        )


# ========== EMAIL CHANGE ==========

import secrets
import string
from datetime import datetime, timedelta

# Глобальное хранилище кодов (в production использовать Redis)
_email_change_codes = {}

def generate_verification_code(length: int = 6) -> str:
    """Генерация 6-значного кода верификации"""
    digits = string.digits
    return ''.join(secrets.choice(digits) for _ in range(length))


@router.post("/email/change-request")
async def request_email_change(
    new_notification_email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Запрос на смену email для рассылки уведомлений
    Это отдельный email от учетной записи!
    """
    if not new_notification_email or "@" not in new_notification_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный email адрес"
        )
    
    if new_notification_email == current_user.notification_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Это уже текущий email для рассылки"
        )
    
    try:
        from src.services.email_service import email_service
        
        if not email_service.is_enabled():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Email сервис не настроен"
            )
        
        # Генерируем код верификации
        code = generate_verification_code()
        
        # Сохраняем код в глобальное хранилище
        code_key = f"{current_user.id}:notification_email:{new_notification_email}"
        _email_change_codes[code_key] = {
            'code': code,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(minutes=15)
        }
        
        # Отправляем код на новый email
        subject = "🔐 ITA Rent: Код подтверждения смены email для рассылки"
        body = f"""
Привет!

Вы запросили изменение email для получения уведомлений на сервисе ITA Rent.

Ваш код подтверждения: {code}

Код действителен 15 минут.

Если это были не вы, игнорируйте это письмо.

С уважением,
Команда ITA Rent
        """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 500px; margin: 0 auto;">
                <h2>🔐 Код подтверждения смены email для рассылки</h2>
                <p>Вы запросили изменение email для получения уведомлений на сервисе ITA Rent.</p>
                
                <div style="background: #f0f0f0; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                    <p style="font-size: 24px; font-weight: bold; letter-spacing: 4px;">{code}</p>
                </div>
                
                <p>Код действителен <strong>15 минут</strong>.</p>
                <p>Если это были не вы, игнорируйте это письмо.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">
                    С уважением,<br>
                    <strong>Команда ITA Rent</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        success = await email_service.send_email(new_notification_email, subject, body, html_body)
        
        if success:
            return {
                "status": "code_sent",
                "message": f"Код верификации отправлен на {new_notification_email}",
                "new_email": new_notification_email
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить код верификации"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting notification email change: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при запросе смены email"
        )


@router.post("/email/change-confirm")
def confirm_email_change(
    new_notification_email: str,
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Подтверждение смены email для рассылки по коду верификации
    """
    if not code or len(code) != 6 or not code.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный код верификации"
        )
    
    try:
        # Проверяем код
        code_key = f"{current_user.id}:notification_email:{new_notification_email}"
        
        if code_key not in _email_change_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Запрос смены email не найден. Начните заново."
            )
        
        request_data = _email_change_codes[code_key]
        
        # Проверяем истечение времени
        if datetime.now() > request_data['expires_at']:
            del _email_change_codes[code_key]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Код верификации истек. Запросите новый код."
            )
        
        # Проверяем код
        if request_data['code'] != code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный код верификации"
            )
        
        # Обновляем email для рассылки (НЕ меняем email для логина!)
        old_notification_email = current_user.notification_email
        current_user.notification_email = new_notification_email
        current_user.email_verified_at = datetime.now()
        
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        # Удаляем использованный запрос
        del _email_change_codes[code_key]
        
        logger.info(f"Notification email changed for user {current_user.id}: {old_notification_email} -> {new_notification_email}")
        
        return {
            "status": "success",
            "message": "Email для рассылки успешно изменен",
            "new_email": new_notification_email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming notification email change: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при подтверждении смены email"
        )


# ========== TELEGRAM LINKING ==========

@router.post("/telegram/link")
def link_telegram_account(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Привязка аккаунта к Telegram через код из бота
    
    Пользователь:
    1. Пишет боту /start
    2. Получает код связки
    3. Вводит код здесь
    4. Аккаунт привязывается
    """
    if not code or len(code) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный код"
        )
    
    try:
        # Получаем данные о коде из бота (нужно передать через глобальное хранилище или Redis)
        # Для MVP используем простой механизм - бот хранит коды в памяти
        # В production использовать Redis
        
        from src.services.telegram_linking_service import telegram_linking_service
        
        linking_data = telegram_linking_service.get_code(code)
        
        if not linking_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Код не найден или истек"
            )
        
        # Обновляем пользователя с Telegram данными
        current_user.telegram_chat_id = str(linking_data['chat_id'])
        current_user.telegram_username = linking_data['telegram_username']
        current_user.telegram_notifications_enabled = True  # Включаем по умолчанию
        
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        # Удаляем использованный код
        telegram_linking_service.remove_code(code)
        
        logger.info(f"✅ Telegram привязан к аккаунту {current_user.email} (ID: {linking_data['chat_id']})")
        
        return {
            "status": "success",
            "message": "Telegram успешно привязан к аккаунту",
            "telegram_username": current_user.telegram_username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking telegram: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при привязке Telegram"
        )


@router.post("/telegram/unlink")
def unlink_telegram_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Отвязка Telegram от аккаунта
    """
    try:
        current_user.telegram_chat_id = None
        current_user.telegram_username = None
        
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"✅ Telegram отвязан от аккаунта {current_user.email}")
        
        return {
            "status": "success",
            "message": "Telegram успешно отвязан от аккаунта"
        }
        
    except Exception as e:
        logger.error(f"Error unlinking telegram: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отвязке Telegram"
        ) 