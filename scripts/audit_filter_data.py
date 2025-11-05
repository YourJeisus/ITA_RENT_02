"""
Скрипт для аудита данных фильтров в БД
Анализирует реальные значения этажей, года постройки, типа здания и политики Children/Pets
"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json
from collections import Counter

# Подключение к БД
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ita_rent.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def analyze_floor_data():
    """Анализирует данные об этажах"""
    print("\n" + "="*80)
    print("📊 АНАЛИЗ ДАННЫХ ЭТАЖЕЙ")
    print("="*80)
    
    session = SessionLocal()
    try:
        # Получаем уникальные значения floor
        result = session.execute(text("""
            SELECT floor, COUNT(*) as count
            FROM listings
            WHERE floor IS NOT NULL AND floor != ''
            GROUP BY floor
            ORDER BY count DESC
            LIMIT 50
        """))
        
        print("\n🏢 Топ-50 значений поля 'floor':")
        print("-" * 80)
        floor_examples = []
        for row in result:
            floor_val, count = row
            print(f"  {floor_val[:80]:<80} | {count:>5} раз")
            floor_examples.append(floor_val)
        
        # Получаем примеры с total_floors
        result = session.execute(text("""
            SELECT floor, total_floors, COUNT(*) as count
            FROM listings
            WHERE total_floors IS NOT NULL
            GROUP BY floor, total_floors
            ORDER BY count DESC
            LIMIT 20
        """))
        
        print("\n🏗️  Значения с total_floors:")
        print("-" * 80)
        for row in result:
            floor_val, total_floors, count = row
            print(f"  Floor: {str(floor_val)[:40]:<40} | Total: {total_floors:>2} | {count:>3} раз")
        
        return floor_examples
        
    finally:
        session.close()

def analyze_year_building():
    """Анализирует данные о годе постройки и типе здания"""
    print("\n" + "="*80)
    print("📊 АНАЛИЗ ГОДА ПОСТРОЙКИ И ТИПА ЗДАНИЯ")
    print("="*80)
    
    session = SessionLocal()
    try:
        # Year built
        result = session.execute(text("""
            SELECT year_built, COUNT(*) as count
            FROM listings
            WHERE year_built IS NOT NULL
            GROUP BY year_built
            ORDER BY count DESC
        """))
        
        years = list(result)
        print(f"\n📅 Год постройки (всего записей: {len(years)}):")
        print("-" * 80)
        if years:
            for row in years[:20]:
                year, count = row
                print(f"  {year} | {count} раз")
        else:
            print("  ❌ Нет данных")
        
        # Building type
        result = session.execute(text("""
            SELECT building_type, COUNT(*) as count
            FROM listings
            WHERE building_type IS NOT NULL
            GROUP BY building_type
            ORDER BY count DESC
        """))
        
        print(f"\n🏛️  Тип здания:")
        print("-" * 80)
        building_types = list(result)
        if building_types:
            for row in building_types:
                btype, count = row
                print(f"  {btype:<30} | {count:>5} раз")
        else:
            print("  ❌ Нет данных")
            
        # Renovation type
        result = session.execute(text("""
            SELECT renovation_type, COUNT(*) as count
            FROM listings
            WHERE renovation_type IS NOT NULL
            GROUP BY renovation_type
            ORDER BY count DESC
        """))
        
        print(f"\n🔨 Тип ремонта:")
        print("-" * 80)
        renovation_types = list(result)
        if renovation_types:
            for row in renovation_types:
                rtype, count = row
                print(f"  {rtype:<30} | {count:>5} раз")
        else:
            print("  ❌ Нет данных")
        
    finally:
        session.close()

def analyze_pets_children():
    """Анализирует данные о политике pets/children"""
    print("\n" + "="*80)
    print("📊 АНАЛИЗ ПОЛИТИКИ PETS/CHILDREN")
    print("="*80)
    
    session = SessionLocal()
    try:
        # Pets allowed
        result = session.execute(text("""
            SELECT pets_allowed, COUNT(*) as count
            FROM listings
            GROUP BY pets_allowed
            ORDER BY count DESC
        """))
        
        print(f"\n🐾 Pets allowed:")
        print("-" * 80)
        for row in result:
            value, count = row
            status = "✅ Allowed" if value else "❌ Not allowed" if value is False else "❓ Unknown"
            print(f"  {status:<20} | {count:>5} раз")
        
        # Children friendly
        result = session.execute(text("""
            SELECT children_friendly, COUNT(*) as count
            FROM listings
            GROUP BY children_friendly
            ORDER BY count DESC
        """))
        
        print(f"\n👶 Children friendly:")
        print("-" * 80)
        for row in result:
            value, count = row
            status = "✅ Friendly" if value else "❌ Not friendly" if value is False else "❓ Unknown"
            print(f"  {status:<20} | {count:>5} раз")
        
        # Agency commission
        result = session.execute(text("""
            SELECT agency_commission, COUNT(*) as count
            FROM listings
            GROUP BY agency_commission
            ORDER BY count DESC
        """))
        
        print(f"\n💰 Agency commission:")
        print("-" * 80)
        for row in result:
            value, count = row
            status = "✅ Has commission" if value else "❌ No commission" if value is False else "❓ Unknown"
            print(f"  {status:<20} | {count:>5} раз")
        
        # Примеры описаний с запретами
        print(f"\n📝 Примеры описаний с явными запретами на животных:")
        print("-" * 80)
        result = session.execute(text("""
            SELECT description, pets_allowed
            FROM listings
            WHERE description LIKE '%no animali%' 
               OR description LIKE '%animali non ammessi%'
               OR description LIKE '%no pets%'
            LIMIT 5
        """))
        
        for row in result:
            desc, pets = row
            desc_short = desc[:150] if desc else ""
            print(f"  Pets={pets} | {desc_short}...")
            print()
        
        print(f"\n📝 Примеры описаний БЕЗ комиссии:")
        print("-" * 80)
        result = session.execute(text("""
            SELECT description, agency_commission
            FROM listings
            WHERE description LIKE '%senza commissioni%' 
               OR description LIKE '%no commission%'
               OR description LIKE '%privato%'
               OR description LIKE '%proprietario%'
            LIMIT 5
        """))
        
        for row in result:
            desc, commission = row
            desc_short = desc[:150] if desc else ""
            print(f"  Commission={commission} | {desc_short}...")
            print()
            
    finally:
        session.close()

def analyze_description_patterns():
    """Анализирует паттерны в описаниях для этажей"""
    print("\n" + "="*80)
    print("📊 АНАЛИЗ ПАТТЕРНОВ В ОПИСАНИЯХ")
    print("="*80)
    
    session = SessionLocal()
    try:
        # Ищем упоминания этажей в описаниях
        print(f"\n🔍 Поиск упоминаний 'piano' в описаниях:")
        print("-" * 80)
        result = session.execute(text("""
            SELECT description, floor
            FROM listings
            WHERE description LIKE '%piano%'
            LIMIT 10
        """))
        
        for row in result:
            desc, floor = row
            # Извлекаем контекст вокруг "piano"
            if desc and 'piano' in desc.lower():
                idx = desc.lower().find('piano')
                context = desc[max(0, idx-30):min(len(desc), idx+50)]
                print(f"  Floor field: {str(floor)[:30]}")
                print(f"  Context: ...{context}...")
                print()
        
    finally:
        session.close()

def main():
    print("\n" + "="*80)
    print("🔍 АУДИТ ДАННЫХ ФИЛЬТРОВ В БАЗЕ ДАННЫХ")
    print("="*80)
    
    # Общая статистика
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT COUNT(*) FROM listings WHERE is_active = 1"))
        total = result.scalar()
        print(f"\n📊 Всего активных объявлений: {total}")
    finally:
        session.close()
    
    # Запускаем анализ
    analyze_floor_data()
    analyze_year_building()
    analyze_pets_children()
    analyze_description_patterns()
    
    print("\n" + "="*80)
    print("✅ АУДИТ ЗАВЕРШЕН")
    print("="*80)

if __name__ == "__main__":
    main()

