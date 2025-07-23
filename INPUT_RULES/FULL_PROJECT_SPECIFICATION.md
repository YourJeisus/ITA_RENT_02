# 📋 Полная техническая спецификация ITA_RENT_BOT

## 🎯 Обзор проекта

**ITA_RENT_BOT** - это полнофункциональная платформа для агрегации и поиска объявлений аренды недвижимости в Италии с системой уведомлений через Telegram.

### Ключевые возможности

- 🔍 Агрегация объявлений с популярных итальянских сайтов недвижимости
- 📱 Система уведомлений через Telegram бота
- 🌐 Современный веб-интерфейс с картами
- 🔐 Многоуровневая система авторизации
- 💾 Интеллектуальное кеширование
- 📊 Система подписок с тарифными планами
- 🗺️ Интерактивные карты с геолокацией

## 🏗️ Архитектура системы

### Общая архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        ITA_RENT_BOT                             │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Frontend      │   API Server    │      External Services      │
│   (React TS)    │   (FastAPI)     │                             │
│                 │                 │  ┌─────────────────────────┐│
│ ┌─────────────┐ │ ┌─────────────┐ │  │    Telegram Bot API     ││
│ │ Web App     │◄┼►│ REST API    │ │  └─────────────────────────┘│
│ │ (Vite/React)│ │ │ (FastAPI)   │ │                             │
│ └─────────────┘ │ └─────────────┘ │  ┌─────────────────────────┐│
│                 │                 │  │     ScraperAPI          ││
│ ┌─────────────┐ │ ┌─────────────┐ │  │  (Web Scraping Service) ││
│ │ Maps        │ │ │ Parsers     │ │  └─────────────────────────┘│
│ │ (Leaflet)   │ │ │ (Scrapers)  │ │                             │
│ └─────────────┘ │ └─────────────┘ │  ┌─────────────────────────┐│
└─────────────────┼─────────────────┤  │   Target Websites       ││
                  │                 │  │ • Idealista.it          ││
┌─────────────────┼─────────────────┤  │ • Immobiliare.it        ││
│   Data Layer    │  Bot Services   │  │ • Subito.it (planned)   ││
│                 │                 │  └─────────────────────────┘│
│ ┌─────────────┐ │ ┌─────────────┐ │                             │
│ │ PostgreSQL  │ │ │ Telegram    │ │                             │
│ │ (Primary DB)│ │ │ Bot Service │ │                             │
│ └─────────────┘ │ └─────────────┘ │                             │
│                 │                 │                             │
│ ┌─────────────┐ │ ┌─────────────┐ │                             │
│ │ Redis Cache │ │ │ Notification│ │                             │
│ │ (Optional)  │ │ │ Dispatcher  │ │                             │
│ └─────────────┘ │ └─────────────┘ │                             │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Микросервисная архитектура (рекомендуемая для масштабирования)

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Frontend   │  │   API Gateway│  │  Auth Service│  │ User Service │
│   Service    │◄►│   (FastAPI)  │◄►│   (JWT)      │◄►│  (CRUD)      │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Scraping     │  │ Notification │  │  Map Service │
│ Service      │  │   Service    │  │   (Geo)      │
│              │  │ (Telegram)   │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │ Redis Cache  │  │ Message Queue│
│   Database   │  │   Service    │  │ (RabbitMQ)   │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 🛠️ Технологический стек

### Backend (Python)

**Основной фреймворк:**

- **FastAPI** 0.104+ - современный, быстрый веб-фреймворк
- **Python** 3.11+ - язык программирования
- **Uvicorn** - ASGI сервер для production

**База данных:**

- **PostgreSQL** 15+ - основная база данных
- **SQLAlchemy** 2.0+ - ORM для работы с БД
- **Alembic** - система миграций
- **Psycopg2** - драйвер PostgreSQL

**Кеширование:**

- **Redis** 7+ - для кеширования и сессий
- **redis-py** - Python клиент для Redis

**Парсинг и скрапинг:**

- **aiohttp** - асинхронные HTTP запросы
- **BeautifulSoup4** - парсинг HTML
- **Selenium** 4+ - для динамического контента (опционально)
- **ScraperAPI** - внешний сервис для обхода блокировок

**Telegram интеграция:**

- **python-telegram-bot** 20+ - библиотека для Telegram Bot API
- **asyncio** - асинхронное программирование

**Аутентификация и безопасность:**

- **python-jose** - JWT токены
- **passlib** - хеширование паролей
- **python-multipart** - для обработки форм
- **cryptography** - криптографические функции

**Утилиты:**

- **Pydantic** 2.0+ - валидация данных и настройки
- **python-dotenv** - управление переменными окружения
- **pytest** - тестирование
- **black** + **flake8** - форматирование и линтинг кода

### Frontend (TypeScript/React)

**Основной фреймворк:**

- **React** 18+ - библиотека для UI
- **TypeScript** 5+ - типизированный JavaScript
- **Vite** 5+ - быстрый сборщик и dev сервер

**Маршрутизация и состояние:**

- **React Router** 6+ - маршрутизация SPA
- **Zustand** 4+ - управление состоянием (легче чем Redux)

**UI и стили:**

- **Sass/SCSS** - препроцессор CSS
- **CSS Modules** - локальная область видимости стилей
- **Leaflet** + **React-Leaflet** - интерактивные карты
- **Material Icons** - иконки (опционально)

**HTTP и утилиты:**

- **Axios** - HTTP клиент
- **date-fns** - работа с датами
- **react-hook-form** - обработка форм (рекомендуется)

**Инструменты разработки:**

- **ESLint** + **Prettier** - линтинг и форматирование
- **@types/\*** - типы для TypeScript
- **Vitest** - тестирование (альтернатива Jest)

### DevOps и инфраструктура

**Контейнеризация:**

- **Docker** 24+ - контейнеризация приложений
- **Docker Compose** - оркестрация локальной разработки

**Деплой и хостинг:**

- **Vercel** - деплой фронтенда (рекомендуется)
- **Railway** / **Render** / **DigitalOcean** - деплой бэкенда
- **PostgreSQL** - управляемая база данных в облаке
- **Redis Cloud** - управляемый Redis

**CI/CD (рекомендуется):**

- **GitHub Actions** - автоматизация деплоя
- **Pre-commit hooks** - проверки перед коммитом

**Мониторинг (для production):**

- **Sentry** - отслеживание ошибок
- **Grafana** + **Prometheus** - метрики и мониторинг
- **Loguru** - структурированное логирование

## 📁 Структура проекта

```
ITA_RENT_BOT/
├── 📁 backend/                       # Весь бэкенд код
│   ├── apps/                         # Микросервисы бэкенда
│   │   ├── api/                      # Основное FastAPI приложение
│   │   ├── scraper/                  # Микросервис парсинга
│   │   ├── telegram-bot/             # Telegram бот
│   │   ├── notification-worker/      # Воркер уведомлений
│   │   └── geo-service/              # Микросервис геолокации
│   ├── shared/                       # Общие бэкенд библиотеки
│   │   ├── database/                 # Общие модели и утилиты БД
│   │   ├── auth/                     # Общие утилиты авторизации
│   │   ├── cache/                    # Общие утилиты кеширования
│   │   ├── messaging/                # Общие утилиты для сообщений
│   │   ├── monitoring/               # Общие утилиты мониторинга
│   │   └── utils/                    # Общие утилиты
│   ├── scripts/                      # Бэкенд скрипты
│   │   ├── database/                 # Скрипты для БД
│   │   ├── scraping/                 # Скрипты парсинга
│   │   ├── deployment/               # Скрипты деплоя
│   │   └── monitoring/               # Скрипты мониторинга
│   └── tests/                        # Интеграционные тесты
├── 📁 frontend/                      # Весь фронтенд код
│   ├── apps/                         # Фронтенд приложения
│   │   ├── web/                      # Основное React приложение
│   │   ├── admin/                    # Админ панель
│   │   └── landing/                  # Лендинг страница
│   └── packages/                     # Общие фронтенд пакеты
│       ├── ui/                       # UI библиотека компонентов
│       ├── utils/                    # Общие утилиты фронтенда
│       └── config/                   # Общие конфигурации
├── 📁 shared/                        # Общие пакеты для всего проекта
│   ├── types/                        # Общие TypeScript/Python типы
│   ├── schemas/                      # Общие схемы данных
│   └── constants/                    # Общие константы
├── 📁 infrastructure/                # Инфраструктура как код
│   ├── docker/                       # Docker конфигурации
│   ├── kubernetes/                   # Kubernetes манифесты
│   ├── terraform/                    # Terraform конфигурации
│   └── monitoring/                   # Мониторинг настройки
├── 📁 tools/                         # Инструменты разработки
│   ├── scripts/                      # Скрипты автоматизации
│   ├── generators/                   # Генераторы кода
│   └── cli/                          # CLI инструменты
├── 📁 docs/                          # Документация
│   ├── api/                          # API документация
│   ├── architecture/                 # Архитектурная документация
│   ├── guides/                       # Руководства
│   ├── specs/                        # Спецификации
│   └── assets/                       # Диаграммы и изображения
├── 📁 data/                          # Данные и конфигурации
│   ├── fixtures/                     # Тестовые данные
│   ├── migrations/                   # Миграции данных
│   ├── seeds/                        # Начальные данные
│   └── backups/                      # Резервные копии
├── 📁 .github/                       # GitHub конфигурации
├── 📁 .vscode/                       # VS Code настройки
├── 📁 logs/                          # Логи (не в git)
└── 📁 tmp/                           # Временные файлы (не в git)              # Основной README
```

## 🗄️ Модель данных

### Основные сущности

```python
# User - Пользователь системы
class User(Base):
    id: int (PK)
    email: str (unique)
    hashed_password: str
    first_name: str
    last_name: str (optional)
    is_active: bool = True
    subscription_type: str = "free"  # free, premium_monthly, premium_annual
    telegram_chat_id: int (optional, unique)
    telegram_user_id: int (optional, unique)
    google_id: str (optional, unique)
    created_at: datetime
    updated_at: datetime

    # Relationships
    filters: List["Filter"] = relationship(back_populates="user")
    notifications: List["Notification"] = relationship(back_populates="user")

# Listing - Объявление о недвижимости
class Listing(Base):
    id: int (PK)
    external_id: str (unique)  # ID на источнике
    source: str  # idealista, immobiliare, subito
    title: str
    description: text (optional)
    price: float
    price_currency: str = "EUR"
    property_type: str  # apartment, house, room, studio
    rooms: int (optional)
    bedrooms: int (optional)
    bathrooms: int (optional)
    area: float (optional)  # площадь в м²
    floor: int (optional)
    total_floors: int (optional)
    furnished: bool (optional)
    pets_allowed: bool (optional)

    # Геолокация
    address: str
    city: str
    district: str (optional)
    latitude: float (optional)
    longitude: float (optional)

    # Медиа
    images: JSON  # список URL изображений
    virtual_tour_url: str (optional)

    # Метаданные
    url: str  # ссылка на источник
    is_active: bool = True
    scraped_at: datetime
    created_at: datetime
    updated_at: datetime

    # Индексы для быстрого поиска
    __table_args__ = (
        Index('idx_listing_city_price', 'city', 'price'),
        Index('idx_listing_rooms_area', 'rooms', 'area'),
        Index('idx_listing_coordinates', 'latitude', 'longitude'),
        Index('idx_listing_source_active', 'source', 'is_active'),
    )

# Filter - Фильтр поиска пользователя
class Filter(Base):
    id: int (PK)
    user_id: int (FK -> User.id)
    name: str  # название фильтра от пользователя

    # Параметры фильтра
    city: str (optional)
    min_price: float (optional)
    max_price: float (optional)
    property_type: str (optional)
    min_rooms: int (optional)
    max_rooms: int (optional)
    min_area: float (optional)
    max_area: float (optional)
    furnished: bool (optional)
    pets_allowed: bool (optional)

    # Геофильтры
    latitude: float (optional)
    longitude: float (optional)
    radius_km: float (optional)  # радиус поиска

    # Настройки уведомлений
    is_active: bool = True
    notification_enabled: bool = True
    last_notification_sent: datetime (optional)
    notification_frequency_hours: int = 24  # частота уведомлений

    created_at: datetime
    updated_at: datetime

    # Relationships
    user: "User" = relationship(back_populates="filters")
    notifications: List["Notification"] = relationship(back_populates="filter")

# Notification - Уведомление пользователю
class Notification(Base):
    id: int (PK)
    user_id: int (FK -> User.id)
    filter_id: int (FK -> Filter.id)
    listing_id: int (FK -> Listing.id)

    notification_type: str = "new_listing"  # new_listing, price_change
    status: str = "pending"  # pending, sent, failed
    sent_at: datetime (optional)
    error_message: str (optional)

    created_at: datetime

    # Relationships
    user: "User" = relationship(back_populates="notifications")
    filter: "Filter" = relationship(back_populates="notifications")
    listing: "Listing" = relationship()

# Subscription - Подписка и лимиты (опционально)
class Subscription(Base):
    id: int (PK)
    user_id: int (FK -> User.id, unique)
    plan_type: str  # free, premium_monthly, premium_annual
    status: str = "active"  # active, cancelled, expired

    # Лимиты
    max_filters: int
    max_notifications_per_day: int
    notification_interval_hours: int

    # Даты
    started_at: datetime
    expires_at: datetime (optional)
    cancelled_at: datetime (optional)

    created_at: datetime
    updated_at: datetime

    # Relationships
    user: "User" = relationship()
```

### Связи между сущностями

```
User (1) -----> (N) Filter
User (1) -----> (N) Notification
User (1) -----> (1) Subscription

Filter (1) -----> (N) Notification
Listing (1) -----> (N) Notification

Listing (N) <----> (N) User (через Notification)
```

## 🔧 API спецификация

### Основные эндпоинты

```python
# Авторизация
POST   /api/v1/auth/register          # Регистрация
POST   /api/v1/auth/login             # Вход по email/password
POST   /api/v1/auth/telegram          # Вход через Telegram
POST   /api/v1/auth/google            # Вход через Google
POST   /api/v1/auth/refresh           # Обновление токена
POST   /api/v1/auth/logout            # Выход
POST   /api/v1/auth/link-telegram     # Привязка Telegram к аккаунту

# Пользователи
GET    /api/v1/users/me               # Текущий пользователь
PUT    /api/v1/users/me               # Обновление профиля
DELETE /api/v1/users/me               # Удаление аккаунта
GET    /api/v1/users/subscription     # Информация о подписке

# Объявления
GET    /api/v1/listings               # Поиск объявлений
GET    /api/v1/listings/{id}          # Детали объявления
GET    /api/v1/listings/suggestions   # Предложения для автодополнения

# Фильтры
GET    /api/v1/filters                # Список фильтров пользователя
POST   /api/v1/filters                # Создание фильтра
GET    /api/v1/filters/{id}           # Детали фильтра
PUT    /api/v1/filters/{id}           # Обновление фильтра
DELETE /api/v1/filters/{id}           # Удаление фильтра
POST   /api/v1/filters/{id}/test      # Тестирование фильтра

# Уведомления
GET    /api/v1/notifications          # История уведомлений
POST   /api/v1/notifications/subscribe # Подписка на уведомления
POST   /api/v1/notifications/confirm  # Подтверждение подписки
PUT    /api/v1/notifications/{id}/read # Отметить как прочитанное

# Парсинг (админ)
POST   /api/v1/scraping/run           # Запуск парсинга
GET    /api/v1/scraping/status        # Статус парсинга
GET    /api/v1/scraping/stats         # Статистика парсинга
POST   /api/v1/scraping/cache/clear   # Очистка кеша

# Геолокация
GET    /api/v1/geo/cities             # Список городов
GET    /api/v1/geo/districts          # Районы города
POST   /api/v1/geo/geocode            # Геокодирование адреса
POST   /api/v1/geo/reverse-geocode    # Обратное геокодирование

# Система
GET    /api/v1/health                 # Проверка здоровья
GET    /api/v1/metrics                # Метрики системы
```

### Схемы данных (Pydantic)

```python
# Пользователь
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str = None

class UserUpdate(BaseModel):
    first_name: str = None
    last_name: str = None
    subscription_type: str = None

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str = None
    subscription_type: str
    is_active: bool
    created_at: datetime

# Объявление
class ListingSearch(BaseModel):
    city: str = None
    min_price: float = None
    max_price: float = None
    property_type: str = None
    min_rooms: int = None
    max_rooms: int = None
    min_area: float = None
    max_area: float = None
    furnished: bool = None
    pets_allowed: bool = None
    latitude: float = None
    longitude: float = None
    radius_km: float = None
    page: int = 1
    limit: int = 50

class ListingResponse(BaseModel):
    id: int
    source: str
    title: str
    price: float
    property_type: str
    rooms: int = None
    area: float = None
    address: str
    city: str
    images: List[str]
    url: str
    latitude: float = None
    longitude: float = None
    created_at: datetime

# Фильтр
class FilterCreate(BaseModel):
    name: str
    city: str = None
    min_price: float = None
    max_price: float = None
    property_type: str = None
    min_rooms: int = None
    max_rooms: int = None
    notification_enabled: bool = True
    notification_frequency_hours: int = 24

class FilterResponse(BaseModel):
    id: int
    name: str
    city: str = None
    min_price: float = None
    max_price: float = None
    property_type: str = None
    min_rooms: int = None
    max_rooms: int = None
    is_active: bool
    notification_enabled: bool
    created_at: datetime
```

## 🔐 Система авторизации

### Многоуровневая авторизация

1. **Email + Password** - классическая регистрация
2. **Telegram Login Widget** - авторизация через Telegram
3. **Google OAuth** - авторизация через Google
4. **Связывание аккаунтов** - один пользователь, несколько способов входа

### JWT токены

```python
# Структура JWT токена
{
    "sub": "user_id",           # ID пользователя
    "email": "user@example.com", # Email пользователя
    "subscription": "premium",   # Тип подписки
    "exp": 1640995200,          # Время истечения
    "iat": 1640908800,          # Время создания
    "type": "access"            # Тип токена (access/refresh)
}

# Refresh токен (более длительное время жизни)
{
    "sub": "user_id",
    "type": "refresh",
    "exp": 1643587200  # 30 дней
}
```

### Telegram авторизация

```python
# Проверка данных от Telegram Login Widget
def verify_telegram_auth(auth_data: dict) -> bool:
    bot_token = settings.TELEGRAM_BOT_TOKEN
    secret_key = hashlib.sha256(bot_token.encode()).digest()

    # Создаем строку для проверки
    check_string = "\n".join([
        f"{k}={v}" for k, v in sorted(auth_data.items())
        if k != "hash"
    ])

    # Вычисляем HMAC
    expected_hash = hmac.new(
        secret_key,
        check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return auth_data.get("hash") == expected_hash
```

## 🤖 Система уведомлений

### Telegram бот

```python
# Основные команды бота
/start - Приветствие и регистрация
/help - Справка по командам
/register - Регистрация в системе
/filters - Список активных фильтров
/add_filter - Добавить новый фильтр
/edit_filter - Редактировать фильтр
/delete_filter - Удалить фильтр
/subscription - Информация о подписке
/settings - Настройки уведомлений
/pause - Приостановить уведомления
/resume - Возобновить уведомления
```

### Формат уведомлений

```python
# Шаблон уведомления о новом объявлении
template = """
🏠 <b>Новое объявление!</b>

📍 {address}
💰 <b>{price}€/месяц</b>
📐 {area} м² • 🚪 {rooms} комн.
{additional_info}

🔍 <i>Фильтр: "{filter_name}"</i>

<a href="{url}">👀 Посмотреть объявление</a>
<a href="{map_url}">🗺 Показать на карте</a>

/pause_{filter_id} - приостановить этот фильтр
"""

# Пример готового уведомления
🏠 Новое объявление!

📍 Via del Corso, 123, Roma
💰 1,800€/месяц
📐 85 м² • 🚪 3 комн. • 🛏 2 сп.
🪑 Меблированная • 🐕 Разрешены питомцы

🔍 Фильтр: "Квартира в центре Рима"

👀 Посмотреть объявление
🗺 Показать на карте

/pause_123 - приостановить этот фильтр
```

### Логика отправки уведомлений

```python
# Алгоритм диспетчера уведомлений
async def dispatch_notifications():
    # 1. Получить все активные фильтры
    active_filters = get_active_filters()

    for filter in active_filters:
        # 2. Проверить время последнего уведомления
        if not should_send_notification(filter):
            continue

        # 3. Найти новые объявления по фильтру
        new_listings = find_new_listings(filter)

        if not new_listings:
            continue

        # 4. Проверить лимиты подписки
        if not check_notification_limits(filter.user):
            continue

        # 5. Отправить уведомления
        for listing in new_listings[:5]:  # максимум 5 за раз
            await send_telegram_notification(
                filter.user.telegram_chat_id,
                listing,
                filter
            )

        # 6. Обновить время последнего уведомления
        update_last_notification_time(filter)
```

## 🗺️ Система карт

### Leaflet интеграция

```typescript
// Основной компонент карты
interface MapViewProps {
  listings: Listing[];
  center?: [number, number];
  zoom?: number;
  onListingClick?: (listing: Listing) => void;
}

const MapView: React.FC<MapViewProps> = ({
  listings,
  center = [41.9028, 12.4964], // Рим по умолчанию
  zoom = 11,
  onListingClick,
}) => {
  return (
    <MapContainer center={center} zoom={zoom} className="map-container">
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="© OpenStreetMap contributors"
      />

      {listings.map((listing) => (
        <Marker
          key={listing.id}
          position={[listing.latitude, listing.longitude]}
          icon={getMarkerIcon(listing.source)}
          eventHandlers={{
            click: () => onListingClick?.(listing),
          }}
        >
          <Popup>
            <ListingPopup listing={listing} />
          </Popup>
        </Marker>
      ))}

      <MarkerClusterGroup>{/* Кластеризация маркеров */}</MarkerClusterGroup>
    </MapContainer>
  );
};
```

### Геолокация

```python
# Сервис геолокации
class GeoService:
    @staticmethod
    def extract_coordinates_from_listing(listing_html: str, source: str) -> Tuple[float, float]:
        """Извлечение координат из HTML страницы объявления"""
        if source == "idealista":
            return IdealistaParser.extract_coordinates(listing_html)
        elif source == "immobiliare":
            return ImmobiliareParser.extract_coordinates(listing_html)
        return None, None

    @staticmethod
    def geocode_address(address: str, city: str) -> Tuple[float, float]:
        """Геокодирование адреса через внешний API"""
        # Nominatim OpenStreetMap API (бесплатный)
        url = f"https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"{address}, {city}, Italy",
            "format": "json",
            "limit": 1
        }
        response = requests.get(url, params=params)
        data = response.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        return None, None

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Расчет расстояния между двумя точками в км"""
        from math import radians, sin, cos, sqrt, asin

        # Формула гаверсинуса
        R = 6371  # радиус Земли в км

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        return R * c
```

## ⚡ Система кеширования

### Двухуровневое кеширование

```python
# Гибридный кеш с автоматическим fallback
class HybridCacheService:
    def __init__(self):
        self.redis_cache = RedisCacheService() if redis_available else None
        self.memory_cache = MemoryCacheService()
        self.ttl_minutes = settings.CACHE_TTL_MINUTES

    async def get(self, key: str) -> Optional[dict]:
        # Попытка получить из Redis
        if self.redis_cache:
            result = await self.redis_cache.get(key)
            if result:
                return result

        # Fallback на memory кеш
        return self.memory_cache.get(key)

    async def set(self, key: str, value: dict, ttl_minutes: int = None):
        ttl = ttl_minutes or self.ttl_minutes

        # Сохранить в оба кеша
        if self.redis_cache:
            await self.redis_cache.set(key, value, ttl)

        self.memory_cache.set(key, value, ttl)

    def generate_cache_key(self, filters: dict, max_pages: int) -> str:
        # Нормализация фильтров для стабильного ключа
        normalized = {
            k: v for k, v in sorted(filters.items())
            if v is not None
        }
        normalized["max_pages"] = max_pages

        # MD5 хеш для компактности
        import hashlib
        import json
        key_string = json.dumps(normalized, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
```

### Стратегии кеширования

```python
# Кеширование на разных уровнях
class CacheStrategy:
    # Уровень 1: Результаты поиска (12 часов)
    SEARCH_RESULTS_TTL = 720  # минут

    # Уровень 2: Детали объявлений (6 часов)
    LISTING_DETAILS_TTL = 360

    # Уровень 3: Геоданные (24 часа)
    GEO_DATA_TTL = 1440

    # Уровень 4: Статистика (1 час)
    STATS_TTL = 60

    @classmethod
    def get_ttl_for_data_type(cls, data_type: str) -> int:
        return {
            "search_results": cls.SEARCH_RESULTS_TTL,
            "listing_details": cls.LISTING_DETAILS_TTL,
            "geo_data": cls.GEO_DATA_TTL,
            "stats": cls.STATS_TTL
        }.get(data_type, 60)  # по умолчанию 1 час
```

## 🔧 Парсинг и скрапинг

### Архитектура парсеров

```python
# Базовый класс парсера
class BaseParser:
    def __init__(self, scraperapi_key: str):
        self.scraperapi_key = scraperapi_key
        self.session = aiohttp.ClientSession()

    async def scrape_listings(self, filters: dict, max_pages: int) -> List[dict]:
        raise NotImplementedError

    def parse_listing_container(self, container) -> dict:
        raise NotImplementedError

    async def get_page_content(self, url: str) -> str:
        params = {
            'api_key': self.scraperapi_key,
            'url': url,
            'country_code': 'it',
            'device_type': 'desktop',
            'premium': 'true'
        }

        async with self.session.get(
            'https://api.scraperapi.com',
            params=params,
            timeout=aiohttp.ClientTimeout(total=90)
        ) as response:
            return await response.text()

# Конкретная реализация для Idealista
class IdealistaParser(BaseParser):
    BASE_URL = "https://www.idealista.it"

    def build_search_url(self, filters: dict, page: int = 1) -> str:
        params = {
            'operation': 'rent',
            'propertyType': 'homes',
            'locationId': self.get_location_id(filters.get('city')),
            'priceMin': filters.get('min_price'),
            'priceMax': filters.get('max_price'),
            'rooms': filters.get('min_rooms'),
            'sort': 'publicationDate',
            'page': page
        }
        # Фильтрация None значений и построение URL
        clean_params = {k: v for k, v in params.items() if v is not None}
        return f"{self.BASE_URL}/affitto-case?" + urlencode(clean_params)

    def parse_listing_container(self, container) -> dict:
        try:
            return {
                'external_id': self.extract_id(container),
                'title': container.select_one('a.item-link')?.get_text(strip=True),
                'price': self.extract_price(container),
                'rooms': self.extract_rooms(container),
                'area': self.extract_area(container),
                'address': self.extract_address(container),
                'images': self.extract_images(container),
                'url': self.extract_url(container),
                'source': 'idealista'
            }
        except Exception as e:
            logger.error(f"Error parsing Idealista listing: {e}")
            return None
```

### Координатор парсинга

```python
# Асинхронный координатор всех парсеров
class AsyncScrapingCoordinator:
    def __init__(self):
        self.parsers = {
            'idealista': IdealistaParser(settings.SCRAPERAPI_KEY),
            'immobiliare': ImmobiliareParser(settings.SCRAPERAPI_KEY),
            'subito': SubitoParser(settings.SCRAPERAPI_KEY)
        }
        self.cache = HybridCacheService()

    async def scrape_all_sources(self, filters: dict, max_pages: int = 5) -> List[dict]:
        # Проверка кеша
        cache_key = self.cache.generate_cache_key(filters, max_pages)
        cached_results = await self.cache.get(cache_key)

        if cached_results:
            logger.info(f"Returning cached results for key: {cache_key}")
            return cached_results['listings']

        # Параллельный запуск всех парсеров
        tasks = []
        for source, parser in self.parsers.items():
            if settings.SOURCES_ENABLED.get(source, True):
                task = self.scrape_single_source(parser, filters, max_pages)
                tasks.append(task)

        # Ожидание результатов
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Объединение результатов
        all_listings = []
        for result in results:
            if isinstance(result, list):
                all_listings.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Parser error: {result}")

        # Дедупликация по external_id + source
        unique_listings = self.deduplicate_listings(all_listings)

        # Сохранение в кеш
        cache_data = {
            'listings': unique_listings,
            'total_count': len(unique_listings),
            'scraped_at': datetime.utcnow().isoformat(),
            'sources': list(self.parsers.keys())
        }
        await self.cache.set(cache_key, cache_data)

        return unique_listings

    async def scrape_single_source(self, parser: BaseParser, filters: dict, max_pages: int) -> List[dict]:
        try:
            return await parser.scrape_listings(filters, max_pages)
        except Exception as e:
            logger.error(f"Error in {parser.__class__.__name__}: {e}")
            return []
```

## 🚀 Деплой и инфраструктура

### Docker конфигурация

```dockerfile
# Dockerfile для production
FROM python:3.11-slim

# Системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание пользователя
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Запуск
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### Docker Compose для разработки

```yaml
# docker-compose.yml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ita_rent_bot
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=development
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ita_rent_bot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev -- --host

volumes:
  postgres_data:
  redis_data:
```

### Конфигурация для продакшена

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      - redis
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    depends_on:
      - api

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru

  telegram-bot:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    command: python run_telegram_bot.py
    depends_on:
      - api

  notification-dispatcher:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    command: python -m src.services.notification_dispatcher
    depends_on:
      - api

volumes:
  redis_data:
```

### Деплой на облачные платформы

```yaml
# Vercel (Frontend)
# vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_API_URL": "@api_url"
  }
}

# Railway (Backend)
# railway.toml
[build]
builder = "dockerfile"

[deploy]
startCommand = "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300

[[services]]
name = "api"

[[services]]
name = "telegram-bot"
startCommand = "python run_telegram_bot.py"

[[services]]
name = "worker"
startCommand = "python -m src.services.notification_dispatcher"
```

## 📊 Мониторинг и метрики

### Основные метрики

```python
# Метрики для отслеживания
class MetricsCollector:
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.REDIS_URL)

    def track_api_request(self, endpoint: str, status_code: int, response_time: float):
        """Отслеживание API запросов"""
        key = f"metrics:api:{endpoint}:{status_code}"
        self.redis.incr(key)
        self.redis.expire(key, 86400)  # 24 часа

        # Время ответа
        time_key = f"metrics:response_time:{endpoint}"
        self.redis.lpush(time_key, response_time)
        self.redis.ltrim(time_key, 0, 999)  # последние 1000 запросов

    def track_scraping_result(self, source: str, success: bool, listings_count: int):
        """Отслеживание результатов парсинга"""
        status = "success" if success else "error"
        key = f"metrics:scraping:{source}:{status}"
        self.redis.incr(key)

        if success:
            count_key = f"metrics:scraping:{source}:listings_count"
            self.redis.lpush(count_key, listings_count)
            self.redis.ltrim(count_key, 0, 99)  # последние 100 запусков

    def track_notification_sent(self, user_id: int, filter_id: int, success: bool):
        """Отслеживание отправки уведомлений"""
        status = "sent" if success else "failed"
        key = f"metrics:notifications:{status}"
        self.redis.incr(key)

        # Уведомления по пользователям
        user_key = f"metrics:notifications:user:{user_id}"
        self.redis.incr(user_key)
        self.redis.expire(user_key, 86400)

    def get_system_metrics(self) -> dict:
        """Получение системных метрик"""
        import psutil

        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "active_connections": len(psutil.net_connections()),
            "uptime": time.time() - psutil.boot_time()
        }
```

### Health checks

```python
# Проверки здоровья системы
@app.get("/health")
async def health_check():
    checks = {
        "api": "healthy",
        "database": await check_database_health(),
        "redis": await check_redis_health(),
        "scraperapi": await check_scraperapi_health(),
        "telegram": await check_telegram_health()
    }

    overall_status = "healthy" if all(
        status == "healthy" for status in checks.values()
    ) else "unhealthy"

    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION
    }

async def check_database_health() -> str:
    try:
        async with database.get_session() as db:
            result = await db.execute("SELECT 1")
            return "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return "unhealthy"

async def check_redis_health() -> str:
    try:
        redis_client = redis.Redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        return "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return "unhealthy"
```

## 🔒 Безопасность

### Основные меры безопасности

```python
# Конфигурация безопасности
class SecuritySettings:
    # JWT
    SECRET_KEY: str = settings.SECRET_KEY
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 30

    # Пароли
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True

    # Rate limiting
    API_RATE_LIMIT = "100/minute"
    AUTH_RATE_LIMIT = "5/minute"
    SCRAPING_RATE_LIMIT = "10/hour"

    # CORS
    ALLOWED_ORIGINS = [
        "https://ita-rent-bot.vercel.app",
        "http://localhost:5173"
    ]

    # Headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }

# Middleware безопасности
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    response = await call_next(request)

    # Добавление security headers
    for header, value in SecuritySettings.SECURITY_HEADERS.items():
        response.headers[header] = value

    return response

# Валидация паролей
def validate_password(password: str) -> bool:
    if len(password) < SecuritySettings.PASSWORD_MIN_LENGTH:
        raise ValueError("Password too short")

    if SecuritySettings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain uppercase letter")

    if SecuritySettings.PASSWORD_REQUIRE_NUMBERS and not re.search(r'\d', password):
        raise ValueError("Password must contain number")

    if SecuritySettings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Password must contain special character")

    return True
```

### Rate limiting

```python
# Ограничение частоты запросов
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, user_credentials: UserLogin):
    # Логика авторизации
    pass

@app.get("/api/v1/listings")
@limiter.limit("100/minute")
async def search_listings(request: Request, filters: ListingSearch):
    # Логика поиска
    pass
```

## 📈 Планы масштабирования

### Этапы масштабирования

**Этап 1: Оптимизация текущей архитектуры**

- Кеширование на всех уровнях
- Оптимизация SQL запросов
- Connection pooling
- Асинхронные операции

**Этап 2: Горизонтальное масштабирование**

- Load balancer (Nginx)
- Несколько инстансов API
- Separate database и Redis кластер
- CDN для статических файлов

**Этап 3: Микросервисная архитектура**

- Разделение на отдельные сервисы
- Message Queue (RabbitMQ/Apache Kafka)
- API Gateway
- Service discovery

**Этап 4: Облачная инфраструктура**

- Kubernetes оркестрация
- Auto-scaling
- Managed databases
- Monitoring и alerting

### Целевые метрики производительности

```python
# Целевые показатели для production
class PerformanceTargets:
    # API Response времена
    API_RESPONSE_TIME_P95 = 1.0  # секунды
    API_RESPONSE_TIME_P99 = 2.0  # секунды

    # Throughput
    REQUESTS_PER_SECOND = 1000
    CONCURRENT_USERS = 10000

    # Availability
    UPTIME_TARGET = 99.9  # процентов

    # Database
    DB_QUERY_TIME_P95 = 0.1  # секунды
    DB_CONNECTION_POOL_SIZE = 20

    # Cache
    CACHE_HIT_RATE = 90  # процентов
    CACHE_RESPONSE_TIME = 0.01  # секунды

    # Scraping
    SCRAPING_SUCCESS_RATE = 95  # процентов
    SCRAPING_FREQUENCY = 3600  # секунды (1 час)

    # Notifications
    NOTIFICATION_DELIVERY_RATE = 98  # процентов
    NOTIFICATION_LATENCY = 30  # секунд
```

---

**Дата создания**: Январь 2025  
**Версия спецификации**: 1.0  
**Статус**: Готов к реализации

Эта спецификация покрывает все аспекты проекта от архитектуры до деплоя и может служить полным руководством для создания аналогичной системы.
