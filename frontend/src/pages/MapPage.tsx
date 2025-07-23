import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import MapView from '../components/map/MapView';
import { listingsService } from '../services/listingsService';
import styles from './MapPage.module.scss';

interface Listing {
  id: number;
  title: string;
  price: string;
  location_address: string;
  latitude?: number;
  longitude?: number;
  url_details: string;
  image_urls: string[];
  area_sqm?: string;
  rooms_count?: string;
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
        const searchFilters = {
          city: searchParams.get('city') || 'roma',
          min_price: searchParams.get('min_price')
            ? parseInt(searchParams.get('min_price')!)
            : undefined,
          max_price: searchParams.get('max_price')
            ? parseInt(searchParams.get('max_price')!)
            : undefined,
          min_area: searchParams.get('min_area')
            ? parseInt(searchParams.get('min_area')!)
            : undefined,
          max_area: searchParams.get('max_area')
            ? parseInt(searchParams.get('max_area')!)
            : undefined,
          rooms_count: searchParams.get('rooms_count')
            ? parseInt(searchParams.get('rooms_count')!)
            : undefined,
          property_type: searchParams.get('property_type') || undefined,
          source_site: searchParams.get('source_site') || undefined,
        };

        console.log(
          '🗺️ Загрузка объявлений для карты с фильтрами:',
          searchFilters
        );

        // Используем быстрый поиск в базе данных
        const response = await listingsService.fastSearch(
          searchFilters,
          0,
          1000
        );

        if (response.success) {
          setListings(response.listings || []);
          console.log(
            `✅ Загружено ${response.listings?.length || 0} объявлений для карты из базы данных`
          );
        } else {
          throw new Error(response.error || 'Ошибка загрузки данных');
        }
      } catch (err) {
        console.error('❌ Ошибка загрузки объявлений для карты:', err);
        setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
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
