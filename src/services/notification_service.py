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
from src.db.models import User, Filter, Listing, Notification, SentNotification
# from src.crud.crud_user import get_all_active_users  # Не используется в MVP
from src.crud.crud_filter import filter as crud_filter
from src.crud.crud_listing import search_listings
from src.services.telegram_bot import send_notification_to_user

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для управления уведомлениями пользователей"""
    
    def __init__(self):
        self.db = None
        self._ensure_sent_notifications_table()
    
    def get_db(self) -> Session:
        """Получение сессии базы данных"""
        if not self.db:
            self.db = next(get_db())
        return self.db
    
    def _ensure_sent_notifications_table(self):
        """Создает таблицу sent_notifications если её нет"""
        try:
            from src.db.database import engine, Base
            # Создаем все таблицы (включая SentNotification)
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Таблица sent_notifications проверена/создана")
        except Exception as e:
            logger.warning(f"Ошибка создания таблицы sent_notifications: {e}")
    
    def should_send_notification(self, user: User, filter_obj: Filter) -> bool:
        """
        Проверка, нужно ли отправлять уведомление для этого фильтра
        """
        if not filter_obj.is_active:
            logger.info(f"❌ Фильтр {filter_obj.id} неактивен")
            return False
        
        if not user.telegram_chat_id:
            logger.info(f"❌ У пользователя {user.email} нет telegram_chat_id")
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
                logger.info(f"⏰ Слишком рано для уведомления. Прошло {time_since_last}, нужно {notification_frequency}")
                return False
        
        logger.info(f"✅ Можно отправлять уведомление для фильтра {filter_obj.id}")
        return True
    
    def get_new_listings_for_filter(self, filter_obj: Filter, user_id: int) -> List[Listing]:
        """
        Получение новых объявлений по фильтру с защитой от дубликатов
        
        Логика:
        1. Если первый запуск фильтра (нет last_notification_sent) - до 30 самых свежих
        2. Если повторный запуск - только новые за 24 часа
        3. Исключаем уже отправленные объявления
        """
        try:
            db = self.get_db()
            
            # Определяем режим работы
            is_first_run = filter_obj.last_notification_sent is None
            logger.info(f"🚀 Фильтр {filter_obj.id}: {'первый запуск' if is_first_run else 'повторный запуск'}")
            
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
            }
            
            # Удаляем None значения
            search_params = {k: v for k, v in search_params.items() if v is not None}
            
            # Ищем объявления напрямую через CRUD
            from src.crud.crud_listing import listing as crud_listing
            
            if is_first_run:
                # Первый запуск - берем до 30 самых свежих объявлений
                all_listings = crud_listing.search(db, limit=30, **search_params)
                logger.info(f"🔍 Первый запуск: найдено {len(all_listings)} объявлений (лимит 30)")
            else:
                # Повторный запуск - только новые за 24 часа
                since_time = datetime.now(timezone.utc) - timedelta(hours=24)
                all_listings = crud_listing.search(db, limit=50, **search_params)
                
                # Фильтруем по дате
                fresh_listings = []
                for listing in all_listings:
                    if listing.created_at:
                        listing_time = listing.created_at
                        compare_time = since_time
                        
                        # Приводим к единому формату
                        if listing_time.tzinfo is None and compare_time.tzinfo is not None:
                            compare_time = compare_time.replace(tzinfo=None)
                        elif listing_time.tzinfo is not None and compare_time.tzinfo is None:
                            listing_time = listing_time.replace(tzinfo=None)
                        
                        if listing_time >= compare_time:
                            fresh_listings.append(listing)
                
                all_listings = fresh_listings
                logger.info(f"🔍 Повторный запуск: найдено {len(all_listings)} новых объявлений за 24ч")
            
            # Получаем список уже отправленных объявлений для этого пользователя
            sent_listing_ids = set(
                row[0] for row in 
                db.query(SentNotification.listing_id)
                .filter(SentNotification.user_id == user_id)
                .all()
            )
            
            # Исключаем уже отправленные объявления
            new_listings = [
                listing for listing in all_listings 
                if listing.id not in sent_listing_ids
            ]
            
            logger.info(f"📋 Исключено {len(all_listings) - len(new_listings)} уже отправленных объявлений")
            logger.info(f"✅ Найдено {len(new_listings)} новых объявлений для отправки")
            
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
                db = self.get_db()
                
                # Обновляем время последнего уведомления
                filter_obj.last_notification_sent = datetime.now(timezone.utc).replace(tzinfo=None)
                db.add(filter_obj)
                
                # Сохраняем каждое отправленное объявление в SentNotification
                for listing in listings:
                    try:
                        sent_notification = SentNotification(
                            user_id=user.id,
                            filter_id=filter_obj.id,
                            listing_id=listing.id,
                            notification_type="new_listing"
                        )
                        db.add(sent_notification)
                    except Exception as e:
                        # Игнорируем ошибки дублирования (уникальный индекс)
                        logger.debug(f"Объявление {listing.id} уже было отправлено пользователю {user.id}")
                
                # Создаем общую запись в Notification для статистики
                try:
                    notification = Notification(
                        user_id=user.id,
                        filter_id=filter_obj.id,
                        listing_id=listings[0].id if listings else None,
                        notification_type="new_listing",
                        status="sent",
                        sent_at=datetime.now(timezone.utc).replace(tzinfo=None),
                        message=f"Отправлено {len(listings)} объявлений"
                    )
                    db.add(notification)
                except Exception as e:
                    logger.warning(f"Не удалось сохранить запись статистики: {e}")
                
                try:
                    db.commit()
                    logger.info(f"📧 Уведомление отправлено пользователю {user.email} о {len(listings)} объявлениях")
                    return True
                except Exception as e:
                    logger.error(f"Ошибка сохранения в БД: {e}")
                    db.rollback()
                    return False
            
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
                    logger.info(f"⏰ Пропускаем фильтр {filter_obj.id} - слишком рано для следующего уведомления")
                    continue
                
                # Получаем новые объявления
                new_listings = self.get_new_listings_for_filter(filter_obj, user.id)
                
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