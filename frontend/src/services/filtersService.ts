import apiClient from "./apiClient";
import { Filter } from "@/types";

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
  notification_enabled?: boolean;
  notification_frequency_hours?: number;
}

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
  notification_enabled?: boolean;
  notification_frequency_hours?: number;
}

interface FilterTestResult {
  success: boolean;
  filter_name: string;
  total_matches: number;
  sample_listings: Array<{
    title: string;
    price: number;
    city: string;
    address: string;
    source: string;
  }>;
  message: string;
}

class FiltersService {
  async getUserFilters(): Promise<Filter[]> {
    try {
      const response = await apiClient.get("/filters/");
      return response.data;
    } catch (error) {
      console.error("Error getting user filters:", error);
      throw error;
    }
  }

  async createFilter(data: FilterCreateData): Promise<Filter> {
    try {
      const response = await apiClient.post("/filters/", data);
      return response.data;
    } catch (error) {
      console.error("Error creating filter:", error);
      throw error;
    }
  }

  async getFilter(filterId: number): Promise<Filter> {
    try {
      const response = await apiClient.get(`/filters/${filterId}`);
      return response.data;
    } catch (error) {
      console.error("Error getting filter:", error);
      throw error;
    }
  }

  async updateFilter(
    filterId: number,
    data: FilterUpdateData
  ): Promise<Filter> {
    try {
      const response = await apiClient.put(`/filters/${filterId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating filter:", error);
      throw error;
    }
  }

  async deleteFilter(filterId: number): Promise<{ message: string }> {
    try {
      const response = await apiClient.delete(`/filters/${filterId}`);
      return response.data;
    } catch (error) {
      console.error("Error deleting filter:", error);
      throw error;
    }
  }

  async testFilter(filterId: number): Promise<FilterTestResult> {
    try {
      const response = await apiClient.post(`/filters/${filterId}/test`);
      return response.data;
    } catch (error) {
      console.error("Error testing filter:", error);
      throw error;
    }
  }

  // Конвертируем FilterState в FilterCreateData
  convertFilterStateToCreateData(
    name: string,
    filters: any,
    notificationEnabled: boolean = true
  ): FilterCreateData {
    return {
      name,
      city: filters.city?.name || null,
      min_price: filters.priceMin || null,
      max_price: filters.priceMax || null,
      min_rooms:
        filters.rooms && filters.rooms.length > 0
          ? Math.min(...filters.rooms)
          : null,
      max_rooms:
        filters.rooms && filters.rooms.length > 0
          ? Math.max(...filters.rooms)
          : null,
      property_type:
        filters.propertyType === "all" ? null : filters.propertyType,
      min_area: filters.areaMin || null,
      max_area: filters.areaMax || null,
      notification_enabled: notificationEnabled,
      notification_frequency_hours: 24, // По умолчанию раз в день
    };
  }

  // Создать фильтр из состояния поиска
  async createFilterFromState(
    name: string,
    filters: any,
    notificationEnabled: boolean = true
  ): Promise<Filter> {
    const createData = this.convertFilterStateToCreateData(
      name,
      filters,
      notificationEnabled
    );
    return this.createFilter(createData);
  }

  // Получить первый фильтр пользователя (для простоты)
  async getUserFilter(): Promise<Filter | null> {
    try {
      const filters = await this.getUserFilters();
      return filters.length > 0 ? filters[0] : null;
    } catch (error) {
      console.error("Error getting user filter:", error);
      return null;
    }
  }

  // Создать или обновить фильтр пользователя
  async createOrUpdateUserFilter(data: FilterUpdateData): Promise<Filter> {
    try {
      const existingFilter = await this.getUserFilter();

      if (existingFilter) {
        return this.updateFilter(existingFilter.id, data);
      } else {
        // Создаем новый фильтр
        const createData: FilterCreateData = {
          name: data.name || "Мой фильтр",
          ...data,
        };
        return this.createFilter(createData);
      }
    } catch (error) {
      console.error("Error creating or updating filter:", error);
      throw error;
    }
  }

  // Сброс уведомлений (пока просто обновляем фильтр)
  async resetNotifications(): Promise<{ message: string }> {
    try {
      const filter = await this.getUserFilter();
      if (filter) {
        await this.updateFilter(filter.id, {
          notification_enabled: false,
        });
        return { message: "Уведомления отключены" };
      }
      return { message: "Фильтр не найден" };
    } catch (error) {
      console.error("Error resetting notifications:", error);
      throw error;
    }
  }
}

export const filtersService = new FiltersService();
export default filtersService;
