import axios from 'axios';

// Автоматическое определение базового URL API
const getApiBaseUrl = (): string => {
  // 1. Если есть переменная окружения - используем её
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // 2. Для локальной разработки
  if (import.meta.env.DEV || window.location.hostname === 'localhost') {
    return 'http://localhost:8000';
  }

  // 3. Для Railway - используем относительные пути (same origin)
  if (window.location.hostname.includes('railway.app')) {
    return ''; // Пустая строка = относительные пути к тому же домену
  }

  // 4. Fallback для других окружений
  return 'https://itarentbot-production.up.railway.app';
};

const API_BASE_URL = getApiBaseUrl();

console.log('🔗 API Base URL:', API_BASE_URL);
console.log('🌍 Current environment:', {
  isDev: import.meta.env.DEV,
  hostname: window.location.hostname,
  viteApiUrl: import.meta.env.VITE_API_URL,
  isRailway: window.location.hostname.includes('railway.app'),
});

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`, // Добавляем префикс API
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // Увеличиваем таймаут до 15 секунд
});

// Перехватчик для добавления токена авторизации
apiClient.interceptors.request.use(
  (config) => {
    // Предполагается, что токен хранится в localStorage
    // В реальном приложении используйте более безопасное хранилище или Zustand/Context для токена
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Перехватчик для обработки ответов и ошибок
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);

    // Если API недоступен, показываем предупреждение но не ломаем приложение
    if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
      console.warn('API недоступен, используем моковые данные');
    }

    return Promise.reject(error);
  }
);

export default apiClient;

// --- Моковые функции для разработки UI пока нет бэкенда для них ---
import { City, FilterState, Listing, ApiResponse } from '../types'; // Убедитесь, что путь правильный

const mockCitiesData: City[] = [
  { id: 'rome', name: 'Рим' },
  { id: 'milan', name: 'Милан' },
  // ... другие города Италии
];

export const fetchCities = async (): Promise<City[]> => {
  console.log('apiClient: fetchCities (mocked)');
  return new Promise((resolve) =>
    setTimeout(() => resolve(mockCitiesData), 300)
  );
};

export const fetchLocationSuggestions = async (
  query: string
): Promise<string[]> => {
  console.log(
    `apiClient: fetchLocationSuggestions (mocked) for query: ${query}`
  );
  const mockLocations = [
    'Trastevere',
    'Monti',
    'Prati',
    'Testaccio',
    'Termini',
    'Vaticano',
    'Fontana di Trevi',
    'Colosseo',
    'San Giovanni',
    'EUR',
  ];
  return new Promise((resolve) => {
    setTimeout(() => {
      if (!query) {
        resolve([]);
        return;
      }
      const results = mockLocations.filter((loc) =>
        loc.toLowerCase().includes(query.toLowerCase())
      );
      resolve(results.slice(0, 5)); // Limit suggestions
    }, 200);
  });
};

// Моковая функция fetchListingsFromApi из плана, но она не будет использоваться напрямую,
// так как логика фетчинга перенесена в listingStore. Оставлена для справки или если понадобится позже.
/*
const mockListings: Listing[] = [
  {
    id: '1',
    title: '2-комн. кв., 75 м², Центр',
    price: 1500,
    currency: '€',
    address: 'Рим, ул. Корсо, 10',
    metroStations: [{ name: 'Spagna', distance: '5 мин' }],
    imageUrls: ['https://via.placeholder.com/300x200/AABBCC/FFFFFF?Text=App1+View1', 'https://via.placeholder.com/300x200/CCDDEE/FFFFFF?Text=App1+View2'],
    source: 'Immobiliare.it',
    originalUrl: '#',
    type: '2-комн. кв.',
    area: 75,
    floor: '3/5 этаж',
    renovationType: 'Евроремонт',
  },
  {
    id: '2',
    title: 'Студия, 40 м², Трастевере',
    price: 900,
    currency: '€',
    address: 'Рим, пл. Санта-Мария-ин-Трастевере, 5',
    imageUrls: ['https://via.placeholder.com/300x200/112233/FFFFFF?Text=Studio1'],
    source: 'Idealista',
    originalUrl: '#',
    type: 'Студия',
    area: 40,
    floor: '1/3 этаж',
    commission: 'Без комиссии'
  },
];

export const fetchListingsFromApi_Mock = async (
  filters: FilterState,
  page: number,
  limit: number
): Promise<ApiResponse<Listing>> => {
  console.log('(Mock) Fetching with filters:', filters, 'Page:', page, 'Limit:', limit);
  return new Promise((resolve) => {
    setTimeout(() => {
      let filtered = [...mockListings];
      // TODO: Применить логику фильтрации из плана, если нужно будет тестировать моки
      const total = filtered.length;
      const paginatedData = filtered.slice((page - 1) * limit, page * limit);
      resolve({ data: paginatedData, total });
    }, 500);
  });
};
*/
