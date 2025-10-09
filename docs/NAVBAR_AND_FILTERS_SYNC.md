# Динамическая навигация и синхронизация фильтров

## Обзор изменений

Реализована динамическая смена кнопок в навигации в зависимости от статуса авторизации и синхронизация фильтров между страницей поиска и настройками.

## 1. Динамическая навигация

### NewNavbar

Обновлен компонент `NewNavbar` для отображения разных кнопок в зависимости от статуса авторизации:

**Для незалогиненных пользователей:**
- ✅ Кнопка "Log in" (ведет на `/auth/login`)
- ✅ Кнопка "Sign up" (ведет на `/auth/signup`)

**Для залогиненных пользователей:**
- ✅ Кнопка "Settings & Filters" (ведет на `/settings`)

### AuthHeader

Обновлен компонент `AuthHeader` аналогичным образом для использования на странице настроек.

### Где работает

- ✅ Главная страница (`NewHomePage`)
- ✅ Страница поиска (`NewSearchResultsPage`)
- ✅ Страница настроек (`SettingsPage`)

## 2. Синхронизация фильтров

### FilterStore

Создан новый store (`frontend/src/store/filterStore.ts`) для управления фильтрами:

```typescript
interface UserFilter {
  id: string;
  name: string;
  city: string;
  property_type: PropertyType[];  // 'apartment' | 'room' | 'house'
  rooms: RoomType[];              // 'studio' | '1' | '2' | '3' | '4' | '5+'
  price_min: string;
  price_max: string;
  min_area: string;
  max_area: string;
  no_commission: boolean;
  pets_allowed: boolean;
  children_allowed: boolean;
  createdAt: string;
}
```

### Возможности FilterStore

1. **Сохранение фильтров**
   - `saveFilter()` - сохраняет новый фильтр
   - Фильтры сохраняются в localStorage (persist)
   - Каждый фильтр получает уникальный ID

2. **Управление фильтрами**
   - `updateFilter()` - обновляет существующий фильтр
   - `deleteFilter()` - удаляет фильтр
   - `loadFilter()` - загружает фильтр в currentFilter
   - `clearCurrentFilter()` - очищает текущий фильтр

3. **Текущий фильтр**
   - `currentFilter` - фильтр который сейчас редактируется
   - `setCurrentFilter()` - обновляет currentFilter

## 3. Обновленная страница Settings

### Реальные фильтры

Страница `SettingsPage` теперь использует реальные фильтры из `filterStore`:

#### City (Город)
- Выпадающий список с городами:
  - Rome
  - Milan
  - Florence
  - Naples
  - Turin
  - Venice
  - Bologna

#### Property Type (Тип недвижимости)
- Кнопки-тоггл (можно выбрать несколько):
  - Apartment
  - Room
  - House

#### Rooms (Комнаты)
- Кнопки-тоггл (можно выбрать несколько):
  - Studio
  - 1, 2, 3, 4, 5+

#### Price (Цена)
- Диапазон: From - To
- Числовые поля в евро

#### Area (Площадь)
- Диапазон: From - To
- Числовые поля в м²

#### Additional Preferences (Дополнительные настройки)
- Чекбоксы:
  - No commission
  - Pets allowed
  - Children allowed

### Сохраненные фильтры

Добавлена секция "Saved filters" в начале раздела "My filters":

```typescript
// Отображение сохраненных фильтров
{savedFilters.map(filter => (
  <div>
    <h4>{filter.name}</h4>
    <p>{filter.city} • {property_type} • {rooms}</p>
    <button onClick={() => loadFilter(filter.id)}>Load</button>
    <button onClick={() => deleteFilter(filter.id)}>Delete</button>
  </div>
))}
```

### Функциональность

1. **Сохранение фильтра**
   - Пользователь настраивает фильтр
   - Вводит название фильтра
   - Нажимает "Save Filter"
   - Фильтр добавляется в список сохраненных

2. **Загрузка фильтра**
   - Пользователь видит список сохраненных фильтров
   - Нажимает "Load" на нужном фильтре
   - Все настройки фильтра применяются к форме

3. **Удаление фильтра**
   - Нажимает "Delete" на ненужном фильтре
   - Фильтр удаляется из списка

4. **Сброс фильтра**
   - Нажимает "Reset"
   - Все поля возвращаются к значениям по умолчанию

## 4. Убранные поля

Следующие поля были удалены как неактуальные:

- ❌ Neighborhood (Район)
- ❌ Metro (Метро)
- ❌ Furnishing (Меблировка)
- ❌ Rental period (Срок аренды)
- ❌ More (Дополнительно)

Эти поля были заменены на более релевантные чекбоксы в "Additional Preferences".

## 5. Использование

### Для пользователей

1. **Создание фильтра:**
   - Зайти на страницу Settings
   - Настроить нужные параметры
   - Ввести название фильтра
   - Нажать "Save Filter"

2. **Использование фильтра:**
   - Загрузить сохраненный фильтр на странице Settings
   - Перейти на страницу поиска
   - Фильтр автоматически применится (в будущем)

### Для разработчиков

```typescript
// Использование filterStore
import { useFilterStore } from '../store/filterStore';

const MyComponent = () => {
  const { 
    currentFilter, 
    setCurrentFilter, 
    saveFilter,
    savedFilters 
  } = useFilterStore();

  // Обновить текущий фильтр
  const updateCity = (city: string) => {
    setCurrentFilter({ ...currentFilter, city });
  };

  // Сохранить фильтр
  const handleSave = () => {
    saveFilter({
      name: 'My Filter',
      ...currentFilter,
    });
  };

  return (
    // JSX
  );
};
```

## 6. Структура файлов

```
frontend/src/
├── store/
│   └── filterStore.ts          # Новый store для фильтров
├── pages/
│   ├── SettingsPage.tsx        # Обновлена для работы с filterStore
│   ├── NewHomePage.tsx         # Обновлен футер
│   └── NewSearchResultsPage.tsx # Обновлен футер
└── components/
    ├── auth/
    │   └── AuthHeader.tsx      # Динамические кнопки навигации
    └── new-home/
        └── NewNavbar.tsx       # Динамические кнопки навигации
```

## 7. Следующие шаги

### Приоритет 1 (Критично)
- [ ] Интегрировать filterStore с NewFiltersSidebar на странице поиска
- [ ] Автоматически применять загруженный фильтр к результатам поиска

### Приоритет 2 (Важно)
- [ ] Добавить валидацию диапазонов (price_min < price_max)
- [ ] Добавить счетчик результатов для фильтра
- [ ] Добавить возможность редактирования сохраненного фильтра

### Приоритет 3 (Улучшения)
- [ ] Добавить возможность дублирования фильтра
- [ ] Добавить сортировку сохраненных фильтров (по дате, имени)
- [ ] Добавить поиск по сохраненным фильтрам

## 8. Технические детали

### Persist

FilterStore использует `persist` middleware из Zustand для сохранения в localStorage:

```typescript
persist(
  (set, get) => ({
    // store implementation
  }),
  {
    name: 'filter-storage',
  }
)
```

### TypeScript типы

```typescript
type PropertyType = 'apartment' | 'room' | 'house';
type RoomType = 'studio' | '1' | '2' | '3' | '4' | '5+';
```

### Состояние по умолчанию

```typescript
const defaultFilter = {
  city: 'Rome',
  property_type: [],
  rooms: [],
  price_min: '',
  price_max: '',
  min_area: '',
  max_area: '',
  no_commission: false,
  pets_allowed: false,
  children_allowed: false,
};
```

## 9. Примеры использования

### Загрузка фильтра

```typescript
const handleLoadFilter = (filterId: string) => {
  const { loadFilter } = useFilterStore.getState();
  loadFilter(filterId);
};
```

### Применение фильтра к поиску

```typescript
const handleApplyFilter = () => {
  const { currentFilter } = useFilterStore.getState();
  
  // Создать URL параметры из фильтра
  const params = new URLSearchParams();
  if (currentFilter.city) params.set('city', currentFilter.city.toLowerCase());
  currentFilter.property_type?.forEach(type => params.append('property_type', type));
  // ... другие параметры
  
  // Перейти на страницу поиска
  navigate(`/search?${params.toString()}`);
};
```

## Статус

✅ **Завершено**
- Динамическая навигация на всех страницах
- FilterStore с сохранением в localStorage
- Реальные фильтры на странице Settings
- Сохранение, загрузка и удаление фильтров

⏳ **В разработке**
- Интеграция с NewFiltersSidebar
- Автоматическое применение фильтров к поиску

---

**Дата:** 10 января 2025  
**Версия:** 1.0

