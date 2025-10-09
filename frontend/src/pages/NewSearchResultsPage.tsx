import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { CircularProgress, Alert, Pagination, Box } from "@mui/material";
import NewListingCard from "../components/search/NewListingCard/NewListingCard";
import NewFiltersSidebar from "../components/search/NewFiltersSidebar/NewFiltersSidebar";
import NewFooter from "../components/new-home/NewFooter";
import { useListingStore } from "../store/listingStore";
import { FilterState } from "../types";

const NewSearchResultsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [page, setPage] = useState(1);

  const {
    listings,
    totalListings,
    isLoading,
    error,
    fetchListings,
    listingsPerPage,
  } = useListingStore();

  const totalPages = Math.ceil(totalListings / listingsPerPage);

  // Маппинг английских названий городов в итальянские
  const cityMapping: { [key: string]: { id: string; name: string } } = {
    rome: { id: "Roma", name: "Rome" },
    milan: { id: "Milano", name: "Milan" },
    florence: { id: "Firenze", name: "Florence" },
    naples: { id: "Napoli", name: "Naples" },
    turin: { id: "Torino", name: "Turin" },
    venice: { id: "Venezia", name: "Venice" },
    bologna: { id: "Bologna", name: "Bologna" },
    // По умолчанию, если город уже на итальянском
    roma: { id: "Roma", name: "Rome" },
    milano: { id: "Milano", name: "Milan" },
    firenze: { id: "Firenze", name: "Florence" },
    napoli: { id: "Napoli", name: "Naples" },
    torino: { id: "Torino", name: "Turin" },
    venezia: { id: "Venezia", name: "Venice" },
  };

  const normalizeCity = (cityInput: string) => {
    const cityLower = cityInput?.toLowerCase() || "";
    return cityMapping[cityLower] || { id: "Roma", name: "Rome" };
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

    fetchListings(filtersForStore, page);
  }, [searchParams, page, fetchListings]);

  const handlePageChange = (
    event: React.ChangeEvent<unknown>,
    value: number
  ) => {
    setPage(value);
    window.scrollTo(0, 0);
  };

  const cityFromUrl = searchParams.get("city") || "rome";
  const cityDisplay = normalizeCity(cityFromUrl).name;

  return (
    <div className="bg-[#eaf4fd] min-h-screen">
      {/* Navbar */}
      <nav className="bg-white h-[72px] flex items-center px-[312px] justify-between">
        <div
          className="font-bold text-[22px] text-blue-600 cursor-pointer"
          onClick={() => navigate("/")}
        >
          RentAg
        </div>
        <div className="flex items-center gap-[32px]">
          <span className="font-normal text-[16px] text-gray-900 cursor-pointer hover:text-blue-600 transition-colors">
            Apartment search
          </span>
          <span className="font-normal text-[16px] text-gray-900 cursor-pointer hover:text-blue-600 transition-colors">
            How it works
          </span>
          <span className="font-normal text-[16px] text-gray-900 cursor-pointer hover:text-blue-600 transition-colors">
            Contact
          </span>
          <span className="font-normal text-[16px] text-gray-900 cursor-pointer hover:text-blue-600 transition-colors">
            FAQ
          </span>
        </div>
        <div className="flex items-center gap-[12px]">
          <button
            onClick={() => navigate("/auth")}
            className="border border-slate-300 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-gray-900 hover:bg-gray-50 transition-colors"
          >
            Log in
          </button>
          <button
            onClick={() => navigate("/auth")}
            className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white hover:bg-blue-700 transition-colors"
          >
            Sign up
          </button>
        </div>
      </nav>

      <div className="px-[312px] py-[48px]">
        {/* Breadcrumb */}
        <p className="font-normal text-[16px] leading-[24px] text-gray-600 mb-[16px]">
          Home / {cityDisplay} / Rent an apartment
        </p>

        {/* Title */}
        <h1 className="font-bold text-[36px] leading-[40px] text-gray-900 mb-[16px]">
          Rent an apartment in {cityDisplay}
        </h1>

        {/* Count */}
        <div className="flex items-center gap-[16px] mb-[24px]">
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
        </div>

        {/* Main content: Sidebar + Listings grid */}
        <div className="flex gap-[24px]">
          {/* Filters Sidebar */}
          <NewFiltersSidebar />

          {/* Listings grid */}
          <div className="flex-1">
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
                      onFlag={(id) => console.log("Flag", id)}
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
      <NewFooter />
    </div>
  );
};

export default NewSearchResultsPage;
