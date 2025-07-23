import apiClient from './apiClient';
import { Listing, ApiResponse } from '@/types';

interface SearchParams {
  skip?: number;
  limit?: number;
  city?: string;
  min_price?: number;
  max_price?: number;
  property_type?: string;
  min_rooms?: number;
  max_rooms?: number;
  min_area?: number;
  max_area?: number;
  source_site?: string;
  sort_by?: string;
  is_available?: boolean;
}

interface FastSearchParams {
  city?: string;
  min_price?: number;
  max_price?: number;
  min_rooms?: number;
  max_rooms?: number;
  min_area?: number;
  max_area?: number;
  property_type?: string;
  language?: string;
  ordering?: string;
}

interface FastSearchResponse {
  success: boolean;
  listings: any[];
  total_count: number;
  returned_count: number;
  filters_used: FastSearchParams;
  sites_scraped: string[];
  search_type: string;
  message: string;
  error?: string;
}

interface DatabaseHealth {
  success: boolean;
  health_status: string;
  stats: {
    total_listings: number;
    active_listings: number;
    inactive_listings: number;
    sites: Record<string, number>;
    top_cities: Record<string, number>;
    average_price: number;
    date_range: {
      oldest: string;
      newest: string;
    };
  };
  recent_listings_24h: number;
  data_freshness: {
    total_active: number;
    recent_24h: number;
    freshness_ratio: number;
  };
  recommendations: string[];
}

interface SearchSuggestions {
  success: boolean;
  city: string;
  price_range: {
    min: number;
    max: number;
    average: number;
  };
  popular_rooms: Array<{
    rooms: number;
    count: number;
  }>;
  popular_districts: Array<{
    district: string;
    count: number;
  }>;
}

class ListingsService {
  async searchListings(params: SearchParams): Promise<ApiResponse<Listing>> {
    const response = await apiClient.get('/listings', { params });
    return response.data;
  }

  async getListing(id: string): Promise<Listing> {
    const response = await apiClient.get(`/listings/${id}`);
    return response.data;
  }

  async getListingsByFilter(
    filterParams: Record<string, any>
  ): Promise<ApiResponse<Listing>> {
    const response = await apiClient.post('/listings/search', {
      filter_params: filterParams,
      site_to_monitor: 'all',
      name: 'Search',
    });
    return response.data;
  }

  async fastSearch(
    params: FastSearchParams,
    skip: number = 0,
    limit: number = 100
  ): Promise<FastSearchResponse> {
    try {
      const response = await apiClient.post('/scraping/search/fast', params, {
        params: { skip, limit },
      });
      return response.data;
    } catch (error) {
      console.error('Fast search error:', error);
      throw error;
    }
  }

  async smartSearch(
    params: FastSearchParams,
    skip: number = 0,
    limit: number = 100
  ): Promise<FastSearchResponse> {
    try {
      const fastResult = await this.fastSearch(params, skip, limit);

      return {
        ...fastResult,
        message: fastResult.success
          ? `Найдено ${fastResult.total_count} объявлений в базе данных`
          : 'Ошибка при поиске в базе данных',
      };
    } catch (error) {
      console.error('Smart search error:', error);
      throw error;
    }
  }

  async scrapeSites(
    params: FastSearchParams,
    maxPages: number = 1
  ): Promise<FastSearchResponse> {
    try {
      const response = await apiClient.post(
        '/scraping/scrape/all-async',
        params,
        {
          params: { max_pages: maxPages },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Scraping error:', error);
      throw error;
    }
  }

  async getDatabaseHealth(): Promise<DatabaseHealth> {
    try {
      const response = await apiClient.get('/scraping/database/health');
      return response.data;
    } catch (error) {
      console.error('Database health check error:', error);
      throw error;
    }
  }

  async getSearchSuggestions(
    city: string = 'roma'
  ): Promise<SearchSuggestions> {
    try {
      const response = await apiClient.get('/scraping/search/suggestions', {
        params: { city },
      });
      return response.data;
    } catch (error) {
      console.error('Search suggestions error:', error);
      throw error;
    }
  }

  async startPreload(
    city: string = 'roma'
  ): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiClient.post('/scraping/preload/start', null, {
        params: { city },
      });
      return response.data;
    } catch (error) {
      console.error('Preload start error:', error);
      throw error;
    }
  }

  async getDatabaseStats(): Promise<any> {
    try {
      const response = await apiClient.get('/scraping/database/stats');
      return response.data;
    } catch (error) {
      console.error('Database stats error:', error);
      throw error;
    }
  }
}

export const listingsService = new ListingsService();
