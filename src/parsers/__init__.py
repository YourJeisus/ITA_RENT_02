"""
Парсеры для извлечения данных с сайтов недвижимости
"""

from .base_parser import BaseParser
from .immobiliare_scraper import ImmobiliareScraper

__all__ = [
    'BaseParser',
    'ImmobiliareScraper'
] 