#!/usr/bin/env python3
"""
🚀 УПРОЩЕННЫЙ ПАРАЛЛЕЛЬНЫЙ ПАРСЕР IMMOBILIARE.IT
Простой запрос без рендеринга + парсинг детальных страниц для описания
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from src.core.config import settings
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

class ImmobiliareScraper:
    """Простой парсер Immobiliare без лишних параметров"""
    
    def __init__(self, enable_geocoding: bool = False):
        self.base_url = "https://www.immobiliare.it"
        self.search_url = "https://www.immobiliare.it/affitto-case/roma/?criterio=data&ordine=desc"
        self.api_url = "https://api.scraperapi.com/"
        self.api_key = settings.SCRAPERAPI_KEY
        self.enable_geocoding = enable_geocoding  # Для совместимости с интерфейсом
        
        self.stats = {
            'list_pages_success': 0,
            'list_pages_failed': 0,
            'details_success': 0,
            'details_failed': 0,
            'with_description': 0,
            'with_coords': 0,
        }
    
    async def fetch_html(self, session: aiohttp.ClientSession, url: str, use_simple: bool = True) -> Optional[str]:
        """Получает HTML через ScraperAPI"""
        if use_simple:
            # Простой запрос - быстрый и дешевый
            params = {
                'api_key': self.api_key,
                'url': url
            }
        else:
            # Для детальных страниц используем ultra_premium
            params = {
                'api_key': self.api_key,
                'url': url,
                'render': 'true',
                'ultra_premium': 'true'
            }
        
        try:
            timeout = aiohttp.ClientTimeout(total=90)
            async with session.get(self.api_url, params=params, timeout=timeout) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"    ❌ HTTP {response.status}")
                return None
        except asyncio.TimeoutError:
            print(f"    ⏰ Таймаут")
            return None
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")
            return None
    
    def extract_next_data(self, html: str) -> Optional[Dict[str, Any]]:
        """Извлекает данные из __NEXT_DATA__"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__')
            
            if script and script.string:
                return json.loads(script.string)
            
            return None
        except Exception:
            return None
    
    def parse_list_page(self, html: str) -> List[Dict[str, Any]]:
        """Парсит страницу со списком"""
        next_data = self.extract_next_data(html)
        
        if not next_data:
            return []
        
        try:
            results = next_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['results']
            
            listings = []
            for item in results:
                estate = item.get('realEstate', {})
                properties = estate.get('properties', [{}])[0] if estate.get('properties') else {}
                
                # URL
                canonical_url = item.get('seo', {}).get('url')
                if not canonical_url:
                    continue
                
                # ID
                external_id = None
                match = re.search(r'/annunci/(\d+)/', canonical_url)
                if match:
                    external_id = match.group(1)
                
                if not external_id:
                    continue
                
                # Координаты
                lat, lon = self._extract_coords(item)
                
                listing = {
                    'external_id': f"immobiliare_{external_id}",
                    'url': canonical_url,
                    'title': properties.get('caption', ''),
                    'price': estate.get('price', {}).get('value'),
                    'property_type': self._normalize_property_type(properties.get('typology', {}).get('name', '')),
                    'rooms': self._extract_number(properties.get('rooms')),
                    'bathrooms': self._extract_number(properties.get('bathrooms')),
                    'area_sqm': self._extract_number(properties.get('surface')),
                    'floor': self._extract_floor(properties.get('floor')),
                    'address': properties.get('location', {}).get('caption', ''),
                    'latitude': lat,
                    'longitude': lon,
                    'images': self._extract_images(item),
                    'agency_name': estate.get('advertiser', {}).get('agency', {}).get('displayName'),
                    'features': [],
                    'description': '',  # Будет заполнено позже
                    'source': 'immobiliare',
                    'city': 'Roma',
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                listings.append(listing)
            
            return listings
            
        except KeyError as e:
            print(f"❌ Ошибка ключа при парсинге списка: {e}")
            print(f"   Доступные ключи: {list(next_data.get('props', {}).get('pageProps', {}).keys()) if next_data else 'N/A'}")
            return []
        except Exception as e:
            print(f"❌ Ошибка парсинга списка: {e}")
            return []
    
    def _extract_number(self, value) -> Optional[int]:
        if not value:
            return None
        match = re.search(r'\d+', str(value))
        return int(match.group(0)) if match else None
    
    def _extract_floor(self, floor_data) -> Optional[str]:
        """Извлекает этаж"""
        if not floor_data:
            return None
        if isinstance(floor_data, dict):
            return floor_data.get('value') or floor_data.get('abbreviation')
        return str(floor_data)
    
    def _extract_coords(self, item: Dict) -> tuple:
        try:
            estate = item.get('realEstate', {})
            properties = estate.get('properties', [{}])[0] if estate.get('properties') else {}
            
            location = properties.get('location', {})
            lat = location.get('latitude') or location.get('lat')
            lon = location.get('longitude') or location.get('lng')
            
            if lat and lon:
                return float(lat), float(lon)
            
            return None, None
        except:
            return None, None
    
    def _extract_images(self, item: Dict) -> List[str]:
        images = []
        try:
            estate = item.get('realEstate', {})
            properties = estate.get('properties', [{}])[0] if estate.get('properties') else {}
            
            multimedia = properties.get('multimedia', {})
            photos = multimedia.get('photos', [])
            
            for photo in photos[:20]:  # Максимум 20 изображений
                if isinstance(photo, dict) and 'urls' in photo:
                    urls = photo['urls']
                    # Берем лучшее качество
                    for size in ['large', 'medium', 'small']:
                        if size in urls and urls[size]:
                            if urls[size] not in images:
                                images.append(urls[size])
                            break
            
            return images
        except:
            return []
    
    def _normalize_property_type(self, type_str: str) -> str:
        """Нормализует тип недвижимости"""
        mapping = {
            'Appartamento': 'apartment',
            'Villa': 'house',
            'Casa': 'house',
            'Attico': 'penthouse',
            'Superattico': 'penthouse',
            'Monolocale': 'studio',
            'Studio': 'studio',
            'Stanza': 'room',
            'Camera': 'room'
        }
        return mapping.get(type_str, 'apartment')
    
    def parse_detail_page(self, html: str) -> Optional[str]:
        """Извлекает полное описание из детальной страницы"""
        try:
            next_data = self.extract_next_data(html)
            
            if not next_data:
                return None
            
            # Вариант 1: в props.listing
            page_props = next_data.get('props', {}).get('pageProps', {})
            listing_data = page_props.get('listing', {})
            
            if 'properties' in listing_data:
                desc = listing_data['properties'].get('description')
                if desc:
                    return desc
            
            # Вариант 2: в dehydratedState.queries
            queries = page_props.get('dehydratedState', {}).get('queries', [])
            for query in queries:
                state_data = query.get('state', {}).get('data', {})
                if 'properties' in state_data:
                    desc = state_data['properties'].get('description')
                    if desc:
                        return desc
            
            # Вариант 3: Поиск в HTML
            soup = BeautifulSoup(html, 'html.parser')
            desc_div = soup.find('div', class_=lambda x: x and 'description' in str(x).lower())
            if desc_div:
                return desc_div.get_text(strip=True)
            
            return None
            
        except Exception as e:
            return None
    
    async def scrape_multiple_pages(self, max_pages: int = 5):
        """Основной метод с параллельным парсингом (совместимый интерфейс)"""
        return await self.scrape_listings(num_pages=max_pages, max_details=0)
    
    async def scrape_listings(self, num_pages: int = 2, max_details: int = 10):
        """Основной метод парсинга"""
        print("=" * 80)
        print(f"🚀 ПАРСИНГ IMMOBILIARE.IT С ДЕТАЛЬНОЙ ИНФОРМАЦИЕЙ")
        print("=" * 80)
        print(f"📄 Страниц списков: {num_pages}")
        print(f"📝 Детальных страниц: до {max_details}")
        print("=" * 80)
        
        start_time = datetime.utcnow()
        
        async with aiohttp.ClientSession() as session:
            # ЭТАП 1: Собираем URL со страниц списков
            print("\n📋 ЭТАП 1: Сбор базовой информации")
            print("-" * 80)
            
            all_listings = []
            for page_num in range(1, num_pages + 1):
                if page_num == 1:
                    page_url = self.search_url
                else:
                    page_url = f"{self.search_url}&pag={page_num}"
                
                print(f"Страница {page_num}: {page_url}")
                html = await self.fetch_html(session, page_url, use_simple=True)
                
                if html:
                    print(f"    ✅ Получено {len(html)} символов")
                    listings = self.parse_list_page(html)
                    print(f"    📊 Найдено {len(listings)} объявлений")
                    all_listings.extend(listings)
                    self.stats['list_pages_success'] += 1
                else:
                    print(f"    ❌ Не удалось получить HTML")
                    self.stats['list_pages_failed'] += 1
            
            print(f"\n📊 ВСЕГО: {len(all_listings)} объявлений")
            
            # Ограничиваем количество детальных страниц
            listings_to_detail = all_listings[:max_details]
            
            # ЭТАП 2: Парсим детальные страницы
            print("\n" + "=" * 80)
            print(f"🔍 ЭТАП 2: Парсинг детальных страниц ({len(listings_to_detail)} шт)")
            print("=" * 80)
            
            for i, listing in enumerate(listings_to_detail, 1):
                print(f"[{i}/{len(listings_to_detail)}] {listing['url']}")
                
                detail_html = await self.fetch_html(session, listing['url'], use_simple=False)
                
                if detail_html:
                    description = self.parse_detail_page(detail_html)
                    
                    if description:
                        listing['description'] = description
                        self.stats['with_description'] += 1
                        print(f"    ✅ Описание: {len(description)} символов")
                    else:
                        print(f"    ⚠️ Описание не найдено")
                    
                    self.stats['details_success'] += 1
                else:
                    print(f"    ❌ Не удалось получить страницу")
                    self.stats['details_failed'] += 1
                
                # Статистика координат
                if listing.get('latitude'):
                    self.stats['with_coords'] += 1
        
        end_time = datetime.utcnow()
        elapsed = (end_time - start_time).total_seconds()
        
        # ИТОГИ
        print("\n" + "=" * 80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 80)
        print(f"📄 Страниц списков:")
        print(f"   ✅ Успешно: {self.stats['list_pages_success']}")
        print(f"   ❌ Ошибки: {self.stats['list_pages_failed']}")
        print()
        print(f"📝 Детальные страницы:")
        print(f"   ✅ Успешно: {self.stats['details_success']}")
        print(f"   ❌ Ошибки: {self.stats['details_failed']}")
        print()
        print(f"📊 Качество данных:")
        print(f"   📝 С полным описанием: {self.stats['with_description']}/{len(listings_to_detail)}")
        print(f"   🌍 С координатами: {self.stats['with_coords']}/{len(all_listings)}")
        print(f"   🖼️  С изображениями: {sum(1 for l in all_listings if l.get('images'))}/{len(all_listings)}")
        print()
        print(f"⏱️  Общее время: {elapsed:.1f} секунд")
        if listings_to_detail:
            print(f"⚡ Среднее время детальной страницы: {elapsed/len(listings_to_detail):.2f} сек")
        
        return all_listings


async def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', type=int, default=2, help='Страниц списков')
    parser.add_argument('--details', type=int, default=10, help='Детальных страниц')
    
    args = parser.parse_args()
    
    scraper = ImmobiliareSimpleScraper()
    listings = await scraper.scrape_listings(num_pages=args.pages, max_details=args.details)
    
    if listings:
        output_file = '/tmp/immobiliare_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(listings, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в {output_file}")


if __name__ == "__main__":
    asyncio.run(main())

