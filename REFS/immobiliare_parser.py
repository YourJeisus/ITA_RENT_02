#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import re
import time
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from src.core.config import settings

logger = logging.getLogger(__name__)

def normalize_property_type(property_type: Optional[str], title: str = '') -> str:
    """
    Нормализует тип недвижимости на основе данных API и заголовка.
    
    Args:
        property_type: Тип недвижимости из API
        title: Заголовок объявления для дополнительного анализа
        
    Returns:
        Нормализованный тип недвижимости
    """
    if not property_type and not title:
        return 'appartamento'  # По умолчанию
    
    # Словарь для нормализации типов из API
    type_mapping = {
        'Appartamento': 'appartamento',
        'Villa': 'villa',
        'Villetta': 'villetta',
        'Casa': 'casa',
        'Casa indipendente': 'casa_indipendente',
        'Attico': 'attico',
        'Mansarda': 'mansarda',
        'Loft': 'loft',
        'Monolocale': 'monolocale',
        'Bilocale': 'bilocale',
        'Trilocale': 'trilocale',
        'Quadrilocale': 'quadrilocale',
        'Palazzo': 'palazzo',
        'Castello': 'castello',
        'Rustico': 'rustico',
        'Casale': 'casale',
        'Masseria': 'masseria',
        'Trullo': 'trullo',
        'Baita': 'baita'
    }
    
    # Если есть тип из API, используем его
    if property_type and property_type in type_mapping:
        return type_mapping[property_type]
    
    # Если нет типа из API, анализируем заголовок
    if title:
        title_lower = title.lower()
        
        # Анализ по ключевым словам в заголовке
        title_keywords = {
            'villa': 'villa',
            'villetta': 'villetta', 
            'casa': 'casa',
            'attico': 'attico',
            'mansarda': 'mansarda',
            'loft': 'loft',
            'monolocale': 'monolocale',
            'bilocale': 'bilocale', 
            'trilocale': 'trilocale',
            'quadrilocale': 'quadrilocale',
            'palazzo': 'palazzo',
            'castello': 'castello',
            'rustico': 'rustico',
            'casale': 'casale',
            'masseria': 'masseria',
            'trullo': 'trullo',
            'baita': 'baita'
        }
        
        for keyword, prop_type in title_keywords.items():
            if keyword in title_lower:
                return prop_type
    
    # По умолчанию возвращаем appartamento
    return 'appartamento'

def get_html_with_scraperapi(url: str, retries: int = 3) -> Optional[str]:
    """
    Получает HTML-контент страницы с использованием ScraperAPI с включенным JS-рендерингом.
    """
    if not settings.SCRAPERAPI_KEY:
        logger.error("SCRAPERAPI_KEY не настроен.")
        return None
    
    params = {
        'api_key': settings.SCRAPERAPI_KEY,
        'url': url,
        'render': 'true',
        'premium': 'true',
        'country_code': 'eu'  # Используем 'eu' вместо 'it'
    }
    
    for attempt in range(retries):
        try:
            response = requests.get('https://api.scraperapi.com/', params=params, timeout=180)
            if response.status_code >= 500:
                logger.warning(f"ScraperAPI вернул ошибку {response.status_code}. Попытка {attempt + 1}/{retries}.")
                time.sleep(5 * (attempt + 1))
                continue
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе через ScraperAPI: {e}")
            time.sleep(5 * (attempt + 1))
    return None

def extract_next_data_json(html_content: str) -> Optional[Dict[str, Any]]:
    """Извлекает и парсит JSON-объект __NEXT_DATA__ из HTML-контента."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        if not script_tag:
            logger.warning("Тег <script id='__NEXT_DATA__'> не найден.")
            return None
        return json.loads(script_tag.string)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Ошибка при извлечении или парсинге JSON из __NEXT_DATA__: {e}")
        return None

def parse_listing_from_search_json(listing_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Парсит данные одного объявления из JSON, полученного со страницы результатов поиска.
    """
    try:
        estate = listing_json.get('realEstate', {})
        if not estate:
            return None
        
        properties = estate.get('properties', [{}])[0]
        
        # ✅ Исправленные, правильные пути к данным
        title = properties.get('caption')
        canonical_url = listing_json.get('seo', {}).get('url')

        if not title or not canonical_url:
            logger.warning(f"Пропущено объявление {estate.get('id')}: отсутствует URL или заголовок.")
            return None
            
        price_info = estate.get('price', {})
        
        # Исправляем парсинг характеристик - берем из правильных полей
        area_sqm_raw = properties.get('surface', '')
        num_rooms_raw = properties.get('rooms', '')
        num_bathrooms_raw = properties.get('bathrooms', '')

        # Исправляем парсинг фото - берем small если нет large
        photos = []
        multimedia = properties.get('multimedia', {})
        photo_list = multimedia.get('photos', [])
        for p in photo_list:
            if isinstance(p, dict) and 'urls' in p and isinstance(p['urls'], dict):
                # Приоритет: large -> medium -> small
                if 'large' in p['urls']:
                    photos.append(p['urls']['large'])
                elif 'medium' in p['urls']:
                    photos.append(p['urls']['medium'])
                elif 'small' in p['urls']:
                    photos.append(p['urls']['small'])

        # Извлечение типа недвижимости
        property_type = None
        # Сначала пробуем из properties[0].typology.name
        if properties.get('typology', {}).get('name'):
            property_type = properties['typology']['name']
        # Если нет, пробуем из realEstate.typology.name
        elif estate.get('typology', {}).get('name'):
            property_type = estate['typology']['name']
        
        # Нормализуем типы недвижимости
        property_type_normalized = normalize_property_type(property_type, title)

        return {
            'url': canonical_url,
            'title': title,
            'description': properties.get('description', ''),
            'price': price_info.get('value'),
            'price_raw': price_info.get('formattedValue', ''),
            'surface_m2': int(re.search(r'\d+', str(area_sqm_raw)).group(0)) if re.search(r'\d+', str(area_sqm_raw)) else None,
            'num_rooms': int(re.search(r'\d+', str(num_rooms_raw)).group(0)) if re.search(r'\d+', str(num_rooms_raw)) else None,
            'num_bathrooms': int(re.search(r'\d+', str(num_bathrooms_raw)).group(0)) if re.search(r'\d+', str(num_bathrooms_raw)) else None,
            'floor': properties.get('floor'),
            'photos': photos,
            'property_type': property_type_normalized,
            'agency_name': estate.get('advertiser', {}).get('agency', {}).get('displayName'),
            'original_id': estate.get('id'),
            'source_site': 'immobiliare.it'
        }
    except Exception as e:
        logger.error(f"Ошибка при парсинге JSON-объекта объявления: {e}", exc_info=True)
        return None

def scrape_immobiliare_with_api(city: str, max_pages: int = 1) -> List[Dict[str, Any]]:
    """
    Основная функция для скрапинга Immobiliare.it, которая использует JSON со страницы результатов.
    """
    all_listings = []
    base_url = "https://www.immobiliare.it/affitto-case/"
    
    for page_num in range(1, max_pages + 1):
        search_url = f"{base_url}{city}/?pag={page_num}"
        logger.info(f"Скрапинг страницы {page_num}: {search_url}")

        html_content = get_html_with_scraperapi(search_url)
        if not html_content:
            logger.error(f"Не удалось получить HTML для страницы {page_num}")
            continue

        json_data = extract_next_data_json(html_content)
        if not json_data:
            logger.warning(f"Не найден JSON на странице {page_num}")
            continue
            
        try:
            results = json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['results']
        except (KeyError, IndexError, TypeError):
            logger.info(f"Больше нет объявлений на странице {page_num} или изменилась структура JSON.")
            break
            
        logger.info(f"Найдено {len(results)} объявлений на странице {page_num}.")
        
        parsed_count = 0
        for listing_json in results:
            parsed_listing = parse_listing_from_search_json(listing_json)
            if parsed_listing:
                all_listings.append(parsed_listing)
                parsed_count += 1
        
        logger.info(f"Успешно распарсено {parsed_count} из {len(results)} объявлений.")

        if not results:
            logger.info("Завершаем скрапинг, так как на странице нет объявлений.")
            break
            
    logger.info(f"🎉 Скрапинг завершен! Всего найдено {len(all_listings)} объявлений.")
    return all_listings