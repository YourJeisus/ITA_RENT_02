import React, { useState, useEffect, useMemo, useCallback } from "react";
import { useSearchParams, useNavigate, useLocation } from "react-router-dom";
import { CircularProgress, Alert, Pagination, Box } from "@mui/material";
import NewListingCard from "../components/search/NewListingCard/NewListingCard";
import NewFiltersSidebar from "../components/search/NewFiltersSidebar/NewFiltersSidebar";
import NewNavbar from "../components/new-home/NewNavbar";
import AuthFooter from "../components/auth/AuthFooter";
import { useListingStore } from "../store/listingStore";
import { FilterState } from "../types";
import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useAuthStore } from "../store/authStore";
import {
  filtersService,
  FilterSubscribePayload,
  FilterSubscribeResponse,
} from "../services/filtersService";

const NewSearchResultsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [page, setPage] = useState(1);
  const [subscribeLoading, setSubscribeLoading] = useState(false);
  const [subscribeMessage, setSubscribeMessage] = useState<string | null>(null);
  const [subscribeError, setSubscribeError] = useState<string | null>(null);

  // Отдельные селекторы для каждого значения - предотвращает бесконечные ре-рендеры
  const listings = useListingStore((state) => state.listings);
  const totalListings = useListingStore((state) => state.totalListings);
  const isLoading = useListingStore((state) => state.isLoading);
  const error = useListingStore((state) => state.error);
  const listingsPerPage = useListingStore((state) => state.listingsPerPage);

  const totalPages = useMemo(
    () => Math.ceil(totalListings / listingsPerPage || 1),
    [totalListings, listingsPerPage]
  );

  // Отдельные селекторы для authStore тоже
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  // Маппинг английских названий городов в итальянские
  const cityMapping: {
    [key: string]: { id: string; name: string; coords: [number, number] };
  } = {
    rome: { id: "Roma", name: "Rome", coords: [41.9028, 12.4964] },
    milan: { id: "Milano", name: "Milan", coords: [45.4642, 9.19] },
    florence: { id: "Firenze", name: "Florence", coords: [43.7696, 11.2558] },
    naples: { id: "Napoli", name: "Naples", coords: [40.8518, 14.2681] },
    turin: { id: "Torino", name: "Turin", coords: [45.0703, 7.6869] },
    venice: { id: "Venezia", name: "Venice", coords: [45.4408, 12.3155] },
    bologna: { id: "Bologna", name: "Bologna", coords: [44.4949, 11.3426] },
    // По умолчанию, если город уже на итальянском
    roma: { id: "Roma", name: "Rome", coords: [41.9028, 12.4964] },
    milano: { id: "Milano", name: "Milan", coords: [45.4642, 9.19] },
    firenze: { id: "Firenze", name: "Florence", coords: [43.7696, 11.2558] },
    napoli: { id: "Napoli", name: "Naples", coords: [40.8518, 14.2681] },
    torino: { id: "Torino", name: "Turin", coords: [45.0703, 7.6869] },
    venezia: { id: "Venezia", name: "Venice", coords: [45.4408, 12.3155] },
  };

  const normalizeCity = (cityInput: string) => {
    const cityLower = cityInput?.toLowerCase() || "";
    return (
      cityMapping[cityLower] || {
        id: "Roma",
        name: "Rome",
        coords: [41.9028, 12.4964] as [number, number],
      }
    );
  };

  useEffect(() => {
    // Собираем все параметры из URL
    const filtersFromUrl: any = {};
    searchParams.forEach((value, key) => {
      if (key === "rooms") {
        if (!filtersFromUrl.rooms) filtersFromUrl.rooms = [];
        filtersFromUrl.rooms.push(value);
      } else {
        filtersFromUrl[key] = value;
      }
    });

    // Нормализуем город
    const cityData = normalizeCity(filtersFromUrl.city);

    // Преобразуем параметры в формат FilterState
    const filtersForStore: FilterState = {
      city: cityData,
      transactionType: "rent",
      propertyType: filtersFromUrl.property_type || undefined,
      rooms: filtersFromUrl.rooms ? filtersFromUrl.rooms.map(Number) : null,
      priceMin: filtersFromUrl.price_min
        ? Number(filtersFromUrl.price_min)
        : null,
      priceMax: filtersFromUrl.price_max
        ? Number(filtersFromUrl.price_max)
        : null,
      areaMin: filtersFromUrl.min_area ? Number(filtersFromUrl.min_area) : null,
      areaMax: filtersFromUrl.max_area ? Number(filtersFromUrl.max_area) : null,
      locationQuery: "",
    };

    // Вызываем fetchListings через getState() чтобы избежать зависимости от функции
    useListingStore.getState().fetchListings(filtersForStore, page);
  }, [searchParams, page]);

  const handlePageChange = (
    event: React.ChangeEvent<unknown>,
    value: number
  ) => {
    setPage(value);
    window.scrollTo(0, 0);
  };

  const cityFromUrl = searchParams.get("city") || "rome";
  const cityData = normalizeCity(cityFromUrl);
  const cityDisplay = cityData.name;

  const mapCenter = useMemo<[number, number]>(() => {
    return cityData.coords;
  }, [cityData]);

  const buildRoomsConstraints = useCallback(() => {
    const roomParams = searchParams.getAll("rooms");
    if (roomParams.length === 0) {
      return {
        min_rooms: null as number | null,
        max_rooms: null as number | null,
      };
    }

    let hasStudio = false;
    let hasFivePlus = false;
    const numericValues: number[] = [];

    roomParams.forEach((value) => {
      if (value === "studio") {
        hasStudio = true;
        numericValues.push(0);
        return;
      }

      if (value === "5+") {
        hasFivePlus = true;
        numericValues.push(5);
        return;
      }

      const parsed = Number(value);
      if (!Number.isNaN(parsed)) {
        numericValues.push(parsed);
      }
    });

    if (numericValues.length === 0) {
      return {
        min_rooms: null as number | null,
        max_rooms: null as number | null,
      };
    }

    const minRooms = Math.min(...numericValues);
    let maxRooms: number | null = Math.max(...numericValues);

    if (hasFivePlus) {
      maxRooms = null;
    }

    if (hasStudio && numericValues.length === 1) {
      return { min_rooms: 0, max_rooms: 0 };
    }

    return {
      min_rooms: minRooms,
      max_rooms: maxRooms,
    };
  }, [searchParams]);

  const buildSubscribePayload = useCallback(
    (forceReplace = false): FilterSubscribePayload => {
      const { min_rooms, max_rooms } = buildRoomsConstraints();

      const priceMin = searchParams.get("price_min");
      const priceMax = searchParams.get("price_max");
      const minArea = searchParams.get("min_area");
      const maxArea = searchParams.get("max_area");
      const propertyTypeParam = searchParams.getAll("property_type");
      const propertyType = propertyTypeParam.length
        ? propertyTypeParam[0]
        : null;

      const payload: FilterSubscribePayload = {
        name: `Search in ${cityDisplay}`,
        city: cityData.id,
        min_price: priceMin ? Number(priceMin) : null,
        max_price: priceMax ? Number(priceMax) : null,
        min_rooms,
        max_rooms,
        property_type: propertyType,
        min_area: minArea ? Number(minArea) : null,
        max_area: maxArea ? Number(maxArea) : null,
        notification_enabled: true,
        notification_frequency_hours: 12,
        notify_email: user?.email_notifications_enabled ?? true,
        notify_telegram:
          (Boolean(user?.telegram_chat_id) &&
            (user?.telegram_notifications_enabled ?? true)) ||
          false,
        notify_whatsapp: false,
        force_replace: forceReplace,
      };

      return payload;
    },
    [
      buildRoomsConstraints,
      cityData.id,
      cityDisplay,
      searchParams,
      user?.email_notifications_enabled,
      user?.telegram_chat_id,
      user?.telegram_notifications_enabled,
    ]
  );

  const handleSubscribe = useCallback(async () => {
    setSubscribeMessage(null);
    setSubscribeError(null);

    if (!isAuthenticated) {
      navigate(
        `/login?next=${encodeURIComponent(
          `${location.pathname}${location.search}`
        )}`
      );
      return;
    }

    setSubscribeLoading(true);

    const attemptSubscription = async (
      forceReplace: boolean
    ): Promise<FilterSubscribeResponse> => {
      const payload = buildSubscribePayload(forceReplace);
      return filtersService.subscribeToFilter(payload);
    };

    try {
      const response = await attemptSubscription(false);

      if (response.status === "needs_confirmation") {
        const userConfirmed = window.confirm(
          response.message ||
            "У вас уже есть подписка на фильтр. Заменить существующий фильтр?"
        );

        if (!userConfirmed) {
          setSubscribeMessage("Подписка оставлена без изменений");
          setSubscribeLoading(false);
          return;
        }

        const confirmResponse = await attemptSubscription(true);
        setSubscribeMessage(confirmResponse.message);
      } else {
        setSubscribeMessage(response.message);
      }
    } catch (error: any) {
      const message =
        error?.response?.data?.detail ||
        error?.message ||
        "Не удалось оформить подписку. Попробуйте позже.";
      setSubscribeError(message);
    } finally {
      setSubscribeLoading(false);
    }
  }, [
    buildSubscribePayload,
    isAuthenticated,
    navigate,
    location.pathname,
    location.search,
  ]);

  return (
    <div className="bg-[#eaf4fd] min-h-screen">
      {/* Navbar */}
      <NewNavbar />

      <div className="px-[160px] py-[48px]">
        {/* Breadcrumb */}
        <p className="font-normal text-[16px] leading-[24px] text-gray-600 mb-[16px]">
          Home / {cityDisplay} / Rent an apartment
        </p>

        {/* Title */}
        <h1 className="font-bold text-[36px] leading-[40px] text-gray-900 mb-[16px]">
          Rent an apartment in {cityDisplay}
        </h1>

        {/* Count */}
        <div className="flex flex-wrap items-center gap-[16px] mb-[24px]">
          <p className="font-normal text-[16px] leading-[24px] text-gray-900">
            {totalListings.toLocaleString()} apartments
          </p>
          <button className="font-normal text-[16px] leading-[24px] text-gray-900 hover:text-blue-600 transition-colors flex items-center gap-[8px]">
            <span>Default</span>
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M4 6L8 10L12 6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <button
            type="button"
            onClick={handleSubscribe}
            disabled={subscribeLoading}
            className="ml-auto px-[20px] py-[10px] bg-blue-600 text-white rounded-[8px] font-semibold text-[15px] hover:bg-blue-700 transition disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {subscribeLoading ? "Subscribing..." : "Subscribe to this search"}
          </button>
        </div>

        {subscribeMessage && (
          <div className="mb-4 text-[14px] text-green-600">
            {subscribeMessage}
          </div>
        )}
        {subscribeError && (
          <div className="mb-4 text-[14px] text-red-600">{subscribeError}</div>
        )}

        {/* Main content: Sidebar + Listings grid */}
        <div className="flex gap-[24px]">
          {/* Filters Sidebar */}
          <NewFiltersSidebar />

          {/* Listings grid */}
          <div className="flex-1">
            <div className="relative rounded-[12px] shadow-[0px_4px_12px_rgba(0,0,0,0.04)] bg-white mb-[40px] overflow-hidden">
              <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-white/45 via-transparent to-white/35 z-[1]" />
              <MapContainer
                center={mapCenter}
                zoom={12}
                style={{ height: "140px", width: "100%" }}
                scrollWheelZoom={false}
                dragging={false}
                doubleClickZoom={false}
                zoomControl={false}
                attributionControl={false}
              >
                <TileLayer url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png" />
              </MapContainer>
              <div
                className="pointer-events-none absolute inset-0 flex items-center justify-center"
                style={{ zIndex: 9999 }}
              >
                <button
                  type="button"
                  className="pointer-events-auto flex items-center justify-center bg-white border border-gray-200 px-[24px] py-[8px] rounded-[8px] shadow-[0px_4px_12px_rgba(0,0,0,0.04)] text-[16px] font-semibold text-gray-900"
                  style={{ zIndex: 10000 }}
                >
                  View on map
                </button>
              </div>
            </div>
            {isLoading && page === 1 ? (
              <div className="flex items-center justify-center py-[100px]">
                <CircularProgress />
              </div>
            ) : error ? (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            ) : listings.length === 0 ? (
              <div className="bg-white rounded-[12px] p-[48px] text-center">
                <p className="font-normal text-[18px] text-gray-600">
                  No apartments found matching your criteria
                </p>
              </div>
            ) : (
              <>
                {/* Grid of cards */}
                <div className="grid grid-cols-3 gap-[24px] mb-[48px]">
                  {listings.map((listing) => (
                    <NewListingCard
                      key={listing.id}
                      listing={listing}
                      onFavoriteToggle={(id) => console.log("Favorite", id)}
                      onShare={(id) => console.log("Share", id)}
                      onShowMap={(id) => console.log("Show on map", id)}
                    />
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <Box display="flex" justifyContent="center" mb={4}>
                    <Pagination
                      count={totalPages}
                      page={page}
                      onChange={handlePageChange}
                      color="primary"
                      size="large"
                      showFirstButton
                      showLastButton
                    />
                  </Box>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <AuthFooter />
    </div>
  );
};

export default NewSearchResultsPage;
