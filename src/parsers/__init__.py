"""
Парсеры для извлечения данных с сайтов недвижимости
"""

from .base_parser import BaseParser
from .immobiliare_scraper import ImmobiliareScraper
from .subito_scraper import SubitoScraper
from .idealista_scraper import IdealistaScraper

__all__ = [
    'BaseParser',
    'ImmobiliareScraper',
    'SubitoScraper',
    'IdealistaScraper'
] 