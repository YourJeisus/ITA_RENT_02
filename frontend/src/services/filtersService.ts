import apiClient from './apiClient';
import { Filter } from '@/types';

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
}

class FiltersService {
  async getUserFilter(): Promise<Filter | null> {
    const response = await apiClient.get<Filter | null>('/filters/');
    return response.data;
  }

  async createOrUpdateUserFilter(data: FilterUpdateData): Promise<Filter> {
    const response = await apiClient.post<Filter>('/filters/', data);
    return response.data;
  }

  async resetNotifications(): Promise<{ message: string }> {
    const response = await apiClient.post('/filters/reset-notifications');
    return response.data;
  }
}

export const filtersService = new FiltersService();
