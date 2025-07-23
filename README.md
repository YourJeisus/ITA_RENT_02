# 🏠 ITA_RENT_BOT

Telegram бот для поиска недвижимости в Италии с системой уведомлений и подписок.

## 📋 Статус MVP - Этап 1.1 ✅

**Выполнено**: Минимальная настройка проекта (1-2 дня)

### ✅ Базовая структура проекта

- ✅ Создана структура папок:

  - `src/` - Backend код (FastAPI)
  - `frontend/` - Frontend код (React + Vite)
  - `docs/` - Документация
  - `tests/` - Тесты

- ✅ Настроен `requirements.txt` с минимальными зависимостями
- ✅ Создан `env.example` с примерами переменных окружения
- ✅ Настроен `.gitignore`

### ✅ FastAPI минимум

- ✅ Создан `src/main.py` с базовой конфигурацией
- ✅ Реализован тестовый endpoint `GET /health`
- ✅ Настроена базовая CORS конфигурация
- ✅ Добавлено простое логирование в консоль
- ✅ Настроена обработка ошибок

### ✅ React минимум

- ✅ Создано базовое Vite + React приложение
- ✅ Реализована главная страница с "Coming Soon"
- ✅ Добавлены базовые стили
- ✅ Настроен proxy для API запросов
- ✅ Добавлена проверка статуса backend

## 🚀 Быстрый запуск

### Backend (FastAPI)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
cd src
python main.py
```

Backend будет доступен на: http://localhost:8000

- API документация: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Frontend (React)

```bash
# Установка зависимостей
cd frontend
npm install

# Запуск в режиме разработки
npm run dev
```

Frontend будет доступен на: http://localhost:3000

## 🔧 Структура проекта

```
ITA_RENT_02/
├── src/                    # Backend (FastAPI)
│   ├── api/               # API endpoints
│   ├── core/              # Конфигурация
│   ├── db/                # База данных
│   ├── models/            # SQLAlchemy модели
│   ├── schemas/           # Pydantic схемы
│   ├── crud/              # CRUD операции
│   ├── services/          # Бизнес логика
│   ├── parsers/           # Парсеры сайтов
│   └── main.py            # Точка входа
├── frontend/              # Frontend (React)
│   ├── src/
│   │   ├── components/    # React компоненты
│   │   ├── pages/         # Страницы
│   │   ├── services/      # API сервисы
│   │   └── utils/         # Утилиты
│   ├── public/            # Статические файлы
│   └── package.json
├── docs/                  # Документация
├── tests/                 # Тесты
├── requirements.txt       # Python зависимости
├── env.example           # Пример переменных окружения
└── README.md             # Этот файл
```

## 📊 Критерии готовности этапа 1.1

- ✅ Backend запускается на localhost:8000
- ✅ Frontend запускается на localhost:3000
- ✅ `/health` endpoint возвращает `{"status": "ok"}`
- ✅ Frontend успешно подключается к backend API
- ✅ Базовая структура проекта создана

## 🐳 Docker запуск

### Локальная разработка с Docker

```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

После запуска:

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Production сборка

```bash
# Backend
docker build -f Dockerfile.prod -t ita-rent-backend .

# Frontend
cd frontend
docker build -f Dockerfile.prod -t ita-rent-frontend .
```

## 🚀 Деплой на Railway

### Быстрый деплой (5 минут)

1. **Создайте GitHub репозиторий и загрузите код:**

```bash
git push -u origin main
```

2. **Зайдите на [railway.app](https://railway.app) и создайте проект из GitHub репозитория**

3. **Railway автоматически создаст 2 сервиса:**

   - `backend` (FastAPI + PostgreSQL)
   - `frontend` (React)

4. **Настройте переменные окружения:**
   - Backend: `ENVIRONMENT=production`, `SECRET_KEY=your-key`
   - Frontend: `VITE_API_URL=https://your-backend.railway.app`

**📖 Подробные инструкции:** `DEPLOY_NOW.md` и `RAILWAY_DEPLOYMENT.md`

## 🔄 Следующие этапы

1. **Этап 1.2 ✅**: Контейнеризация и первый деплой
2. **Этап 2**: База данных и базовые модели
3. **Этап 3**: Простая авторизация
4. **Этап 4**: Базовый парсинг

---

**Статус**: ✅ Этап 1.2 полностью выполнен  
**Время выполнения**: ~3 часа  
**Следующий этап**: 2.1 - Настройка базы данных
