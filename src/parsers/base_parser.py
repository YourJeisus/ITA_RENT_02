"""
Базовый класс для всех парсеров недвижимости
"""
import logging
import time
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import aiohttp
import requests
from bs4 import BeautifulSoup

from src.core.config import settings

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """
    Базовый класс для всех парсеров недвижимости
    Определяет общий интерфейс и базовую функциональность
    """
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.scraperapi_key = getattr(settings, 'SCRAPERAPI_KEY', None) or getattr(settings, 'SCRAPER_API_KEY', None)
        self.user_agent = settings.USER_AGENT if hasattr(settings, 'USER_AGENT') else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
    @abstractmethod
    def build_search_url(self, filters: Dict[str, Any], page: int = 1) -> str:
        """
        Построить URL для поиска на основе фильтров
        
        Args:
            filters: Словарь с параметрами поиска
            page: Номер страницы
            
        Returns:
            URL для запроса
        """
        pass
    
    @abstractmethod
    def parse_listings_from_page(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Извлечь объявления со страницы
        
        Args:
            html_content: HTML контент страницы
            
        Returns:
            Список словарей с данными объявлений
        """
        pass
    
    @abstractmethod
    def normalize_listing_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Нормализовать данные объявления к единому формату
        
        Args:
            raw_data: Сырые данные объявления
            
        Returns:
            Нормализованные данные
        """
        pass
    
    def get_html_content(self, url: str, retries: int = 3, use_scraperapi: bool = True) -> Optional[str]:
        """
        Получить HTML контент страницы
        
        Args:
            url: URL страницы
            retries: Количество попыток
            use_scraperapi: Использовать ScraperAPI или обычный запрос
            
        Returns:
            HTML контент или None при ошибке
        """
        if use_scraperapi and self.scraperapi_key:
            return self._get_html_with_scraperapi(url, retries)
        else:
            return self._get_html_direct(url, retries)
    
    def _get_html_with_scraperapi(self, url: str, retries: int = 3) -> Optional[str]:
        """Получить HTML через ScraperAPI"""
        params = {
            'api_key': self.scraperapi_key,
            'url': url,
            'render': 'true',
            'premium': 'true',
            'country_code': 'it'
        }
        
        for attempt in range(retries):
            try:
                logger.info(f"🌐 [{self.name}] Запрос через ScraperAPI: {url[:100]}...")
                response = requests.get(
                    'https://api.scraperapi.com/', 
                    params=params, 
                    timeout=180
                )
                
                if response.status_code >= 500:
                    logger.warning(f"⚠️ [{self.name}] ScraperAPI вернул ошибку {response.status_code}. Попытка {attempt + 1}/{retries}")
                    time.sleep(5 * (attempt + 1))
                    continue
                    
                response.raise_for_status()
                logger.info(f"✅ [{self.name}] Получен HTML контент ({len(response.text)} символов)")
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ [{self.name}] Ошибка при запросе через ScraperAPI: {e}")
                if attempt < retries - 1:
                    time.sleep(5 * (attempt + 1))
                    
        return None
    
    def _get_html_direct(self, url: str, retries: int = 3) -> Optional[str]:
        """Получить HTML напрямую"""
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        for attempt in range(retries):
            try:
                logger.info(f"🌐 [{self.name}] Прямой запрос: {url[:100]}...")
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                logger.info(f"✅ [{self.name}] Получен HTML контент ({len(response.text)} символов)")
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ [{self.name}] Ошибка при прямом запросе: {e}")
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))
                    
        return None
    
    async def get_html_content_async(self, url: str, retries: int = 3) -> Optional[str]:
        """
        Асинхронное получение HTML контента
        
        Args:
            url: URL страницы
            retries: Количество попыток
            
        Returns:
            HTML контент или None при ошибке
        """
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    logger.info(f"🌐 [{self.name}] Асинхронный запрос: {url[:100]}...")
                    async with session.get(url, headers=headers, timeout=30) as response:
                        response.raise_for_status()
                        content = await response.text()
                        logger.info(f"✅ [{self.name}] Получен HTML контент ({len(content)} символов)")
                        return content
                        
            except Exception as e:
                logger.error(f"❌ [{self.name}] Ошибка при асинхронном запросе: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 * (attempt + 1))
                    
        return None
    
    def scrape_listings(
        self, 
        filters: Dict[str, Any], 
        max_pages: int = 5,
        use_scraperapi: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Основной метод для скрапинга объявлений
        
        Args:
            filters: Фильтры поиска
            max_pages: Максимальное количество страниц
            use_scraperapi: Использовать ScraperAPI
            
        Returns:
            Список нормализованных объявлений
        """
        all_listings = []
        
        logger.info(f"🚀 [{self.name}] Начинаем скрапинг с фильтрами: {filters}")
        logger.info(f"📄 [{self.name}] Максимум страниц: {max_pages}")
        
        for page_num in range(1, max_pages + 1):
            try:
                # Построить URL для страницы
                search_url = self.build_search_url(filters, page_num)
                logger.info(f"📄 [{self.name}] Обрабатываем страницу {page_num}: {search_url[:100]}...")
                
                # Получить HTML контент
                html_content = self.get_html_content(search_url, use_scraperapi=use_scraperapi)
                if not html_content:
                    logger.error(f"❌ [{self.name}] Не удалось получить HTML для страницы {page_num}")
                    continue
                
                # Извлечь объявления
                page_listings = self.parse_listings_from_page(html_content)
                if not page_listings:
                    logger.info(f"📄 [{self.name}] На странице {page_num} не найдено объявлений. Завершаем скрапинг.")
                    break
                
                # Нормализовать данные
                normalized_listings = []
                for raw_listing in page_listings:
                    try:
                        normalized = self.normalize_listing_data(raw_listing)
                        if normalized:
                            normalized_listings.append(normalized)
                    except Exception as e:
                        logger.error(f"❌ [{self.name}] Ошибка при нормализации объявления: {e}")
                        continue
                
                all_listings.extend(normalized_listings)
                logger.info(f"✅ [{self.name}] Страница {page_num}: найдено {len(page_listings)}, обработано {len(normalized_listings)}")
                
                # Задержка между страницами
                if page_num < max_pages:
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"❌ [{self.name}] Ошибка при обработке страницы {page_num}: {e}")
                continue
        
        logger.info(f"🎉 [{self.name}] Скрапинг завершен! Всего найдено {len(all_listings)} объявлений")
        return all_listings
    
    def extract_number_from_string(self, text: str) -> Optional[int]:
        """Извлечь число из строки"""
        import re
        if not text:
            return None
        match = re.search(r'\d+', str(text))
        return int(match.group(0)) if match else None
    
    def clean_text(self, text: str) -> str:
        """Очистить текст от лишних символов"""
        if not text:
            return ""
        return text.strip().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    def validate_listing_data(self, data: Dict[str, Any]) -> bool:
        """
        Проверить валидность данных объявления
        
        Args:
            data: Данные объявления
            
        Returns:
            True если данные валидны
        """
        required_fields = ['title', 'url', 'source', 'external_id']
        
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"⚠️ [{self.name}] Пропущено объявление: отсутствует поле '{field}'")
                return False
        
        return True 