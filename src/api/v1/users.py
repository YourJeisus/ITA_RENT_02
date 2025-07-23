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
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        subscription_type=current_user.subscription_type,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
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