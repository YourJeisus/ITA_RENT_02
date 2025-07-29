#!/usr/bin/env python3
"""
🚀 АСИНХРОННЫЙ СКРАПЕР ДЛЯ IDEALISTA.IT V1
Создан на основе архитектуры ImmobiliareScraper и SubitoScraper

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


class IdealistaScraper:
    """
    Асинхронный скрапер для Idealista.it
    Основан на архитектуре ImmobiliareScraper и SubitoScraper
    """
    
    def __init__(self, enable_geocoding: bool = True):
        self.name = "Idealista.it Async Scraper V1"
        self.base_url = "https://www.idealista.it"
        self.search_url = "https://www.idealista.it/affitto-case/roma-roma/"
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
            return f"{self.search_url}?ordine=pubblicazione-desc"
        return f"{self.search_url}lista-{page}.htm?ordine=pubblicazione-desc"
    
    async def submit_async_job(self, url: str, page_num: int) -> Optional[Dict[str, Any]]:
        """Отправляет задачу в ScraperAPI Async API"""
        try:
            payload = {
                "apiKey": settings.SCRAPERAPI_KEY,
                "url": url,
                "device": "desktop",
                "render": "true",  # Включаем рендеринг JS
                "wait": 5000,  # Увеличиваем время ожидания
                "premium": "true",  # Используем премиум
                "session_number": 1  # Используем сессию
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.job_submit_timeout)) as session:
                logger.info(f"🔄 [{self.name}] Отправляем задачу для страницы {page_num}: {url[:80]}...")
                
                async with session.post(self.async_jobs_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        job_id = result.get("id")
                        if job_id:
                            logger.info(f"✅ [{self.name}] Задача отправлена, ID: {job_id}")
                            return {"job_id": job_id, "page_num": page_num, "url": url}
                        else:
                            logger.error(f"❌ [{self.name}] Не получен job_id в ответе: {result}")
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ [{self.name}] Ошибка отправки задачи (status {response.status}): {error_text}")
                        
        except Exception as e:
            logger.error(f"❌ [{self.name}] Исключение при отправке задачи для страницы {page_num}: {e}")
        
        return None
    
    async def poll_job_result(self, job_info: Dict[str, Any]) -> Optional[str]:
        """Опрашивает результат задачи ScraperAPI"""
        job_id = job_info["job_id"]
        page_num = job_info["page_num"]
        
        try:
            result_url = f"{self.async_jobs_url}/{job_id}"
            params = {"apiKey": settings.SCRAPERAPI_KEY}
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.job_poll_timeout)) as session:
                start_time = time.time()
                
                while time.time() - start_time < self.job_poll_timeout:
                    async with session.get(result_url, params=params) as response:
                        if response.status == 200:
                            try:
                                # Проверяем content-type
                                content_type = response.headers.get('content-type', '').lower()
                                if 'application/json' not in content_type:
                                    logger.warning(f"⚠️ [{self.name}] Неожиданный content-type: {content_type} для страницы {page_num}")
                                    text_response = await response.text()
                                    # Если это HTML с результатом, попробуем его использовать
                                    if text_response and '<html' in text_response.lower():
                                        logger.info(f"✅ [{self.name}] Получен HTML результат напрямую для страницы {page_num}")
                                        return text_response
                                    await asyncio.sleep(5)
                                    continue
                                
                                result = await response.json()
                                status = result.get("statusCode")
                                
                                if status == "finished":
                                    response_body = result.get("response", {}).get("body")
                                    if response_body:
                                        logger.info(f"✅ [{self.name}] Получен результат для страницы {page_num}")
                                        return response_body
                                    else:
                                        logger.error(f"❌ [{self.name}] Пустой response body для страницы {page_num}")
                                        return None
                                elif status == "failed":
                                    logger.error(f"❌ [{self.name}] Задача завершилась с ошибкой для страницы {page_num}")
                                    return None
                                else:
                                    # Задача еще выполняется
                                    await asyncio.sleep(5)
                            except Exception as json_error:
                                logger.warning(f"⚠️ [{self.name}] Ошибка парсинга JSON для страницы {page_num}: {json_error}")
                                await asyncio.sleep(5)
                        else:
                            logger.error(f"❌ [{self.name}] Ошибка опроса задачи (status {response.status})")
                            await asyncio.sleep(5)
                
                logger.error(f"⏰ [{self.name}] Таймаут при ожидании результата для страницы {page_num}")
                
        except Exception as e:
            logger.error(f"❌ [{self.name}] Исключение при опросе результата для страницы {page_num}: {e}")
        
        return None
    
    async def fallback_sync_request(self, url: str, page_num: int) -> Optional[str]:
        """Fallback на синхронный API ScraperAPI или прямой запрос"""
        # Сначала пробуем ScraperAPI без геотаргетинга
        try:
            params = {
                "api_key": settings.SCRAPERAPI_KEY,
                "url": url,
                "device_type": "desktop",
                "render": "true",
                "wait": 5000,
                "premium": "true",
                "session_number": 1
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.sync_request_timeout)) as session:
                logger.info(f"🔄 [{self.name}] Fallback ScraperAPI запрос для страницы {page_num}")
                
                async with session.get(self.sync_api_url, params=params) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        logger.info(f"✅ [{self.name}] Fallback ScraperAPI успешен для страницы {page_num}")
                        return html_content
                    else:
                        error_text = await response.text()
                        logger.warning(f"⚠️ [{self.name}] ScraperAPI fallback ошибка (status {response.status}): {error_text[:200]}...")
                        
        except Exception as e:
            logger.warning(f"⚠️ [{self.name}] ScraperAPI fallback исключение для страницы {page_num}: {e}")
        
        # Если ScraperAPI не работает, пробуем прямой запрос (только для тестирования)
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                logger.info(f"🔄 [{self.name}] Прямой запрос для страницы {page_num} (тестирование)")
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        logger.info(f"✅ [{self.name}] Прямой запрос успешен для страницы {page_num}")
                        return html_content
                    else:
                        logger.error(f"❌ [{self.name}] Прямой запрос ошибка (status {response.status})")
                        
        except Exception as e:
            logger.error(f"❌ [{self.name}] Исключение в прямом запросе для страницы {page_num}: {e}")
        
        return None
    
    def parse_listings_from_html(self, html_content: str, page_num: int) -> List[Dict[str, Any]]:
        """Извлекает объявления из HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Ищем контейнеры с объявлениями (расширенные селекторы для Idealista)
            listing_containers = (
                soup.find_all('article', class_='item') or
                soup.find_all('div', class_='item') or
                soup.find_all('article', class_='item-multimedia-container') or
                soup.find_all('div', class_='item-multimedia-container') or
                soup.find_all('div', class_='item-info-container') or
                soup.find_all('article', {'data-element-id': True}) or
                soup.find_all('div', {'data-adid': True}) or
                soup.find_all('div', {'data-id': True}) or
                soup.find_all('article', {'itemtype': re.compile(r'.*Product.*')}) or
                # Альтернативные селекторы
                soup.find_all('div', class_=re.compile(r'.*item.*')) or
                soup.find_all('article', class_=re.compile(r'.*item.*'))
            )
            
            if not listing_containers:
                # Отладочная информация
                logger.warning(f"⚠️ [{self.name}] Не найдены контейнеры объявлений на странице {page_num}")
                
                # Проверяем, что вообще есть на странице
                title_tag = soup.find('title')
                page_title = title_tag.get_text(strip=True) if title_tag else "Неизвестно"
                logger.info(f"🔍 [{self.name}] Заголовок страницы: {page_title}")
                
                # Проверяем наличие ошибок или редиректов
                if any(keyword in page_title.lower() for keyword in ['error', 'not found', '404', 'captcha', 'blocked']):
                    logger.error(f"❌ [{self.name}] Страница содержит ошибку: {page_title}")
                elif 'idealista' not in page_title.lower():
                    logger.warning(f"⚠️ [{self.name}] Возможно получена неправильная страница: {page_title}")
                
                # Ищем любые ссылки на объявления
                all_links = soup.find_all('a', href=True)
                listing_links = [link for link in all_links if '/immobile/' in link.get('href', '')]
                if listing_links:
                    logger.info(f"🔗 [{self.name}] Найдено {len(listing_links)} ссылок на объявления, но не удалось извлечь контейнеры")
                
                return []
            
            listings = []
            
            for container in listing_containers:
                try:
                    listing = self.parse_single_listing(container)
                    if listing and listing.get('external_id'):
                        # Проверяем дедупликацию
                        external_id = listing['external_id']
                        if external_id not in self.seen_listing_ids:
                            self.seen_listing_ids.add(external_id)
                            listings.append(listing)
                        else:
                            logger.debug(f"🔄 Дубликат объявления пропущен: {external_id}")
                except Exception as e:
                    logger.error(f"❌ [{self.name}] Ошибка при парсинге объявления: {e}")
                    continue
            
            logger.info(f"📊 [{self.name}] Страница {page_num}: найдено {len(listing_containers)} контейнеров, извлечено {len(listings)} уникальных объявлений")
            return listings
            
        except Exception as e:
            logger.error(f"❌ [{self.name}] Критическая ошибка парсинга HTML страницы {page_num}: {e}")
            return []
    
    def parse_single_listing(self, container) -> Optional[Dict[str, Any]]:
        """Парсит одно объявление из контейнера"""
        try:
            # ID объявления
            external_id = None
            
            # Пробуем разные способы извлечения ID
            if container.get('data-element-id'):
                external_id = container.get('data-element-id')
            elif container.get('data-adid'):
                external_id = container.get('data-adid')
            elif container.get('id'):
                external_id = container.get('id')
            else:
                # Пробуем найти в ссылке
                link = container.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    # Извлекаем ID из URL типа /immobile/123456/
                    id_match = re.search(r'/immobile/(\d+)/', href)
                    if id_match:
                        external_id = id_match.group(1)
            
            if not external_id:
                return None
            
            # Заголовок - пробуем разные селекторы
            title_elem = (
                container.find('a', class_='item-link') or
                container.find('h2') or
                container.find('h3') or
                container.find('h4') or
                container.find('span', class_='item-title') or
                container.find('div', class_='item-title') or
                container.find('a', class_='item-title') or
                container.find('a', href=re.compile(r'/immobile/')) or
                container.find('a', href=True)
            )
            
            title = title_elem.get_text(strip=True) if title_elem else "Без названия"
            
            # Цена - исправленный парсинг для Idealista
            price = 0
            # Попробуем разные подходы к поиску цены
            price_elem = None
            
            # Подход 1: CSS селекторы
            price_candidates = container.select('span.item-price, .price-row, [class*=\"price\"]')
            for candidate in price_candidates:
                text = candidate.get_text(strip=True)
                if '€' in text and any(c.isdigit() for c in text):
                    price_elem = candidate
                    break
            
            # Подход 2: поиск по классам без BeautifulSoup find
            if not price_elem:
                for elem in container.find_all(['span', 'div']):
                    classes = elem.get('class', [])
                    classes_str = ' '.join(classes) if classes else ''
                    if 'price' in classes_str and '€' in elem.get_text():
                        price_elem = elem
                        break
            
            # Debug информация для логов
            if price_elem:
                logger.debug(f"Price element found: {price_elem.name} with classes {price_elem.get('class', [])}")
            
            if price_elem:
                if hasattr(price_elem, 'get_text'):
                    price_text = price_elem.get_text(strip=True)
                else:
                    price_text = str(price_elem).strip()
                
                # Парсим цены в итальянском формате (1.500€, 4.000€/mese)
                # Удаляем все кроме цифр, точек и запятых
                price_clean = re.sub(r'[^\d,.]', '', price_text)
                
                # Обрабатываем итальянский формат чисел (точка = разделитель тысяч, запятая = десятичные)
                if ',' in price_clean and '.' in price_clean:
                    # Есть и точки и запятые: 1.234,56
                    parts = price_clean.split(',')
                    if len(parts) == 2:
                        integer_part = parts[0].replace('.', '')  # убираем точки-разделители тысяч
                        decimal_part = parts[1]
                        price_clean = f"{integer_part}.{decimal_part}"
                elif '.' in price_clean and len(price_clean.split('.')[-1]) != 2:
                    # Только точки, но не десятичные: 4.000 (разделитель тысяч)
                    price_clean = price_clean.replace('.', '')
                elif ',' in price_clean:
                    # Только запятая: 1234,56
                    price_clean = price_clean.replace(',', '.')
                
                # Извлекаем число
                try:
                    if price_clean and price_clean.replace('.', '').isdigit():
                        price = float(price_clean)
                        logger.debug(f"Price parsed successfully: '{price_text}' -> {price}€")
                    else:
                        logger.warning(f"Price clean is not a number: '{price_clean}' from '{price_text}'")
                except ValueError as e:
                    logger.error(f"Error parsing price: '{price_text}' -> {e}")
            
            # Площадь
            area = None
            area_elem = container.find('span', string=re.compile(r'm²|mq')) or \
                       container.find('div', string=re.compile(r'm²|mq'))
            
            if area_elem:
                area_text = area_elem.get_text(strip=True)
                area_match = re.search(r'(\d+)', area_text)
                if area_match:
                    area = int(area_match.group(1))
            
            # Количество комнат - улучшенный парсинг
            rooms = None
            
            # Метод 1: Поиск по содержимому текста
            rooms_elem = container.find('span', string=re.compile(r'locale|stanz|camer')) or \
                        container.find('div', string=re.compile(r'locale|stanz|camer'))
            
            if not rooms_elem:
                # Метод 2: Поиск в заголовке (bilocale, trilocale, etc.)
                title_lower = title.lower()
                if 'monolocale' in title_lower or 'mono' in title_lower:
                    rooms = 1
                elif 'bilocale' in title_lower or 'bilo' in title_lower:
                    rooms = 2
                elif 'trilocale' in title_lower or 'trilo' in title_lower:
                    rooms = 3
                elif 'quadrilocale' in title_lower:
                    rooms = 4
                else:
                    # Метод 3: Поиск паттернов "X локали" или "X комнат"
                    rooms_match = re.search(r'(\d+)\s*(?:local|stanz|camer|room)', title_lower)
                    if rooms_match:
                        rooms = int(rooms_match.group(1))
            
            if rooms_elem and not rooms:
                # Парсинг из найденного элемента
                rooms_text = rooms_elem.get_text(strip=True)
                rooms_match = re.search(r'(\d+)', rooms_text)
                if rooms_match:
                    rooms = int(rooms_match.group(1))
            
            # Адрес/местоположение
            address = "Roma, Italia"
            address_elem = container.find('span', class_='item-zone') or \
                          container.find('div', class_='location') or \
                          container.find('span', class_='zone')
            
            if address_elem:
                address_text = address_elem.get_text(strip=True)
                if address_text:
                    address = f"{address_text}, Roma, Italia"
            
            # Ссылка на объявление
            url = ""
            link_elem = container.find('a', href=True)
            if link_elem:
                href = link_elem.get('href')
                if href.startswith('/'):
                    url = urljoin(self.base_url, href)
                else:
                    url = href
            
            # Изображения
            images = []
            img_elem = container.find('img', src=True)
            if img_elem:
                img_src = img_elem.get('src')
                if img_src and not img_src.startswith('data:'):
                    if img_src.startswith('/'):
                        img_src = urljoin(self.base_url, img_src)
                    images.append(img_src)
            
            listing = {
                'external_id': f"idealista_{external_id}",
                'source': 'idealista',
                'title': title,
                'price': price,
                'property_type': 'apartment',  # Добавляем property_type для фильтрации
                'area': area,
                'rooms': rooms,
                'address': address,
                'city': 'Roma',
                'url': url,
                'images': images,
                'scraped_at': datetime.utcnow()
            }
            
            return listing
            
        except Exception as e:
            logger.error(f"❌ [{self.name}] Ошибка парсинга объявления: {e}")
            return None
    
    async def geocode_listing(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Добавляет координаты к объявлению"""
        if not self.enable_geocoding:
            return listing
        
        try:
            address = listing.get('address', '')
            if not address or address == "Roma, Italia":
                # Используем координаты центра Рима
                listing['latitude'] = 41.9028
                listing['longitude'] = 12.4964
                return listing
            
            # Геокодирование через Nominatim
            geocode_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'it'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(geocode_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data:
                            listing['latitude'] = float(data[0]['lat'])
                            listing['longitude'] = float(data[0]['lon'])
                        else:
                            # Fallback координаты Рима
                            listing['latitude'] = 41.9028
                            listing['longitude'] = 12.4964
                    else:
                        listing['latitude'] = 41.9028
                        listing['longitude'] = 12.4964
            
            # Небольшая задержка для уважения к API
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"❌ [{self.name}] Ошибка геокодирования: {e}")
            # Fallback координаты Рима
            listing['latitude'] = 41.9028
            listing['longitude'] = 12.4964
        
        return listing
    
    async def scrape_single_page(self, page_num: int) -> List[Dict[str, Any]]:
        """Парсит одну страницу"""
        url = self.build_page_url(page_num)
        
        # Сначала пробуем async API
        job_info = await self.submit_async_job(url, page_num)
        html_content = None
        
        if job_info:
            html_content = await self.poll_job_result(job_info)
        
        # Fallback на sync API
        if not html_content:
            logger.info(f"🔄 [{self.name}] Переходим на fallback для страницы {page_num}")
            html_content = await self.fallback_sync_request(url, page_num)
        
        if not html_content:
            logger.error(f"❌ [{self.name}] Не удалось получить HTML для страницы {page_num}")
            return []
        
        # Парсим объявления
        listings = self.parse_listings_from_html(html_content, page_num)
        
        # Добавляем геокодирование если включено
        if self.enable_geocoding and listings:
            geocoded_listings = []
            for listing in listings:
                geocoded_listing = await self.geocode_listing(listing)
                geocoded_listings.append(geocoded_listing)
            return geocoded_listings
        
        return listings
    
    async def scrape_multiple_pages(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Парсит несколько страниц параллельно"""
        logger.info(f"🚀 [{self.name}] Начинаем парсинг {max_pages} страниц")
        
        # Очищаем кеш для дедупликации
        self.seen_listing_ids.clear()
        
        # Создаем задачи для всех страниц
        tasks = []
        for page_num in range(1, max_pages + 1):
            task = self.scrape_single_page(page_num)
            tasks.append(task)
        
        # Выполняем все задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Собираем все объявления
        all_listings = []
        successful_pages = 0
        
        for page_num, result in enumerate(results, 1):
            if isinstance(result, Exception):
                logger.error(f"❌ [{self.name}] Ошибка на странице {page_num}: {result}")
            elif isinstance(result, list):
                all_listings.extend(result)
                successful_pages += 1
                logger.info(f"✅ [{self.name}] Страница {page_num}: {len(result)} объявлений")
        
        logger.info(f"🎉 [{self.name}] Завершено! Обработано {successful_pages}/{max_pages} страниц, получено {len(all_listings)} уникальных объявлений")
        return all_listings


# Функция для быстрого тестирования
async def test_idealista_scraper():
    """Тестирует скрапер Idealista"""
    scraper = IdealistaScraper(enable_geocoding=False)
    listings = await scraper.scrape_multiple_pages(max_pages=2)
    
    print(f"\n🎉 Получено {len(listings)} объявлений с Idealista.it")
    
    if listings:
        print("\n📋 Первые 3 объявления:")
        for i, listing in enumerate(listings[:3], 1):
            print(f"\n{i}. {listing.get('title', 'Без названия')}")
            print(f"   💰 Цена: {listing.get('price', 0)}€")
            print(f"   📐 Площадь: {listing.get('area', 'N/A')} м²")
            print(f"   🚪 Комнаты: {listing.get('rooms', 'N/A')}")
            print(f"   📍 Адрес: {listing.get('address', 'N/A')}")
            print(f"   🔗 URL: {listing.get('url', 'N/A')}")


if __name__ == "__main__":
    # Быстрый тест
    asyncio.run(test_idealista_scraper()) 