import apiClient from "./apiClient";
import { Filter } from "../types";

interface FilterUpdateData {
  name?: string;
  is_active?: boolean;
  city?: string | null;
  min_price?: number | null;
  max_price?: number | null;
  min_rooms?: number | null;
  max_rooms?: number | null;
  property_type?: string | null;
  min_area?: number | null;
  max_area?: number | null;
  furnished?: boolean | null;
  pets_allowed?: boolean | null;
  notification_enabled?: boolean;
  notification_frequency_hours?: number;
}

interface FilterCreateData {
  name: string;
  city?: string | null;
  min_price?: number | null;
  max_price?: number | null;
  min_rooms?: number | null;
  max_rooms?: number | null;
  property_type?: string | null;
  min_area?: number | null;
  max_area?: number | null;
  furnished?: boolean | null;
  pets_allowed?: boolean | null;
  notification_enabled?: boolean;
  notification_frequency_hours?: number;
}

class FiltersService {
  async getUserFilters(): Promise<Filter[]> {
    const response = await apiClient.get<Filter[]>("/filters/");
    return response.data;
  }

  async getUserFilter(): Promise<Filter | null> {
    // Для обратной совместимости - получаем первый фильтр
    const filters = await this.getUserFilters();
    return filters.length > 0 ? filters[0] : null;
  }

  async createFilter(data: FilterCreateData): Promise<Filter> {
    const response = await apiClient.post<Filter>("/filters/", data);
    return response.data;
  }

  async createOrUpdateUserFilter(data: FilterUpdateData): Promise<Filter> {
    // Пытаемся создать новый фильтр
    const createData: FilterCreateData = {
      name: data.name || "Новый фильтр",
      city: data.city,
      min_price: data.min_price,
      max_price: data.max_price,
      min_rooms: data.min_rooms,
      max_rooms: data.max_rooms,
      property_type: data.property_type,
      min_area: data.min_area,
      max_area: data.max_area,
      furnished: data.furnished,
      pets_allowed: data.pets_allowed,
      notification_enabled: data.notification_enabled ?? true,
      notification_frequency_hours: data.notification_frequency_hours ?? 24,
    };

    return await this.createFilter(createData);
  }

  async updateFilter(
    filterId: number,
    data: FilterUpdateData
  ): Promise<Filter> {
    const response = await apiClient.put<Filter>(`/filters/${filterId}`, data);
    return response.data;
  }

  async deleteFilter(filterId: number): Promise<{ message: string }> {
    const response = await apiClient.delete(`/filters/${filterId}`);
    return response.data;
  }

  async testFilter(filterId: number): Promise<{
    success: boolean;
    filter_name: string;
    total_matches: number;
    sample_listings: any[];
    message: string;
  }> {
    const response = await apiClient.post(`/filters/${filterId}/test`);
    return response.data;
  }

  async resetNotifications(): Promise<{ message: string }> {
    const response = await apiClient.post("/filters/reset-notifications");
    return response.data;
  }
}

export const filtersService = new FiltersService();
