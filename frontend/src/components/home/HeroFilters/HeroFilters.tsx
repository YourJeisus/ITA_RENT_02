import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useFilterStore } from "@/store/filterStore";
import { City, PropertyType, TransactionType } from "@/types";
import SubscriptionModal from "@/components/common/SubscriptionModal";
import styles from "./HeroFilters.module.scss";

// Города Италии
const italianCities: City[] = [
  { id: "roma", name: "Рим" },
  { id: "milano", name: "Милан" },
  { id: "napoli", name: "Неаполь" },
  { id: "torino", name: "Турин" },
  { id: "firenze", name: "Флоренция" },
  { id: "bologna", name: "Болонья" },
  { id: "venezia", name: "Венеция" },
  { id: "genova", name: "Генуя" },
  { id: "palermo", name: "Палермо" },
  { id: "verona", name: "Верона" },
];

const HeroFilters: React.FC = () => {
  const navigate = useNavigate();
  const filters = useFilterStore();
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();

    const queryParams = new URLSearchParams();

    // Город (обязательный параметр)
    if (filters.city?.name) {
      queryParams.append("city", filters.city.name);
    } else {
      queryParams.append("city", "Roma"); // По умолчанию
    }

    // Тип недвижимости
    if (filters.propertyType && filters.propertyType !== "all") {
      queryParams.append("property_type", filters.propertyType);
    }

    // Цена
    if (filters.priceMin) {
      queryParams.append("min_price", filters.priceMin.toString());
    }
    if (filters.priceMax) {
      queryParams.append("max_price", filters.priceMax.toString());
    }

    // Комнаты
    if (filters.rooms && filters.rooms.length > 0) {
      const minRooms = Math.min(...filters.rooms);
      const maxRooms = Math.max(...filters.rooms);
      queryParams.append("min_rooms", String(minRooms));
      if (minRooms !== maxRooms) {
        queryParams.append("max_rooms", String(maxRooms));
      }
    }

    // Площадь
    if (filters.areaMin) {
      queryParams.append("min_area", String(filters.areaMin));
    }
    if (filters.areaMax) {
      queryParams.append("max_area", String(filters.areaMax));
    }

    // Район/местоположение (пока не используется в API, но сохраняем для будущего)
    if (filters.locationQuery) {
      queryParams.append("locationQuery", filters.locationQuery);
    }

    // Навигация на страницу результатов с параметрами
    navigate(`/search?${queryParams.toString()}`);
  };

  const handleSubscribeClick = () => {
    setShowSubscriptionModal(true);
  };

  const getSubscriptionFilters = () => {
    return {
      city: filters.city?.name || undefined,
      min_price: filters.priceMin || undefined,
      max_price: filters.priceMax || undefined,
      min_rooms:
        filters.rooms && filters.rooms.length > 0
          ? Math.min(...filters.rooms)
          : undefined,
      max_rooms:
        filters.rooms && filters.rooms.length > 0
          ? Math.max(...filters.rooms)
          : undefined,
      property_type:
        filters.propertyType === "all" ? undefined : filters.propertyType,
    };
  };

  return (
    <section className={styles.heroFiltersContainer}>
      <h1 className={styles.title}>Найдите идеальное жилье в Италии</h1>
      <p className={styles.subtitle}>
        Агрегатор объявлений с Idealista, Immobiliare и других сайтов
      </p>
      <form onSubmit={handleSearch} className={styles.form}>
        <div className={styles.formGroup}>
          <select
            value={filters.city?.id || ""}
            onChange={(e) => {
              const selectedCity =
                italianCities.find((c) => c.id === e.target.value) || null;
              filters.setCity(selectedCity);
            }}
            className={styles.select}
          >
            <option value="" disabled>
              Выберите город
            </option>
            {italianCities.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.formGroup}>
          <select
            value={filters.transactionType}
            onChange={(e) =>
              filters.setTransactionType(e.target.value as TransactionType)
            }
            className={styles.select}
          >
            <option value="rent">Аренда</option>
            <option value="buy">Покупка</option>
          </select>
        </div>

        <div className={styles.formGroup}>
          <select
            value={filters.propertyType}
            onChange={(e) =>
              filters.setPropertyType(e.target.value as PropertyType)
            }
            className={styles.select}
          >
            <option value="all">Все типы</option>
            <option value="apartment">Квартира</option>
            <option value="house">Дом</option>
            <option value="penthouse">Пентхаус</option>
            <option value="studio">Студия</option>
            <option value="room">Комната</option>
          </select>
        </div>

        <div className={styles.formGroup}>
          <select
            value={
              filters.rooms && filters.rooms.length === 1
                ? String(filters.rooms[0])
                : ""
            }
            onChange={(e) =>
              filters.setRooms(
                e.target.value === "" ? null : [Number(e.target.value)]
              )
            }
            className={styles.select}
          >
            <option value="">Количество комнат</option>
            <option value="0">Студия</option>
            <option value="1">1 комната</option>
            <option value="2">2 комнаты</option>
            <option value="3">3 комнаты</option>
            <option value="4">4 комнаты</option>
            <option value="5">5+ комнат</option>
          </select>
        </div>

        <div className={`${styles.formGroup} ${styles.priceRange}`}>
          <input
            type="number"
            placeholder="Цена от €"
            value={filters.priceMin === null ? "" : filters.priceMin}
            onChange={(e) =>
              filters.setPriceMin(
                e.target.value === "" ? null : Number(e.target.value)
              )
            }
            min="0"
            className={styles.input}
          />
          <span className={styles.priceSeparator}>—</span>
          <input
            type="number"
            placeholder="до €"
            value={filters.priceMax === null ? "" : filters.priceMax}
            onChange={(e) =>
              filters.setPriceMax(
                e.target.value === "" ? null : Number(e.target.value)
              )
            }
            min={filters.priceMin === null ? 0 : filters.priceMin}
            className={styles.input}
          />
        </div>

        <div className={`${styles.formGroup} ${styles.locationInput}`}>
          <input
            type="text"
            placeholder="Район, улица, метро..."
            value={filters.locationQuery}
            onChange={(e) => filters.setLocationQuery(e.target.value)}
            className={styles.input}
          />
        </div>

        <div className={styles.buttonGroup}>
          <button type="submit" className={styles.submitButton}>
            Найти объявления
          </button>
          <button
            type="button"
            className={styles.subscribeButton}
            onClick={handleSubscribeClick}
          >
            🔔 Подписаться на уведомления
          </button>
        </div>
      </form>

      <div className={styles.subscriptionPromo}>
        <div className={styles.promoContent}>
          <div className={styles.promoIcon}>📱</div>
          <div className={styles.promoText}>
            <h3>Не пропустите лучшие предложения!</h3>
            <p>
              Подпишитесь на уведомления в Telegram и первыми узнавайте о новых
              объявлениях
            </p>
          </div>
        </div>
      </div>

      <SubscriptionModal
        isOpen={showSubscriptionModal}
        onClose={() => setShowSubscriptionModal(false)}
        filters={getSubscriptionFilters()}
      />
    </section>
  );
};

export default HeroFilters;
