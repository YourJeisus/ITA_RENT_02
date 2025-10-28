export interface City {
  id: string;
  name: string;
}

export type TransactionType = "buy" | "rent";
export type PropertyType =
  | "apartment"
  | "house"
  | "penthouse"
  | "studio"
  | "room"
  | "all";
export type RoomOption = "studio" | "1" | "2" | "3" | "4" | "5+";

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
  telegram_username?: string;
  whatsapp_phone?: string;
  whatsapp_enabled: boolean;
  email_notifications_enabled: boolean;
  telegram_notifications_enabled: boolean;
  email_verified_at?: string;
  email_last_sent_at?: string;
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

  // Search parameters
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

  // Notification settings
  notification_enabled: boolean;
  notification_frequency_hours: number;
  last_notification_sent?: string | null;

  // Notification channels
  notify_telegram: boolean;
  notify_email: boolean;
  notify_whatsapp: boolean;

  // Deprecated field for backwards compatibility
  filter_params?: Record<string, any>;
  site_to_monitor?: string;
}

export interface Subscription {
  id: number;
  user_id: number;
  subscription_type: "free" | "premium_monthly" | "premium_annual";
  start_date: string;
  end_date?: string;
  is_active: boolean;
}

export interface NotificationSettings {
  email_notifications_enabled: boolean;
  telegram_notifications_enabled: boolean;
  has_telegram: boolean;
  has_whatsapp: boolean;
  whatsapp_enabled: boolean;
  email_verified_at?: string | null;
  email_last_sent_at?: string | null;
}
