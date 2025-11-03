import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";
import "leaflet.markercluster"; // ВАЖНО: импортируем сам плагин
import styles from "./MapView.module.scss";

// Исправляем иконки маркеров Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

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

interface MapViewProps {
  listings: Listing[];
  center?: [number, number];
  zoom?: number;
}

const MapView: React.FC<MapViewProps> = ({
  listings,
  center = [41.9028, 12.4964],
  zoom = 11,
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);

  const listingsWithCoords = listings.filter(
    (listing) => listing.latitude && listing.longitude
  );

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Инициализируем карту
    if (!mapRef.current) {
      mapRef.current = L.map(mapContainerRef.current).setView(center, zoom);

      L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        {
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          maxZoom: 19,
        }
      ).addTo(mapRef.current);
    }

    const map = mapRef.current;

    // Очищаем старые маркеры
    map.eachLayer((layer) => {
      if (layer.options && layer.options.maxClusterRadius !== undefined) {
        map.removeLayer(layer);
      }
    });

    // Создаем группу кластеров
    const markerClusterGroup = L.markerClusterGroup({
      maxClusterRadius: 80,
      showCoverageOnHover: false,
      iconCreateFunction: (cluster) => {
        const count = cluster.getChildCount();
        let size = "30px";
        let fontSize = "14px";

        if (count > 100) {
          size = "45px";
          fontSize = "18px";
        } else if (count > 50) {
          size = "40px";
          fontSize = "16px";
        } else if (count > 10) {
          size = "35px";
          fontSize = "15px";
        }

        return L.divIcon({
          html: `
            <div style="
              background-color: #1e40af;
              width: ${size};
              height: ${size};
              border-radius: 50%;
              box-shadow: 0 2px 8px rgba(0,0,0,0.4);
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: ${fontSize};
              font-weight: bold;
              color: white;
              font-family: Arial, sans-serif;
            ">
              ${count}
            </div>
          `,
          iconSize: [parseInt(size), parseInt(size)],
          iconAnchor: [parseInt(size) / 2, parseInt(size) / 2],
          className: "marker-cluster",
        });
      },
    });

    // Добавляем маркеры
    listingsWithCoords.forEach((listing) => {
      const marker = L.marker([listing.latitude!, listing.longitude!], {
        icon: L.divIcon({
          className: "custom-marker",
          html: `
            <div style="
              background-color: #2563EB;
              width: 25px;
              height: 25px;
              border-radius: 50%;
              box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            "></div>
          `,
          iconSize: [25, 25],
          iconAnchor: [12, 12],
        }),
      });

      const popupContent = `
        <div style="max-width: 250px;">
          <h4 style="margin: 0 0 10px 0; font-size: 14px;">${listing.title?.substring(0, 60)}</h4>
          ${listing.images && listing.images.length > 0 ? `<img src="${listing.images[0]}" alt="img" style="width: 100%; height: 150px; object-fit: cover; border-radius: 4px; margin-bottom: 10px;" onerror="this.style.display='none'">` : ""}
          <div style="font-size: 13px; color: #555;">
            💰 €${listing.price?.toLocaleString("en-US") || "—"} / месяц
            ${listing.area_sqm ? `<br>📐 ${listing.area_sqm} м²` : ""}
            ${listing.num_rooms ? `<br>🏠 ${listing.num_rooms} комн.` : ""}
            <br>📍 ${listing.address_text}
          </div>
          <a href="${listing.url}" target="_blank" rel="noopener noreferrer" style="color: #2563EB; text-decoration: none; font-size: 12px; display: block; margin-top: 8px;">Посмотреть →</a>
        </div>
      `;

      marker.bindPopup(popupContent);
      markerClusterGroup.addLayer(marker);
    });

    map.addLayer(markerClusterGroup);

    // Подгоняем вид на маркеры
    if (listingsWithCoords.length > 0) {
      const bounds = L.latLngBounds(
        listingsWithCoords.map((l) => [l.latitude!, l.longitude!])
      );
      map.fitBounds(bounds, { padding: [50, 50] });
    }

    return () => {
      map.removeLayer(markerClusterGroup);
    };
  }, [listingsWithCoords, center, zoom]);

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
            style={{ backgroundColor: "#2563EB" }}
          ></div>
          <span>Объявления</span>
        </div>
        <div className={styles.legendItem}>
          <div
            className={styles.legendMarker}
            style={{ backgroundColor: "#1e40af" }}
          ></div>
          <span>Группы объявлений</span>
        </div>
      </div>

      <div
        ref={mapContainerRef}
        className={styles.map}
        style={{ width: "100%", height: "100%" }}
      />

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
