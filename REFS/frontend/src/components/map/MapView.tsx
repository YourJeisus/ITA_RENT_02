import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import styles from './MapView.module.scss';

// Исправляем иконки маркеров Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

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

interface MapViewProps {
  listings: Listing[];
  center?: [number, number];
  zoom?: number;
}

// Компонент для автоматического подгона карты под маркеры
const FitBounds: React.FC<{ listings: Listing[] }> = ({ listings }) => {
  const map = useMap();

  useEffect(() => {
    const validListings = listings.filter(
      (listing) => listing.latitude && listing.longitude
    );

    if (validListings.length > 0) {
      const bounds = L.latLngBounds(
        validListings.map((listing) => [listing.latitude!, listing.longitude!])
      );
      map.fitBounds(bounds, { padding: [20, 20] });
    }
  }, [listings, map]);

  return null;
};

const MapView: React.FC<MapViewProps> = ({
  listings,
  center = [41.9028, 12.4964], // Рим по умолчанию
  zoom = 11,
}) => {
  const [mapReady, setMapReady] = useState(false);

  // Фильтруем объявления с координатами
  const listingsWithCoords = listings.filter(
    (listing) => listing.latitude && listing.longitude
  );

  const formatPrice = (price: string) => {
    return price
      .replace(/[^\d]/g, '')
      .replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
  };

  const getMarkerIcon = (sourcesite: string) => {
    const color = sourcesite === 'immobiliare.it' ? '#e74c3c' : '#3498db';

    return L.divIcon({
      className: 'custom-marker',
      html: `
        <div style="
          background-color: ${color};
          width: 25px;
          height: 25px;
          border-radius: 50%;
          border: 3px solid white;
          box-shadow: 0 2px 5px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 12px;
        ">
          ${sourcesite === 'immobiliare.it' ? 'I' : 'Id'}
        </div>
      `,
      iconSize: [25, 25],
      iconAnchor: [12, 12],
    });
  };

  return (
    <div className={styles.mapContainer}>
      <div className={styles.mapHeader}>
        <h2>🗺️ Карта объявлений</h2>
        <div className={styles.mapStats}>
          <span className={styles.totalListings}>Всего: {listings.length}</span>
          <span className={styles.mappedListings}>
            На карте: {listingsWithCoords.length}
          </span>
        </div>
      </div>

      <div className={styles.mapLegend}>
        <div className={styles.legendItem}>
          <div
            className={styles.legendMarker}
            style={{ backgroundColor: '#e74c3c' }}
          >
            I
          </div>
          <span>Immobiliare.it</span>
        </div>
        <div className={styles.legendItem}>
          <div
            className={styles.legendMarker}
            style={{ backgroundColor: '#3498db' }}
          >
            Id
          </div>
          <span>Idealista.it</span>
        </div>
      </div>

      <MapContainer
        center={center}
        zoom={zoom}
        className={styles.map}
        whenReady={() => setMapReady(true)}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {mapReady && <FitBounds listings={listingsWithCoords} />}

        {listingsWithCoords.map((listing) => (
          <Marker
            key={listing.id}
            position={[listing.latitude!, listing.longitude!]}
            icon={getMarkerIcon(listing.source_site)}
          >
            <Popup className={styles.customPopup}>
              <div className={styles.popupContent}>
                <div className={styles.popupHeader}>
                  <h3 className={styles.popupTitle}>
                    {listing.title?.substring(0, 60)}
                    {listing.title && listing.title.length > 60 ? '...' : ''}
                  </h3>
                  <span className={styles.sourceTag}>
                    {listing.source_site}
                  </span>
                </div>

                {listing.image_urls && listing.image_urls.length > 0 && (
                  <img
                    src={listing.image_urls[0]}
                    alt={listing.title}
                    className={styles.popupImage}
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                )}

                <div className={styles.popupDetails}>
                  <div className={styles.price}>
                    💰 €{formatPrice(listing.price)} / месяц
                  </div>

                  <div className={styles.features}>
                    {listing.area_sqm && (
                      <span className={styles.feature}>
                        📐 {listing.area_sqm} м²
                      </span>
                    )}
                    {listing.rooms_count && (
                      <span className={styles.feature}>
                        🏠 {listing.rooms_count} комн.
                      </span>
                    )}
                  </div>

                  <div className={styles.address}>
                    📍 {listing.location_address}
                  </div>
                </div>

                <a
                  href={listing.url_details}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.viewButton}
                >
                  Посмотреть объявление →
                </a>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {listingsWithCoords.length === 0 && (
        <div className={styles.noDataMessage}>
          <p>📍 Нет объявлений с координатами для отображения на карте</p>
          <p>Попробуйте изменить фильтры поиска</p>
        </div>
      )}
    </div>
  );
};

export default MapView;
