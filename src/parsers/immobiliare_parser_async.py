#!/usr/bin/env python3
"""
🚀 ИСПРАВЛЕННЫЙ АСИНХРОННЫЙ ПАРСЕР ДЛЯ IMMOBILIARE.IT
Использует настоящую асинхронную логику ScraperAPI согласно документации

Исправления:
- ✅ Улучшенная обработка ошибок HTTP
- ✅ Правильные таймауты для длительных операций
- ✅ Лучшая обработка JSON ответов
- ✅ Fallback на обычный ScraperAPI при проблемах с Async API
- ✅ Более стабильная логика опроса статуса
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


class ImmobiliareAsyncParser(BaseParser):
    """
    Исправленный асинхронный парсер для Immobiliare.it
    """
    
    def __init__(self, enable_geocoding: bool = True):
        super().__init__(
            name="Immobiliare.it (Async Fixed)",
            base_url="https://www.immobiliare.it"
        )
        self.main_page_url = "https://www.immobiliare.it/affitto-case/roma/"
        self.enable_geocoding = enable_geocoding
        self.async_api_url = "https://async.scraperapi.com/jobs"
        self.sync_api_url = "https://api.scraperapi.com"
        
        # Настройки таймаутов
        self.job_timeout = 30  # Таймаут для создания задачи
        self.poll_timeout = 300  # Максимальное время ожидания результата
        self.request_timeout = 90  # Таймаут для обычных запросов
    
    def build_search_url(self, filters: Dict[str, Any] = None, page: int = 1) -> str:
        """Построить URL для парсинга"""
        if page > 1:
            return f"{self.main_page_url}?pag={page}"
        return self.main_page_url
    
    async def scrape_page_fallback(self, page_num: int) -> List[Dict[str, Any]]:
        """
        Исправленный fallback метод через обычный ScraperAPI
        Использует только проверенные рабочие параметры
        """
        url = self.build_search_url(page=page_num)
        
        # Добавляем задержку между запросами
        if page_num > 1:
            delay = min(1 + (page_num * 0.3), 3)  # От 1.3 до 3 секунд
            logger.info(f"⏳ Задержка {delay:.1f}с перед fallback запросом страницы {page_num}")
            await asyncio.sleep(delay)
        
        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        
        # Проверенные рабочие параметры (из успешного теста)
        working_params = [
            # Попытка 1: Базовые параметры (работает!)
            {
                'api_key': settings.SCRAPERAPI_KEY,
                'url': url,
                'render': 'false'  # Ключевое изменение - НЕ используем JS рендеринг
            },
            # Попытка 2: Мобильная версия (работает!)
            {
                'api_key': settings.SCRAPERAPI_KEY,
                'url': url,
                'render': 'true',
                'device_type': 'mobile'
            },
            # Попытка 3: Без геотаргетинга (работает!)
            {
                'api_key': settings.SCRAPERAPI_KEY,
                'url': url,
                'render': 'true',
                'premium': 'true'
            }
        ]
        
        for attempt_num, attempt_params in enumerate(working_params, 1):
            try:
                logger.info(f"🔄 Fallback попытка {attempt_num}/3 для страницы {page_num}")
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(self.sync_api_url, params=attempt_params) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            
                            # Проверяем, что получили валидный HTML с контентом
                            if len(html_content) > 10000 and any(indicator in html_content.lower() for indicator in 
                                                                ['immobiliare', 'affitto', 'roma', 'annunci']):
                                logger.info(f"✅ Fallback успешен для страницы {page_num} (попытка {attempt_num}), размер: {len(html_content)}")
                                return await self.parse_html_content(html_content, page_num)
                            else:
                                logger.warning(f"⚠️ Получен HTML без ожидаемого контента на попытке {attempt_num}: {len(html_content)} символов")
                        else:
                            logger.warning(f"⚠️ Fallback HTTP {response.status} на попытке {attempt_num} для страницы {page_num}")
                            
                # Короткая задержка между попытками
                if attempt_num < len(working_params):
                    await asyncio.sleep(1)
                        
            except Exception as e:
                logger.warning(f"⚠️ Fallback исключение на попытке {attempt_num} для страницы {page_num}: {e}")
                if attempt_num < len(working_params):
                    await asyncio.sleep(1)
        
        logger.error(f"❌ Все fallback попытки провалились для страницы {page_num}")
        return []
    
    async def submit_scraping_job(self, url: str, meta: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Отправляет задачу скрапинга в ScraperAPI Async с улучшенной обработкой ошибок
        """
        if not settings.SCRAPERAPI_KEY:
            logger.error("❌ SCRAPERAPI_KEY не настроен")
            return None
        
        payload = {
            "apiKey": settings.SCRAPERAPI_KEY,
            "url": url,
            "apiParams": {
                "render": True,
                "premium": True,
                "country_code": "it",
                "device_type": "desktop",
                "autoparse": False,
                "retry_404": True,
                "follow_redirect": True
            }
        }
        
        if meta:
            payload["meta"] = meta
        
        timeout = aiohttp.ClientTimeout(total=self.job_timeout)
        
        try:
            logger.info(f"📤 Отправляем задачу в ScraperAPI Async: {url}")
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.async_api_url, 
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    
                    # Читаем ответ как текст сначала
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            job_data = json.loads(response_text)
                            logger.info(f"✅ Задача создана: {job_data.get('id')} | Статус: {job_data.get('status')}")
                            return job_data
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ Ошибка парсинга JSON ответа: {e}")
                            logger.debug(f"Ответ сервера: {response_text[:500]}")
                            return None
                    else:
                        logger.error(f"❌ HTTP ошибка {response.status}: {response_text[:200]}")
                        return None
                    
        except asyncio.TimeoutError:
            logger.error(f"⏰ Таймаут при создании задачи для {url}")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка создания задачи: {e}")
            return None
    
    async def poll_job_status(self, status_url: str, max_wait_time: int = None) -> Optional[Dict[str, Any]]:
        """
        Улучшенный опрос статуса задачи с экспоненциальной задержкой
        """
        if max_wait_time is None:
            max_wait_time = self.poll_timeout
            
        timeout = aiohttp.ClientTimeout(total=30)
        start_time = time.time()
        poll_interval = 3  # Начальный интервал
        max_poll_interval = 20  # Максимальный интервал
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                while time.time() - start_time < max_wait_time:
                    elapsed = time.time() - start_time
                    logger.info(f"🔄 Проверяем статус... ({elapsed:.1f}s)")
                    
                    try:
                        async with session.get(status_url) as response:
                            response_text = await response.text()
                            
                            if response.status != 200:
                                logger.warning(f"⚠️ HTTP {response.status} при опросе статуса")
                                await asyncio.sleep(poll_interval)
                                continue
                            
                            # Пытаемся распарсить JSON
                            try:
                                job_status = json.loads(response_text)
                            except json.JSONDecodeError:
                                logger.warning(f"⚠️ Не удалось распарсить JSON: {response_text[:100]}")
                                await asyncio.sleep(poll_interval)
                                continue
                            
                            status = job_status.get("status")
                            job_id = job_status.get("id", "unknown")
                            
                            if status == "finished":
                                logger.info(f"✅ Задача {job_id} завершена успешно!")
                                return job_status
                            
                            elif status == "failed":
                                fail_reason = job_status.get("failReason", "unknown")
                                logger.error(f"❌ Задача {job_id} провалилась: {fail_reason}")
                                return None
                            
                            elif status in ["running", "pending"]:
                                logger.info(f"⏳ Задача {job_id} выполняется... Ждем {poll_interval}s")
                                await asyncio.sleep(poll_interval)
                                # Увеличиваем интервал опроса (экспоненциально)
                                poll_interval = min(poll_interval * 1.2, max_poll_interval)
                            
                            else:
                                logger.warning(f"⚠️ Неизвестный статус: {status}")
                                await asyncio.sleep(poll_interval)
                    
                    except asyncio.TimeoutError:
                        logger.warning("⏰ Таймаут при опросе статуса, повторяем...")
                        await asyncio.sleep(poll_interval)
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Ошибка при опросе статуса: {e}")
                        await asyncio.sleep(poll_interval)
                
                logger.error(f"⏰ Превышено время ожидания ({max_wait_time}s)")
                return None
                
        except Exception as e:
            logger.error(f"❌ Критическая ошибка опроса статуса: {e}")
            return None
    
    async def scrape_page_async(self, page_num: int) -> List[Dict[str, Any]]:
        """
        Асинхронно скрапит одну страницу с fallback на обычный API
        """
        # Сначала пытаемся через Async API
        url = self.build_search_url(page=page_num)
        meta = {"page_num": page_num, "timestamp": time.time()}
        
        # Шаг 1: Отправляем задачу
        job_data = await self.submit_scraping_job(url, meta)
        if not job_data:
            logger.warning(f"⚠️ Async API недоступен для страницы {page_num}, используем fallback")
            return await self.scrape_page_fallback(page_num)
        
        # Шаг 2: Ждем завершения
        status_url = job_data.get("statusUrl")
        if not status_url:
            logger.warning(f"⚠️ Нет statusUrl для страницы {page_num}, используем fallback")
            return await self.scrape_page_fallback(page_num)
        
        result = await self.poll_job_status(status_url)
        if not result:
            logger.warning(f"⚠️ Не удалось получить результат для страницы {page_num}, используем fallback")
            return await self.scrape_page_fallback(page_num)
        
        # Шаг 3: Извлекаем HTML из результата
        try:
            response_data = result.get("response", {})
            html_content = response_data.get("body")
            status_code = response_data.get("statusCode", 0)
            
            if not html_content:
                logger.warning(f"⚠️ Пустой HTML для страницы {page_num}, используем fallback")
                return await self.scrape_page_fallback(page_num)
            
            # Если получили 403 или другую ошибку, сразу используем fallback
            if status_code == 403:
                logger.warning(f"⚠️ Получен 403 (Forbidden) для страницы {page_num}, используем fallback")
                return await self.scrape_page_fallback(page_num)
            elif status_code != 200:
                logger.warning(f"⚠️ Статус код {status_code} для страницы {page_num}, используем fallback")
                return await self.scrape_page_fallback(page_num)
            
            logger.info(f"✅ Получен HTML для страницы {page_num}, размер: {len(html_content)} символов")
            
            # Шаг 4: Парсим HTML
            parsed_listings = await self.parse_html_content(html_content, page_num)
            
            # Если парсинг не дал результатов, пробуем fallback
            if not parsed_listings:
                logger.warning(f"⚠️ Парсинг не дал результатов для страницы {page_num}, пробуем fallback")
                return await self.scrape_page_fallback(page_num)
            
            return parsed_listings
            
        except Exception as e:
            logger.error(f"❌ Ошибка извлечения HTML для страницы {page_num}: {e}")
            return await self.scrape_page_fallback(page_num)
    
    async def parse_html_content(self, html_content: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Парсит HTML контент и извлекает объявления
        """
        try:
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
            
            # Парсим каждое объявление асинхронно с геокодированием
            page_listings = []
            for listing_json in results:
                parsed_listing = await self.parse_single_listing_async(listing_json)
                if parsed_listing:
                    page_listings.append(parsed_listing)
            
            logger.info(f"✅ Страница {page_num}: обработано {len(page_listings)} объявлений")
            return page_listings
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга HTML для страницы {page_num}: {e}")
            return []
    
    def extract_next_data_json(self, html_content: str) -> Optional[Dict[str, Any]]:
        """Извлекает JSON из __NEXT_DATA__ тега"""
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
        Извлекает ВСЕ фотографии из объявления (унаследовано из старого парсера)
        Цель: получить ~20+ фотографий на объявление
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
                    # Добавляем все доступные размеры фото (лучшее качество первым)
                    for size in ['large', 'medium', 'small']:
                        if size in urls and urls[size]:
                            photo_url = urls[size]
                            if photo_url and photo_url not in photos:  # Избегаем дубликатов
                                photos.append(photo_url)
                            break  # Берем только лучшее качество для каждого фото
            
            logger.info(f"📸 Найдено {len(photos)} фотографий для объявления")
            return photos
            
        except Exception as e:
            logger.error(f"❌ Ошибка извлечения фото: {e}")
            return []
    
    async def parse_single_listing_async(self, listing_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Асинхронно парсит одно объявление из JSON с геокодированием"""
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
            
            # Цена
            price_info = estate.get('price', {})
            price = price_info.get('value')
            
            # Характеристики
            rooms = self._extract_number(properties.get('rooms', ''))
            area = self._extract_number(properties.get('surface', ''))
            bathrooms = self._extract_number(properties.get('bathrooms', ''))
            
            # Извлекаем ВСЕ фотографии (унаследовано из старого парсера)
            all_photos = self.extract_all_photos(listing_json)
            
            # Координаты и адрес с геокодированием
            address = self._extract_address(listing_json)
            if self.enable_geocoding:
                latitude, longitude = await self._extract_coordinates_with_geocoding(listing_json)
            else:
                latitude, longitude = self._extract_coordinates(listing_json)
            
            # Тип недвижимости (унаследованная логика из старого парсера)
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
                'pets_allowed': None,  # Не всегда доступно в JSON
                'features': self._extract_features(properties),
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
    
    def parse_single_listing(self, listing_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Синхронная версия для совместимости (без геокодирования)"""
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
            
            # Цена
            price_info = estate.get('price', {})
            price = price_info.get('value')
            
            # Характеристики
            rooms = self._extract_number(properties.get('rooms', ''))
            area = self._extract_number(properties.get('surface', ''))
            bathrooms = self._extract_number(properties.get('bathrooms', ''))
            
            # Извлекаем ВСЕ фотографии
            all_photos = self.extract_all_photos(listing_json)
            
            # Координаты и адрес (только из JSON)
            address = self._extract_address(listing_json)
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
                'images': all_photos,
                'virtual_tour_url': None,
                'agency_name': estate.get('advertiser', {}).get('agency', {}).get('displayName'),
                'contact_info': None,
                'is_active': True,
                'published_at': None,
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга объявления: {e}")
            return None
    
    async def scrape_listings(self, filters: Dict[str, Any] = None, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        ОСНОВНОЙ МЕТОД: Асинхронно парсит объявления с улучшенной обработкой ошибок
        """
        logger.info("🚀 НАЧИНАЕМ ИСПРАВЛЕННЫЙ АСИНХРОННЫЙ ПАРСИНГ IMMOBILIARE.IT")
        logger.info(f"🎯 URL: {self.main_page_url}")
        logger.info(f"📄 Максимум страниц: {max_pages}")
        logger.info(f"⚡ Режим: ScraperAPI Async + Fallback")
        
        start_time = time.time()
        
        # Создаем задачи для всех страниц с ограничением параллелизма
        semaphore = asyncio.Semaphore(3)  # Максимум 3 параллельных запроса
        
        async def scrape_page_with_semaphore(page_num: int):
            async with semaphore:
                return await self.scrape_page_async(page_num)
        
        tasks = []
        for page_num in range(1, max_pages + 1):
            task = scrape_page_with_semaphore(page_num)
            tasks.append(task)
        
        logger.info(f"🔄 Запускаем {len(tasks)} задач с ограничением параллелизма...")
        
        # Выполняем все задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Собираем результаты
        all_listings = []
        successful_pages = 0
        error_pages = 0
        fallback_pages = 0
        
        for page_num, result in enumerate(results, 1):
            if isinstance(result, Exception):
                logger.error(f"❌ Исключение на странице {page_num}: {result}")
                error_pages += 1
            elif isinstance(result, list):
                all_listings.extend(result)
                if result:
                    successful_pages += 1
                    logger.info(f"✅ Страница {page_num}: {len(result)} объявлений")
                else:
                    logger.info(f"🔚 Страница {page_num}: пустая")
            else:
                logger.warning(f"⚠️ Неожиданный результат для страницы {page_num}: {type(result)}")
        
        # Дедупликация
        unique_listings = []
        seen_ids = set()
        
        for listing in all_listings:
            listing_id = listing.get('external_id')
            if listing_id and listing_id not in seen_ids:
                seen_ids.add(listing_id)
                unique_listings.append(listing)
        
        elapsed_time = time.time() - start_time
        
        logger.info(f"🎉 ИСПРАВЛЕННЫЙ АСИНХРОННЫЙ ПАРСИНГ ЗАВЕРШЕН!")
        logger.info(f"📊 Статистика:")
        logger.info(f"   ⏱️ Время выполнения: {elapsed_time:.1f}с")
        logger.info(f"   ✅ Успешных страниц: {successful_pages}")
        logger.info(f"   ❌ Ошибок: {error_pages}")
        logger.info(f"   📋 Всего объявлений: {len(all_listings)}")
        logger.info(f"   🔄 Уникальных объявлений: {len(unique_listings)}")
        
        # Статистика по фотографиям
        if unique_listings:
            photo_counts = [len(listing.get('images', [])) for listing in unique_listings]
            avg_photos = sum(photo_counts) / len(photo_counts)
            logger.info(f"   📸 Среднее количество фото: {avg_photos:.1f}")
            
            # Статистика по координатам
            with_coords = sum(1 for listing in unique_listings if listing.get('latitude') and listing.get('longitude'))
            coord_percentage = (with_coords / len(unique_listings)) * 100
            logger.info(f"   🗺️ С координатами: {with_coords}/{len(unique_listings)} ({coord_percentage:.1f}%)")
        
        return unique_listings
    
    # Вспомогательные методы
    def _extract_number(self, value: str) -> Optional[int]:
        """Извлекает число из строки"""
        if not value:
            return None
        match = re.search(r'\d+', str(value))
        return int(match.group(0)) if match else None
    
    async def _extract_coordinates_with_geocoding(self, listing_json: Dict[str, Any]) -> tuple[Optional[float], Optional[float]]:
        """
        Извлекает координаты из JSON или через геокодирование OpenStreetMap
        Сначала пытается найти координаты в JSON, затем геокодирует адрес
        """
        try:
            # Сначала пытаемся найти координаты в JSON (как в старом парсере)
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
                        logger.debug(f"📍 Координаты найдены в JSON: {lat}, {lon}")
                        return lat, lon
            
            # Если координат нет в JSON, пытаемся геокодировать адрес
            address = self._extract_address(listing_json)
            if address and len(address.strip()) > 10:  # Только если есть подробный адрес
                logger.debug(f"🗺️ Геокодируем адрес: {address}")
                return await self._geocode_address(address, "Roma, Italy")
            
            return None, None
            
        except Exception as e:
            logger.debug(f"Ошибка извлечения координат: {e}")
            return None, None
    
    async def _geocode_address(self, address: str, city: str) -> tuple[Optional[float], Optional[float]]:
        """
        Геокодирование адреса через OpenStreetMap Nominatim API
        """
        try:
            # Строим запрос для геокодирования
            full_address = f"{address}, {city}"
            url = "https://nominatim.openstreetmap.org/search"
            
            params = {
                'q': full_address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'it',  # Ограничиваем поиск Италией
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'ITA_RENT_BOT/1.0 (rental search bot)'  # Обязательный User-Agent для Nominatim
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
                            
                            # Проверяем, что координаты в пределах Италии
                            if 35.0 <= lat <= 47.0 and 6.0 <= lon <= 19.0:
                                logger.debug(f"✅ Геокодирование успешно: {lat}, {lon}")
                                return lat, lon
                            else:
                                logger.debug(f"⚠️ Координаты вне Италии: {lat}, {lon}")
                        else:
                            logger.debug(f"🔍 Адрес не найден: {full_address}")
                    else:
                        logger.debug(f"❌ Ошибка геокодирования: HTTP {response.status}")
                        
                    # Добавляем небольшую задержку для соблюдения лимитов API
                    await asyncio.sleep(1)
                    
            return None, None
            
        except Exception as e:
            logger.debug(f"❌ Ошибка геокодирования для '{address}': {e}")
            return None, None
    
    def _extract_coordinates(self, listing_json: Dict[str, Any]) -> tuple[Optional[float], Optional[float]]:
        """Синхронная версия для совместимости (только из JSON)"""
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
                    if 35.0 <= lat <= 47.0 and 6.0 <= lon <= 19.0:
                        return lat, lon
            
            return None, None
            
        except Exception:
            return None, None
    
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
    
    def _normalize_property_type(self, properties: Dict[str, Any], title: str) -> str:
        """
        Нормализует тип недвижимости (унаследовано из старого парсера)
        Поддерживает: apartment, house, studio, room
        """
        # Извлекаем тип из JSON
        property_type = None
        if properties.get('typology', {}).get('name'):
            property_type = properties['typology']['name']
        
        # Расширенный маппинг типов из старого парсера
        type_mapping = {
            'Appartamento': 'apartment',
            'Villa': 'house',
            'Casa': 'house',
            'Villetta': 'house',
            'Attico': 'apartment',
            'Loft': 'apartment',
            'Monolocale': 'studio',
            'Bilocale': 'apartment',
            'Trilocale': 'apartment',
            'Quadrilocale': 'apartment',
            'Stanza': 'room',
            'Posto letto': 'room',
            'Camera': 'room'
        }
        
        # Проверяем прямой маппинг
        if property_type and property_type in type_mapping:
            return type_mapping[property_type]
        
        # Анализ заголовка (как в старом парсере)
        title_lower = title.lower()
        if 'monolocale' in title_lower or 'studio' in title_lower:
            return 'studio'
        elif any(word in title_lower for word in ['villa', 'casa', 'villetta', 'casa indipendente']):
            return 'house'
        elif any(word in title_lower for word in ['stanza', 'posto letto', 'camera']):
            return 'room'
        
        return 'apartment'  # По умолчанию
    
    def _is_furnished(self, properties: Dict[str, Any], title: str) -> Optional[bool]:
        """Определяет, меблированная ли недвижимость"""
        # Проверяем в свойствах
        furnished_info = properties.get('furnished')
        if furnished_info is not None:
            return bool(furnished_info)
        
        # Проверяем в заголовке
        title_lower = title.lower()
        if any(word in title_lower for word in ['arredato', 'arredata', 'arredati', 'furnished']):
            return True
        elif any(word in title_lower for word in ['non arredato', 'non arredata', 'vuoto', 'unfurnished']):
            return False
        
        return None
    
    def _extract_features(self, properties: Dict[str, Any]) -> List[str]:
        """Извлекает дополнительные характеристики"""
        features = []
        
        # Проверяем различные поля
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
    
    def parse_listings_from_page(self, html_content: str) -> List[Dict[str, Any]]:
        """Реализация абстрактного метода - синхронная версия для совместимости"""
        # Это синхронная версия, используем асинхронную parse_html_content
        import asyncio
        return asyncio.run(self.parse_html_content(html_content, 1))
    
    def normalize_listing_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Реализация абстрактного метода"""
        return raw_data 