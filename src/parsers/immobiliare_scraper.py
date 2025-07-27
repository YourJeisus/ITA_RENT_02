#!/usr/bin/env python3
"""
🚀 НОВЫЙ АСИНХРОННЫЙ СКРАПЕР ДЛЯ IMMOBILIARE.IT V2
Создан с нуля на основе актуальной документации ScraperAPI

Основные принципы:
✅ Правильная реализация ScraperAPI Async API
✅ Job submission -> Status polling -> Result extraction
✅ Правильная дедупликация по external_id
✅ Обработка разных страниц с разными объявлениями
✅ Fallback на обычный API при проблемах
✅ Геокодирование через OpenStreetMap
"""
import asyncio
import aiohttp
import logging
import json
import re
import time
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from bs4 import BeautifulSoup
from ..core.config import settings

logger = logging.getLogger(__name__)


class ImmobiliareScraper:
    """
    Новый асинхронный скрапер для Immobiliare.it
    Правильная реализация ScraperAPI Async API
    """
    
    def __init__(self, enable_geocoding: bool = True):
        self.name = "Immobiliare.it Async Scraper V2"
        self.base_url = "https://www.immobiliare.it"
        self.search_url = "https://www.immobiliare.it/affitto-case/roma/?criterio=data&ordine=desc"
        self.enable_geocoding = enable_geocoding
        
        # ScraperAPI endpoints
        self.async_jobs_url = "https://async.scraperapi.com/jobs"
        self.sync_api_url = "https://api.scraperapi.com"
        
        # Настройки таймаутов
        self.job_submit_timeout = 30
        self.job_poll_timeout = 300  # 5 минут максимум
        self.sync_request_timeout = 70  # Рекомендуется в документации
        
        # Кеш для дедупликации
        self.seen_listing_ids: Set[str] = set()
    
    def build_page_url(self, page: int) -> str:
        """Строит URL для конкретной страницы"""
        if page <= 1:
            return self.search_url
        return f"{self.search_url}&pag={page}"
    
    async def submit_async_job(self, url: str, page_num: int) -> Optional[Dict[str, Any]]:
        """
        Отправляет задачу в ScraperAPI Async Jobs API
        
        Согласно документации:
        POST https://async.scraperapi.com/jobs
        {
            "apiKey": "YOUR_API_KEY",
            "url": "target_url",
            "render": true/false,
            "premium": true/false,
            ...
        }
        """
        if not settings.SCRAPERAPI_KEY:
            logger.error("❌ SCRAPERAPI_KEY не установлен")
            return None
        
        payload = {
            "apiKey": settings.SCRAPERAPI_KEY,
            "url": url,
            "render": False,  # Не используем JS рендеринг (он вызывал ошибки)
            "premium": False,  # Базовые прокси
            "country_code": "it",
            "device_type": "desktop"
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        timeout = aiohttp.ClientTimeout(total=self.job_submit_timeout)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.async_jobs_url,
                    json=payload,
                    headers=headers
                ) as response:
                    
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            job_data = json.loads(response_text)
                            job_id = job_data.get("id")
                            status = job_data.get("status")
                            status_url = job_data.get("statusUrl")
                            
                            logger.debug(f"📤 Job {job_id} создан для страницы {page_num}")
                            return {
                                "id": job_id,
                                "status": status,
                                "statusUrl": status_url,
                                "page_num": page_num,
                                "url": url
                            }
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ Ошибка парсинга JSON ответа: {e}")
                            return None
                    else:
                        logger.error(f"❌ HTTP ошибка {response.status} для страницы {page_num}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Исключение при создании job для страницы {page_num}: {e}")
            return None
    
    async def poll_job_status(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Опрашивает статус задачи до завершения
        
        GET https://async.scraperapi.com/jobs/{job_id}
        """
        job_id = job_data.get("id")
        status_url = job_data.get("statusUrl")
        page_num = job_data.get("page_num")
        
        if not status_url:
            logger.error(f"❌ Нет statusUrl для job {job_id}")
            return None
        
        start_time = time.time()
        poll_interval = 3  # Начинаем с 3 секунд
        max_poll_interval = 15  # Максимум 15 секунд
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                while time.time() - start_time < self.job_poll_timeout:
                    elapsed = time.time() - start_time
                    
                    try:
                        async with session.get(status_url) as response:
                            if response.status != 200:
                                await asyncio.sleep(poll_interval)
                                continue
                            
                            response_text = await response.text()
                            
                            try:
                                job_status = json.loads(response_text)
                            except json.JSONDecodeError:
                                await asyncio.sleep(poll_interval)
                                continue
                            
                            status = job_status.get("status")
                            
                            if status == "finished":
                                logger.debug(f"✅ Job {job_id} (страница {page_num}) завершен за {elapsed:.1f}s")
                                return job_status
                            
                            elif status == "failed":
                                fail_reason = job_status.get("failReason", "unknown")
                                logger.error(f"❌ Job {job_id} провалился: {fail_reason}")
                                return None
                            
                            elif status in ["queued", "running"]:
                                # Просто ждем без лишних логов
                                await asyncio.sleep(poll_interval)
                                # Постепенно увеличиваем интервал
                                poll_interval = min(poll_interval * 1.2, max_poll_interval)
                                continue
                            
                            else:
                                logger.warning(f"⚠️ Неизвестный статус {status} для job {job_id}")
                                await asyncio.sleep(poll_interval)
                                continue
                    
                    except asyncio.TimeoutError:
                        logger.warning(f"⚠️ Таймаут при опросе job {job_id}")
                        await asyncio.sleep(poll_interval)
                        continue
                    
                    except Exception as e:
                        logger.warning(f"⚠️ Ошибка при опросе job {job_id}: {e}")
                        await asyncio.sleep(poll_interval)
                        continue
                
                # Превышен общий таймаут
                logger.error(f"⏰ Превышено время ожидания для job {job_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Критическая ошибка при опросе job {job_id}: {e}")
            return None
    
    async def scrape_page_sync_fallback(self, page_num: int) -> Optional[str]:
        """
        Fallback на обычный ScraperAPI при проблемах с Async API
        """
        url = self.build_page_url(page_num)
        
        params = {
            "api_key": settings.SCRAPERAPI_KEY,
            "url": url,
            "render": "false",  # Без JS рендеринга
        }
        
        timeout = aiohttp.ClientTimeout(total=self.sync_request_timeout)
        
        try:
            logger.info(f"🔄 Fallback sync API для страницы {page_num}")
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.sync_api_url, params=params) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Проверяем, что получили валидный контент
                        if len(html_content) > 5000 and "immobiliare" in html_content.lower():
                            logger.info(f"✅ Sync fallback успешен для страницы {page_num}")
                            return html_content
                        else:
                            logger.warning(f"⚠️ Получен невалидный контент для страницы {page_num}")
                            return None
                    else:
                        logger.error(f"❌ Sync fallback HTTP {response.status} для страницы {page_num}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Sync fallback исключение для страницы {page_num}: {e}")
            return None
    
    async def scrape_single_page(self, page_num: int) -> List[Dict[str, Any]]:
        """
        Скрапит одну страницу через Async API с fallback
        """
        url = self.build_page_url(page_num)
        
        # Шаг 1: Попытка через Async API
        job_data = await self.submit_async_job(url, page_num)
        
        html_content = None
        
        if job_data:
            # Шаг 2: Ожидание завершения job
            job_result = await self.poll_job_status(job_data)
            
            if job_result:
                # Шаг 3: Извлечение HTML из результата
                response_data = job_result.get("response", {})
                html_content = response_data.get("body")
                status_code = response_data.get("statusCode", 0)
                
                if html_content and status_code == 200:
                    logger.info(f"✅ Async API успешен для страницы {page_num}")
                else:
                    logger.warning(f"⚠️ Проблема с Async API для страницы {page_num} (код: {status_code})")
                    html_content = None
        
        # Fallback на sync API если async не сработал
        if not html_content:
            html_content = await self.scrape_page_sync_fallback(page_num)
        
        if not html_content:
            logger.error(f"❌ Не удалось получить HTML для страницы {page_num}")
            return []
        
        # Парсим HTML
        return await self.parse_html_content(html_content, page_num)
    
    async def parse_html_content(self, html_content: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Парсит HTML контент и извлекает объявления
        """
        try:
            # Извлекаем JSON данные из __NEXT_DATA__
            soup = BeautifulSoup(html_content, 'html.parser')
            script_tag = soup.find('script', id='__NEXT_DATA__')
            
            if not script_tag:
                logger.warning(f"⚠️ Не найден __NEXT_DATA__ на странице {page_num}")
                return []
            
            try:
                json_data = json.loads(script_tag.string)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Ошибка парсинга JSON на странице {page_num}: {e}")
                return []
            
            # Извлекаем массив объявлений
            try:
                results = json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['results']
            except (KeyError, IndexError, TypeError) as e:
                logger.warning(f"⚠️ Не найден массив results на странице {page_num}: {e}")
                return []
            
            if not results:
                logger.info(f"🔚 Пустая страница {page_num}")
                return []
            
            # Парсим каждое объявление
            page_listings = []
            for listing_json in results:
                parsed_listing = await self.parse_single_listing(listing_json)
                if parsed_listing:
                    # Проверяем дедупликацию
                    listing_id = parsed_listing.get('external_id')
                    if listing_id and listing_id not in self.seen_listing_ids:
                        self.seen_listing_ids.add(listing_id)
                        page_listings.append(parsed_listing)
            
            logger.debug(f"✅ Страница {page_num}: {len(page_listings)}/{len(results)} уникальных")
            return page_listings
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга HTML страницы {page_num}: {e}")
            return []
    
    async def parse_single_listing(self, listing_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
                return None
            
            # Извлекаем ID из URL
            external_id = None
            if canonical_url:
                match = re.search(r'/annunci/(\d+)/', canonical_url)
                if match:
                    external_id = match.group(1)
            
            if not external_id:
                logger.warning(f"⚠️ Не удалось извлечь ID из URL: {canonical_url}")
                return None
            
            # Цена
            price_info = estate.get('price', {})
            price = price_info.get('value')
            
            # Характеристики
            rooms = self._extract_number(properties.get('rooms', ''))
            area = self._extract_number(properties.get('surface', ''))
            bathrooms = self._extract_number(properties.get('bathrooms', ''))
            
            # Фотографии
            images = self._extract_images(listing_json)
            
            # Адрес и координаты
            address = self._extract_address(listing_json)
            
            if self.enable_geocoding:
                latitude, longitude = await self._extract_coordinates_with_geocoding(listing_json)
            else:
                latitude, longitude = self._extract_coordinates(listing_json)
            
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
                'furnished': self._is_furnished(properties, title),
                'pets_allowed': None,
                'features': self._extract_features(properties),
                'address': address,
                'city': 'Roma',
                'district': None,
                'postal_code': None,
                'latitude': latitude,
                'longitude': longitude,
                'images': images,
                'virtual_tour_url': None,
                'agency_name': estate.get('advertiser', {}).get('agency', {}).get('displayName'),
                'contact_info': None,
                'is_active': True,
                'published_at': None,
                'scraped_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга объявления: {e}")
            return None
    
    async def scrape_multiple_pages(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        ОСНОВНОЙ МЕТОД: Скрапит несколько страниц асинхронно
        """
        logger.info(f"🚀 Запуск парсинга {max_pages} страниц...")
        
        start_time = time.time()
        
        # Очищаем кеш дедупликации
        self.seen_listing_ids.clear()
        
        # Создаем задачи для всех страниц с ограничением параллелизма
        semaphore = asyncio.Semaphore(3)  # Максимум 3 параллельных запроса
        
        async def scrape_page_with_semaphore(page_num: int):
            async with semaphore:
                return await self.scrape_single_page(page_num)
        
        # Создаем задачи
        tasks = []
        for page_num in range(1, max_pages + 1):
            task = scrape_page_with_semaphore(page_num)
            tasks.append(task)
        
        logger.info(f"🔄 Запускаем {len(tasks)} задач с семафором...")
        
        # Выполняем все задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Собираем результаты
        all_listings = []
        successful_pages = 0
        error_pages = 0
        
        for page_num, result in enumerate(results, 1):
            if isinstance(result, Exception):
                logger.error(f"❌ Ошибка на странице {page_num}: {result}")
                error_pages += 1
            elif isinstance(result, list):
                all_listings.extend(result)
                if result:
                    successful_pages += 1
                else:
                    logger.debug(f"🔚 Страница {page_num}: пустая")
            else:
                logger.warning(f"⚠️ Неожиданный результат для страницы {page_num}: {type(result)}")
        
        elapsed_time = time.time() - start_time
        
        logger.info(f"✅ Парсинг завершен: {len(all_listings)} объявлений за {elapsed_time:.1f}с")
        
        return all_listings
    
    # Вспомогательные методы
    def _extract_number(self, value: str) -> Optional[int]:
        """Извлекает число из строки"""
        if not value:
            return None
        match = re.search(r'\d+', str(value))
        return int(match.group(0)) if match else None
    
    def _extract_images(self, listing_json: Dict[str, Any]) -> List[str]:
        """Извлекает все фотографии из объявления"""
        images = []
        try:
            estate = listing_json.get('realEstate', {})
            properties = estate.get('properties', [{}])[0] if estate.get('properties') else {}
            
            multimedia = properties.get('multimedia', {})
            photo_list = multimedia.get('photos', [])
            
            for photo in photo_list:
                if isinstance(photo, dict) and 'urls' in photo:
                    urls = photo['urls']
                    # Берем лучшее качество
                    for size in ['large', 'medium', 'small']:
                        if size in urls and urls[size]:
                            photo_url = urls[size]
                            if photo_url and photo_url not in images:
                                images.append(photo_url)
                            break
            
            return images
            
        except Exception as e:
            logger.debug(f"Ошибка извлечения фото: {e}")
            return []
    
    def _extract_address(self, listing_json: Dict[str, Any]) -> Optional[str]:
        """Извлекает адрес из JSON"""
        try:
            estate = listing_json.get('realEstate', {})
            properties = estate.get('properties', [{}])[0] if estate.get('properties') else {}
            
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
            
        except Exception:
            return None
    
    def _extract_coordinates(self, listing_json: Dict[str, Any]) -> tuple[Optional[float], Optional[float]]:
        """Извлекает координаты из JSON"""
        try:
            estate = listing_json.get('realEstate', {})
            properties = estate.get('properties', [{}])[0] if estate.get('properties') else {}
            
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
            
        except Exception:
            return None, None
    
    async def _extract_coordinates_with_geocoding(self, listing_json: Dict[str, Any]) -> tuple[Optional[float], Optional[float]]:
        """Извлекает координаты из JSON или через геокодирование"""
        # Сначала пытаемся найти в JSON
        lat, lon = self._extract_coordinates(listing_json)
        if lat and lon:
            return lat, lon
        
        # Если нет в JSON, пытаемся геокодировать адрес
        address = self._extract_address(listing_json)
        if address and len(address.strip()) > 10:
            return await self._geocode_address(address, "Roma, Italy")
        
        return None, None
    
    async def _geocode_address(self, address: str, city: str) -> tuple[Optional[float], Optional[float]]:
        """Геокодирование адреса через OpenStreetMap Nominatim API"""
        try:
            full_address = f"{address}, {city}"
            url = "https://nominatim.openstreetmap.org/search"
            
            params = {
                'q': full_address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'it',
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'ITA_RENT_BOT/2.0 (rental search bot)'
            }
            
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data and len(data) > 0:
                            result = data[0]
                            lat = float(result.get('lat', 0))
                            lon = float(result.get('lon', 0))
                            
                            if 35.0 <= lat <= 47.0 and 6.0 <= lon <= 19.0:
                                return lat, lon
                        
                    await asyncio.sleep(1)  # Уважаем лимиты API
                    
            return None, None
            
        except Exception as e:
            logger.debug(f"Ошибка геокодирования для '{address}': {e}")
            return None, None
    
    def _normalize_property_type(self, properties: Dict[str, Any], title: str) -> str:
        """Нормализует тип недвижимости"""
        property_type = None
        if properties.get('typology', {}).get('name'):
            property_type = properties['typology']['name']
        
        type_mapping = {
            'Appartamento': 'apartment',
            'Villa': 'house',
            'Casa': 'house',
            'Villetta': 'house',
            'Attico': 'penthouse',         # Исправлено: пентхаус
            'Superattico': 'penthouse',    # Супер-пентхаус
            'Loft': 'apartment',
            'Monolocale': 'studio',        # Студия
            'Studio': 'studio',            # Студия (англ.)
            'Bilocale': 'apartment',
            'Trilocale': 'apartment',
            'Quadrilocale': 'apartment',
            'Plurilocale': 'apartment',
            'Stanza': 'room',
            'Posto letto': 'room',
            'Camera': 'room'
        }
        
        if property_type and property_type in type_mapping:
            return type_mapping[property_type]
        
        title_lower = title.lower()
        
        # Приоритетный анализ заголовка
        if any(word in title_lower for word in ['attico', 'superattico', 'penthouse']):
            return 'penthouse'
        elif any(word in title_lower for word in ['monolocale', 'studio']):
            return 'studio'
        elif any(word in title_lower for word in ['villa', 'casa', 'villetta']):
            return 'house'
        elif any(word in title_lower for word in ['stanza', 'posto letto', 'camera', 'room']):
            return 'room'
        
        return 'apartment'
    
    def _is_furnished(self, properties: Dict[str, Any], title: str) -> Optional[bool]:
        """Определяет, меблированная ли недвижимость"""
        furnished_info = properties.get('furnished')
        if furnished_info is not None:
            return bool(furnished_info)
        
        title_lower = title.lower()
        if any(word in title_lower for word in ['arredato', 'arredata', 'arredati', 'furnished']):
            return True
        elif any(word in title_lower for word in ['non arredato', 'non arredata', 'vuoto']):
            return False
        
        return None
    
    def _extract_features(self, properties: Dict[str, Any]) -> List[str]:
        """Извлекает дополнительные характеристики"""
        features = []
        
        if properties.get('hasElevator'):
            features.append('elevator')
        if properties.get('hasParking'):
            features.append('parking')
        if properties.get('hasBalcony'):
            features.append('balcony')
        if properties.get('hasTerrace'):
            features.append('terrace')
        if properties.get('hasGarden'):
            features.append('garden')
        
        return features 