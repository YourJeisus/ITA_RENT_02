# 🏠 Парсер Immobiliare.it

## Обзор

Парсер для сайта [Immobiliare.it](https://www.immobiliare.it) - одного из крупнейших итальянских сайтов недвижимости. Парсер интегрирован в общую архитектуру проекта и поддерживает как прямые запросы, так и использование ScraperAPI для обхода блокировок.

## Особенности

### ✅ Что умеет парсер

- **JSON-парсинг**: Использует данные из `__NEXT_DATA__` для более надежного извлечения информации
- **Гибкая фильтрация**: Поддержка всех основных фильтров поиска
- **Нормализация данных**: Приведение к единому формату проекта
- **Дедупликация**: Автоматическое удаление дубликатов
- **Обработка ошибок**: Устойчивость к изменениям структуры сайта
- **ScraperAPI интеграция**: Обход блокировок и rate limiting

### 🎯 Поддерживаемые фильтры

```python
filters = {
    'city': 'roma',              # Город (обязательно)
    'min_price': 800,            # Минимальная цена в EUR
    'max_price': 1500,           # Максимальная цена в EUR
    'min_rooms': 2,              # Минимальное количество комнат
    'max_rooms': 4,              # Максимальное количество комнат
    'min_area': 50,              # Минимальная площадь в м²
    'max_area': 120,             # Максимальная площадь в м²
    'property_type': 'apartment', # Тип недвижимости
    'furnished': True            # Меблированная
}
```

### 🏙️ Поддерживаемые города

- Roma
- Milano
- Napoli
- Torino
- Firenze
- Bologna
- Venezia
- Bari
- Catania
- Palermo

## Использование

### 1. Прямое использование парсера

```python
from src.parsers.immobiliare_parser import ImmobiliareParser

# Инициализация
parser = ImmobiliareParser()

# Настройка фильтров
filters = {
    'city': 'roma',
    'min_price': 800,
    'max_price': 1500,
    'min_rooms': 2
}

# Парсинг
listings = parser.scrape_listings(
    filters=filters,
    max_pages=3,
    use_scraperapi=True
)

print(f"Найдено {len(listings)} объявлений")
```

### 2. Через сервис парсинга

```python
from src.services.scraping_service import ScrapingService

# Инициализация сервиса
service = ScrapingService()

# Парсинг одного источника
listings = service.scrape_single_source(
    source='immobiliare',
    filters={'city': 'roma'},
    max_pages=2
)

# Парсинг с сохранением в БД
stats = service.scrape_and_save(
    filters={'city': 'milano', 'min_price': 1000},
    db=db_session,
    sources=['immobiliare'],
    max_pages=5
)
```

### 3. Через API

```bash
# Получить информацию о парсере
GET /api/v1/scraping/parsers/immobiliare

# Протестировать парсер
POST /api/v1/scraping/test
{
    "source": "immobiliare",
    "test_filters": {"city": "roma"}
}

# Запустить парсинг
POST /api/v1/scraping/run
{
    "filters": {
        "city": "roma",
        "min_price": 800,
        "max_price": 1500
    },
    "sources": ["immobiliare"],
    "max_pages": 3,
    "use_scraperapi": true
}
```

## Структура данных

### Входящие фильтры

```python
{
    "city": str,              # Название города
    "min_price": int,         # Минимальная цена
    "max_price": int,         # Максимальная цена
    "min_rooms": int,         # Минимальное количество комнат
    "max_rooms": int,         # Максимальное количество комнат
    "min_area": int,          # Минимальная площадь
    "max_area": int,          # Максимальная площадь
    "property_type": str,     # Тип недвижимости
    "furnished": bool         # Меблированная
}
```

### Результат парсинга

```python
{
    "external_id": "12345678",
    "source": "immobiliare",
    "url": "https://www.immobiliare.it/annunci/...",
    "title": "Appartamento in affitto a Roma",
    "description": "Bellissimo appartamento...",
    "price": 1200.0,
    "price_currency": "EUR",
    "property_type": "apartment",
    "rooms": 3,
    "bathrooms": 2,
    "area": 85.0,
    "floor": "2",
    "city": "Roma",
    "district": "Centro Storico",
    "address": "Via del Corso, 123",
    "images": [
        "https://img.immobiliare.it/...",
        "https://img.immobiliare.it/..."
    ],
    "agency_name": "Agenzia Immobiliare Roma",
    "is_active": true,
    "scraped_at": null
}
```

## Настройка

### Переменные окружения

```bash
# ScraperAPI ключ (рекомендуется)
SCRAPERAPI_KEY=your_scraperapi_key_here

# User Agent для запросов
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

### Конфигурация в коде

```python
# Настройка парсера
parser = ImmobiliareParser()

# Проверка настроек
print(f"ScraperAPI: {'✅' if parser.scraperapi_key else '❌'}")
print(f"Поддерживаемые города: {parser.get_supported_cities()}")
```

## Тестирование

### Запуск тестов

```bash
# Базовое тестирование
python test_immobiliare_parser.py

# Тестирование через API
curl -X POST "http://localhost:8000/api/v1/scraping/test" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"source": "immobiliare"}'
```

### Пример тестового вывода

```
🧪 Тестирование парсера Immobiliare.it
==================================================
📋 Тестовые фильтры: {'city': 'roma', 'min_price': 800, 'max_price': 1500, 'min_rooms': 2}

🔗 Тест 1: Построение URL
   URL: https://www.immobiliare.it/affitto-case/roma/?prezzoMin=800&prezzoMax=1500&localiMin=2

✅ Тест 2: Валидация фильтров
   Очищенные фильтры: {'city': 'roma', 'min_price': 800, 'max_price': 1500, 'min_rooms': 2}

🏙️ Тест 3: Поддерживаемые города
   Города: ['roma', 'milano', 'napoli', 'torino', 'firenze', 'bologna', 'venezia', 'bari', 'catania', 'palermo']

🕷️ Тест 4: Парсинг объявлений
   ✅ Найдено 20 объявлений

🎉 Все тесты завершены успешно!
```

## Производительность

### Рекомендуемые настройки

- **max_pages**: 3-5 для обычного поиска, 1-2 для тестирования
- **use_scraperapi**: `true` для production, `false` для разработки
- **Задержки**: 2 секунды между страницами (встроено)

### Лимиты

- **ScraperAPI**: зависит от вашего плана
- **Прямые запросы**: ~10-20 запросов в минуту
- **Объявления на странице**: обычно 20-25

## Обработка ошибок

### Типичные ошибки

1. **Блокировка IP**: Используйте ScraperAPI
2. **Изменение структуры**: Парсер автоматически пробует разные пути к данным
3. **Нет результатов**: Проверьте фильтры и доступность города

### Логирование

```python
import logging

# Включить подробное логирование
logging.getLogger('src.parsers.immobiliare_parser').setLevel(logging.DEBUG)
```

## Расширение функциональности

### Добавление нового города

```python
# В классе ImmobiliareParser
self.city_mapping = {
    'roma': 'roma',
    'your_city': 'your_city_slug',  # Добавить здесь
    # ...
}
```

### Добавление нового фильтра

1. Обновить `build_search_url()` для построения URL
2. Добавить валидацию в `validate_filters()`
3. Обновить нормализацию в `normalize_listing_data()`

## Интеграция с базой данных

Парсер автоматически интегрируется с базой данных через сервис:

```python
# Парсинг с сохранением
stats = scraping_service.scrape_and_save(
    filters={'city': 'roma'},
    db=db_session,
    update_existing=True  # Обновлять существующие объявления
)

print(f"Создано: {stats['database_stats']['created']}")
print(f"Обновлено: {stats['database_stats']['updated']}")
```

## Мониторинг

### Метрики для отслеживания

- Количество успешных запросов
- Время выполнения парсинга
- Количество найденных объявлений
- Ошибки парсинга

### Логи

Все важные события логируются с соответствующими уровнями:

- `INFO`: Успешные операции
- `WARNING`: Пропущенные объявления
- `ERROR`: Ошибки парсинга
- `DEBUG`: Подробная информация

---

**Статус**: ✅ Готов к использованию  
**Последнее обновление**: Январь 2025  
**Версия**: 1.0.0
