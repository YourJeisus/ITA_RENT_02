#!/usr/bin/env python3
"""
🚀 ПАРАЛЛЕЛЬНЫЙ ПАРСЕР IDEALISTA
Скорость: в 5-10 раз быстрее последовательного парсинга
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

class IdealistaScraper:
    """Параллельный парсер с ограничением одновременных запросов"""
    
    def __init__(self, max_concurrent: int = 10, enable_geocoding: bool = False):
        self.base_url = "https://www.idealista.it"
        self.api_url = "https://api.scraperapi.com/"
        self.api_key = settings.SCRAPERAPI_KEY
        self.max_concurrent = max_concurrent  # Максимум одновременных запросов
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.enable_geocoding = enable_geocoding  # Для совместимости с интерфейсом
        
        # Статистика
        self.stats = {
            'success': 0,
            'failed': 0,
            'coords_from_html': 0,
            'coords_from_geocoding': 0,
            'coords_not_found': 0
        }
    
    def extract_area_from_features(self, features: List[str]) -> Optional[int]:
        """Извлекает площадь из features"""
        for feat in features:
            match = re.search(r'(\d+)\s*m[²q]', feat, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def extract_rooms_from_features(self, features: List[str]) -> Optional[int]:
        """Извлекает количество комнат из features"""
        for feat in features:
            match = re.search(r'(\d+)\s*(?:local|stanz)', feat, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def extract_bathrooms_from_features(self, features: List[str]) -> Optional[int]:
        """Извлекает количество ванных из features"""
        for feat in features:
            match = re.search(r'(\d+)\s*bagn', feat, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def extract_floor_from_features(self, features: List[str]) -> Optional[str]:
        """Извлекает этаж из features"""
        for feat in features:
            if 'piano' in feat.lower():
                match = re.search(r'(\d+)[º°]?\s*piano', feat, re.IGNORECASE)
                if match:
                    return match.group(1)
                if 'terra' in feat.lower():
                    return '0'
                return feat.strip()
        return None

    async def fetch_html(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Получает HTML через ScraperAPI с семафором для ограничения параллелизма"""
        async with self.semaphore:  # Ограничиваем количество одновременных запросов
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
                    else:
                        return None
            except Exception as e:
                return None
    
    def parse_listing_card(self, container) -> Optional[Dict[str, Any]]:
        """Парсит карточку объявления из списка"""
        try:
            external_id = container.get('data-adid') or container.get('data-element-id')
            if not external_id:
                return None
            
            title_elem = container.find('a', class_='item-link')
            if not title_elem or not title_elem.get('href'):
                return None
            
            detail_url = self.base_url + title_elem['href']
            
            return {
                'external_id': f"idealista_{external_id}",
                'url': detail_url
            }
        except Exception as e:
            return None
    
    def parse_detail_page(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """Парсит детальную страницу объявления"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            data = {'url': url, 'scraped_at': datetime.utcnow().isoformat()}
            
            # Заголовок
            title_elem = soup.find('h1', class_='main-info__title-main')
            if title_elem:
                data['title'] = title_elem.get_text(strip=True)
            
            # Цена
            price_elem = soup.find('span', class_='info-data-price')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                numbers = re.findall(r'\d+', price_text.replace('.', ''))
                if numbers:
                    data['price'] = int(''.join(numbers))
            
            # Адрес
            address_elem = soup.find('span', class_='main-info__title-minor')
            if address_elem:
                data['address'] = address_elem.get_text(strip=True)
            
            # Координаты из Google Maps Static API
            all_text = str(soup)
            maps_match = re.search(r'maps\.googleapis\.com/maps/api/staticmap[^"\'<>]*center=([\d.]+)%2C([\d.]+)', all_text)
            if maps_match:
                data['latitude'] = float(maps_match.group(1))
                data['longitude'] = float(maps_match.group(2))
            
            # Описание
            description_elem = soup.find('div', class_='comment')
            if description_elem:
                for button in description_elem.find_all('button'):
                    button.decompose()
                data['description'] = description_elem.get_text(strip=True)
            
            # Особенности
            features = []
            details_section = soup.find('div', class_='details-property')
            if details_section:
                feature_items = details_section.find_all('li')
                for item in feature_items:
                    feature_text = item.get_text(strip=True)
                    if feature_text:
                        features.append(feature_text)
            
            data['features'] = features
            
            # Изображения (улучшенный парсинг)
            images = []
            
            # Вариант 1: detail-image
            for img in soup.find_all('img'):
                img_url = img.get('src') or img.get('data-src') or img.get('data-ondemand-img')
                if img_url and img_url.startswith('http'):
                    # Исключаем карты и иконки
                    if ('maps.googleapis.com' not in img_url and 
                        'idealista.it' in img_url and
                        any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp'])):
                        if img_url not in images:
                            images.append(img_url)
            
            # Вариант 2: Поиск в JavaScript через регулярки
            all_text = str(soup)
            js_images = re.findall(r'https://img\d*\.idealista\.it[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)', all_text)
            for img_url in js_images:
                if img_url not in images:
                    images.append(img_url)
            
            data['images'] = images[:20]  # Ограничиваем до 20 изображений
            
            # Контакт
            contact_elem = soup.find('p', class_='advertiser-name')
            if contact_elem:
                data['contact_name'] = contact_elem.get_text(strip=True)
            
            # ID и метаданные
            id_match = re.search(r'/immobile/(\d+)/', url)
            if id_match:
                data['external_id'] = f"idealista_{id_match.group(1)}"
            
            data['source'] = 'idealista'
            data['city'] = 'Roma'
            
            # Извлечение характеристик из features
            if features:
                area = self.extract_area_from_features(features)
                if area:
                    data['area_sqm'] = area
                
                rooms = self.extract_rooms_from_features(features)
                if rooms:
                    data['rooms'] = rooms
                
                bathrooms = self.extract_bathrooms_from_features(features)
                if bathrooms:
                    data['bathrooms'] = bathrooms
                
                floor = self.extract_floor_from_features(features)
                if floor:
                    data['floor'] = floor
            
            return data
            
        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            return None
    
    async def scrape_single_listing(self, session: aiohttp.ClientSession, url: str, index: int, total: int) -> Optional[Dict[str, Any]]:
        """Парсит одно объявление"""
        print(f"[{index}/{total}] Запрашиваем: {url}")
        
        html = await self.fetch_html(session, url)
        
        if not html:
            self.stats['failed'] += 1
            print(f"    ❌ Не удалось получить HTML")
            return None
        
        listing_data = self.parse_detail_page(html, url)
        
        if listing_data:
            self.stats['success'] += 1
            
            # Статистика координат
            if listing_data.get('latitude'):
                self.stats['coords_from_html'] += 1
            
            # Короткий вывод
            coords_status = "🌍" if listing_data.get('latitude') else "❌"
            images_count = len(listing_data.get('images', []))
            print(f"    ✅ {listing_data.get('price', 0)}€ | {listing_data.get('address', 'N/A')[:30]} | {coords_status} | 🖼️  {images_count}")
        else:
            self.stats['failed'] += 1
            print(f"    ⚠️ Не удалось распарсить")
        
        return listing_data
    
    async def scrape_list_page(self, session: aiohttp.ClientSession, page_num: int) -> List[str]:
        """Парсит страницу списка объявлений"""
        if page_num == 1:
            list_url = f"{self.base_url}/affitto-case/roma-roma/?ordine=pubblicazione-desc"
        else:
            list_url = f"{self.base_url}/affitto-case/roma-roma/lista-{page_num}.htm?ordine=pubblicazione-desc"
        
        print(f"\n🔄 Страница {page_num}: {list_url}")
        
        html = await self.fetch_html(session, list_url)
        
        if not html:
            print(f"   ❌ Не удалось получить HTML")
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        containers = soup.find_all('article', class_='item')
        
        print(f"   ✅ Найдено {len(containers)} объявлений")
        
        urls = []
        for container in containers:
            listing_data = self.parse_listing_card(container)
            if listing_data:
                urls.append(listing_data['url'])
        
        return urls
    
    async def scrape_multiple_pages(self, max_pages: int = 5):
        """Основной метод с параллельным парсингом (совместимый интерфейс)"""
        return await self.scrape_parallel(num_pages=max_pages)
    
    async def scrape_parallel(self, num_pages: int = 2):
        """Основной метод с параллельным парсингом"""
        print("=" * 80)
        print(f"🚀 ПАРАЛЛЕЛЬНЫЙ ПАРСИНГ IDEALISTA (до {self.max_concurrent} одновременно)")
        print("=" * 80)
        print(f"📄 Страниц списка: {num_pages}")
        print("=" * 80)
        
        start_time = datetime.utcnow()
        
        async with aiohttp.ClientSession() as session:
            # ЭТАП 1: Собираем URL со страниц списков
            print("\n📋 ЭТАП 1: Сбор URL объявлений")
            print("-" * 80)
            
            # Параллельно парсим все страницы списков
            list_tasks = [
                self.scrape_list_page(session, page_num)
                for page_num in range(1, num_pages + 1)
            ]
            
            list_results = await asyncio.gather(*list_tasks)
            
            # Объединяем все URL
            all_urls = []
            for urls in list_results:
                all_urls.extend(urls)
            
            # Убираем дубликаты
            all_urls = list(dict.fromkeys(all_urls))
            
            print(f"\n{'=' * 80}")
            print(f"📊 ИТОГО собрано {len(all_urls)} уникальных URL")
            print(f"{'=' * 80}")
            
            # ЭТАП 2: Параллельно парсим детальные страницы
            print("\n🔍 ЭТАП 2: Параллельный парсинг детальных страниц")
            print("-" * 80)
            
            # Создаем задачи для всех URL
            detail_tasks = [
                self.scrape_single_listing(session, url, i+1, len(all_urls))
                for i, url in enumerate(all_urls)
            ]
            
            # Запускаем все задачи параллельно
            results = await asyncio.gather(*detail_tasks)
            
            # Фильтруем None
            all_listings = [r for r in results if r is not None]
        
        end_time = datetime.utcnow()
        elapsed = (end_time - start_time).total_seconds()
        
        # ИТОГОВАЯ СТАТИСТИКА
        print("\n" + "=" * 80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 80)
        print(f"✅ Успешно: {self.stats['success']}")
        print(f"❌ Ошибки: {self.stats['failed']}")
        print(f"🌍 Координаты из HTML: {self.stats['coords_from_html']}/{self.stats['success']} ({self.stats['coords_from_html']/max(self.stats['success'],1)*100:.1f}%)")
        print()
        print(f"⏱️  Общее время: {elapsed:.1f} секунд")
        print(f"⚡ Среднее время на объявление: {elapsed/len(all_urls):.1f} сек")
        print(f"🚀 Скорость: {len(all_urls)/elapsed*60:.1f} объявлений/минуту")
        
        return all_listings


async def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Параллельный парсер Idealista')
    parser.add_argument('--pages', type=int, default=2, help='Количество страниц (по умолчанию: 2)')
    parser.add_argument('--concurrent', type=int, default=10, help='Одновременных запросов (по умолчанию: 10)')
    
    args = parser.parse_args()
    
    scraper = IdealistaParallelScraper(max_concurrent=args.concurrent)
    
    # Парсим
    listings = await scraper.scrape_parallel(num_pages=args.pages)
    
    # Сохраняем
    if listings:
        output_file = f'/tmp/idealista_parallel_results.json'
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

