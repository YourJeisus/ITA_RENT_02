#!/usr/bin/env python3
"""
🔍 Диагностика проблем с уведомлениями

Проверяет:
- Последние объявления в БД
- Отправленные уведомления  
- Фильтры пользователей
- Логику сопоставления
"""
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from src.db.database import SessionLocal
from src.db.models import User, Filter, Listing, SentNotification
from src.crud.crud_listing import listing as crud_listing
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def check_recent_listings():
    """Проверяет последние объявления"""
    print("\n" + "="*60)
    print("🆕 ПОСЛЕДНИЕ ОБЪЯВЛЕНИЯ (за 2 часа)")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Последние 2 часа
        since_2h = datetime.utcnow() - timedelta(hours=2)
        
        recent_listings = db.query(Listing).filter(
            Listing.created_at >= since_2h,
            Listing.is_active == True
        ).order_by(desc(Listing.created_at)).limit(20).all()
        
        if not recent_listings:
            print("❌ Новых объявлений за последние 2 часа не найдено")
            return []
        
        print(f"📋 Найдено {len(recent_listings)} новых объявлений за 2 часа:")
        
        source_stats = {}
        for listing in recent_listings:
            source = listing.source or 'unknown'
            source_stats[source] = source_stats.get(source, 0) + 1
            
            created_time = listing.created_at.strftime("%H:%M:%S") if listing.created_at else "неизвестно"
            price = f"{listing.price}€" if listing.price else "без цены"
            
            print(f"   {listing.id}. [{source.upper()}] {listing.title[:50]}...")
            print(f"      💰 {price} | 📍 {listing.city} | ⏰ {created_time}")
        
        print(f"\n📊 По источникам: {source_stats}")
        return recent_listings
        
    finally:
        db.close()


def check_user_filters():
    """Проверяет фильтры пользователей"""
    print("\n" + "="*60)
    print("🔍 ФИЛЬТРЫ ПОЛЬЗОВАТЕЛЕЙ")
    print("="*60)
    
    db = SessionLocal()
    try:
        users = db.query(User).filter(
            User.is_active == True,
            User.telegram_chat_id.isnot(None)
        ).all()
        
        for user in users:
            print(f"\n👤 {user.email}:")
            print(f"   Chat ID: {user.telegram_chat_id}")
            
            filters = db.query(Filter).filter(Filter.user_id == user.id).all()
            active_filters = [f for f in filters if f.is_active]
            
            print(f"   Фильтров: {len(filters)} (активных: {len(active_filters)})")
            
            for filter_obj in active_filters:
                last_sent = filter_obj.last_notification_sent
                last_sent_str = last_sent.strftime("%d.%m %H:%M") if last_sent else "никогда"
                
                print(f"\n   🔍 Фильтр {filter_obj.id}: '{filter_obj.name}'")
                print(f"      🏙️ Город: {filter_obj.city}")
                print(f"      💰 Цена: {filter_obj.min_price}-{filter_obj.max_price}€")
                print(f"      🏠 Тип: {filter_obj.property_type}")
                print(f"      🚪 Комнаты: {filter_obj.min_rooms}-{filter_obj.max_rooms}")
                print(f"      📅 Последнее уведомление: {last_sent_str}")
                print(f"      ⏰ Частота: {filter_obj.notification_frequency_hours}ч")
                
                # Проверяем подходящие объявления
                check_matching_listings(db, filter_obj, user.id)
                
    finally:
        db.close()


def check_matching_listings(db, filter_obj: Filter, user_id: int):
    """Проверяет какие объявления подходят под фильтр"""
    # Создаем параметры поиска
    search_params = {
        "city": filter_obj.city,
        "min_price": filter_obj.min_price,
        "max_price": filter_obj.max_price,
        "property_type": filter_obj.property_type,
        "min_rooms": filter_obj.min_rooms,
        "max_rooms": filter_obj.max_rooms,
    }
    
    # Удаляем None значения
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    # Ищем за последние 24 часа
    since_24h = datetime.utcnow() - timedelta(hours=24)
    all_listings = crud_listing.search(db, limit=50, **search_params)
    
    # Фильтруем по дате
    fresh_listings = []
    for listing in all_listings:
        if listing.created_at and listing.created_at >= since_24h:
            fresh_listings.append(listing)
    
    print(f"      📊 Найдено подходящих за 24ч: {len(fresh_listings)}")
    
    if fresh_listings:
        source_stats = {}
        for listing in fresh_listings:
            source = listing.source or 'unknown'
            source_stats[source] = source_stats.get(source, 0) + 1
        print(f"      📌 По источникам: {source_stats}")
    
    # Проверяем отправленные уведомления
    sent_listing_ids = set(
        row[0] for row in 
        db.query(SentNotification.listing_id)
        .filter(SentNotification.user_id == user_id)
        .all()
    )
    
    # Новые объявления (не отправленные)
    new_listings = [
        listing for listing in fresh_listings 
        if listing.id not in sent_listing_ids
    ]
    
    print(f"      ✅ Новых для отправки: {len(new_listings)}")
    print(f"      📋 Уже отправлено: {len(fresh_listings) - len(new_listings)}")
    
    if new_listings:
        new_source_stats = {}
        for listing in new_listings:
            source = listing.source or 'unknown'
            new_source_stats[source] = new_source_stats.get(source, 0) + 1
        print(f"      🆕 Новые по источникам: {new_source_stats}")
        
        print(f"      📋 Примеры новых объявлений:")
        for listing in new_listings[:3]:
            print(f"         - ID {listing.id}: {listing.title[:30]}... ({listing.source})")


def check_sent_notifications():
    """Проверяет отправленные уведомления"""
    print("\n" + "="*60)
    print("📨 ОТПРАВЛЕННЫЕ УВЕДОМЛЕНИЯ")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Последние 24 часа
        since_24h = datetime.utcnow() - timedelta(hours=24)
        
        recent_notifications = db.query(SentNotification).filter(
            SentNotification.sent_at >= since_24h
        ).order_by(desc(SentNotification.sent_at)).limit(20).all()
        
        print(f"📊 Уведомлений за 24 часа: {len(recent_notifications)}")
        
        if recent_notifications:
            print(f"\n📋 Последние уведомления:")
            for notif in recent_notifications:
                sent_time = notif.sent_at.strftime("%d.%m %H:%M") if notif.sent_at else "неизвестно"
                print(f"   • Пользователь {notif.user_id}, объявление {notif.listing_id} - {sent_time}")
        
        # Всего уведомлений
        total_notifications = db.query(func.count(SentNotification.id)).scalar()
        print(f"\n📈 Всего уведомлений в системе: {total_notifications}")
        
    finally:
        db.close()


def suggest_fixes():
    """Предлагает решения"""
    print("\n" + "="*60)
    print("🔧 ВОЗМОЖНЫЕ РЕШЕНИЯ")
    print("="*60)
    
    print("1. 🗑️ Очистить таблицу sent_notifications:")
    print("   DELETE FROM sent_notifications WHERE sent_at < NOW() - INTERVAL '7 days';")
    
    print("\n2. 🐛 Включить режим отладки:")
    print("   DEBUG_NOTIFICATIONS=true")
    
    print("\n3. ⏰ Изменить частоту уведомлений в фильтрах:")
    print("   notification_frequency_hours = 1 (вместо 24)")
    
    print("\n4. 🔄 Перезапустить notification worker")


def main():
    """Главная функция диагностики"""
    print("🔍 ДИАГНОСТИКА УВЕДОМЛЕНИЙ ITA_RENT_BOT")
    print("=" * 60)
    print(f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    
    # Запускаем все проверки
    recent_listings = check_recent_listings()
    check_user_filters()
    check_sent_notifications()
    suggest_fixes()
    
    print("\n" + "="*60)
    print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("="*60)


if __name__ == "__main__":
    main() 