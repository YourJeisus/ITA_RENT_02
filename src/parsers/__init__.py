"""
Парсеры для извлечения данных с сайтов недвижимости
"""

from .base_parser import BaseParser
from .immobiliare_parser import ImmobiliareParser
from .immobiliare_scraper import ImmobiliareScraper

__all__ = [
    'BaseParser',
    'ImmobiliareParser', 
    'ImmobiliareScraper'
] 