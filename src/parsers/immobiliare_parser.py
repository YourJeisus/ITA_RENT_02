#!/usr/bin/env python3
"""
Упрощенный парсер для Immobiliare.it через ScraperAPI
Парсит только главную страницу аренды в Риме без фильтров
"""
import asyncio
import aiohttp
import logging
import json
import re
import time
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from .base_parser import BaseParser
from ..core.config import settings

logger = logging.getLogger(__name__)


class ImmobiliareParser(BaseParser):
    """
    Упрощенный парсер для Immobiliare.it
    Парсит только главную страницу аренды в Риме
    """
    
    def __init__(self, enable_geocoding: bool = True):
        super().__init__(
            name="Immobiliare.it",
            base_url="https://www.immobiliare.it"
        )
        # Фиксированный URL главной страницы аренды в Риме
        self.main_page_url = "https://www.immobiliare.it/affitto-case/roma/"
        # Флаг для включения/выключения геокодирования
        self.enable_geocoding = enable_geocoding
    
    def build_search_url(self, filters: Dict[str, Any] = None, page: int = 1) -> str:
        """
        Построить URL для парсинга
        Игнорирует фильтры, всегда возвращает главную страницу
        """
        if page > 1:
            return f"{self.main_page_url}?pag={page}"
        return self.main_page_url
    
    async def get_html_with_scraperapi(self, url: str, retries: int = 3) -> Optional[str]:
        """
        Асинхронно получает HTML через ScraperAPI с JS рендерингом
        """
        if not settings.SCRAPERAPI_KEY:
            logger.error("❌ SCRAPERAPI_KEY не настроен")
            return None
        
        params = {
            'api_key': settings.SCRAPERAPI_KEY,
            'url': url,
            'render': 'true',
            'premium': 'true',
            'country_code': 'eu'
        }
        
        timeout = aiohttp.ClientTimeout(total=180)
        
        for attempt in range(retries):
            try:
                logger.info(f"📡 ScraperAPI запрос (попытка {attempt + 1}): {url}")
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get('https://api.scraperapi.com/', params=params) as response:
                        
                        if response.status >= 500:
                            logger.warning(f"⚠️ ScraperAPI ошибка {response.status}. Попытка {attempt + 1}/{retries}")
                            await asyncio.sleep(5 * (attempt + 1))
                            continue
                        
                        response.raise_for_status()
                        html_content = await response.text()
                        logger.info(f"✅ HTML получен, размер: {len(html_content)} символов")
                        return html_content
                        
            except aiohttp.ClientError as e:
                logger.error(f"❌ Ошибка ScraperAPI: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(5 * (attempt + 1))
                    
        return None
    
    def extract_next_data_json(self, html_content: str) -> Optional[Dict[str, Any]]:
        """
        Извлекает JSON из __NEXT_DATA__ тега
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            script_tag = soup.find('script', id='__NEXT_DATA__')
            if not script_tag:
                logger.warning("❌ Тег __NEXT_DATA__ не найден")
                return None
            return json.loads(script_tag.string)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            return None
    
    def extract_all_photos(self, listing_json: Dict[str, Any]) -> List[str]:
        """
        Извлекает ВСЕ фотографии из объявления
        """
        photos = []
        try:
            estate = listing_json.get('realEstate', {})
            properties = estate.get('properties', [{}])[0] if estate.get('properties') else {}
            
            multimedia = properties.get('multimedia', {})
            photo_list = multimedia.get('photos', [])
            
            for photo in photo_list:
                if isinstance(photo, dict) and 'urls' in photo:
                    urls = photo['urls']
                    # Добавляем все доступные размеры фото
                    for size in ['large', 'medium', 'small']:
                        if size in urls and urls[size]:
                            photos.append(urls[size])
                            break  # Берем только лучшее качество
            
            logger.info(f"📸 Найдено {len(photos)} фотографий для объявления")
            return photos
            
        except Exception as e:
            logger.error(f"❌ Ошибка извлечения фото: {e}")
            return []
    
    def parse_single_listing(self, listing_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Парсит одно объявление из JSON
        """
        try:
            estate = listing_json.get('realEstate', {})
            if not estate:
                return None
            
            properties = estate.get('properties', [{}])[0] if estate.get('properties') else {}
            
            # Основные данные
            title = properties.get('caption')
            canonical_url = listing_json.get('seo', {}).get('url')
            
            if not title or not canonical_url:
                logger.warning(f"⚠️ Пропущено объявление: нет URL или заголовка")
                return None
            
            # Извлекаем ID из URL
            external_id = None
            if canonical_url:
                match = re.search(r'/annunci/(\d+)/', canonical_url)
                if match:
                    external_id = match.group(1)
            
            # Цена
            price_info = estate.get('price', {})
            price = price_info.get('value')
            
            # Характеристики
            rooms = None
            area = None
            bathrooms = None
            
            rooms_raw = properties.get('rooms', '')
            if rooms_raw:
                match = re.search(r'\d+', str(rooms_raw))
                if match:
                    rooms = int(match.group(0))
            
            area_raw = properties.get('surface', '')
            if area_raw:
                match = re.search(r'\d+', str(area_raw))
                if match:
                    area = int(match.group(0))
            
            bathrooms_raw = properties.get('bathrooms', '')
            if bathrooms_raw:
                match = re.search(r'\d+', str(bathrooms_raw))
                if match:
                    bathrooms = int(match.group(0))
            
            # Извлекаем ВСЕ фотографии
            all_photos = self.extract_all_photos(listing_json)
            
            # Координаты и адрес (в зависимости от настроек)
            if self.enable_geocoding:
                latitude, longitude = self._extract_coordinates(listing_json)
                address = self._extract_address(listing_json)
            else:
                latitude, longitude = None, None
                address = None
            
            # Тип недвижимости
            property_type = self._normalize_property_type(properties, title)
            
            return {
                'external_id': external_id,
                'source': 'immobiliare',
                'url': canonical_url,
                'title': title,
                'description': properties.get('description', ''),
                'price': price,
                'price_currency': 'EUR',
                'property_type': property_type,
                'rooms': rooms,
                'bathrooms': bathrooms,
                'area': area,
                'floor': str(properties.get('floor', '')),
                'furnished': None,
                'pets_allowed': None,
                'features': None,
                'address': address,
                'city': 'Roma',
                'district': None,
                'postal_code': None,
                'latitude': latitude,
                'longitude': longitude,
                'images': all_photos,  # ВСЕ фотографии списком
                'virtual_tour_url': None,
                'agency_name': estate.get('advertiser', {}).get('agency', {}).get('displayName'),
                'contact_info': None,
                'is_active': True,
                'published_at': None,
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга объявления: {e}")
            return None
    
    async def scrape_single_page(self, page_num: int) -> List[Dict[str, Any]]:
        """
        Асинхронно парсит одну страницу
        
        Args:
            page_num: Номер страницы
            
        Returns:
            Список объявлений с этой страницы
        """
        try:
            # Строим URL страницы
            page_url = self.build_search_url(page=page_num)
            logger.info(f"📄 Обрабатываем страницу {page_num}: {page_url}")
            
            # Получаем HTML через ScraperAPI
            html_content = await self.get_html_with_scraperapi(page_url)
            if not html_content:
                logger.error(f"❌ Не удалось получить HTML для страницы {page_num}")
                return []
            
            # Извлекаем JSON данные
            json_data = self.extract_next_data_json(html_content)
            if not json_data:
                logger.warning(f"⚠️ Не найден JSON на странице {page_num}")
                return []
            
            # Извлекаем объявления из JSON
            try:
                results = json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['results']
            except (KeyError, IndexError, TypeError):
                logger.info(f"🔚 Больше нет объявлений на странице {page_num}")
                return []
            
            if not results:
                logger.info(f"🔚 Пустая страница {page_num}")
                return []
            
            logger.info(f"📋 Найдено {len(results)} объявлений на странице {page_num}")
            
            # Парсим каждое объявление
            page_listings = []
            for listing_json in results:
                parsed_listing = self.parse_single_listing(listing_json)
                if parsed_listing:
                    page_listings.append(parsed_listing)
            
            logger.info(f"✅ Страница {page_num}: обработано {len(page_listings)} объявлений")
            return page_listings
            
        except Exception as e:
            logger.error(f"❌ Ошибка на странице {page_num}: {e}")
            return []

    async def scrape_all_listings(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        ОСНОВНОЙ МЕТОД: Асинхронно парсит все объявления с главной страницы
        
        Args:
            max_pages: Максимальное количество страниц для парсинга
            
        Returns:
            Список всех объявлений
        """
        logger.info("🚀 НАЧИНАЕМ АСИНХРОННЫЙ ПАРСИНГ IMMOBILIARE.IT")
        logger.info(f"🎯 URL: {self.main_page_url}")
        logger.info(f"📄 Максимум страниц: {max_pages}")
        logger.info(f"⚡ Режим: ПАРАЛЛЕЛЬНЫЙ (все страницы одновременно)")
        
        # Создаем задачи для всех страниц
        tasks = []
        for page_num in range(1, max_pages + 1):
            task = self.scrape_single_page(page_num)
            tasks.append(task)
        
        logger.info(f"🔄 Запускаем {len(tasks)} задач параллельно...")
        
        # Выполняем все задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Собираем все объявления
        all_listings = []
        successful_pages = 0
        error_pages = 0
        
        for page_num, result in enumerate(results, 1):
            if isinstance(result, Exception):
                logger.error(f"❌ Ошибка на странице {page_num}: {result}")
                error_pages += 1
            elif isinstance(result, list):
                all_listings.extend(result)
                if result:  # Если есть объявления
                    successful_pages += 1
            else:
                logger.warning(f"⚠️ Неожиданный результат для страницы {page_num}: {type(result)}")
        
        logger.info(f"🎉 АСИНХРОННЫЙ ПАРСИНГ ЗАВЕРШЕН!")
        logger.info(f"📊 Статистика:")
        logger.info(f"   ✅ Успешных страниц: {successful_pages}")
        logger.info(f"   ❌ Ошибок: {error_pages}")
        logger.info(f"   📋 Всего объявлений: {len(all_listings)}")
        
        return all_listings
    
    # Вспомогательные методы
    def _extract_coordinates(self, listing_json: Dict[str, Any]) -> tuple[Optional[float], Optional[float]]:
        """Извлечь координаты из JSON"""
        try:
            estate = listing_json.get('realEstate', {})
            properties = estate.get('properties', [{}])[0] if estate.get('properties') else {}
            
            # Проверяем разные места в JSON
            location_sources = [
                properties.get('location', {}),
                estate.get('location', {}),
                properties.get('coordinates', {}),
                estate.get('coordinates', {})
            ]
            
            for location in location_sources:
                lat = location.get('latitude') or location.get('lat')
                lon = location.get('longitude') or location.get('lng')
                
                if lat and lon:
                    lat, lon = float(lat), float(lon)
                    # Проверка для Италии
                    if 35.0 <= lat <= 47.0 and 6.0 <= lon <= 19.0:
                        return lat, lon
            
            return None, None
            
        except Exception as e:
            logger.debug(f"Ошибка извлечения координат: {e}")
            return None, None
    
    def _extract_address(self, listing_json: Dict[str, Any]) -> Optional[str]:
        """Извлечь адрес из JSON"""
        try:
            estate = listing_json.get('realEstate', {})
            properties = estate.get('properties', [{}])[0] if estate.get('properties') else {}
            
            # Проверяем разные поля с адресом
            address_fields = [
                properties.get('address'),
                properties.get('location', {}).get('address'),
                properties.get('street'),
                estate.get('address')
            ]
            
            for addr in address_fields:
                if addr and isinstance(addr, str) and len(addr.strip()) > 5:
                    return addr.strip()
            
            return None
            
        except Exception as e:
            logger.debug(f"Ошибка извлечения адреса: {e}")
            return None
    
    def _normalize_property_type(self, properties: Dict[str, Any], title: str) -> str:
        """Нормализовать тип недвижимости"""
        # Извлекаем тип из JSON
        property_type = None
        if properties.get('typology', {}).get('name'):
            property_type = properties['typology']['name']
        
        # Маппинг типов
        type_mapping = {
            'Appartamento': 'apartment',
            'Villa': 'house',
            'Casa': 'house',
            'Attico': 'apartment',
            'Loft': 'apartment',
            'Monolocale': 'studio',
            'Bilocale': 'apartment',
            'Trilocale': 'apartment',
            'Quadrilocale': 'apartment'
        }
        
        if property_type and property_type in type_mapping:
            return type_mapping[property_type]
        
        # Анализ заголовка
        if 'monolocale' in title.lower():
            return 'studio'
        elif any(word in title.lower() for word in ['villa', 'casa']):
            return 'house'
        
        return 'apartment'  # По умолчанию
    
    # Реализация абстрактных методов BaseParser
    def parse_listings_from_page(self, html_content: str) -> List[Dict[str, Any]]:
        """Реализация абстрактного метода"""
        json_data = self.extract_next_data_json(html_content)
        if not json_data:
            return []
        
        try:
            results = json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['results']
        except (KeyError, IndexError, TypeError):
            return []
        
        listings = []
        for listing_json in results:
            parsed = self.parse_single_listing(listing_json)
            if parsed:
                listings.append(parsed)
        
        return listings
    
    def normalize_listing_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Реализация абстрактного метода"""
        return raw_data
    
    # Для совместимости с существующим кодом
    async def scrape_listings(self, filters: Dict[str, Any] = None, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Совместимость с существующим API"""
        return await self.scrape_all_listings(max_pages=max_pages) 