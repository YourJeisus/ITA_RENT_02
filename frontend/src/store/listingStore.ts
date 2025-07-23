import { create } from "zustand";
import { Listing, FilterState } from "@/types";
import { listingsService } from "@/services/listingsService";

interface ListingState {
  listings: Listing[];
  totalListings: number;
  currentPage: number;
  listingsPerPage: number;
  isLoading: boolean;
  error: string | null;
  searchType: "database" | "scraping" | null;
  searchMessage: string | null;
  databaseStats: any | null;

  // Основной метод поиска
  fetchListings: (filters: FilterState, page?: number) => Promise<void>;

  // Утилиты
  checkDatabaseStats: () => Promise<void>;
  clearResults: () => void;
  setPage: (page: number) => void;
}

export const useListingStore = create<ListingState>((set, get) => ({
  listings: [],
  totalListings: 0,
  currentPage: 1,
  listingsPerPage: 50,
  isLoading: false,
  error: null,
  searchType: null,
  searchMessage: null,
  databaseStats: null,

  fetchListings: async (filters: FilterState, page = 1) => {
    set({ isLoading: true, error: null });

    try {
      const result = await listingsService.search(
        filters,
        page,
        get().listingsPerPage
      );

      set({
        listings: result.listings,
        totalListings: result.total,
        currentPage: page,
        searchType: result.searchType as "database" | "scraping",
        searchMessage: result.searchMessage,
        isLoading: false,
      });
    } catch (error: any) {
      console.error("Error fetching listings:", error);
      set({
        error:
          error.response?.data?.detail ||
          error.message ||
          "Ошибка при загрузке объявлений",
        isLoading: false,
        listings: [],
        totalListings: 0,
      });
    }
  },

  checkDatabaseStats: async () => {
    try {
      const stats = await listingsService.getDatabaseStats();
      set({ databaseStats: stats });
    } catch (error) {
      console.error("Error checking database stats:", error);
    }
  },

  clearResults: () => {
    set({
      listings: [],
      totalListings: 0,
      currentPage: 1,
      searchType: null,
      searchMessage: null,
      error: null,
    });
  },

  setPage: (page: number) => {
    set({ currentPage: page });
  },
}));
