"""
API эндпоинты для управления WhatsApp уведомлениями
"""
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.api.deps import get_current_active_user, get_db
from src.db.models import User
from src.crud.crud_user import link_whatsapp, unlink_whatsapp, toggle_whatsapp_notifications
from src.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["whatsapp"])


# Схемы запросов и ответов
class WhatsAppLinkRequest(BaseModel):
    phone_number: str = Field(..., description="Номер телефона в международном формате", example="+393401234567")
    instance_id: Optional[str] = Field(None, description="ID инстанса WhatsApp (опционально)")

class WhatsAppStatusResponse(BaseModel):
    enabled: bool
    phone_number: Optional[str]
    instance_id: Optional[str]
    verified: bool = False

class WhatsAppToggleRequest(BaseModel):
    enabled: bool = Field(..., description="Включить/выключить WhatsApp уведомления")

class WhatsAppTestRequest(BaseModel):
    phone_number: str = Field(..., description="Номер телефона для тестирования")


@router.get("/status", response_model=WhatsAppStatusResponse)
async def get_whatsapp_status(
    current_user: User = Depends(get_current_active_user)
) -> WhatsAppStatusResponse:
    """
    Получить статус WhatsApp уведомлений для текущего пользователя
    """
    return WhatsAppStatusResponse(
        enabled=current_user.whatsapp_enabled or False,
        phone_number=current_user.whatsapp_phone,
        instance_id=current_user.whatsapp_instance_id,
        verified=bool(current_user.whatsapp_phone)
    )


@router.post("/link")
async def link_whatsapp_account(
    request: WhatsAppLinkRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Привязать WhatsApp номер к аккаунту пользователя
    """
    if not settings.WHATSAPP_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp уведомления отключены на сервере"
        )
    
    try:
        # Очищаем и форматируем номер телефона
        clean_phone = ''.join(filter(str.isdigit, request.phone_number))
        
        # Проверяем формат номера
        if len(clean_phone) < 10 or len(clean_phone) > 15:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат номера телефона"
            )
        
        # Добавляем код страны если его нет
        if not clean_phone.startswith(('7', '39', '1', '44', '49', '33')):
            clean_phone = '39' + clean_phone  # Италия по умолчанию
        
        # Проверяем, не занят ли этот номер
        from src.crud.crud_user import get_by_whatsapp_phone
        existing_user = get_by_whatsapp_phone(db, whatsapp_phone=clean_phone)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Этот номер уже привязан к другому аккаунту"
            )
        
        # Привязываем номер
        updated_user = link_whatsapp(
            db=db,
            user_id=current_user.id,
            whatsapp_phone=clean_phone,
            whatsapp_instance_id=request.instance_id,
            enabled=True
        )
        
        logger.info(f"WhatsApp номер {clean_phone[:3]}***{clean_phone[-3:]} привязан к пользователю {current_user.email}")
        
        return {
            "success": True,
            "message": "WhatsApp номер успешно привязан",
            "phone_number": clean_phone,
            "enabled": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка привязки WhatsApp для пользователя {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при привязке WhatsApp номера"
        )


@router.delete("/unlink")
async def unlink_whatsapp_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Отвязать WhatsApp номер от аккаунта пользователя
    """
    try:
        updated_user = unlink_whatsapp(db=db, user_id=current_user.id)
        
        logger.info(f"WhatsApp номер отвязан от пользователя {current_user.email}")
        
        return {
            "success": True,
            "message": "WhatsApp номер успешно отвязан"
        }
        
    except Exception as e:
        logger.error(f"Ошибка отвязки WhatsApp для пользователя {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отвязке WhatsApp номера"
        )


@router.post("/toggle")
async def toggle_whatsapp_notifications(
    request: WhatsAppToggleRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Включить/выключить WhatsApp уведомления
    """
    if not current_user.whatsapp_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сначала привяжите WhatsApp номер"
        )
    
    try:
        updated_user = toggle_whatsapp_notifications(
            db=db,
            user_id=current_user.id,
            enabled=request.enabled
        )
        
        action = "включены" if request.enabled else "выключены"
        logger.info(f"WhatsApp уведомления {action} для пользователя {current_user.email}")
        
        return {
            "success": True,
            "message": f"WhatsApp уведомления {action}",
            "enabled": request.enabled
        }
        
    except Exception as e:
        logger.error(f"Ошибка изменения статуса WhatsApp для пользователя {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при изменении настроек WhatsApp"
        )


@router.post("/test")
async def test_whatsapp_notification(
    request: WhatsAppTestRequest,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Отправить тестовое WhatsApp уведомление
    """
    if not settings.WHATSAPP_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp уведомления отключены на сервере"
        )
    
    try:
        from src.services.whatsapp_service import send_whatsapp_notification
        
        # Форматируем номер
        clean_phone = ''.join(filter(str.isdigit, request.phone_number))
        
        # Создаем тестовое сообщение
        test_message = (
            f"🏠 *Тест WhatsApp уведомлений ITA_RENT_BOT*\n\n"
            f"Привет, {current_user.first_name or 'друг'}!\n\n"
            f"Это тестовое сообщение для проверки WhatsApp уведомлений.\n"
            f"Если вы получили это сообщение, значит все настроено правильно! ✅\n\n"
            f"Теперь вы будете получать уведомления о новых объявлениях по вашим фильтрам.\n\n"
            f"💡 _Настройте фильтры в личном кабинете для получения релевантных уведомлений._"
        )
        
        # Отправляем тестовое сообщение
        success = await send_whatsapp_notification(clean_phone, test_message)
        
        if success:
            logger.info(f"Тестовое WhatsApp сообщение отправлено пользователю {current_user.email}")
            return {
                "success": True,
                "message": "Тестовое сообщение отправлено успешно",
                "phone_number": clean_phone
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось отправить тестовое сообщение"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка отправки тестового WhatsApp сообщения для {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отправке тестового сообщения"
        )


@router.get("/settings")
async def get_whatsapp_settings() -> Dict[str, Any]:
    """
    Получить настройки WhatsApp для клиента
    """
    return {
        "enabled": settings.WHATSAPP_ENABLED,
        "features": {
            "text_messages": True,
            "template_messages": settings.WHATSAPP_ENABLED,
            "rich_media": False  # Пока не поддерживаем
        },
        "limits": {
            "max_listings_per_message": 3,
            "message_length_limit": 4096
        }
    } 