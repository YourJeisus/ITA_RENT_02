import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import MapView from "../components/map/MapView";
import { listingsService } from "../services/listingsService";
import apiClient from "../services/apiClient";
import styles from "./MapPage.module.scss";

interface Listing {
  id: string;
  title: string;
  price: number;
  address_text: string;
  latitude?: number;
  longitude?: number;
  url: string;
  images: string[];
  area_sqm?: number;
  num_rooms?: number;
  source_site: string;
}

const MapPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadListings = async () => {
      try {
        setLoading(true);
        setError(null);

        // Получаем параметры поиска из URL
        const city = searchParams.get("city") || "roma";
        const minPrice = searchParams.get("min_price")
          ? parseInt(searchParams.get("min_price")!)
          : undefined;
        const maxPrice = searchParams.get("max_price")
          ? parseInt(searchParams.get("max_price")!)
          : undefined;
        const propertyType = searchParams.get("property_type") || undefined;
        const sourceSite = searchParams.get("source_site") || undefined;

        console.log(
          "🗺️ Загрузка объявлений для карты с фильтрами:",
          { city, minPrice, maxPrice, propertyType, sourceSite }
        );

        // Используем apiClient с правильным URL
        const response = await apiClient.get("/listings/map", {
          params: {
            ...(city && { city }),
            ...(minPrice && { min_price: minPrice }),
            ...(maxPrice && { max_price: maxPrice }),
            ...(propertyType && { property_type: propertyType }),
            ...(sourceSite && { source_site: sourceSite }),
            limit: 500
          }
        });

        const data = response.data;

        if (data.success) {
          setListings(data.listings || []);
          console.log(
            `✅ Загружено ${data.listings?.length || 0} объявлений для карты (${data.total} с координатами)`
          );
        } else {
          throw new Error(data.error || "Ошибка загрузки данных");
        }
      } catch (err) {
        console.error("❌ Ошибка загрузки объявлений для карты:", err);
        setError(err instanceof Error ? err.message : "Неизвестная ошибка");
      } finally {
        setLoading(false);
      }
    };

    loadListings();
  }, [searchParams]);

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loadingSpinner}>
          <div className={styles.spinner}></div>
          <p>Загрузка карты объявлений...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <div className={styles.errorMessage}>
          <h2>❌ Ошибка загрузки</h2>
          <p>{error}</p>
          <button
            onClick={() => window.location.reload()}
            className={styles.retryButton}
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.mapPageContainer}>
      <MapView listings={listings} />
    </div>
  );
};

export default MapPage;
