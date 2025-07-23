import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  City,
  FilterState,
  PropertyType,
  TransactionType,
  RoomOption,
} from '@/types';

const initialFilters: FilterState = {
  city: { id: 'rome', name: 'Рим' },
  transactionType: 'rent',
  propertyType: 'all',
  rooms: null,
  priceMin: null,
  priceMax: null,
  locationQuery: '',
  roomOptions: [],
  areaMin: null,
  areaMax: null,
  floorType: null,
  selectedFeatures: null,
  selectedLocations: null,
};

interface FilterActions {
  setCity: (city: City | null) => void;
  setTransactionType: (type: TransactionType) => void;
  setPropertyType: (type: PropertyType) => void;
  setRooms: (rooms: number | null) => void;
  setPriceMin: (price: number | null) => void;
  setPriceMax: (price: number | null) => void;
  setLocationQuery: (query: string) => void;
  setRoomOptions: (options: RoomOption[]) => void;
  setAreaMin: (area: number | null) => void;
  setAreaMax: (area: number | null) => void;
  setFloorType: (floorType: string[] | null) => void;
  setSelectedFeatures: (features: string[] | null) => void;
  setSelectedLocations: (locations: string[] | null) => void;
  setAllFilters: (filters: Partial<FilterState>) => void;
  resetFilters: () => void;
}

export const useFilterStore = create<FilterState & FilterActions>()(
  devtools(
    (set, get) => ({
      ...initialFilters,
      setCity: (city) => set({ city }),
      setTransactionType: (type) => set({ transactionType: type }),
      setPropertyType: (type) => set({ propertyType: type }),
      setRooms: (rooms) => set({ rooms }),
      setPriceMin: (price) => set({ priceMin: price }),
      setPriceMax: (price) => set({ priceMax: price }),
      setLocationQuery: (query) => set({ locationQuery: query }),
      setRoomOptions: (options) => set({ roomOptions: options }),
      setAreaMin: (area) => set({ areaMin: area }),
      setAreaMax: (area) => set({ areaMax: area }),
      setFloorType: (floorType) => set({ floorType: floorType }),
      setSelectedFeatures: (features) => set({ selectedFeatures: features }),
      setSelectedLocations: (locations) =>
        set({ selectedLocations: locations }),
      setAllFilters: (filters) => set((state) => ({ ...state, ...filters })),
      resetFilters: () => set(initialFilters),
    }),
    { name: 'FilterStore' }
  )
);
