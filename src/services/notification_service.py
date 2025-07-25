"""
Сервис системы уведомлений для ITA_RENT_BOT
MVP версия для отправки уведомлений о новых объявлениях через Telegram
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.database import get_db
from src.db.models import User, Filter, Listing, Notification
# from src.crud.crud_user import get_all_active_users  # Не используется в MVP
from src.crud.crud_filter import filter as crud_filter
from src.crud.crud_listing import search_listings
from src.services.telegram_bot import send_notification_to_user

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для управления уведомлениями пользователей"""
    
    def __init__(self):
        self.db = None
    
    def get_db(self) -> Session:
        """Получение сессии базы данных"""
        if not self.db:
            self.db = next(get_db())
        return self.db
    
    def should_send_notification(self, user: User, filter_obj: Filter) -> bool:
        """
        Проверка, нужно ли отправлять уведомление для этого фильтра
        """
        if not filter_obj.is_active:
            return False
        
        if not user.telegram_chat_id:
            return False
        
        # Определяем частоту уведомлений в зависимости от подписки
        if user.subscription_type == "premium":
            notification_frequency = timedelta(minutes=30)
        else:
            notification_frequency = timedelta(hours=24)
        
        # Проверяем время последнего уведомления для этого фильтра
        if filter_obj.last_notification_sent:
            now = datetime.now(timezone.utc)
            last_sent = filter_obj.last_notification_sent
            
            # Приводим к единому формату для сравнения
            if last_sent.tzinfo is None and now.tzinfo is not None:
                now = now.replace(tzinfo=None)
            elif last_sent.tzinfo is not None and now.tzinfo is None:
                last_sent = last_sent.replace(tzinfo=None)
            
            time_since_last = now - last_sent
            if time_since_last < notification_frequency:
                return False
        
        return True
    
    def get_new_listings_for_filter(self, filter_obj: Filter, since_hours: int = 24) -> List[Listing]:
        """
        Получение новых объявлений по фильтру за последние N часов
        """
        try:
            # Время, после которого объявления считаются новыми
            since_time = datetime.now(timezone.utc) - timedelta(hours=since_hours)
            
            # Создаем параметры поиска из фильтра
            search_params = {
                "city": filter_obj.city,
                "min_price": filter_obj.min_price,
                "max_price": filter_obj.max_price,
                "property_type": filter_obj.property_type,
                "min_rooms": filter_obj.min_rooms,
                "max_rooms": filter_obj.max_rooms,
                "min_area": filter_obj.min_area,
                "max_area": filter_obj.max_area,
                "page": 1,
                "limit": 10  # Максимум 10 новых объявлений за раз
            }
            
            # Удаляем None значения
            search_params = {k: v for k, v in search_params.items() if v is not None}
            
            # Упрощенный поиск для уведомлений - не используем пагинацию
            search_params_no_page = {k: v for k, v in search_params.items() if k not in ['page', 'limit']}
            
            # Ищем объявления напрямую через CRUD
            from src.crud.crud_listing import listing as crud_listing
            all_listings = crud_listing.search(self.get_db(), limit=50, **search_params_no_page)
            
            # Фильтруем только новые объявления
            new_listings = []
            for listing in all_listings:
                if listing.created_at:
                    # Приводим даты к единому формату для сравнения
                    listing_time = listing.created_at
                    compare_time = since_time
                    
                    # Если одна дата с timezone, а другая без - приводим к naive
                    if listing_time.tzinfo is None and compare_time.tzinfo is not None:
                        compare_time = compare_time.replace(tzinfo=None)
                    elif listing_time.tzinfo is not None and compare_time.tzinfo is None:
                        listing_time = listing_time.replace(tzinfo=None)
                    
                    if listing_time >= compare_time:
                        new_listings.append(listing)
            
            logger.info(f"Найдено {len(new_listings)} новых объявлений для фильтра {filter_obj.id}")
            return new_listings
            
        except Exception as e:
            logger.error(f"Ошибка поиска новых объявлений для фильтра {filter_obj.id}: {e}")
            return []
    
    def format_notification_message(self, listings: List[Listing], filter_obj: Filter) -> str:
        """
        Форматирование сообщения с уведомлением о новых объявлениях
        """
        if not listings:
            return ""
        
        # Заголовок сообщения
        message = f"🏠 *Новые объявления по фильтру '{filter_obj.name}'*\n\n"
        
        # Добавляем информацию о каждом объявлении
        for i, listing in enumerate(listings[:5], 1):  # Максимум 5 объявлений
            # Базовая информация
            price_text = f"{listing.price}€/мес" if listing.price else "Цена не указана"
            
            # Дополнительная информация
            details = []
            if listing.rooms:
                details.append(f"🚪 {listing.rooms} комн.")
            if listing.area:
                details.append(f"📐 {listing.area} м²")
            if listing.property_type:
                details.append(f"🏠 {listing.property_type}")
            
            details_text = " • ".join(details) if details else ""
            
            message += f"*{i}. {listing.title[:50]}{'...' if len(listing.title) > 50 else ''}*\n"
            message += f"📍 {listing.address}\n"
            message += f"💰 {price_text}\n"
            
            if details_text:
                message += f"{details_text}\n"
            
            message += f"🔗 [Посмотреть объявление]({listing.url})\n\n"
        
        # Если объявлений больше 5, добавляем информацию об этом
        if len(listings) > 5:
            message += f"...и еще {len(listings) - 5} объявлений!\n\n"
        
        # Информация о фильтре
        message += f"🔍 *Фильтр:* {filter_obj.name}\n"
        if filter_obj.city:
            message += f"📍 Город: {filter_obj.city}\n"
        
        # Управление фильтром
        message += f"\n/pause_{filter_obj.id} - приостановить этот фильтр\n"
        message += "/filters - все ваши фильтры"
        
        return message
    
    async def send_notification_for_filter(self, user: User, filter_obj: Filter, listings: List[Listing]) -> bool:
        """
        Отправка уведомления пользователю о новых объявлениях
        """
        try:
            # Форматируем сообщение
            message = self.format_notification_message(listings, filter_obj)
            
            if not message:
                return False
            
            # Отправляем уведомление
            success = await send_notification_to_user(
                telegram_chat_id=user.telegram_chat_id,
                message=message
            )
            
            if success:
                # Обновляем время последнего уведомления
                filter_obj.last_notification_sent = datetime.now(timezone.utc).replace(tzinfo=None)
                self.get_db().add(filter_obj)
                self.get_db().commit()
                
                # Создаем запись уведомления (опционально для статистики)
                try:
                    # Берем первое объявление из списка для записи
                    first_listing_id = listings[0].id if listings else None
                    
                    notification = Notification(
                        user_id=user.id,
                        filter_id=filter_obj.id,
                        listing_id=first_listing_id,  # Берем первое объявление
                        notification_type="new_listing",
                        status="sent",
                        sent_at=datetime.now(timezone.utc).replace(tzinfo=None),
                        message=f"Отправлено {len(listings)} объявлений"
                    )
                    self.get_db().add(notification)
                    self.get_db().commit()
                except Exception as e:
                    logger.warning(f"Не удалось сохранить запись уведомления: {e}")
                
                logger.info(f"Уведомление отправлено пользователю {user.email} для фильтра {filter_obj.id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")
            return False
    
    async def process_user_notifications(self, user: User) -> int:
        """
        Обработка уведомлений для одного пользователя
        Возвращает количество отправленных уведомлений
        """
        if not user.telegram_chat_id:
            return 0
        
        try:
            # Получаем активные фильтры пользователя
            filters = crud_filter.get_by_user(self.get_db(), user_id=user.id)
            active_filters = [f for f in filters if f.is_active]
            
            if not active_filters:
                return 0
            
            sent_count = 0
            
            for filter_obj in active_filters:
                # Проверяем, нужно ли отправлять уведомление
                if not self.should_send_notification(user, filter_obj):
                    continue
                
                # Получаем новые объявления
                new_listings = self.get_new_listings_for_filter(filter_obj)
                
                if not new_listings:
                    continue
                
                # Отправляем уведомление
                success = await self.send_notification_for_filter(user, filter_obj, new_listings)
                
                if success:
                    sent_count += 1
                
                # Небольшая пауза между уведомлениями
                await asyncio.sleep(1)
            
            return sent_count
            
        except Exception as e:
            logger.error(f"Ошибка обработки уведомлений для пользователя {user.email}: {e}")
            return 0
    
    async def process_all_notifications(self) -> Dict[str, int]:
        """
        Обработка уведомлений для всех пользователей
        Основная функция диспетчера уведомлений
        """
        logger.info("🔔 Запуск диспетчера уведомлений...")
        
        stats = {
            "users_processed": 0,
            "notifications_sent": 0,
            "errors": 0
        }
        
        try:
            # Получаем всех активных пользователей с привязанными Telegram аккаунтами
            users = self.get_db().query(User).filter(
                User.is_active == True,
                User.telegram_chat_id.isnot(None)
            ).all()
            
            logger.info(f"Найдено {len(users)} пользователей с привязанными Telegram аккаунтами")
            
            for user in users:
                try:
                    sent_count = await self.process_user_notifications(user)
                    stats["users_processed"] += 1
                    stats["notifications_sent"] += sent_count
                    
                    if sent_count > 0:
                        logger.info(f"Отправлено {sent_count} уведомлений пользователю {user.email}")
                    
                    # Пауза между пользователями для предотвращения rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки пользователя {user.email}: {e}")
                    stats["errors"] += 1
            
            logger.info(
                f"✅ Диспетчер уведомлений завершен. "
                f"Обработано пользователей: {stats['users_processed']}, "
                f"Отправлено уведомлений: {stats['notifications_sent']}, "
                f"Ошибок: {stats['errors']}"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Критическая ошибка диспетчера уведомлений: {e}")
            stats["errors"] += 1
            return stats


# Глобальный экземпляр сервиса
notification_service = NotificationService()


async def run_notification_dispatcher():
    """
    Функция для запуска диспетчера уведомлений
    Используется в cron задачах или отдельном процессе
    """
    return await notification_service.process_all_notifications()


if __name__ == "__main__":
    """Запуск диспетчера для тестирования"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def main():
        stats = await run_notification_dispatcher()
        print(f"Результат: {stats}")
    
    asyncio.run(main()) 