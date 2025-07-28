#!/usr/bin/env python3
"""
🚀 АСИНХРОННЫЙ СКРАПЕР ДЛЯ SUBITO.IT V1
Создан на основе архитектуры ImmobiliareScraper

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
from urllib.parse import urljoin, urlparse, parse_qs
from ..core.config import settings

logger = logging.getLogger(__name__)


class SubitoScraper:
    """
    Асинхронный скрапер для Subito.it
    Основан на архитектуре ImmobiliareScraper
    """
    
    def __init__(self, enable_geocoding: bool = True):
        self.name = "Subito.it Async Scraper V1"
        self.base_url = "https://www.subito.it"
        self.search_url = "https://www.subito.it/annunci-lazio/affitto/immobili/roma/roma/"
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
        return f"{self.search_url}?o={page}"
    
    async def submit_async_job(self, url: str, page_num: int) -> Optional[Dict[str, Any]]:
        """
        Отправляет задачу в ScraperAPI Async Jobs API
        """
        if not settings.SCRAPERAPI_KEY:
            logger.error("❌ SCRAPERAPI_KEY не установлен")
            return None
        
        payload = {
            "apiKey": settings.SCRAPERAPI_KEY,
            "url": url,
            "render": False,  # Не используем JS рендеринг
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
                        if len(html_content) > 5000 and "subito" in html_content.lower():
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
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Subito.it использует карточки объявлений с классом .item-card
            listing_containers = soup.select('.item-card')
            logger.debug(f"📋 Найдено {len(listing_containers)} объявлений с селектором .item-card")
            
            if not listing_containers:
                logger.warning(f"⚠️ Не найдены объявления на странице {page_num}")
                return []
            
            # Парсим каждое объявление
            page_listings = []
            for container in listing_containers:
                parsed_listing = await self.parse_single_listing_from_html(container)
                if parsed_listing:
                    # Проверяем дедупликацию
                    listing_id = parsed_listing.get('external_id')
                    if listing_id and listing_id not in self.seen_listing_ids:
                        self.seen_listing_ids.add(listing_id)
                        page_listings.append(parsed_listing)
            
            logger.debug(f"✅ Страница {page_num}: {len(page_listings)}/{len(listing_containers)} уникальных")
            return page_listings
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга HTML страницы {page_num}: {e}")
            return []
    
    async def parse_single_listing_from_html(self, container) -> Optional[Dict[str, Any]]:
        """
        Парсит одно объявление из HTML контейнера
        """
        try:
            # Поиск ссылки на объявление (всегда первая ссылка в карточке)
            link_elem = container.find('a', href=True)
            if not link_elem:
                return None
            
            listing_url = link_elem.get('href')
            if not listing_url:
                return None
            
            # Делаем URL абсолютным
            if listing_url.startswith('/'):
                listing_url = urljoin(self.base_url, listing_url)
            
            # Извлекаем ID из URL
            external_id = self._extract_id_from_url(listing_url)
            if not external_id:
                return None
            
            # Заголовок (всегда в h2)
            title_elem = container.select_one('h2')
            title = title_elem.get_text(strip=True) if title_elem else None
            if not title:
                return None
            
            # Цена (в элементе с классом содержащим "price")
            price = self._extract_price_from_card(container)
            
            # Местоположение (в элементе с классом содержащим "location")
            address = self._extract_location_from_card(container)
            
            # Изображения
            images = self._extract_images_from_card(container)
            
            # Характеристики недвижимости из заголовка
            rooms = self._extract_rooms_from_title(title)
            area = self._extract_area_from_title(title)
            
            # Координаты
            if self.enable_geocoding and address:
                latitude, longitude = await self._geocode_address(address, "Roma, Italy")
            else:
                latitude, longitude = None, None
            
            # Тип недвижимости из URL и заголовка
            property_type = self._normalize_property_type_from_url_and_title(listing_url, title)
            
            return {
                'external_id': external_id,
                'source': 'subito',
                'url': listing_url,
                'title': title,
                'description': '',  # Subito не показывает описание в карточках
                'price': price,
                'price_currency': 'EUR',
                'property_type': property_type,
                'rooms': rooms,
                'bathrooms': None,  # Subito обычно не указывает ванные отдельно
                'area': area,
                'floor': None,
                'furnished': self._is_furnished_from_title(title),
                'pets_allowed': None,
                'features': [],
                'address': address or 'Roma',
                'city': 'Roma',
                'district': None,
                'postal_code': None,
                'latitude': latitude,
                'longitude': longitude,
                'images': images,
                'virtual_tour_url': None,
                'agency_name': None,
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
        logger.info(f"🚀 Запуск парсинга Subito.it: {max_pages} страниц...")
        
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
        
        logger.info(f"✅ Парсинг Subito.it завершен: {len(all_listings)} объявлений за {elapsed_time:.1f}с")
        
        return all_listings
    
    # Вспомогательные методы для парсинга
    def _extract_id_from_url(self, url: str) -> Optional[str]:
        """Извлекает ID объявления из URL"""
        try:
            # Subito.it использует формат: /category/title-ID.htm
            # Пример: /appartamenti/appio-latino-bilocale-arredato-roma-610923878.htm
            match = re.search(r'-(\d+)\.htm', url)
            if match:
                return match.group(1)
            
            return None
        except Exception:
            return None
    
    def _extract_price_from_card(self, container) -> Optional[float]:
        """Извлекает цену из карточки Subito.it"""
        try:
            price_elem = container.select_one('[class*="price"]')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                return self._parse_price_from_text(price_text)
            return None
        except Exception:
            return None
    
    def _parse_price_from_text(self, price_text: str) -> Optional[float]:
        """Парсит цену из текста"""
        if not price_text:
            return None
        
        # Убираем символы валюты и пробелы, заменяем запятые на точки
        price_clean = re.sub(r'[€$\s]', '', price_text)
        price_clean = price_clean.replace(',', '.')
        match = re.search(r'(\d+(?:\.\d+)?)', price_clean)
        
        if match:
            return float(match.group(1))
        
        return None
    
    def _extract_location_from_card(self, container) -> Optional[str]:
        """Извлекает местоположение из карточки Subito.it"""
        try:
            location_elem = container.select_one('[class*="location"]')
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                # Извлекаем только город из текста вида "Roma(RM)Oggi alle 14:35"
                match = re.search(r'([A-Za-z\s]+)', location_text)
                if match:
                    return match.group(1).strip()
            return None
        except Exception:
            return None
    
    def _extract_images_from_card(self, container) -> List[str]:
        """Извлекает изображения из карточки Subito.it"""
        images = []
        
        try:
            # Ищем img теги в карточке
            img_elements = container.find_all('img')
            for img in img_elements:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy')
                if src and src.startswith('http') and 'camera.svg' not in src:
                    if src not in images:
                        images.append(src)
        except Exception:
            pass
        
        return images
    
    def _extract_rooms_from_title(self, title: str) -> Optional[int]:
        """Извлекает количество комнат из заголовка"""
        text = title.lower()
        
        # Итальянские термины для количества комнат
        if 'monolocale' in text:
            return 1
        elif 'bilocale' in text:
            return 2
        elif 'trilocale' in text:
            return 3
        elif 'quadrilocale' in text:
            return 4
        elif 'cinque locali' in text or '5 locali' in text:
            return 5
        
        # Ищем числа перед "комн", "stanze", "locali"
        patterns = [
            r'(\d+)\s*locali',
            r'(\d+)\s*stanze',
            r'(\d+)\s*комн',
            r'(\d+)\s*room'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_area_from_title(self, title: str) -> Optional[float]:
        """Извлекает площадь из заголовка"""
        # Ищем числа перед "м²", "mq", "metri"
        patterns = [
            r'(\d+)\s*m[²q2]',
            r'(\d+)\s*metri\s*quadr',
            r'(\d+)\s*sq'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title.lower())
            if match:
                return float(match.group(1))
        
        return None
    
    def _normalize_property_type_from_url_and_title(self, url: str, title: str) -> str:
        """Нормализует тип недвижимости из URL и заголовка"""
        # Сначала проверяем URL на категорию
        if '/appartamenti/' in url:
            return 'apartment'
        elif '/camere-posti-letto/' in url:
            return 'room'
        elif '/case-indipendenti/' in url:
            return 'house'
        elif '/attici-mansarde/' in url:
            return 'penthouse'
        elif '/uffici-locali-commerciali/' in url:
            return 'commercial'  # коммерческая недвижимость
        elif '/garage-e-box/' in url:
            return 'garage'
        
        # Если URL не дал результата, анализируем заголовок
        text = title.lower()
        
        if any(word in text for word in ['monolocale', 'studio']):
            return 'studio'
        elif any(word in text for word in ['villa', 'casa']):
            return 'house'
        elif any(word in text for word in ['stanza', 'camera', 'posto letto']):
            return 'room'
        elif any(word in text for word in ['attico', 'mansarda']):
            return 'penthouse'
        elif any(word in text for word in ['appartamento', 'bilocale', 'trilocale', 'quadrilocale']):
            return 'apartment'
        
        return 'apartment'  # По умолчанию
    
    def _is_furnished_from_title(self, title: str) -> Optional[bool]:
        """Определяет, меблированная ли недвижимость из заголовка"""
        text = title.lower()
        
        if any(word in text for word in ['arredato', 'arredata', 'arredati', 'furnished']):
            return True
        elif any(word in text for word in ['non arredato', 'vuoto', 'unfurnished']):
            return False
        
        return None
    
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