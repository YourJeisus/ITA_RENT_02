"""
Утилита для анализа описания объявления и извлечения информации о фильтрах
"""
import re
import json
from typing import Optional, Dict, Any
from datetime import datetime


class DescriptionAnalyzer:
    """Анализирует описание объявления для извлечения данных фильтров"""
    
    # Ключевые слова для поиска комиссии (ОТСУТСТВИЕ комиссии)
    NO_COMMISSION_KEYWORDS = [
        "senza commissioni", "senza commissione",
        "no commission", "no agenzia", "no agenzia",
        "privato", "proprietario", "proprietaria",
        "senza spese agenzia", "senza spese",
        "seller pays commission", "agency paid"
    ]
    
    # Ключевые слова для запретов на животных
    PETS_BAN_KEYWORDS = [
        "no animali", "no animali", "animali non ammessi", 
        "no pets", "pets not allowed", "vietati animali",
        "non sono ammessi animali", "senza animali"
    ]
    
    # Ключевые слова для запретов на детей
    CHILDREN_BAN_KEYWORDS = [
        "no bambini", "no children", "bambini non ammessi",
        "vietati bambini", "no families with children",
        "non sono ammessi bambini", "senza bambini"
    ]
    
    # Ключевые слова для типа ремонта
    RENOVATED_KEYWORDS = [
        "ristrutturato", "completamente ristrutturato",
        "nuova ristrutturazione", "appena ristrutturato",
        "recently renovated", "fully renovated"
    ]
    
    NEW_CONSTRUCTION_KEYWORDS = [
        "nuovo", "nuova costruzione", "appena costruito",
        "new building", "newly built", "brand new",
        "nuova realizzazione"
    ]
    
    NOT_RENOVATED_KEYWORDS = [
        "da ristrutturare", "da rinnovare",
        "necessita ristrutturazione", "needs renovation",
        "requires renovation", "da recuperare"
    ]
    
    PARTIALLY_RENOVATED_KEYWORDS = [
        "parzialmente ristrutturato", "partly renovated",
        "partially renovated", "semi-renovated"
    ]
    
    # Удалено: LUXURY_KEYWORDS - больше не используется
    # Все "люксовые" квартиры теперь классифицируются как "renovated"
    
    # Ключевые слова для типа здания
    HISTORIC_BUILDING_KEYWORDS = [
        "palazzo storico", "edificio storico", "palazzo d'epoca",
        "historic building", "antico", "d'epoca",
        "monumento", "architettonico", "storico", "heritage",
        "palazzo signorile", "edificio d'epoca", "architecture d'epoca"
    ]
    
    NEW_BUILDING_KEYWORDS = [
        "nuovo edificio", "edificio nuovo", "building new",
        "modern structure", "new construction", "construction neuve",
        "costruzione recente"
    ]
    
    RENOVATED_BUILDING_KEYWORDS = [
        "palazzo ristrutturato", "edificio ristrutturato",
        "building renovated", "completamente ristrutturato",
        "edificio completamente ristrutturato"
    ]
    
    @classmethod
    def analyze(cls, description: str, **kwargs) -> Dict[str, Any]:
        """
        Анализирует описание и извлекает информацию о фильтрах
        
        Args:
            description: Текст описания объявления
            **kwargs: Дополнительные параметры (напр., floor, total_floors из JSON)
        
        Returns:
            Dict с ключами:
            - agency_commission: Optional[bool] (False = без комиссии, None/True = с комиссией)
            - pets_allowed: Optional[bool] (False = запрет, True = разрешено, None = неизвестно)
            - children_friendly: Optional[bool] (False = запрет, True = разрешено, None = неизвестно)
            - renovation_type: Optional[str]
            - building_type: Optional[str]
            - year_built: Optional[int]
            - total_floors: Optional[int]
            - floor_number: Optional[int]
            - is_first_floor: Optional[bool]
            - is_top_floor: Optional[bool]
            - park_nearby: Optional[bool]
            - noisy_roads_nearby: Optional[bool]
        """
        if not description:
            return cls._get_defaults(**kwargs)
        
        desc_lower = description.lower()
        
        # Анализ этажей
        floor_data = cls._analyze_floor_normalized(description, **kwargs)
        
        result = {
            'agency_commission': cls._analyze_commission(desc_lower),
            'pets_allowed': cls._analyze_pets(desc_lower),
            'children_friendly': cls._analyze_children(desc_lower),
            'renovation_type': cls._analyze_renovation(desc_lower),
            'building_type': cls._analyze_building_type(desc_lower),
            'year_built': cls._analyze_year_built(description),
            'total_floors': floor_data.get('total_floors'),
            'floor_number': floor_data.get('floor_number'),
            'is_first_floor': floor_data.get('is_first_floor'),
            'is_top_floor': floor_data.get('is_top_floor'),
            'park_nearby': cls._analyze_park(desc_lower),
            'noisy_roads_nearby': None,  # Пока недостаточно данных для определения
        }
        
        return result
    
    @classmethod
    def _get_defaults(cls, **kwargs) -> Dict[str, Any]:
        """Возвращает значения по умолчанию"""
        floor_data = cls._analyze_floor_normalized("", **kwargs) if kwargs else {}
        
        return {
            'agency_commission': None,
            'pets_allowed': None,  # Изменено: None вместо True (неизвестно по умолчанию)
            'children_friendly': None,  # Изменено: None вместо True (неизвестно по умолчанию)
            'renovation_type': None,
            'building_type': None,  # Изменено: None вместо 'modern'
            'year_built': None,
            'total_floors': floor_data.get('total_floors'),
            'floor_number': floor_data.get('floor_number'),
            'is_first_floor': floor_data.get('is_first_floor'),
            'is_top_floor': floor_data.get('is_top_floor'),
            'park_nearby': None,
            'noisy_roads_nearby': None,
        }
    
    @classmethod
    def _analyze_commission(cls, desc_lower: str) -> Optional[bool]:
        """
        Анализирует наличие комиссии
        
        Returns:
            False - нет комиссии
            None - не указано / есть комиссия
        """
        if any(kw in desc_lower for kw in cls.NO_COMMISSION_KEYWORDS):
            return False
        return None
    
    @classmethod
    def _analyze_pets(cls, desc_lower: str) -> Optional[bool]:
        """
        Анализирует политику по животным
        
        Returns:
            False - явный запрет на животных в ОПИСАНИИ
            True - явное разрешение в описании
            None - информация отсутствует
        """
        # Проверяем явные запреты
        if any(kw in desc_lower for kw in cls.PETS_BAN_KEYWORDS):
            return False
        
        # Проверяем явные разрешения
        pets_allowed_keywords = [
            "animali ammessi", "pets allowed", "pets welcome",
            "animali domestici ammessi", "si accettano animali"
        ]
        if any(kw in desc_lower for kw in pets_allowed_keywords):
            return True
        
        # Если ничего не указано - возвращаем None
        return None
    
    @classmethod
    def _analyze_children(cls, desc_lower: str) -> Optional[bool]:
        """
        Анализирует политику по детям
        
        Returns:
            False - явный запрет на детей в ОПИСАНИИ
            True - явное разрешение в описании
            None - информация отсутствует
        """
        # Проверяем явные запреты
        if any(kw in desc_lower for kw in cls.CHILDREN_BAN_KEYWORDS):
            return False
        
        # Проверяем явные разрешения
        children_allowed_keywords = [
            "bambini ammessi", "children allowed", "children welcome",
            "adatto a famiglie", "family friendly", "si accettano bambini"
        ]
        if any(kw in desc_lower for kw in children_allowed_keywords):
            return True
        
        # Если ничего не указано - возвращаем None
        return None
    
    @classmethod
    def _analyze_renovation(cls, desc_lower: str) -> Optional[str]:
        """Анализирует тип ремонта"""
        
        # Проверяем типы в порядке приоритета
        if any(kw in desc_lower for kw in cls.RENOVATED_KEYWORDS):
            return "renovated"
        
        if any(kw in desc_lower for kw in cls.NEW_CONSTRUCTION_KEYWORDS):
            return "new_construction"
        
        if any(kw in desc_lower for kw in cls.PARTIALLY_RENOVATED_KEYWORDS):
            return "partially_renovated"
        
        if any(kw in desc_lower for kw in cls.NOT_RENOVATED_KEYWORDS):
            return "not_renovated"
        
        return None
    
    @classmethod
    def _analyze_building_type(cls, desc_lower: str) -> Optional[str]:
        """Анализирует тип здания"""
        
        if any(kw in desc_lower for kw in cls.HISTORIC_BUILDING_KEYWORDS):
            return "historic"
        
        if any(kw in desc_lower for kw in cls.NEW_BUILDING_KEYWORDS):
            return "new_construction"
        
        # Если есть слово "ristrutturato" в контексте здания
        if any(kw in desc_lower for kw in cls.RENOVATED_BUILDING_KEYWORDS):
            return "renovated_building"
        
        # Если упоминается современность
        if any(kw in desc_lower for kw in ["moderno", "contemporaneo", "modern", "contemporary"]):
            return "modern"
        
        # Если ничего не указано - возвращаем None
        return None
    
    @classmethod
    def _analyze_year_built(cls, description: str) -> Optional[int]:
        """
        Извлекает год постройки из описания
        
        Ищет паттерны вроде "costruito nel 1950", "built in 1950", "del 1950"
        """
        patterns = [
            r"costruito\s+(?:nel|in|nel\s+)?(\d{4})",
            r"built\s+(?:in\s+)?(\d{4})",
            r"del\s+(\d{4})",
            r"anno\s+(?:di\s+costruzione\s+)?(\d{4})",
            r"(\d{4})\s+(?:anno|year)",
            r"risale\s+al\s+(\d{4})",
            r"datato\s+(\d{4})",
            r"edificio\s+del\s+(\d{4})",
            r"palazzo\s+del\s+(\d{4})",
            r"realizzato\s+nel\s+(\d{4})",
            r"anno\s+di\s+realizzazione:\s*(\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                # Проверяем что год разумный (1800-текущий год)
                if 1800 <= year <= datetime.now().year:
                    return year
        
        return None
    
    @classmethod
    def _analyze_total_floors(cls, description: str, **kwargs) -> Optional[int]:
        """
        Извлекает количество этажей в доме
        
        Может быть в kwargs как total_floors из JSON, или извлекается из текста
        """
        # Сначала проверяем kwargs (для Immobiliare которая передает JSON)
        if 'total_floors' in kwargs and kwargs['total_floors']:
            return kwargs['total_floors']
        
        # Проверяем поле floor если оно содержит информацию о количестве этажей
        if 'floor' in kwargs and kwargs['floor']:
            floor_data = kwargs['floor']
        elif 'floor_data' in kwargs and kwargs['floor_data']:
            floor_data = kwargs['floor_data']
        else:
            floor_data = None
        
        if floor_data:
            # Если это строка или JSON объект со строкой 'value'
            floor_str = floor_data
            if isinstance(floor_data, dict):
                floor_str = floor_data.get('value', '') or floor_data.get('floorOnlyValue', '')
            elif isinstance(floor_data, str):
                # Попробуем распарсить как JSON если это строка
                try:
                    floor_dict = json.loads(floor_data)
                    if isinstance(floor_dict, dict):
                        floor_str = floor_dict.get('value', '') or floor_dict.get('floorOnlyValue', '')
                    else:
                        floor_str = floor_data
                except (json.JSONDecodeError, ValueError):
                    # Если не JSON, используем как есть
                    floor_str = floor_data
            
            if floor_str:
                # Ищем паттерны вроде "2 piani", "3 piani", "2 piani:" в начале или везде
                patterns = [
                    r"^(\d+)\s+piani",  # "2 piani" в начале
                    r"(\d+)\s+piani:",  # "2 piani:" с двоеточием
                    r"(\d+)\s+piani",   # "2 piani" где угодно
                ]
                for pattern in patterns:
                    match = re.search(pattern, str(floor_str), re.IGNORECASE)
                    if match:
                        floors = int(match.group(1))
                        if 1 <= floors <= 50:
                            return floors
        
        # Ищем паттерны вроде "3º piano di 5", "piano 3 di 5", "floor 3 of 5"
        patterns = [
            r"piano\s+\d+\s+di\s+(\d+)",  # "piano 3 di 5"
            r"floor\s+\d+\s+of\s+(\d+)",  # "floor 3 of 5"
            r"(\d+)\s+(?:piani|piano|floors?|étages?)",  # "5 piani", "5 floors"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                floors = int(match.group(1))
                if 1 <= floors <= 50:  # Разумный диапазон
                    return floors
        
        return None
    
    @classmethod
    def _analyze_park(cls, desc_lower: str) -> Optional[bool]:
        """
        Анализирует наличие парка рядом
        
        Ищет слова вроде "parco", "park", "giardino"
        """
        park_keywords = [
            "parco", "parco pubblico", "verde pubblico",
            "park nearby", "near park", "close to park",
            "giardini", "gardens"
        ]
        
        if any(kw in desc_lower for kw in park_keywords):
            return True
        
        return None
    
    @classmethod
    def _analyze_floor_normalized(cls, description: str, **kwargs) -> Dict[str, Any]:
        """
        Нормализует информацию об этажах в числовой формат
        
        Returns:
            Dict с ключами:
            - floor_number: Optional[int] - номер этажа (0 = piano terra, -1 = seminterrato)
            - total_floors: Optional[int] - количество этажей в здании
            - is_first_floor: Optional[bool] - первый этаж (не считая ground)
            - is_top_floor: Optional[bool] - последний этаж
        """
        result = {
            'floor_number': None,
            'total_floors': None,
            'is_first_floor': None,
            'is_top_floor': None,
        }
        
        # Извлекаем floor из kwargs
        floor_data = kwargs.get('floor')
        
        if floor_data:
            # Если это JSON строка или dict
            if isinstance(floor_data, str):
                try:
                    floor_dict = json.loads(floor_data)
                    if isinstance(floor_dict, dict):
                        floor_data = floor_dict
                except (json.JSONDecodeError, ValueError):
                    # Это обычная строка
                    pass
            
            # Обработка dict (Immobiliare формат)
            if isinstance(floor_data, dict):
                floor_value = floor_data.get('floorOnlyValue') or floor_data.get('value', '')
                floor_value_lower = str(floor_value).lower()
                
                # Извлечение номера этажа
                if 'piano terra' in floor_value_lower or floor_value_lower == 't':
                    result['floor_number'] = 0
                elif 'seminterrato' in floor_value_lower or 'interrato' in floor_value_lower:
                    result['floor_number'] = -1
                elif 'piano rialzato' in floor_value_lower or floor_value_lower == 'r':
                    result['floor_number'] = 0  # Рассматриваем как ground floor
                elif 'ultimo' in floor_value_lower:
                    result['is_top_floor'] = True
                    # Пытаемся извлечь номер
                    match = re.search(r'(\d+)', floor_value_lower)
                    if match:
                        result['floor_number'] = int(match.group(1))
                else:
                    # Ищем число
                    match = re.search(r'^(\d+)', floor_value_lower)
                    if match:
                        result['floor_number'] = int(match.group(1))
                
                # Проверка на многоэтажность (2 piani: ...)
                if 'piani:' in floor_value_lower:
                    match = re.search(r'(\d+)\s+piani:', floor_value_lower)
                    if match:
                        # Это квартира на нескольких этажах, берем первый
                        result['total_floors'] = int(match.group(1))
            
            # Обработка простой строки/числа
            else:
                floor_str = str(floor_data).lower()
                
                if 'piano terra' in floor_str or floor_str == 't':
                    result['floor_number'] = 0
                elif 'seminterrato' in floor_str or 'interrato' in floor_str:
                    result['floor_number'] = -1
                elif 'piano rialzato' in floor_str or floor_str == 'r':
                    result['floor_number'] = 0
                elif 'ultimo' in floor_str:
                    result['is_top_floor'] = True
                    match = re.search(r'(\d+)', floor_str)
                    if match:
                        result['floor_number'] = int(match.group(1))
                else:
                    # Простое число
                    try:
                        result['floor_number'] = int(floor_str)
                    except ValueError:
                        # Пытаемся извлечь число из строки типа "3° piano"
                        match = re.search(r'(\d+)', floor_str)
                        if match:
                            result['floor_number'] = int(match.group(1))
        
        # Определяем is_first_floor (первый этаж после ground)
        if result['floor_number'] == 1:
            result['is_first_floor'] = True
        elif result['floor_number'] is not None and result['floor_number'] != 1:
            result['is_first_floor'] = False
        
        # Извлечение total_floors из kwargs или старого метода
        if 'total_floors' in kwargs and kwargs['total_floors']:
            result['total_floors'] = kwargs['total_floors']
        else:
            result['total_floors'] = cls._analyze_total_floors(description, **kwargs)
        
        # Определяем is_top_floor если знаем total_floors и floor_number
        if result['total_floors'] and result['floor_number'] is not None:
            if result['floor_number'] >= result['total_floors'] - 1:
                result['is_top_floor'] = True
            else:
                result['is_top_floor'] = False
        
        return result
