import apiClient from "./apiClient";
import { Listing, ApiResponse, FilterState } from "../types";

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

interface SearchResponse {
  success: boolean;
  listings: any[];
  total_count: number;
  returned_count: number;
  filters_used: SearchParams;
  search_type: string;
  message: string;
  error?: string;
}

interface DatabaseStats {
  success: boolean;
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
    recent_listings_24h: number;
    data_freshness: {
      total_active: number;
      recent_24h: number;
      freshness_ratio: number;
    };
  };
}

class ListingsService {
  async searchListings(params: SearchParams): Promise<SearchResponse> {
    try {
      const response = await apiClient.get("/listings/", { params });
      return response.data;
    } catch (error) {
      console.error("Error searching listings:", error);
      throw error;
    }
  }

  async getListing(id: string): Promise<Listing> {
    try {
      const response = await apiClient.get(`/listings/${id}`);
      return response.data;
    } catch (error) {
      console.error("Error getting listing:", error);
      throw error;
    }
  }

  async getCities(): Promise<string[]> {
    try {
      const response = await apiClient.get("/listings/suggestions/cities");
      return response.data;
    } catch (error) {
      console.error("Error getting cities:", error);
      // Возвращаем моковые данные в случае ошибки
      return ["Roma", "Milano", "Napoli", "Torino", "Firenze", "Bologna"];
    }
  }

  async getDatabaseStats(): Promise<DatabaseStats> {
    try {
      const response = await apiClient.get("/listings/stats/database");
      return response.data;
    } catch (error) {
      console.error("Error getting database stats:", error);
      throw error;
    }
  }

  // Конвертируем FilterState в параметры поиска
  convertFiltersToSearchParams(filters: FilterState): SearchParams {
    let minRooms: number | undefined = undefined;
    let maxRooms: number | undefined = undefined;

    if (filters.rooms && filters.rooms.length > 0) {
      const validRooms = filters.rooms.filter((r) => !isNaN(r) && isFinite(r));
      if (validRooms.length > 0) {
        minRooms = Math.min(...validRooms);
        maxRooms = Math.max(...validRooms);
      }
    }

    return {
      city: filters.city?.id || undefined,
      min_price: filters.priceMin || undefined,
      max_price: filters.priceMax || undefined,
      property_type:
        filters.propertyType === "all" ? undefined : filters.propertyType,
      min_rooms: minRooms,
      max_rooms: maxRooms,
      min_area: filters.areaMin || undefined,
      max_area: filters.areaMax || undefined,
    };
  }

  // Конвертируем ответ API в формат Listing
  convertApiListingToListing(apiListing: any): Listing {
    // Отладочная информация
    console.log("Converting listing:", {
      id: apiListing.id,
      images: apiListing.images?.length || 0,
      photos_urls: apiListing.photos_urls?.length || 0,
    });

    return {
      id: apiListing.id,
      source_site: apiListing.source_site,
      original_id: apiListing.original_id,
      url: apiListing.url,
      title: apiListing.title,
      description: apiListing.description,
      price: apiListing.price,
      currency: apiListing.currency || "EUR",
      address_text: apiListing.address_text,
      city: apiListing.city,
      postal_code: apiListing.postal_code,
      district: apiListing.district,
      latitude: apiListing.latitude,
      longitude: apiListing.longitude,
      area_sqm: apiListing.area_sqm,
      num_rooms: apiListing.num_rooms,
      num_bedrooms: apiListing.num_bedrooms,
      num_bathrooms: apiListing.num_bathrooms,
      floor: apiListing.floor,
      property_type: apiListing.property_type,
      listing_type: apiListing.listing_type,
      features: apiListing.features || [],
      photos_urls: apiListing.images || apiListing.photos_urls || [],
      published_at: apiListing.published_at,
      created_at: apiListing.created_at,
      last_seen_at: apiListing.last_seen_at,
      is_available: apiListing.is_available,

      // Для обратной совместимости с существующими компонентами
      address: apiListing.address_text,
      imageUrls: apiListing.images || apiListing.photos_urls || [],
      source: apiListing.source_site,
      originalUrl: apiListing.url,
      type: apiListing.property_type,
      area: apiListing.area_sqm,
    };
  }

  // Основной метод поиска с конвертацией
  async search(
    filters: FilterState,
    page: number = 1,
    limit: number = 50
  ): Promise<{
    listings: Listing[];
    total: number;
    searchType: string;
    searchMessage: string;
  }> {
    try {
      const searchParams = this.convertFiltersToSearchParams(filters);
      searchParams.skip = (page - 1) * limit;
      searchParams.limit = limit;

      const response = await this.searchListings(searchParams);

      const listings = response.listings.map((listing) =>
        this.convertApiListingToListing(listing)
      );

      return {
        listings,
        total: response.total_count,
        searchType: response.search_type,
        searchMessage: response.message,
      };
    } catch (error) {
      console.error("Search error:", error);
      throw error;
    }
  }

  // Запуск парсинга через существующий API
  async runScraping(params: any): Promise<any> {
    try {
      const response = await apiClient.post("/scraping/run", params);
      return response.data;
    } catch (error) {
      console.error("Error running scraping:", error);
      throw error;
    }
  }

  // Получение статуса парсинга
  async getScrapingStatus(): Promise<any> {
    try {
      const response = await apiClient.get("/scraping/status");
      return response.data;
    } catch (error) {
      console.error("Error getting scraping status:", error);
      throw error;
    }
  }
}

export const listingsService = new ListingsService();
export default listingsService;
