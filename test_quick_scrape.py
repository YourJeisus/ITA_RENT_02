#!/usr/bin/env python3
"""
🧪 БЫСТРЫЙ ТЕСТ СКРАПИНГ - для отладки уведомлений

Позволяет быстро добавить объявления в БД для тестирования системы уведомлений
"""
import sys
import os
import asyncio
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

from src.parsers.immobiliare_scraper import ImmobiliareScraper
from src.crud.crud_listing import listing as crud_listing
import sqlalchemy
from sqlalchemy.orm import sessionmaker

# Подключение к онлайн БД Railway
DATABASE_URL = 'postgresql://postgres:TAkDvHCdDTxVzutQsNNfJgbcSttzrgzN@caboose.proxy.rlwy.net:15179/railway'
engine = sqlalchemy.create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def quick_scrape_test(page_url: str = None, max_listings: int = 5):
    """
    Быстрый скрапинг для тестирования уведомлений
    
    Args:
        page_url: URL конкретной страницы для скрапинга
        max_listings: максимум объявлений для добавления
    """
    print("🧪 БЫСТРЫЙ ТЕСТ СКРАПИНГ ДЛЯ ОТЛАДКИ УВЕДОМЛЕНИЙ")
    print("=" * 60)
    
    if not page_url:
        # По умолчанию - первая страница с сортировкой по дате
        page_url = "https://www.immobiliare.it/affitto-case/roma/?criterio=data&ordine=desc"
    
    print(f"🎯 URL: {page_url}")
    print(f"📊 Максимум объявлений: {max_listings}")
    print("=" * 60)
    
    # Создаем скрапер с геокодированием
    scraper = ImmobiliareScraper(enable_geocoding=True)
    
    try:
        print("🔄 Запускаем скрапинг одной страницы...")
        
        # Определяем номер страницы из URL
        if "pag=" in page_url:
            import re
            page_match = re.search(r'pag=(\d+)', page_url)
            page_num = int(page_match.group(1)) if page_match else 1
        else:
            page_num = 1
            
        print(f"📄 Скрапим страницу {page_num}")
        
        # Скрапим одну страницу
        listings = await scraper.scrape_single_page(page_num)
        
        if not listings:
            print("❌ Объявления не найдены!")
            return 0
            
        print(f"✅ Найдено {len(listings)} объявлений")
        
        # Ограничиваем количество
        listings = listings[:max_listings]
        print(f"📋 Берем первые {len(listings)} объявлений")
        
        # Подключаемся к БД и сохраняем
        db = SessionLocal()
        saved_count = 0
        
        try:
            for i, listing_data in enumerate(listings, 1):
                try:
                    # Проверяем, есть ли уже такое объявление
                    existing = crud_listing.get_by_external_id(
                        db, 
                        external_id=listing_data["external_id"],
                        source=listing_data["source"]
                    )
                    
                    if existing:
                        print(f"   ⚠️  {i}. ID {listing_data['external_id']} уже существует")
                        continue
                    
                    # Создаем новое объявление
                    from src.schemas.listing import ListingCreate
                    listing_schema = ListingCreate(**listing_data)
                    new_listing = crud_listing.create(db, obj_in=listing_schema)
                    saved_count += 1
                    
                    print(f"   ✅ {i}. Добавлено: {new_listing.title[:50]}...")
                    print(f"      💰 {new_listing.price}€ | 🏠 {new_listing.property_type} | 📍 {new_listing.city}")
                    
                    if new_listing.city == "Roma" and new_listing.property_type == "house":
                        print(f"      🎯 ПОДХОДИТ ПОД ФИЛЬТР! (дом в Риме)")
                    
                except Exception as e:
                    print(f"   ❌ {i}. Ошибка сохранения: {e}")
                    continue
            
            db.commit()
            print(f"\n🎉 УСПЕШНО ДОБАВЛЕНО: {saved_count} новых объявлений")
            
            if saved_count > 0:
                print(f"\n📱 СЛЕДУЮЩИЙ ШАГ:")
                print(f"   Система уведомлений найдет новые объявления")
                print(f"   и отправит их в Telegram в течение 5 минут!")
            
            return saved_count
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Ошибка скрапинга: {e}")
        return 0
    
    finally:
        # Скрапер не требует закрытия в этой версии
        pass

def main():
    """Главная функция с параметрами командной строки"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Быстрый тест скрапинг для отладки")
    parser.add_argument("--url", type=str, help="URL страницы для скрапинга")
    parser.add_argument("--max", type=int, default=5, help="Максимум объявлений (по умолчанию 5)")
    parser.add_argument("--page", type=int, help="Номер страницы (1-10)")
    
    args = parser.parse_args()
    
    # Если указан номер страницы, строим URL
    if args.page:
        base_url = "https://www.immobiliare.it/affitto-case/roma/?criterio=data&ordine=desc"
        if args.page == 1:
            page_url = base_url
        else:
            page_url = f"{base_url}&pag={args.page}"
        print(f"📄 Используем страницу {args.page}")
    else:
        page_url = args.url
    
    try:
        result = asyncio.run(quick_scrape_test(page_url, args.max))
        if result > 0:
            print(f"\n🚀 ГОТОВО! Добавлено {result} объявлений для тестирования уведомлений")
        sys.exit(0)
    except KeyboardInterrupt:
        print(f"\n⏹️ Скрапинг прерван пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 