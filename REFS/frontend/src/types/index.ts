export interface City {
  id: string;
  name: string;
}

export type TransactionType = 'buy' | 'rent';
export type PropertyType =
  | 'apartment'
  | 'room'
  | 'house'
  | 'studio'
  | 'villa'
  | 'penthouse'
  | 'loft'
  | 'all';
export type RoomOption = 'studio' | '1' | '2' | '3' | '4' | '5+';

export interface FilterState {
  city: City | null;
  transactionType: TransactionType;
  propertyType: PropertyType;
  rooms: number[] | null;
  priceMin: number | null;
  priceMax: number | null;
  locationQuery: string;
  areaMin?: number | null;
  areaMax?: number | null;
  floorType?: string[] | null;
  selectedFeatures?: string[] | null;
  selectedLocations?: string[] | null;
}

export interface Listing {
  id: string;
  source_site: string;
  original_id: string;
  url: string;
  title: string;
  description?: string;
  price?: number;
  currency?: string;
  address_text?: string;
  city?: string;
  postal_code?: string;
  district?: string;
  latitude?: number;
  longitude?: number;
  area_sqm?: number;
  num_rooms?: number;
  num_bedrooms?: number;
  num_bathrooms?: number;
  floor?: string;
  property_type?: string;
  listing_type?: string;
  features?: string[];
  photos_urls?: string[];
  published_at?: string;
  created_at: string;
  last_seen_at: string;
  is_available: boolean;

  // Старые поля для обратной совместимости (можно удалить позже)
  address?: string;
  metroStations?: { name: string; distance: string }[];
  imageUrls?: string[];
  source?: string;
  originalUrl?: string;
  type?: string;
  area?: number;
  commission?: string;
  renovationType?: string;
}

export interface ApiResponse<T> {
  data: T[];
  total: number;
  // any other pagination/meta info
}

export interface User {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  telegram_chat_id?: string;
  whatsapp_number?: string;
  created_at: string;
  updated_at?: string;
}

export interface Filter {
  id: number;
  user_id: number;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;

  // New, specific fields (optional)
  city?: string | null;
  min_price?: number | null;
  max_price?: number | null;
  min_rooms?: number | null;
  max_rooms?: number | null;
  property_type?: string | null;

  // Deprecated field for backwards compatibility
  filter_params?: Record<string, any>;
  site_to_monitor?: string; // It was missing but seems important
}

export interface Subscription {
  id: number;
  user_id: number;
  subscription_type: 'free' | 'premium_monthly' | 'premium_annual';
  start_date: string;
  end_date?: string;
  is_active: boolean;
}
