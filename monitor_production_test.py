#!/usr/bin/env python3
"""
🎯 МОНИТОРИНГ ПРОДАКШЕН ТЕСТИРОВАНИЯ ITA_RENT_BOT

Отслеживает:
- Новые объявления в БД
- Отправленные уведомления
- Дедупликацию
- Реальные продакшен условия
"""
import time
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Подключение к онлайн БД Railway
DATABASE_URL = 'postgresql://postgres:TAkDvHCdDTxVzutQsNNfJgbcSttzrgzN@caboose.proxy.rlwy.net:15179/railway'
engine = sqlalchemy.create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_stats():
    """Получает текущую статистику"""
    db = SessionLocal()
    
    try:
        # Общая статистика
        total_listings = db.execute(sqlalchemy.text("SELECT COUNT(*) FROM listings")).scalar()
        total_notifications = db.execute(sqlalchemy.text("SELECT COUNT(*) FROM sent_notifications")).scalar()
        
        # Объявления за последний час
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_listings = db.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM listings 
            WHERE created_at > :hour_ago
        """), {"hour_ago": hour_ago}).scalar()
        
        # Уведомления за последний час
        recent_notifications = db.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM sent_notifications 
            WHERE sent_at > :hour_ago
        """), {"hour_ago": hour_ago}).scalar()
        
        # Новые дома в Риме за последний час (подходящие под фильтр)
        new_roma_houses = db.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM listings 
            WHERE city = 'Roma' 
            AND property_type = 'house' 
            AND created_at > :hour_ago
        """), {"hour_ago": hour_ago}).scalar()
        
        # Последние отправленные уведомления
        last_notifications = db.execute(sqlalchemy.text("""
            SELECT listing_id, sent_at 
            FROM sent_notifications 
            WHERE user_id = 1
            ORDER BY sent_at DESC 
            LIMIT 3
        """)).fetchall()
        
        return {
            "total_listings": total_listings,
            "total_notifications": total_notifications,
            "recent_listings": recent_listings,
            "recent_notifications": recent_notifications,
            "new_roma_houses": new_roma_houses,
            "last_notifications": last_notifications,
            "timestamp": datetime.now()
        }
        
    finally:
        db.close()

def print_stats(stats):
    """Красиво выводит статистику"""
    print(f"\n🕐 {stats['timestamp'].strftime('%H:%M:%S')} - ПРОДАКШЕН ТЕСТ ITA_RENT_BOT")
    print("=" * 60)
    print(f"📊 Общая статистика:")
    print(f"   🏠 Всего объявлений: {stats['total_listings']}")
    print(f"   📨 Всего уведомлений: {stats['total_notifications']}")
    print()
    print(f"🔥 За последний час:")
    print(f"   ➕ Новых объявлений: {stats['recent_listings']}")
    print(f"   📱 Отправлено уведомлений: {stats['recent_notifications']}")
    print(f"   🏠 Домов в Риме: {stats['new_roma_houses']} (подходят под фильтр)")
    print()
    
    if stats['last_notifications']:
        print(f"📨 Последние уведомления пользователю:")
        for listing_id, sent_at in stats['last_notifications']:
            time_ago = datetime.now() - sent_at.replace(tzinfo=None)
            minutes_ago = int(time_ago.total_seconds() / 60)
            print(f"   🏠 Listing {listing_id} - {minutes_ago} мин назад")
    else:
        print(f"📨 Уведомлений еще не было")
    
    print()

def main():
    """Основной цикл мониторинга"""
    print("🎯 ЗАПУСК МОНИТОРИНГА ПРОДАКШЕН ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print("🔧 Настройки:")
    print("   DEBUG_NOTIFICATIONS = false (продакшен режим)")
    print("   NOTIFICATION_INTERVAL_SECONDS = 300 (5 минут)")
    print("   Дедупликация: ✅ включена")
    print("   Фильтр: дома в Риме")
    print("=" * 60)
    
    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"\n🔄 Итерация #{iteration}")
            
            try:
                stats = get_stats()
                print_stats(stats)
                
                # Анализ
                if stats['new_roma_houses'] > 0:
                    print(f"✅ Есть новые дома в Риме! Уведомления должны прийти в течение 5 минут.")
                elif stats['recent_notifications'] > 0:
                    print(f"📱 Уведомления отправляются - система работает!")
                else:
                    print(f"⏳ Ожидаем новые объявления или уведомления...")
                
            except Exception as e:
                print(f"❌ Ошибка получения статистики: {e}")
            
            print(f"⏰ Следующая проверка через 60 секунд...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Мониторинг остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка мониторинга: {e}")

if __name__ == "__main__":
    main() 