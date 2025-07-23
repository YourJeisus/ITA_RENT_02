import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { Listing, FilterState, ApiResponse } from '@/types';
import { listingsService } from '@/services/listingsService';

interface ListingState {
  listings: Listing[];
  totalListings: number;
  currentPage: number;
  listingsPerPage: number;
  isLoading: boolean;
  error: string | null;
  searchType: 'database' | 'scraping' | null;
  searchMessage: string | null;
  databaseHealth: any | null;
  searchSuggestions: any | null;

  // Основные методы
  fetchListings: (filters: FilterState, page?: number) => Promise<void>;

  // Новые оптимизированные методы
  fastSearch: (filters: FilterState, page?: number) => Promise<void>;
  smartSearch: (filters: FilterState, page?: number) => Promise<void>;

  // Утилиты
  checkDatabaseHealth: () => Promise<void>;
  loadSearchSuggestions: (city?: string) => Promise<void>;
  startPreload: (city?: string) => Promise<void>;

  // Сброс состояния
  clearResults: () => void;
}

// Функция для преобразования фильтров фронтенда в параметры нового API
const mapFiltersToFastSearchParams = (filters: FilterState) => {
  const params: any = {};

  // Город
  if (filters.city?.id) {
    params.city = filters.city.id;
  } else {
    params.city = 'roma'; // По умолчанию
  }

  // Тип недвижимости
  if (filters.propertyType && filters.propertyType !== 'all') {
    params.property_type = filters.propertyType;
  }
  // Если 'all' или не указан, не передаем property_type вообще

  // Язык
  params.language = 'it';

  // Комнаты
  if (filters.rooms && filters.rooms.length > 0) {
    const numericRooms = filters.rooms.map(Number);
    params.min_rooms = Math.min(...numericRooms);

    if (!numericRooms.includes(4)) {
      // 4 - это "4+"
      params.max_rooms = Math.max(...numericRooms);
    }
  }

  // Цена
  if (filters.priceMin !== null && filters.priceMin !== undefined) {
    params.min_price = filters.priceMin;
  }
  if (filters.priceMax !== null && filters.priceMax !== undefined) {
    params.max_price = filters.priceMax;
  }

  // Площадь
  if (filters.areaMin !== null && filters.areaMin !== undefined) {
    params.min_area = filters.areaMin;
  }
  if (filters.areaMax !== null && filters.areaMax !== undefined) {
    params.max_area = filters.areaMax;
  }

  return params;
};

// Функция для преобразования ответа API в формат Listing
const mapApiResponseToListings = (apiListings: any[]): Listing[] => {
  return apiListings.map((item: any) => ({
    // Основные поля из API
    id: item.listing_id || item.id,
    source_site: item.source_site || '',
    original_id: item.listing_id || item.id,
    url: item.url_details || '',
    title: item.title || '',
    description: item.description_short || '',
    price: item.price || 0,
    currency: item.price_currency || '€',
    address_text: item.location_address || '',
    city: 'Roma', // Пока захардкодим
    area_sqm: item.area_sqm || 0,
    num_rooms: item.rooms_count || 0,
    num_bathrooms: item.bathrooms_count || 0,
    property_type: item.property_type || '',
    features: item.raw_features || [],
    photos_urls: item.image_urls || [],
    created_at: item.created_at || new Date().toISOString(),
    last_seen_at: item.last_seen_at || new Date().toISOString(),
    is_available: true,

    // Поля для обратной совместимости
    address: item.location_address || '',
    imageUrls: item.image_urls || [],
    source: item.source_site || '',
    originalUrl: item.url_details || '',
    type: item.property_type || '',
    area: item.area_sqm || 0,
  }));
};

export const useListingStore = create<ListingState>()(
  devtools(
    (set, get) => ({
      listings: [],
      totalListings: 0,
      currentPage: 1,
      listingsPerPage: 50, // Увеличиваем для лучшего UX
      isLoading: false,
      error: null,
      searchType: null,
      searchMessage: null,
      databaseHealth: null,
      searchSuggestions: null,

      // Основной метод поиска (теперь использует smartSearch)
      fetchListings: async (filters, page = 1) => {
        await get().smartSearch(filters, page);
      },

      // Быстрый поиск только в базе данных
      fastSearch: async (filters, page = 1) => {
        set({ isLoading: true, error: null, currentPage: page });

        try {
          const params = mapFiltersToFastSearchParams(filters);
          const skip = (page - 1) * get().listingsPerPage;
          const limit = get().listingsPerPage;

          const response = await listingsService.fastSearch(
            params,
            skip,
            limit
          );

          if (response.success) {
            const mappedListings = mapApiResponseToListings(response.listings);

            set({
              listings: mappedListings,
              totalListings: response.total_count,
              isLoading: false,
              searchType: 'database',
              searchMessage: response.message,
              error: null,
            });
          } else {
            throw new Error(response.error || 'Ошибка быстрого поиска');
          }
        } catch (err: any) {
          const errorMessage =
            err.response?.data?.detail ||
            err.message ||
            'Ошибка быстрого поиска';
          set({
            error: errorMessage,
            isLoading: false,
            listings: [],
            totalListings: 0,
            searchType: null,
            searchMessage: null,
          });
          console.error('Fast search error:', err);
        }
      },

      // Умный поиск с fallback
      smartSearch: async (filters, page = 1) => {
        set({ isLoading: true, error: null, currentPage: page });

        try {
          const params = mapFiltersToFastSearchParams(filters);
          const skip = (page - 1) * get().listingsPerPage;
          const limit = get().listingsPerPage;

          const response = await listingsService.smartSearch(
            params,
            skip,
            limit
          );

          if (response.success) {
            const mappedListings = mapApiResponseToListings(response.listings);

            set({
              listings: mappedListings,
              totalListings: response.total_count,
              isLoading: false,
              searchType: response.search_type as 'database' | 'scraping',
              searchMessage: response.message,
              error: null,
            });
          } else {
            throw new Error(response.error || 'Ошибка поиска');
          }
        } catch (err: any) {
          const errorMessage =
            err.response?.data?.detail || err.message || 'Ошибка поиска';
          set({
            error: errorMessage,
            isLoading: false,
            listings: [],
            totalListings: 0,
            searchType: null,
            searchMessage: null,
          });
          console.error('Smart search error:', err);
        }
      },

      // Проверка состояния базы данных
      checkDatabaseHealth: async () => {
        try {
          const health = await listingsService.getDatabaseHealth();
          set({ databaseHealth: health });
        } catch (err: any) {
          console.error('Database health check error:', err);
          set({ databaseHealth: null });
        }
      },

      // Загрузка предложений для поиска
      loadSearchSuggestions: async (city = 'roma') => {
        try {
          const suggestions = await listingsService.getSearchSuggestions(city);
          set({ searchSuggestions: suggestions });
        } catch (err: any) {
          console.error('Search suggestions error:', err);
          set({ searchSuggestions: null });
        }
      },

      // Запуск предзагрузки
      startPreload: async (city = 'roma') => {
        try {
          const result = await listingsService.startPreload(city);
          console.log('Preload started:', result.message);
          return result;
        } catch (err: any) {
          console.error('Preload start error:', err);
          throw err;
        }
      },

      // Очистка результатов
      clearResults: () => {
        set({
          listings: [],
          totalListings: 0,
          currentPage: 1,
          error: null,
          searchType: null,
          searchMessage: null,
        });
      },
    }),
    { name: 'ListingStore' }
  )
);
