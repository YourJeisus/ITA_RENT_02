#!/usr/bin/env python3
"""
🚀 ПАРАЛЛЕЛЬНЫЙ ПАРСЕР SUBITO.IT
Парсинг через __NEXT_DATA__ JSON (как Casa.it)
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from src.core.config import settings
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

class SubitoScraper:
    """Быстрый парсер Subito через JSON"""
    
    def __init__(self, enable_geocoding: bool = False, fetch_coords: bool = False):
        self.base_url = "https://www.subito.it"
        self.search_url = "https://www.subito.it/annunci-lazio/affitto/immobili/roma/roma/"
        self.api_url = "https://api.scraperapi.com/"
        self.api_key = settings.SCRAPERAPI_KEY
        self.enable_geocoding = enable_geocoding  # Для совместимости с интерфейсом
        self.fetch_coords = fetch_coords  # Парсить координаты с детальных страниц
        
        self.stats = {
            'success': 0,
            'failed': 0,
            'with_coords': 0,
            'with_images': 0,
        }
    
    async def fetch_html(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Получает HTML через ScraperAPI (простой запрос)"""
        params = {
            'api_key': self.api_key,
            'url': url
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=90)
            async with session.get(self.api_url, params=params, timeout=timeout) as response:
                if response.status == 200:
                    return await response.text()
                return None
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")
            return None
    
    def extract_next_data(self, html: str) -> Optional[Dict[str, Any]]:
        """Извлекает __NEXT_DATA__ из HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__')
            
            if script and script.string:
                return json.loads(script.string)
            
            return None
        except Exception as e:
            print(f"    ❌ Ошибка парсинга JSON: {e}")
            return None
    
    def parse_listing_data(self, item_wrapper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Парсит одно объявление из JSON"""
        try:
            # item_wrapper имеет ключи: ['before', 'item', 'after', 'kind']
            item = item_wrapper.get('item')
            
            if not item or not isinstance(item, dict):
                return None
            
            # Основная информация
            external_id = item.get('urn')
            title = item.get('subject')
            
            if not external_id or not title:
                return None
            
            # URL
            url = item.get('urls', {}).get('default', '')
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            # Features - это dict, а не list!
            features_dict = item.get('features', {})
            
            # Цена (values[0] - это dict с ключами 'key' и 'value')
            price = None
            if '/price' in features_dict:
                price_feature = features_dict['/price']
                values = price_feature.get('values', [])
                if values:
                    value_dict = values[0]
                    if isinstance(value_dict, dict):
                        price_str = value_dict.get('key', '')  # key содержит число
                    else:
                        price_str = str(value_dict)
                    
                    try:
                        price = int(price_str)
                    except:
                        pass
            
            # Характеристики недвижимости
            rooms = None
            if '/room' in features_dict:
                room_values = features_dict['/room'].get('values', [])
                if room_values:
                    value_dict = room_values[0]
                    if isinstance(value_dict, dict):
                        room_str = value_dict.get('key', '')
                    else:
                        room_str = str(value_dict)
                    
                    try:
                        rooms = int(re.search(r'\d+', room_str).group())
                    except:
                        pass
            
            area = None
            if '/size' in features_dict:
                size_values = features_dict['/size'].get('values', [])
                if size_values:
                    value_dict = size_values[0]
                    if isinstance(value_dict, dict):
                        size_str = value_dict.get('key', '')
                    else:
                        size_str = str(value_dict)
                    
                    try:
                        area = int(re.search(r'\d+', size_str).group())
                    except:
                        pass
            
            floor = None
            if '/floor' in features_dict:
                floor_values = features_dict['/floor'].get('values', [])
                if floor_values:
                    value_dict = floor_values[0]
                    if isinstance(value_dict, dict):
                        floor = value_dict.get('value', '')
                    else:
                        floor = str(value_dict)
            
            # Тип недвижимости из категории
            property_type = 'apartment'
            category = item.get('category', {})
            cat_name = category.get('friendlyName', '').lower()
            
            if 'stanza' in cat_name or 'camera' in cat_name or 'posto-letto' in cat_name:
                property_type = 'room'
            elif 'monolocale' in cat_name:
                property_type = 'studio'
            elif 'villa' in cat_name or 'casa' in cat_name:
                property_type = 'house'
            elif 'appartamenti' in cat_name:
                property_type = 'apartment'
            
            # Геолокация
            geo = item.get('geo', {})
            map_data = geo.get('map', {})
            
            # В списках Subito не предоставляет координаты
            latitude = map_data.get('lat') if map_data else None
            longitude = map_data.get('lng') if map_data else None
            address = map_data.get('address', '') if map_data else None
            
            # Район
            town = geo.get('town', {}).get('value', '')
            
            # Если нет адреса, берем название города
            if not address:
                city_value = geo.get('city', {}).get('value', '')
                if city_value:
                    address = city_value
            
            # Изображения (в JSON только baseUrl, нужно дополнять)
            images = []
            gallery = item.get('images', [])
            for img_item in gallery[:20]:  # Максимум 20
                base_url = img_item.get('cdnBaseUrl') or img_item.get('url')
                if base_url:
                    # Для Subito нужно добавить параметры размера
                    if 'sbito.it' in base_url:
                        img_url = f"{base_url}?rule=width-300"
                    else:
                        img_url = base_url
                    
                    if img_url not in images:
                        images.append(img_url)
            
            # Описание
            description = item.get('body', '')
            
            # Дата публикации
            published_at = item.get('date')
            
            return {
                'external_id': f"subito_{external_id}",
                'source': 'subito',
                'url': url,
                'title': title,
                'description': description,
                'price': price,
                'property_type': property_type,
                'rooms': rooms,
                'area': area,
                'floor': floor,
                'bathrooms': None,  # Subito обычно не указывает
                'latitude': float(latitude) if latitude else None,
                'longitude': float(longitude) if longitude else None,
                'address': address or town,
                'city': 'Roma',
                'district': town,
                'images': images,
                'published_at': published_at,
                'scraped_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"    ❌ Ошибка парсинга объявления: {e}")
            return None
    
    def parse_page(self, html: str) -> List[Dict[str, Any]]:
        """Парсит страницу и извлекает все объявления"""
        next_data = self.extract_next_data(html)
        
        if not next_data:
            return []
        
        try:
            items_list = next_data['props']['pageProps']['initialState']['items']['list']
            
            listings = []
            for item_wrapper in items_list:
                listing = self.parse_listing_data(item_wrapper)
                if listing:
                    listings.append(listing)
                    
                    # Статистика
                    if listing.get('latitude'):
                        self.stats['with_coords'] += 1
                    if listing.get('images'):
                        self.stats['with_images'] += 1
            
            return listings
            
        except Exception as e:
            print(f"    ❌ Ошибка парсинга страницы: {e}")
            return []
    
    def parse_detail_page_for_coords(self, html: str) -> Optional[tuple]:
        """Извлекает координаты из детальной страницы"""
        try:
            next_data = self.extract_next_data(html)
            if not next_data:
                return None
            
            # Навигация: props.pageProps.ad.geo.map
            ad_data = next_data.get('props', {}).get('pageProps', {}).get('ad', {})
            geo = ad_data.get('geo', {})
            map_data = geo.get('map', {})
            
            latitude = map_data.get('latitude')
            longitude = map_data.get('longitude')
            
            if latitude and longitude:
                return float(latitude), float(longitude)
            
            return None
        except Exception as e:
            return None
    
    async def scrape_multiple_pages(self, max_pages: int = 5):
        """Основной метод с параллельным парсингом (совместимый интерфейс)"""
        return await self.scrape_pages(num_pages=max_pages, fetch_coords=self.fetch_coords)
    
    async def scrape_pages(self, num_pages: int = 2, fetch_coords: bool = False, max_coords_fetch: int = 20, coords_concurrent: int = 10):
        """Параллельный парсинг нескольких страниц"""
        print("=" * 80)
        print(f"🚀 ПАРАЛЛЕЛЬНЫЙ ПАРСИНГ SUBITO.IT")
        print("=" * 80)
        print(f"📄 Страниц списков: {num_pages}")
        if fetch_coords:
            print(f"🌍 Получение координат: до {max_coords_fetch} объявлений")
            print(f"⚡ Параллельных запросов: {coords_concurrent}")
        print("=" * 80)
        
        start_time = datetime.utcnow()
        
        async with aiohttp.ClientSession() as session:
            # Генерируем URLs для страниц
            page_urls = []
            for page_num in range(1, num_pages + 1):
                if page_num == 1:
                    page_urls.append(self.search_url)
                else:
                    page_urls.append(f"{self.search_url}?o={page_num}")
            
            print(f"\n📋 Загрузка {len(page_urls)} страниц...")
            print("-" * 80)
            
            # Параллельная загрузка
            tasks = [self.fetch_html(session, url) for url in page_urls]
            htmls = await asyncio.gather(*tasks)
            
            # Парсинг всех страниц
            all_listings = []
            for i, html in enumerate(htmls, 1):
                if html:
                    print(f"Страница {i}: {len(html)} символов")
                    listings = self.parse_page(html)
                    print(f"    ✅ Найдено {len(listings)} объявлений")
                    all_listings.extend(listings)
                    self.stats['success'] += 1
                else:
                    print(f"Страница {i}: ❌ не загружена")
                    self.stats['failed'] += 1
            
            # ЭТАП 2: Получение координат с детальных страниц (если включено)
            if fetch_coords and all_listings:
                print("\n" + "=" * 80)
                print(f"🌍 ЭТАП 2: Параллельное получение координат")
                print("=" * 80)
                
                listings_to_fetch = all_listings[:max_coords_fetch]
                print(f"📍 Обрабатываем {len(listings_to_fetch)} объявлений параллельно...")
                
                # Параллельная загрузка детальных страниц
                semaphore = asyncio.Semaphore(coords_concurrent)
                
                async def fetch_and_parse_coords(listing, index):
                    async with semaphore:
                        detail_html = await self.fetch_html(session, listing['url'])
                        
                        if detail_html:
                            coords = self.parse_detail_page_for_coords(detail_html)
                            
                            if coords:
                                listing['latitude'], listing['longitude'] = coords
                                self.stats['with_coords'] += 1
                                print(f"[{index}/{len(listings_to_fetch)}] ✅ {listing['title'][:40]}... → {coords[0]:.6f}, {coords[1]:.6f}")
                                return True
                            else:
                                print(f"[{index}/{len(listings_to_fetch)}] ⚠️ {listing['title'][:40]}... → координаты не найдены")
                                return False
                        else:
                            print(f"[{index}/{len(listings_to_fetch)}] ❌ {listing['title'][:40]}... → не загружена")
                            return False
                
                # Запускаем все задачи параллельно
                tasks = [fetch_and_parse_coords(listing, i) for i, listing in enumerate(listings_to_fetch, 1)]
                await asyncio.gather(*tasks)
        
        end_time = datetime.utcnow()
        elapsed = (end_time - start_time).total_seconds()
        
        # ИТОГИ
        print("\n" + "=" * 80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 80)
        print(f"✅ Успешно загружено страниц: {self.stats['success']}")
        print(f"❌ Ошибок загрузки: {self.stats['failed']}")
        print(f"📦 Всего объявлений: {len(all_listings)}")
        print()
        print(f"📊 Качество данных:")
        if all_listings:
            print(f"   🌍 С координатами: {self.stats['with_coords']}/{len(all_listings)} ({self.stats['with_coords']/len(all_listings)*100:.0f}%)")
            print(f"   🖼️  С изображениями: {self.stats['with_images']}/{len(all_listings)} ({self.stats['with_images']/len(all_listings)*100:.0f}%)")
        
        # Статистика других полей
        if all_listings:
            with_price = sum(1 for l in all_listings if l.get('price'))
            with_rooms = sum(1 for l in all_listings if l.get('rooms'))
            with_area = sum(1 for l in all_listings if l.get('area_sqm'))
            with_description = sum(1 for l in all_listings if l.get('description'))
            
            print(f"   💰 С ценой: {with_price}/{len(all_listings)} ({with_price/len(all_listings)*100:.0f}%)")
            print(f"   🚪 С комнатами: {with_rooms}/{len(all_listings)} ({with_rooms/len(all_listings)*100:.0f}%)")
            print(f"   📐 С площадью: {with_area}/{len(all_listings)} ({with_area/len(all_listings)*100:.0f}%)")
            print(f"   📝 С описанием: {with_description}/{len(all_listings)} ({with_description/len(all_listings)*100:.0f}%)")
        print()
        print(f"⏱️  Общее время: {elapsed:.1f} секунд")
        if all_listings:
            print(f"⚡ Скорость: {len(all_listings)/elapsed*60:.1f} объявлений/минуту")
            print(f"📈 Среднее время: {elapsed/len(all_listings):.2f} сек/объявление")
        
        return all_listings


async def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', type=int, default=2, help='Количество страниц списков')
    parser.add_argument('--coords', action='store_true', help='Получить координаты с детальных страниц')
    parser.add_argument('--max-coords', type=int, default=20, help='Максимум объявлений для получения координат')
    parser.add_argument('--concurrent', type=int, default=10, help='Параллельных запросов для координат (default: 10)')
    
    args = parser.parse_args()
    
    scraper = SubitoParallelScraper()
    listings = await scraper.scrape_pages(
        num_pages=args.pages,
        fetch_coords=args.coords,
        max_coords_fetch=args.max_coords,
        coords_concurrent=args.concurrent
    )
    
    if listings:
        output_file = '/tmp/subito_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(listings, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в {output_file}")
        
        # Пример объявления
        print("\n📝 ПРИМЕР ОБЪЯВЛЕНИЯ:")
        print("=" * 80)
        first = listings[0]
        for key, value in first.items():
            if key == 'images':
                print(f"   {key}: {len(value)} шт")
            elif key == 'description' and len(str(value)) > 100:
                print(f"   {key}: {str(value)[:100]}...")
            else:
                print(f"   {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())

