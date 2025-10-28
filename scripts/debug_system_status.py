#!/usr/bin/env python3
"""
🔍 ДИАГНОСТИЧЕСКИЙ СКРИПТ - ПРОВЕРКА СОСТОЯНИЯ СИСТЕМЫ

Проверяет:
- Статистику базы данных по источникам
- Состояние пользователей и фильтров  
- Работу уведомлений
- Последние объявления

Использование:
    python scripts/debug_system_status.py
"""
import sys
import asyncio
from pathlib import Path

# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.db.database import SessionLocal
from src.services.scraping_service import ScrapingService
from src.services.notification_service import NotificationService
from src.db.models import User, Filter, Listing, SentNotification
from src.crud.crud_listing import listing as crud_listing
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_database_statistics():
    """Выводит статистику базы данных"""
    print("\n" + "="*60)
    print("📊 СТАТИСТИКА БАЗЫ ДАННЫХ")
    print("="*60)
    
    db = SessionLocal()
    try:
        scraping_service = ScrapingService()
        stats = scraping_service.get_database_statistics(db)
        
        print(f"📈 Общая статистика:")
        print(f"   • Всего объявлений: {stats['total_listings']}")
        print(f"   • Активных: {stats['active_listings']}")
        print(f"   • Неактивных: {stats['inactive_listings']}")
        
        print(f"\n📌 По источникам:")
        for source, source_stats in stats['by_source'].items():
            print(f"   • {source.upper()}:")
            print(f"     - Всего: {source_stats['total']}")
            print(f"     - Активных: {source_stats['active']}")
            print(f"     - Неактивных: {source_stats['inactive']}")
        
        print(f"\n⏰ За последние 24 часа:")
        if stats['recent_24h']:
            for source, count in stats['recent_24h'].items():
                print(f"   • {source.upper()}: {count} новых")
        else:
            print("   • Новых объявлений не найдено")
        
        print(f"\n📅 За последнюю неделю:")
        if stats['recent_week']:
            for source, count in stats['recent_week'].items():
                print(f"   • {source.upper()}: {count} новых")
        else:
            print("   • Новых объявлений не найдено")
            
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
    finally:
        db.close()


def print_users_and_filters_status():
    """Выводит статистику пользователей и фильтров"""
    print("\n" + "="*60)
    print("👥 ПОЛЬЗОВАТЕЛИ И ФИЛЬТРЫ")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Статистика пользователей
        total_users = db.query(func.count(User.id)).scalar()
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
        telegram_users = db.query(func.count(User.id)).filter(
            User.is_active == True,
            User.telegram_chat_id.isnot(None)
        ).scalar()
        
        print(f"👤 Пользователи:")
        print(f"   • Всего: {total_users}")
        print(f"   • Активных: {active_users}")
        print(f"   • С Telegram: {telegram_users}")
        
        # Статистика фильтров
        total_filters = db.query(func.count(Filter.id)).scalar()
        active_filters = db.query(func.count(Filter.id)).filter(Filter.is_active == True).scalar()
        
        print(f"\n🔍 Фильтры:")
        print(f"   • Всего: {total_filters}")
        print(f"   • Активных: {active_filters}")
        
        # Детали пользователей с Telegram
        if telegram_users > 0:
            print(f"\n📱 Пользователи с Telegram:")
            telegram_user_list = db.query(User).filter(
                User.is_active == True,
                User.telegram_chat_id.isnot(None)
            ).all()
            
            for user in telegram_user_list:
                user_filters = db.query(Filter).filter(Filter.user_id == user.id).all()
                active_user_filters = [f for f in user_filters if f.is_active]
                
                print(f"   • {user.email}:")
                print(f"     - Chat ID: {user.telegram_chat_id}")
                print(f"     - Фильтров: {len(user_filters)} (активных: {len(active_user_filters)})")
                
                for filter_obj in active_user_filters:
                    last_sent = filter_obj.last_notification_sent
                    last_sent_str = last_sent.strftime("%d.%m %H:%M") if last_sent else "никогда"
                    print(f"       • '{filter_obj.name}' (ID: {filter_obj.id}, последнее: {last_sent_str})")
                    
    except Exception as e:
        print(f"❌ Ошибка получения статистики пользователей: {e}")
    finally:
        db.close()


def print_recent_listings():
    """Выводит последние объявления"""
    print("\n" + "="*60)
    print("🆕 ПОСЛЕДНИЕ ОБЪЯВЛЕНИЯ")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Последние 10 объявлений
        recent_listings = db.query(Listing).filter(
            Listing.is_active == True
        ).order_by(desc(Listing.created_at)).limit(10).all()
        
        if not recent_listings:
            print("❌ Объявления не найдены")
            return
            
        print(f"📋 Последние {len(recent_listings)} объявлений:")
        
        for i, listing in enumerate(recent_listings, 1):
            created_date = listing.created_at.strftime("%d.%m %H:%M") if listing.created_at else "неизвестно"
            price = f"{listing.price}€" if listing.price else "цена не указана"
            
            print(f"   {i}. [{listing.source.upper()}] {listing.title[:50]}...")
            print(f"      💰 {price} | 📍 {listing.city} | 📅 {created_date}")
            
    except Exception as e:
        print(f"❌ Ошибка получения последних объявлений: {e}")
    finally:
        db.close()


def print_notifications_status():
    """Выводит статистику уведомлений"""
    print("\n" + "="*60)
    print("🔔 СТАТИСТИКА УВЕДОМЛЕНИЙ")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Общая статистика уведомлений
        total_notifications = db.query(func.count(SentNotification.id)).scalar()
        
        # За последние 24 часа
        since_24h = datetime.utcnow() - timedelta(hours=24)
        recent_notifications = db.query(func.count(SentNotification.id)).filter(
            SentNotification.sent_at >= since_24h
        ).scalar()
        
        # За последнюю неделю
        since_week = datetime.utcnow() - timedelta(days=7)
        week_notifications = db.query(func.count(SentNotification.id)).filter(
            SentNotification.sent_at >= since_week
        ).scalar()
        
        print(f"📊 Уведомления:")
        print(f"   • Всего отправлено: {total_notifications}")
        print(f"   • За 24 часа: {recent_notifications}")
        print(f"   • За неделю: {week_notifications}")
        
        # Последние уведомления
        recent_sent = db.query(SentNotification).order_by(
            desc(SentNotification.sent_at)
        ).limit(5).all()
        
        if recent_sent:
            print(f"\n📨 Последние 5 уведомлений:")
            for notif in recent_sent:
                sent_time = notif.sent_at.strftime("%d.%m %H:%M") if notif.sent_at else "неизвестно"
                print(f"   • Пользователь {notif.user_id}, объявление {notif.listing_id} - {sent_time}")
        else:
            print(f"\n📨 Уведомления не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка получения статистики уведомлений: {e}")
    finally:
        db.close()


async def test_notification_system():
    """Тестирует работу системы уведомлений"""
    print("\n" + "="*60)
    print("🧪 ТЕСТ СИСТЕМЫ УВЕДОМЛЕНИЙ")
    print("="*60)
    
    try:
        notification_service = NotificationService()
        
        # Запускаем диспетчер уведомлений
        print("🔔 Запуск тестового диспетчера уведомлений...")
        result = await notification_service.process_all_notifications()
        
        if result:
            print(f"✅ Тест завершен:")
            print(f"   • Пользователей обработано: {result.get('users_processed', 0)}")
            print(f"   • Уведомлений отправлено: {result.get('notifications_sent', 0)}")
            print(f"   • Ошибок: {result.get('errors', 0)}")
        else:
            print("❌ Тест не удался - диспетчер вернул пустой результат")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования уведомлений: {e}")


async def main():
    """Главная функция диагностики"""
    print("🔍 ДИАГНОСТИКА СИСТЕМЫ ITA_RENT_BOT")
    print("=" * 60)
    print(f"⏰ Время запуска: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    
    # Проверяем переменные окружения
    try:
        from src.core.config import settings
        print(f"✅ Конфигурация загружена")
        print(f"   • DEBUG_NOTIFICATIONS: {settings.DEBUG_NOTIFICATIONS}")
        print(f"   • SCRAPERAPI_KEY: {'настроен' if settings.SCRAPERAPI_KEY else 'НЕ НАСТРОЕН'}")
        print(f"   • TELEGRAM_BOT_TOKEN: {'настроен' if settings.TELEGRAM_BOT_TOKEN else 'НЕ НАСТРОЕН'}")
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
    
    # Запускаем все проверки
    print_database_statistics()
    print_users_and_filters_status()
    print_recent_listings()
    print_notifications_status()
    await test_notification_system()
    
    print("\n" + "="*60)
    print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main()) 