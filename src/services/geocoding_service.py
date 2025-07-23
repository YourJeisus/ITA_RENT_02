"""
Сервис геокодирования адресов
Получение координат по адресам через Nominatim OpenStreetMap API
"""
import logging
import time
from typing import Optional, Tuple, Dict, Any
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)


class GeocodingService:
    """
    Сервис для получения координат по адресам
    Использует бесплатный Nominatim API от OpenStreetMap
    """
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'ITA_RENT_BOT/1.0 (https://github.com/user/ita-rent-bot)'
        }
        self.request_delay = 1.0  # Задержка между запросами (требование Nominatim)
        self.last_request_time = 0
    
    def geocode_address(self, address: str, city: str = "Roma", country: str = "Italy") -> Optional[Tuple[float, float]]:
        """
        Получить координаты по адресу
        
        Args:
            address: Адрес (например, "Via del Corso, 123")
            city: Город (по умолчанию "Roma")
            country: Страна (по умолчанию "Italy")
            
        Returns:
            Кортеж (latitude, longitude) или None если не найдено
        """
        if not address or address == 'null':
            return None
        
        try:
            # Соблюдаем задержку между запросами
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.request_delay:
                time.sleep(self.request_delay - time_since_last)
            
            # Формируем полный адрес
            full_address = f"{address}, {city}, {country}"
            
            # Параметры запроса
            params = {
                'q': full_address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1,
                'countrycodes': 'it'  # Ограничиваем поиск Италией
            }
            
            logger.debug(f"Геокодирование адреса: {full_address}")
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    result = data[0]
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    
                    # Проверяем, что координаты в пределах Италии
                    if 35.0 <= lat <= 47.0 and 6.0 <= lon <= 19.0:
                        logger.debug(f"Найдены координаты: {lat:.6f}, {lon:.6f}")
                        return (lat, lon)
                    else:
                        logger.warning(f"Координаты вне Италии: {lat}, {lon}")
                        return None
                else:
                    logger.debug(f"Адрес не найден: {full_address}")
                    return None
            else:
                logger.warning(f"Ошибка геокодирования: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при геокодировании адреса '{address}': {e}")
            return None
    
    def geocode_multiple_addresses(self, addresses: list, city: str = "Roma") -> Dict[str, Optional[Tuple[float, float]]]:
        """
        Геокодирование нескольких адресов с задержками
        
        Args:
            addresses: Список адресов
            city: Город
            
        Returns:
            Словарь {адрес: (lat, lon) или None}
        """
        results = {}
        
        for i, address in enumerate(addresses):
            if i > 0:
                # Дополнительная задержка для массовых запросов
                time.sleep(self.request_delay)
            
            coords = self.geocode_address(address, city)
            results[address] = coords
            
            if coords:
                logger.info(f"[{i+1}/{len(addresses)}] ✅ {address} -> {coords[0]:.6f}, {coords[1]:.6f}")
            else:
                logger.info(f"[{i+1}/{len(addresses)}] ❌ {address} -> не найден")
        
        return results
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Обратное геокодирование - получение адреса по координатам
        
        Args:
            latitude: Широта
            longitude: Долгота
            
        Returns:
            Словарь с информацией об адресе или None
        """
        try:
            # Соблюдаем задержку
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.request_delay:
                time.sleep(self.request_delay - time_since_last)
            
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'addressdetails': 1
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return None
                
        except Exception as e:
            logger.error(f"Ошибка обратного геокодирования: {e}")
            return None


# Глобальный экземпляр сервиса
geocoding_service = GeocodingService() 