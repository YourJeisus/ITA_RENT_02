# 🏠 Парсеры недвижимости

Эта папка содержит парсеры для извлечения данных с сайтов недвижимости.

## 📁 Структура

```
src/parsers/
├── __init__.py              # Экспорт парсеров
├── base_parser.py           # Базовый класс для всех парсеров
├── immobiliare_scraper.py   # Асинхронный скрапер для Immobiliare.it
├── run_scraping.py          # 🚀 СКРИПТ ДЛЯ ЗАПУСКА ПАРСИНГА
└── README.md               # Эта документация
```

## 🚀 Быстрый старт

### Запуск парсинга

**Из корня проекта:**

```bash
# С геокодированием (полные данные)
python src/parsers/run_scraping.py

# Без геокодирования (максимальная скорость)
python src/parsers/run_scraping.py --no-geo
```

### Что делает парсер

1. **🎯 Парсит**: `https://www.immobiliare.it/affitto-case/roma/`
2. **📋 Извлекает**: ВСЕ объявления (без фильтров)
3. **⚡ Режим**: АСИНХРОННЫЙ (все страницы параллельно)
4. **📸 Собирает**: ВСЕ фотографии для каждого объявления
5. **🗺️ Получает**: Координаты из JSON или геокодирование
6. **💾 Сохраняет**: Все данные в PostgreSQL базу

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

### Пример использования в коде

```python
from src.parsers.immobiliare_scraper import ImmobiliareScraper

# Создаем скрапер
scraper = ImmobiliareScraper(enable_geocoding=True)

# Парсим 5 страниц
listings = await scraper.scrape_multiple_pages(max_pages=5)

# Получаем статистику
print(f"Найдено: {len(listings)} объявлений")
```

## 📊 Результат парсинга

Каждое объявление содержит:

```python
{
    'external_id': '123456789',
    'source': 'immobiliare',
    'title': 'Appartamento - 3 locali',
    'price': 1500,
    'property_type': 'apartment',  # См. типы ниже
    'rooms': 3,
    'area': 85,
    'address': 'Via del Corso, 123',
    'city': 'Roma',
    'latitude': 41.9028,
    'longitude': 12.4964,
    'images': [
        'https://pwm.im-cdn.it/image/123/large.jpg',
        'https://pwm.im-cdn.it/image/124/large.jpg',
        # ... до 30+ фотографий
    ],
    'url': 'https://www.immobiliare.it/annunci/123456789/',
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
