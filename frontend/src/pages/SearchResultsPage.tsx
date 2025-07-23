import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { CircularProgress, Alert, Pagination, Box } from "@mui/material";
import ListingCard from "../components/search/ListingCard/ListingCard";
import { useListingStore } from "@/store/listingStore";
import { FilterState } from "@/types";
import SearchStatus from "@/components/common/SearchStatus";
import FiltersSidebar from "@/components/search/FiltersSidebar/FiltersSidebar";
import styles from "./SearchResultsPage.module.scss";

const SearchResultsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [page, setPage] = useState(1);

  const {
    listings,
    totalListings,
    isLoading,
    error,
    searchType,
    searchMessage,
    fetchListings,
    listingsPerPage,
  } = useListingStore();

  const totalPages = Math.ceil(totalListings / listingsPerPage);

  useEffect(() => {
    // Собираем все параметры из URL
    const filtersFromUrl: any = {};
    searchParams.forEach((value, key) => {
      // Для комнат, которые могут быть массивом
      if (key === "rooms") {
        if (!filtersFromUrl.rooms) filtersFromUrl.rooms = [];
        filtersFromUrl.rooms.push(value);
      } else {
        filtersFromUrl[key] = value;
      }
    });

    // Преобразуем параметры в формат, который ожидает smartSearch (FilterState)
    const filtersForStore: FilterState = {
      city: {
        id: filtersFromUrl.city || "roma",
        name: filtersFromUrl.city || "Рим",
      },
      transactionType: "rent",
      propertyType: filtersFromUrl.property_type || "apartment",
      rooms: filtersFromUrl.rooms ? filtersFromUrl.rooms.map(Number) : null,
      priceMin: filtersFromUrl.price_min
        ? Number(filtersFromUrl.price_min)
        : null,
      priceMax: filtersFromUrl.price_max
        ? Number(filtersFromUrl.price_max)
        : null,
      areaMin: filtersFromUrl.min_area ? Number(filtersFromUrl.min_area) : null,
      areaMax: filtersFromUrl.max_area ? Number(filtersFromUrl.max_area) : null,
      locationQuery: "", // Не используется пока
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

  const getSourceColor = (source: string) => {
    switch (source) {
      case "idealista":
        return "#E91E63";
      case "immobiliare":
        return "#2196F3";
      case "subito":
        return "#4CAF50";
      default:
        return "#757575";
    }
  };

  if (isLoading && page === 1) {
    return (
      <div className={styles.pageContainer}>
        <div className={styles.loaderContainer}>
          <CircularProgress />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.pageContainer}>
      <FiltersSidebar />
      <main className={styles.mainContent}>
        <SearchStatus
          searchType={searchType}
          searchMessage={searchMessage}
          totalCount={totalListings}
          isLoading={isLoading}
        />

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {!isLoading && listings.length === 0 && (
          <Alert severity="info">
            По вашему запросу ничего не найдено. Попробуйте изменить параметры
            поиска.
          </Alert>
        )}

        <div className={styles.listingsGrid}>
          {listings.map((listing) => (
            <ListingCard
              key={listing.id}
              listing={{
                listing_id: listing.id,
                title: listing.title,
                price: listing.price || 0,
                price_currency: "EUR",
                location_address: listing.city || listing.address_text || "",
                url_details: listing.url,
                image_urls: listing.photos_urls || [],
                area_sqm: listing.area_sqm,
                rooms_count: listing.num_rooms,
                bathrooms_count: listing.num_bathrooms,
                source_site: listing.source_site,
                property_type: listing.property_type,
              }}
            />
          ))}
        </div>

        {totalPages > 1 && (
          <Box sx={{ mt: 4, display: "flex", justifyContent: "center" }}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={handlePageChange}
              color="primary"
              size="large"
            />
          </Box>
        )}
      </main>
    </div>
  );
};

export default SearchResultsPage;
