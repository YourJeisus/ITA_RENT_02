# 🏠 Парсеры недвижимости

Эта папка содержит парсеры для извлечения данных с сайтов недвижимости.

## 📁 Структура

```
src/parsers/
├── __init__.py                  # Экспорт парсеров
├── base_parser.py               # Базовый класс для всех парсеров
├── immobiliare_scraper.py       # Асинхронный скрапер для Immobiliare.it
├── subito_scraper.py            # Асинхронный скрапер для Subito.it
├── idealista_scraper.py         # 🆕 Асинхронный скрапер для Idealista.it
├── run_scraping.py              # Скрипт для запуска парсинга Immobiliare
├── run_subito_scraping.py       # Скрипт для запуска парсинга Subito
├── run_idealista_scraping.py    # 🆕 Скрипт для запуска парсинга Idealista
├── run_all_scraping.py          # 🚀 ПАРАЛЛЕЛЬНЫЙ ПАРСИНГ ВСЕХ ИСТОЧНИКОВ
└── README.md                   # Эта документация
```

## 🚀 Быстрый старт

### Запуск парсинга всех источников (РЕКОМЕНДУЕТСЯ)

**Параллельный парсинг Immobiliare.it + Subito.it + Idealista.it:**

```bash
# С геокодированием (полные данные)
python src/parsers/run_all_scraping.py

# Без геокодирования (максимальная скорость)
python src/parsers/run_all_scraping.py --no-geo
```

### Запуск отдельных источников

**Только Immobiliare.it:**

```bash
python src/parsers/run_scraping.py
```

**Только Subito.it:**

```bash
python src/parsers/run_subito_scraping.py
```

**Только Idealista.it:**

```bash
python src/parsers/run_idealista_scraping.py
```

### Что делают парсеры

**Immobiliare.it:**

1. **🎯 Парсит**: `https://www.immobiliare.it/affitto-case/roma/`
2. **📋 Извлекает**: ВСЕ объявления из JSON (**NEXT_DATA**)
3. **📸 Собирает**: ВСЕ фотографии (large, medium, small)

**Subito.it:**

1. **🎯 Парсит**: `https://www.subito.it/annunci-lazio/affitto/immobili/roma/roma/`
2. **📋 Извлекает**: Объявления из HTML контейнеров
3. **📸 Собирает**: Доступные изображения

**Idealista.it:**

1. **🎯 Парсит**: `https://www.idealista.it/affitto-case/roma-roma/`
2. **📋 Извлекает**: Объявления из HTML контейнеров (article.item)
3. **📸 Собирает**: Основные изображения объявлений

**Общие возможности:**

- **⚡ Режим**: АСИНХРОННЫЙ (все страницы параллельно)
- **🗺️ Получает**: Координаты из данных или геокодирование
- **💾 Сохраняет**: Все данные в PostgreSQL базу
- **🔄 Дедупликация**: По external_id + source

### Требования

- ✅ ScraperAPI ключ в `.env` файле
- ✅ PostgreSQL база данных настроена
- ✅ Все зависимости установлены (`pip install -r requirements.txt`)

## 🔧 Технические детали

### ImmobiliareScraper

- **Метод**: `scrape_multiple_pages(max_pages=10)`
- **Технология**: ScraperAPI Async API + Sync fallback
- **Режим**: ⚡ **АСИНХРОННЫЙ** (все страницы параллельно)
- **Данные**: Извлечение из `__NEXT_DATA__` JSON
- **Фото**: Все размеры (large, medium, small)
- **Координаты**: Автоматическое извлечение из JSON + геокодирование
- **Производительность**:
  - С геокодированием: ~4.65 объявлений/сек
  - Без геокодирования: ~4.83 объявлений/сек
  - Среднее фото на объявление: ~25 шт.
  - Дедупликация по external_id

### SubitoScraper

- **Метод**: `scrape_multiple_pages(max_pages=10)`
- **Технология**: ScraperAPI Async API + Sync fallback
- **Режим**: ⚡ **АСИНХРОННЫЙ** (все страницы параллельно)
- **Данные**: Извлечение из HTML селекторов
- **Фото**: Парсинг img тегов (src, data-src)
- **Координаты**: Геокодирование через OpenStreetMap API
- **Особенности**:
  - Гибкая система селекторов для поиска объявлений
  - Извлечение ID из URL patterns
  - Определение типа недвижимости из заголовков
  - Автоматическое определение меблированности

### IdealistaScraper

- **Метод**: `scrape_multiple_pages(max_pages=10)`
- **Технология**: ScraperAPI Async API + Sync fallback
- **Режим**: ⚡ **АСИНХРОННЫЙ** (все страницы параллельно)
- **Данные**: Извлечение из HTML селекторов (article.item, div.item)
- **Фото**: Парсинг img тегов (src attributes)
- **Координаты**: Геокодирование через OpenStreetMap API
- **Особенности**:
  - Поддержка разных контейнеров объявлений (data-element-id, data-adid)
  - Извлечение ID из URL patterns (/immobile/123456/)
  - Парсинг цен с символом €
  - Автоматическое определение количества комнат и площади

### Пример использования в коде

**Один источник:**

```python
from src.parsers.immobiliare_scraper import ImmobiliareScraper
from src.parsers.subito_scraper import SubitoScraper
from src.parsers.idealista_scraper import IdealistaScraper

# Создаем скрапер Immobiliare
immobiliare_scraper = ImmobiliareScraper(enable_geocoding=True)
listings_immobiliare = await immobiliare_scraper.scrape_multiple_pages(max_pages=5)

# Создаем скрапер Subito
subito_scraper = SubitoScraper(enable_geocoding=True)
listings_subito = await subito_scraper.scrape_multiple_pages(max_pages=5)

# Создаем скрапер Idealista
idealista_scraper = IdealistaScraper(enable_geocoding=True)
listings_idealista = await idealista_scraper.scrape_multiple_pages(max_pages=5)

print(f"Immobiliare: {len(listings_immobiliare)} объявлений")
print(f"Subito: {len(listings_subito)} объявлений")
print(f"Idealista: {len(listings_idealista)} объявлений")
```

**Параллельный парсинг всех источников:**

```python
import asyncio
from src.parsers.immobiliare_scraper import ImmobiliareScraper
from src.parsers.subito_scraper import SubitoScraper
from src.parsers.idealista_scraper import IdealistaScraper

async def scrape_all():
    # Создаем скраперы
    immobiliare = ImmobiliareScraper(enable_geocoding=True)
    subito = SubitoScraper(enable_geocoding=True)
    idealista = IdealistaScraper(enable_geocoding=True)

    # Запускаем параллельно
    results = await asyncio.gather(
        immobiliare.scrape_multiple_pages(max_pages=5),
        subito.scrape_multiple_pages(max_pages=5),
        idealista.scrape_multiple_pages(max_pages=5)
    )

    all_listings = results[0] + results[1] + results[2]  # Объединяем все объявления
    print(f"Всего найдено: {len(all_listings)} объявлений")

asyncio.run(scrape_all())
```

## 📊 Результат парсинга

Каждое объявление содержит унифицированную структуру данных независимо от источника:

**Immobiliare.it объявление:**

```python
{
    'external_id': '123456789',
    'source': 'immobiliare',
    'title': 'Appartamento - 3 locali',
    'price': 1500,
    'property_type': 'apartment',
    'rooms': 3,
    'area': 85,
    'address': 'Via del Corso, 123',
    'city': 'Roma',
    'latitude': 41.9028,
    'longitude': 12.4964,
    'images': [
        'https://pwm.im-cdn.it/image/123/large.jpg',
        'https://pwm.im-cdn.it/image/124/large.jpg',
        # ... до 30+ фотографий высокого качества
    ],
    'url': 'https://www.immobiliare.it/annunci/123456789/',
    'furnished': True,
    'bathrooms': 2,
    'agency_name': 'Agenzia Immobiliare Roma',
    # ... и другие поля
}
```

**Subito.it объявление:**

```python
{
    'external_id': '987654321',
    'source': 'subito',
    'title': 'Appartamento in affitto trilocale',
    'price': 1200,
    'property_type': 'apartment',
    'rooms': 3,
    'area': 70,
    'address': 'Zona Trastevere',
    'city': 'Roma',
    'latitude': 41.8919,
    'longitude': 12.4633,
    'images': [
        'https://subito.it/images/123.jpg',
        'https://subito.it/images/124.jpg',
        # ... фотографии среднего качества
    ],
    'url': 'https://www.subito.it/annunci/appartamento-987654321',
    'furnished': True,
    'bathrooms': None,  # Subito часто не указывает
    'agency_name': None,  # Частные объявления
    # ... и другие поля
}
```

### 🏠 Типы недвижимости (property_type)

Скрапер автоматически определяет тип недвижимости:

| Тип         | Описание                | Итальянские термины          |
| ----------- | ----------------------- | ---------------------------- |
| `apartment` | Квартира (по умолчанию) | Appartamento, Bilocale, etc. |
| `penthouse` | Пентхаус                | Attico, Superattico          |
| `house`     | Дом, вилла              | Villa, Casa, Villetta        |
| `studio`    | Студия, однокомнатная   | Monolocale, Studio           |
| `room`      | Комната                 | Stanza, Camera, Posto letto  |

**Статистика из реальных данных:**

- 🏠 Квартиры: ~92% (самый популярный тип)
- 🏢 Пентхаусы: ~6% (премиум сегмент)
- 🏘️ Дома: ~2% (частные дома и виллы)
- 🏠 Студии: редко на первых страницах
- 🚪 Комнаты: в зависимости от сезона

## 🛠️ Интеграция с API

Парсер интегрирован через `ScrapingService`:

```python
from src.services.scraping_service import ScrapingService

service = ScrapingService()
result = await service.scrape_and_save(
    filters={"city": "roma"},
    db=db_session,
    max_pages=5
)
```

## 📝 Логи

Парсер создает подробные логи:

- ✅ Успешные операции
- ⚠️ Предупреждения
- ❌ Ошибки с деталями

## ⚡ Основные особенности

### 🚀 Асинхронная архитектура

- Использует ScraperAPI Async Jobs API
- Fallback на обычный ScraperAPI при проблемах
- Семафор для контроля параллелизма (максимум 3 запроса)
- Автоматическая дедупликация по external_id

### 🗺️ Геокодирование

- Сначала извлекает координаты из JSON
- При необходимости использует OpenStreetMap Nominatim API
- Проверка координат на принадлежность Италии

### 📸 Максимум фотографий

- Извлекает все доступные фотографии
- Поддерживает разные размеры (large, medium, small)
- В среднем 25+ фотографий на объявление

### 🛡️ Надежность

- Множественные попытки при ошибках
- Экспоненциальные задержки
- Fallback стратегии
- Подробное логирование
