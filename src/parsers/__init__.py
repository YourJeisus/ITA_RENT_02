"""
Парсеры для извлечения данных с сайтов недвижимости
"""
from .base_parser import BaseParser
from .casa_scraper import CasaScraper
from .subito_scraper import SubitoScraper
from .idealista_scraper import IdealistaScraper
from .immobiliare_scraper import ImmobiliareScraper

__all__ = [
    'BaseParser',
    'CasaScraper',
    'SubitoScraper',
    'IdealistaScraper',
    'ImmobiliareScraper'
] 