#!/usr/bin/env python3
"""
🔍 Проверка содержимого базы данных на Railway

Анализирует:
- Последние объявления по источникам
- Качество данных от каждого парсера
- Статистику уведомлений
- Проблемы с фильтрацией
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.db.database import SessionLocal
from src.db.models import User, Filter, Listing, SentNotification
from sqlalchemy import func, desc, and_, text
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def check_recent_listings_by_source():
    """Проверяет последние объявления по источникам"""
    print("\n" + "="*80)
    print("🆕 ПОСЛЕДНИЕ ОБЪЯВЛЕНИЯ ЗА 6 ЧАСОВ ПО ИСТОЧНИКАМ")
    print("="*80)
    
    db = SessionLocal()
    try:
        # Последние 6 часов
        since_6h = datetime.utcnow() - timedelta(hours=6)
        
        # Группируем по источникам
        sources = ['idealista', 'immobiliare', 'subito']
        
        for source in sources:
            print(f"\n📌 {source.upper()}:")
            
            recent_listings = db.query(Listing).filter(
                Listing.created_at >= since_6h,
                Listing.source == source,
                Listing.is_active == True
            ).order_by(desc(Listing.created_at)).limit(10).all()
            
            print(f"   📊 Новых за 6ч: {len(recent_listings)}")
            
            if recent_listings:
                for i, listing in enumerate(recent_listings[:5], 1):
                    created_time = listing.created_at.strftime("%H:%M") if listing.created_at else "??:??"
                    price = f"{listing.price}€" if listing.price else "без цены"
                    rooms = f"{listing.rooms}к" if listing.rooms else "?к"
                    
                    print(f"   {i}. [{created_time}] {listing.title[:40]}...")
                    print(f"      💰 {price} | 🚪 {rooms} | 📍 {listing.city}")
                    print(f"      🔗 {listing.url[:60]}...")
            else:
                print("   ❌ Новых объявлений не найдено")
                
        # Общая статистика за 6 часов
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА ЗА 6 ЧАСОВ:")
        total_stats = db.query(
            Listing.source,
            func.count(Listing.id).label('count')
        ).filter(
            Listing.created_at >= since_6h,
            Listing.is_active == True
        ).group_by(Listing.source).all()
        
        for source, count in total_stats:
            print(f"   • {source}: {count} объявлений")
            
    finally:
        db.close()


def check_filter_matching():
    """Проверяет как фильтры работают с новыми объявлениями"""
    print("\n" + "="*80)
    print("🔍 АНАЛИЗ ФИЛЬТРА И СОВПАДЕНИЙ")
    print("="*80)
    
    db = SessionLocal()
    try:
        # Получаем активный фильтр
        active_filter = db.query(Filter).filter(
            Filter.is_active == True,
            Filter.notification_enabled == True
        ).first()
        
        if not active_filter:
            print("❌ Активных фильтров не найдено")
            return
            
        print(f"🔍 Анализируем фильтр ID {active_filter.id}: '{active_filter.name}'")
        print(f"   🏙️ Город: {active_filter.city}")
        print(f"   💰 Цена: {active_filter.min_price}-{active_filter.max_price}€")
        print(f"   🚪 Комнаты: {active_filter.min_rooms}-{active_filter.max_rooms}")
        print(f"   🏠 Тип: {active_filter.property_type}")
        
        # Ищем совпадения за последние 6 часов по источникам
        since_6h = datetime.utcnow() - timedelta(hours=6)
        
        sources = ['idealista', 'immobiliare', 'subito']
        
        for source in sources:
            print(f"\n📌 {source.upper()} - совпадения с фильтром:")
            
            query = db.query(Listing).filter(
                Listing.created_at >= since_6h,
                Listing.source == source,
                Listing.is_active == True
            )
            
            # Применяем фильтры
            if active_filter.city:
                query = query.filter(func.lower(Listing.city).like(f"%{active_filter.city.lower()}%"))
            if active_filter.min_price:
                query = query.filter(Listing.price >= active_filter.min_price)
            if active_filter.max_price:
                query = query.filter(Listing.price <= active_filter.max_price)
            if active_filter.property_type:
                query = query.filter(Listing.property_type == active_filter.property_type)
            if active_filter.min_rooms:
                query = query.filter(Listing.rooms >= active_filter.min_rooms)
            if active_filter.max_rooms:
                query = query.filter(Listing.rooms <= active_filter.max_rooms)
                
            matching_listings = query.order_by(desc(Listing.created_at)).limit(10).all()
            
            print(f"   ✅ Подходящих: {len(matching_listings)}")
            
            for listing in matching_listings[:3]:
                created_time = listing.created_at.strftime("%H:%M") if listing.created_at else "??:??"
                price = f"{listing.price}€" if listing.price else "без цены"
                rooms = f"{listing.rooms}к" if listing.rooms else "?к"
                
                print(f"   • [{created_time}] {listing.title[:35]}...")
                print(f"     💰 {price} | 🚪 {rooms} | ID: {listing.id}")
                
    finally:
        db.close()


def check_sent_notifications():
    """Проверяет отправленные уведомления"""
    print("\n" + "="*80)
    print("📨 ОТПРАВЛЕННЫЕ УВЕДОМЛЕНИЯ ЗА 6 ЧАСОВ")
    print("="*80)
    
    db = SessionLocal()
    try:
        since_6h = datetime.utcnow() - timedelta(hours=6)
        
        # Получаем уведомления с объявлениями
        notifications = db.query(SentNotification, Listing).join(
            Listing, SentNotification.listing_id == Listing.id
        ).filter(
            SentNotification.sent_at >= since_6h
        ).order_by(desc(SentNotification.sent_at)).limit(20).all()
        
        print(f"📊 Всего уведомлений за 6ч: {len(notifications)}")
        
        if notifications:
            # Группируем по источникам
            source_stats = {}
            for notif, listing in notifications:
                source = listing.source or 'unknown'
                source_stats[source] = source_stats.get(source, 0) + 1
            
            print(f"📊 По источникам:")
            for source, count in source_stats.items():
                print(f"   • {source}: {count} уведомлений")
                
            print(f"\n📋 Последние 10 уведомлений:")
            for i, (notif, listing) in enumerate(notifications[:10], 1):
                sent_time = notif.sent_at.strftime("%H:%M") if notif.sent_at else "??:??"
                price = f"{listing.price}€" if listing.price else "без цены"
                
                print(f"   {i}. [{sent_time}] [{listing.source}] {listing.title[:30]}...")
                print(f"      💰 {price} | ID: {listing.id}")
        else:
            print("❌ Уведомлений за последние 6 часов не найдено")
            
    finally:
        db.close()


def analyze_data_quality():
    """Анализирует качество данных от парсеров"""
    print("\n" + "="*80)
    print("🔬 АНАЛИЗ КАЧЕСТВА ДАННЫХ ПО ИСТОЧНИКАМ")
    print("="*80)
    
    db = SessionLocal()
    try:
        sources = ['idealista', 'immobiliare', 'subito']
        
        for source in sources:
            print(f"\n📌 {source.upper()}:")
            
            # Проверяем наличие ключевых полей
            total_count = db.query(func.count(Listing.id)).filter(
                Listing.source == source,
                Listing.is_active == True
            ).scalar()
            
            # Проверяем заполненность полей
            price_filled = db.query(func.count(Listing.id)).filter(
                Listing.source == source,
                Listing.price.isnot(None),
                Listing.price > 0,
                Listing.is_active == True
            ).scalar()
            
            rooms_filled = db.query(func.count(Listing.id)).filter(
                Listing.source == source,
                Listing.rooms.isnot(None),
                Listing.rooms > 0,
                Listing.is_active == True
            ).scalar()
            
            city_filled = db.query(func.count(Listing.id)).filter(
                Listing.source == source,
                Listing.city.isnot(None),
                Listing.city != '',
                Listing.is_active == True
            ).scalar()
            
            property_type_filled = db.query(func.count(Listing.id)).filter(
                Listing.source == source,
                Listing.property_type.isnot(None),
                Listing.property_type != '',
                Listing.is_active == True
            ).scalar()
            
            print(f"   📊 Всего активных: {total_count}")
            print(f"   💰 С ценой: {price_filled} ({price_filled/total_count*100:.1f}%)")
            print(f"   🚪 С комнатами: {rooms_filled} ({rooms_filled/total_count*100:.1f}%)")
            print(f"   🏙️ С городом: {city_filled} ({city_filled/total_count*100:.1f}%)")
            print(f"   🏠 С типом: {property_type_filled} ({property_type_filled/total_count*100:.1f}%)")
            
            # Примеры объявлений с проблемами
            problematic = db.query(Listing).filter(
                Listing.source == source,
                Listing.is_active == True,
                and_(
                    (Listing.price.is_(None)) | (Listing.price <= 0) |
                    (Listing.rooms.is_(None)) | (Listing.rooms <= 0) |
                    (Listing.city.is_(None)) | (Listing.city == '') |
                    (Listing.property_type.is_(None)) | (Listing.property_type == '')
                )
            ).limit(3).all()
            
            if problematic:
                print(f"   ⚠️ Примеры проблемных объявлений:")
                for listing in problematic:
                    issues = []
                    if not listing.price or listing.price <= 0:
                        issues.append("нет цены")
                    if not listing.rooms or listing.rooms <= 0:
                        issues.append("нет комнат")
                    if not listing.city:
                        issues.append("нет города")
                    if not listing.property_type:
                        issues.append("нет типа")
                    
                    print(f"     • ID {listing.id}: {listing.title[:30]}... ({', '.join(issues)})")
            
    finally:
        db.close()


def main():
    """Главная функция анализа"""
    print("🔍 АНАЛИЗ БАЗЫ ДАННЫХ ITA_RENT_BOT (RAILWAY)")
    print("=" * 80)
    print(f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    
    check_recent_listings_by_source()
    check_filter_matching()
    check_sent_notifications()
    analyze_data_quality()
    
    print("\n" + "="*80)
    print("✅ АНАЛИЗ ЗАВЕРШЕН")
    print("="*80)
    print("\n🔧 ВОЗМОЖНЫЕ ПРИЧИНЫ ПРОБЛЕМ:")
    print("1. Idealista/Immobiliare парсят старые объявления (много дубликатов)")
    print("2. Некачественные данные не проходят фильтр")
    print("3. Объявления не соответствуют критериям фильтра")
    print("4. Проблемы с парсингом ключевых полей (цена, комнаты)")


if __name__ == "__main__":
    main() 