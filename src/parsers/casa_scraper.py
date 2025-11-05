#!/usr/bin/env python3
"""
🚀 ПАРАЛЛЕЛЬНЫЙ ПАРСЕР CASA.IT
Все данные в JSON - максимально быстро!
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from src.core.config import settings
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.parsers.description_analyzer import DescriptionAnalyzer

class CasaScraper:
    """Параллельный парсер Casa.it"""
    
    def __init__(self, max_concurrent: int = 10, enable_geocoding: bool = False):
        self.base_url = "https://www.casa.it"
        self.api_url = "https://api.scraperapi.com/"
        self.api_key = settings.SCRAPERAPI_KEY
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.image_base_url = "https://images-1.casa.it/"
        self.enable_geocoding = enable_geocoding  # Для совместимости с интерфейсом
        
        # Статистика
        self.stats = {
            'success': 0,
            'failed': 0,
            'pages_scraped': 0
        }
    
    async def fetch_html(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Получает HTML через ScraperAPI"""
        async with self.semaphore:
            params = {
                'api_key': self.api_key,
                'url': url,
                'render': 'true',
                'ultra_premium': 'true'
            }
            
            try:
                async with session.get(self.api_url, params=params, timeout=aiohttp.ClientTimeout(total=90)) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
            except Exception as e:
                return None
    
    def extract_initial_state(self, html: str) -> Optional[Dict[str, Any]]:
        """Извлекает JSON данные из window.__INITIAL_STATE__"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for script in soup.find_all('script'):
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    # Извлекаем JSON строку
                    match = re.search(r'JSON\.parse\("(.+?)"\);', script.string, re.DOTALL)
                    
                    if match:
                        json_str = match.group(1)
                        # Декодируем escape последовательности
                        json_str = json_str.replace('\\"', '"')
                        json_str = json_str.replace('\\/', '/')
                        json_str = json_str.encode().decode('unicode_escape')
                        
                        data = json.loads(json_str)
                        return data
            
            return None
            
        except Exception as e:
            print(f"❌ Ошибка извлечения JSON: {e}")
            return None
    
    def extract_advertiser_type(self, listing_data: Dict[str, Any]) -> Optional[bool]:
        """
        Извлекает тип рекламодателя (частное лицо / агентство).
        Возвращает: False = частное (без комиссии), True = агентство (с комиссией), None = неизвестно
        """
        advertiser = listing_data.get('advertiser', {})
        
        # Проверяем isPrivate
        is_private = advertiser.get('isPrivate')
        if is_private is True:
            return False  # Частное лицо - без комиссии
        elif is_private is False:
            return True  # Агентство - с комиссией
        
        # Проверяем type
        adv_type = advertiser.get('type', '').lower()
        if adv_type == 'private' or adv_type == 'privati':
            return False
        elif adv_type == 'agency' or adv_type == 'agenzie':
            return True
        
        return None
    
    def parse_listing(self, listing_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Парсит одно объявление из JSON"""
        try:
            data = {
                'scraped_at': datetime.utcnow().isoformat(),
                'source': 'casa_it',
                'external_id': f"casa_it_{listing_data['id']}",
                'url': self.base_url + listing_data['uri']
            }
            
            # Основная информация
            data['title'] = listing_data.get('highlight') or listing_data.get('title', {}).get('main', '')
            data['description'] = listing_data.get('description', '')
            data['property_type'] = listing_data.get('propertyType', '')
            
            # Характеристики из features
            features = listing_data.get('features', {})
            
            # Площадь
            if features.get('mq'):
                data['area'] = int(features['mq'])
            
            # Комнаты
            if features.get('rooms'):
                data['rooms'] = int(features['rooms'])
            
            # Ванные
            if features.get('bathrooms'):
                data['bathrooms'] = int(features['bathrooms'])
            
            # Этаж
            if features.get('level'):
                data['floor'] = features['level']
            
            # Цена
            price_data = features.get('price', {})
            if price_data.get('value'):
                # Убираем точки (разделители тысяч)
                price_str = str(price_data['value']).replace('.', '')
                data['price'] = float(price_str)
            elif price_data.get('marker', {}).get('price'):
                # Цена договорная
                data['price_text'] = price_data['marker']['price']
            
            # Геолокация
            geo_info = listing_data.get('geoInfos', {})
            
            # Координаты (100% есть!)
            if geo_info.get('lat') and geo_info.get('lon'):
                data['latitude'] = float(geo_info['lat'])
                data['longitude'] = float(geo_info['lon'])
            
            # Адрес
            if geo_info.get('street'):
                data['address'] = geo_info['street']
            
            data['city'] = geo_info.get('city', 'Roma')
            data['district'] = geo_info.get('district_name', '')
            
            # Изображения
            media = listing_data.get('media', {})
            items = media.get('items', [])
            
            images = []
            for item in items:
                if item.get('uri'):
                    # Формируем полный URL изображения
                    uri = item['uri']
                    if uri.startswith('http'):
                        # Уже полный URL
                        img_url = uri
                    else:
                        # Casa.it требует размер в URL: /800x600/ или /360x265/
                        # Убираем начальный слеш из uri если он есть
                        uri = uri.lstrip('/')
                        img_url = self.image_base_url + '800x600/' + uri
                    images.append(img_url)
            
            data['images'] = images
            
            # Издатель (используем agency_name для единообразия)
            publisher = listing_data.get('publisher', {})
            if publisher:
                data['agency_name'] = publisher.get('publisherName', '')
                data['contact_phone'] = publisher.get('publisherPhone', '')
                data['contact_website'] = publisher.get('publisherWebsite', '')
            
            # Дополнительные характеристики
            features_list = []
            if features.get('mq'):
                features_list.append(f"{features['mq']} m²")
            if features.get('rooms'):
                features_list.append(f"{features['rooms']} locali")
            if features.get('bathrooms'):
                features_list.append(f"{features['bathrooms']} bagni")
            if features.get('level'):
                features_list.append(features['level'])
            if features.get('energyClass'):
                features_list.append(f"Classe energetica {features['energyClass']}")
            
            data['features'] = features_list
            
            # Извлекаем тип рекламодателя напрямую из JSON
            agency_commission_from_json = self.extract_advertiser_type(listing_data)
            
            # Анализ описания для извлечения фильтров
            description = data.get('description', '')
            analysis = DescriptionAnalyzer.analyze(description, floor=data.get('floor'))
            
            # Приоритизируем данные из Casa.it JSON над DescriptionAnalyzer
            data['agency_commission'] = agency_commission_from_json if agency_commission_from_json is not None else analysis.get('agency_commission')
            
            # Остальные поля из анализатора
            data['pets_allowed'] = analysis.get('pets_allowed')
            data['children_friendly'] = analysis.get('children_friendly')
            data['renovation_type'] = analysis.get('renovation_type')
            data['building_type'] = analysis.get('building_type')
            data['year_built'] = analysis.get('year_built')
            data['total_floors'] = analysis.get('total_floors')
            data['floor_number'] = analysis.get('floor_number')
            data['is_first_floor'] = analysis.get('is_first_floor')
            data['is_top_floor'] = analysis.get('is_top_floor')
            data['park_nearby'] = analysis.get('park_nearby')
            data['noisy_roads_nearby'] = analysis.get('noisy_roads_nearby')
            
            return data
            
        except Exception as e:
            print(f"❌ Ошибка парсинга объявления: {e}")
            return None
    
    async def scrape_page(self, session: aiohttp.ClientSession, page_num: int) -> List[Dict[str, Any]]:
        """Парсит одну страницу со списком объявлений"""
        
        if page_num == 1:
            url = f"{self.base_url}/affitto/residenziale/roma/"
        else:
            url = f"{self.base_url}/affitto/residenziale/roma/?p={page_num}"
        
        print(f"\n🔄 Страница {page_num}: {url}")
        
        html = await self.fetch_html(session, url)
        
        if not html:
            print(f"   ❌ Не удалось получить HTML")
            return []
        
        # Извлекаем JSON данные
        initial_state = self.extract_initial_state(html)
        
        if not initial_state:
            print(f"   ❌ Не удалось извлечь JSON данные")
            return []
        
        # Получаем список объявлений
        search_data = initial_state.get('search', {})
        listings_data = search_data.get('list', [])
        
        print(f"   ✅ Найдено {len(listings_data)} объявлений")
        
        # Парсим все объявления
        parsed_listings = []
        for listing_data in listings_data:
            parsed = self.parse_listing(listing_data)
            if parsed:
                parsed_listings.append(parsed)
                self.stats['success'] += 1
            else:
                self.stats['failed'] += 1
        
        self.stats['pages_scraped'] += 1
        
        return parsed_listings
    
    async def scrape_multiple_pages(self, max_pages: int = 5):
        """Основной метод с параллельным парсингом (совместимый интерфейс)"""
        return await self.scrape_parallel(num_pages=max_pages)
    
    async def scrape_parallel(self, num_pages: int = 5):
        """Основной метод с параллельным парсингом"""
        print("=" * 80)
        print(f"🚀 ПАРАЛЛЕЛЬНЫЙ ПАРСИНГ CASA.IT (до {self.max_concurrent} одновременно)")
        print("=" * 80)
        print(f"📄 Страниц: {num_pages}")
        print("=" * 80)
        
        start_time = datetime.utcnow()
        
        async with aiohttp.ClientSession() as session:
            # Создаем задачи для всех страниц
            tasks = [
                self.scrape_page(session, page_num)
                for page_num in range(1, num_pages + 1)
            ]
            
            # Запускаем параллельно
            results = await asyncio.gather(*tasks)
            
            # Объединяем результаты
            all_listings = []
            for page_listings in results:
                all_listings.extend(page_listings)
        
        end_time = datetime.utcnow()
        elapsed = (end_time - start_time).total_seconds()
        
        # Статистика
        print("\n" + "=" * 80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 80)
        print(f"✅ Успешно: {self.stats['success']}")
        print(f"❌ Ошибки: {self.stats['failed']}")
        print(f"📄 Страниц: {self.stats['pages_scraped']}")
        print()
        print(f"⏱️  Общее время: {elapsed:.1f} секунд")
        if all_listings:
            print(f"⚡ Среднее время на объявление: {elapsed/len(all_listings):.2f} сек")
            print(f"🚀 Скорость: {len(all_listings)/elapsed*60:.1f} объявлений/минуту")
        
        return all_listings


async def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Параллельный парсер Casa.it')
    parser.add_argument('--pages', type=int, default=5, help='Количество страниц (по умолчанию: 5)')
    parser.add_argument('--concurrent', type=int, default=5, help='Одновременных запросов (по умолчанию: 5)')
    
    args = parser.parse_args()
    
    scraper = CasaScraper(max_concurrent=args.concurrent)
    
    # Парсим
    listings = await scraper.scrape_parallel(num_pages=args.pages)
    
    # Сохраняем
    if listings:
        output_file = f'/tmp/casa_it_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(listings, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в {output_file}")
        
        # Статистика полей
        print("\n📋 ЗАПОЛНЕННОСТЬ ПОЛЕЙ:")
        fields_count = {}
        for listing in listings:
            for key, value in listing.items():
                if key not in fields_count:
                    fields_count[key] = 0
                if value and value != [] and value != 'N/A':
                    fields_count[key] += 1
        
        for key in sorted(fields_count.keys()):
            count = fields_count[key]
            percentage = (count / len(listings)) * 100
            print(f"   • {key:20s}: {count:3d}/{len(listings)} ({percentage:5.1f}%)")


if __name__ == "__main__":
    asyncio.run(main())

