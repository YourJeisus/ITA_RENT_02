"""
API endpoints для Telegram интеграции
MVP версия для связывания аккаунтов и управления уведомлениями
"""
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.api.deps import get_current_active_user, get_db
from src.core.config import settings
from src.crud.crud_user import link_telegram, unlink_telegram
from src.db.models import User
from src.schemas.user import UserTelegramLink, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/link", response_model=UserResponse)
def link_telegram_account(
    link_data: UserTelegramLink,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Привязка Telegram аккаунта к пользователю
    """
    try:
        # Проверяем, не привязан ли уже этот chat_id к другому пользователю
        from src.crud.crud_user import get_by_telegram_chat_id
        existing_user = get_by_telegram_chat_id(db, telegram_chat_id=link_data.telegram_chat_id)
        
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Этот Telegram аккаунт уже привязан к другому пользователю"
            )
        
        # Привязываем Telegram к текущему пользователю
        updated_user = link_telegram(
            db=db,
            user_id=current_user.id,
            telegram_chat_id=link_data.telegram_chat_id,
            telegram_username=link_data.telegram_username
        )
        
        logger.info(f"Telegram привязан для пользователя {current_user.email}: {link_data.telegram_chat_id}")
        
        return updated_user
        
    except Exception as e:
        logger.error(f"Ошибка привязки Telegram: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при привязке Telegram аккаунта"
        )


@router.delete("/unlink", response_model=UserResponse)
def unlink_telegram_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Отвязка Telegram аккаунта от пользователя
    """
    try:
        if not current_user.telegram_chat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telegram аккаунт не привязан"
            )
        
        updated_user = unlink_telegram(db=db, user_id=current_user.id)
        
        logger.info(f"Telegram отвязан для пользователя {current_user.email}")
        
        return updated_user
        
    except Exception as e:
        logger.error(f"Ошибка отвязки Telegram: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отвязке Telegram аккаунта"
        )


@router.get("/status")
def get_telegram_status(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Получение статуса Telegram интеграции
    """
    return {
        "is_linked": bool(current_user.telegram_chat_id),
        "telegram_username": current_user.telegram_username,
        "chat_id": current_user.telegram_chat_id if current_user.telegram_chat_id else None
    }


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Webhook endpoint for Telegram Bot API
    Обрабатывает входящие обновления от Telegram (для production)
    """
    try:
        # Получаем JSON данные от Telegram
        update_data = await request.json()
        
        # В MVP версии мы используем polling, поэтому webhook пока только логируем
        logger.info(f"Получен webhook от Telegram: {update_data}")
        
        # В будущем здесь будет обработка через telegram_bot сервис
        # await telegram_bot.process_update(Update.de_json(update_data, bot.bot))
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Ошибка обработки Telegram webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обработки webhook"
        )


@router.post("/test-notification")
async def send_test_notification(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Отправка тестового уведомления пользователю
    Для проверки работы Telegram интеграции
    """
    if not current_user.telegram_chat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram аккаунт не привязан"
        )
    
    try:
        from src.services.telegram_bot import send_notification_to_user
        
        test_message = (
            "🧪 *Тестовое уведомление*\n\n"
            f"Привет, {current_user.first_name or 'друг'}!\n\n"
            "Это тестовое сообщение для проверки работы уведомлений.\n"
            "Если вы получили это сообщение, значит всё настроено правильно! ✅\n\n"
            "🔔 Теперь вы будете получать уведомления о новых объявлениях "
            "согласно вашим фильтрам поиска."
        )
        
        success = await send_notification_to_user(
            telegram_chat_id=current_user.telegram_chat_id,
            message=test_message
        )
        
        if success:
            return {"status": "sent", "message": "Тестовое уведомление отправлено"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить уведомление"
            )
            
    except Exception as e:
        logger.error(f"Ошибка отправки тестового уведомления: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отправке тестового уведомления"
        ) 