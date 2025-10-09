import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type PropertyType = 'apartment' | 'room' | 'house';
export type RoomType = 'studio' | '1' | '2' | '3' | '4' | '5+';

export interface UserFilter {
  id: string;
  name: string;
  city: string;
  property_type: PropertyType[];
  rooms: RoomType[];
  price_min: string;
  price_max: string;
  min_area: string;
  max_area: string;
  no_commission: boolean;
  pets_allowed: boolean;
  children_allowed: boolean;
  createdAt: string;
}

interface FilterStore {
  savedFilters: UserFilter[];
  currentFilter: Partial<UserFilter>;
  
  // Actions
  saveFilter: (filter: Omit<UserFilter, 'id' | 'createdAt'>) => void;
  updateFilter: (id: string, filter: Partial<UserFilter>) => void;
  deleteFilter: (id: string) => void;
  setCurrentFilter: (filter: Partial<UserFilter>) => void;
  loadFilter: (id: string) => void;
  clearCurrentFilter: () => void;
}

const defaultFilter: Partial<UserFilter> = {
  city: 'Rome',
  property_type: [],
  rooms: [],
  price_min: '',
  price_max: '',
  min_area: '',
  max_area: '',
  no_commission: false,
  pets_allowed: false,
  children_allowed: false,
};

export const useFilterStore = create<FilterStore>()(
  persist(
    (set, get) => ({
      savedFilters: [],
      currentFilter: { ...defaultFilter },

      saveFilter: (filter) => {
        const newFilter: UserFilter = {
          ...filter,
          id: Date.now().toString(),
          createdAt: new Date().toISOString(),
        };
        
        set((state) => ({
          savedFilters: [...state.savedFilters, newFilter],
          currentFilter: newFilter,
        }));
      },

      updateFilter: (id, updatedFilter) => {
        set((state) => ({
          savedFilters: state.savedFilters.map((filter) =>
            filter.id === id ? { ...filter, ...updatedFilter } : filter
          ),
        }));
      },

      deleteFilter: (id) => {
        set((state) => ({
          savedFilters: state.savedFilters.filter((filter) => filter.id !== id),
        }));
      },

      setCurrentFilter: (filter) => {
        set({ currentFilter: filter });
      },

      loadFilter: (id) => {
        const filter = get().savedFilters.find((f) => f.id === id);
        if (filter) {
          set({ currentFilter: filter });
        }
      },

      clearCurrentFilter: () => {
        set({ currentFilter: { ...defaultFilter } });
      },
    }),
    {
      name: 'filter-storage',
    }
  )
);
