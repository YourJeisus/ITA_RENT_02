import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import styles from './FiltersSidebar.module.css';

// Определим типы для большей ясности
type Filters = {
  property_type: string;
  rooms: string[];
  price_min: string;
  price_max: string;
  city: string;
  min_area: string;
  max_area: string;
};

const FiltersSidebar: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState<Filters>({
    property_type: searchParams.get('property_type') || 'all',
    rooms: searchParams.getAll('rooms') || [],
    price_min: searchParams.get('price_min') || '',
    price_max: searchParams.get('price_max') || '',
    city: searchParams.get('city') || 'roma',
    min_area: searchParams.get('min_area') || '',
    max_area: searchParams.get('max_area') || '',
  });

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    setFilters((prev) => {
      const newRooms = checked
        ? [...prev.rooms, value]
        : prev.rooms.filter((room) => room !== value);
      return { ...prev, rooms: newRooms };
    });
  };

  const handleApplyFilters = () => {
    const newParams = new URLSearchParams();

    if (filters.city) newParams.set('city', filters.city);
    if (filters.property_type && filters.property_type !== 'all')
      newParams.set('property_type', filters.property_type);
    if (filters.price_min) newParams.set('price_min', filters.price_min);
    if (filters.price_max) newParams.set('price_max', filters.price_max);

    // Для комнат используем getAll/append, так как их может быть несколько
    filters.rooms.forEach((room) => newParams.append('rooms', room));

    if (filters.min_area) newParams.set('min_area', filters.min_area);
    if (filters.max_area) newParams.set('max_area', filters.max_area);

    setSearchParams(newParams);
  };

  const handleResetFilters = () => {
    const defaultFilters: Filters = {
      property_type: 'all',
      rooms: [],
      price_min: '',
      price_max: '',
      city: 'roma',
      min_area: '',
      max_area: '',
    };
    setFilters(defaultFilters);
    setSearchParams({}); // Очищаем параметры в URL
  };

  // Комнаты, которые мы поддерживаем. Студия (0) удалена.
  const roomOptions = [
    { value: '1', label: '1' },
    { value: '2', label: '2' },
    { value: '3', label: '3' },
    { value: '4', label: '4+' },
  ];

  return (
    <aside className={styles.sidebar}>
      <div className={styles.filterGroup}>
        <h3 className={styles.groupTitle}>Тип жилья</h3>
        <div className={styles.radioGroup}>
          <label>
            <input
              type="radio"
              name="property_type"
              value="all"
              checked={filters.property_type === 'all'}
              onChange={handleInputChange}
            />{' '}
            Все типы
          </label>
          <label>
            <input
              type="radio"
              name="property_type"
              value="apartment"
              checked={filters.property_type === 'apartment'}
              onChange={handleInputChange}
            />{' '}
            Квартира
          </label>
          <label>
            <input
              type="radio"
              name="property_type"
              value="house"
              checked={
                filters.property_type === 'house' ||
                filters.property_type === 'villa'
              }
              onChange={handleInputChange}
            />{' '}
            Дом
          </label>
          <label>
            <input
              type="radio"
              name="property_type"
              value="penthouse"
              checked={filters.property_type === 'penthouse'}
              onChange={handleInputChange}
            />{' '}
            Пентхаус
          </label>
          <label>
            <input
              type="radio"
              name="property_type"
              value="studio"
              checked={filters.property_type === 'studio'}
              onChange={handleInputChange}
            />{' '}
            Студия
          </label>

          <label>
            <input
              type="radio"
              name="property_type"
              value="room"
              checked={filters.property_type === 'room'}
              onChange={handleInputChange}
            />{' '}
            Комната
          </label>
        </div>
      </div>

      <div className={styles.filterGroup}>
        <h3 className={styles.groupTitle}>Количество комнат</h3>
        <div className={styles.checkboxGroup}>
          {roomOptions.map((opt) => (
            <label key={opt.value}>
              <input
                type="checkbox"
                name="rooms"
                value={opt.value}
                checked={filters.rooms.includes(opt.value)}
                onChange={handleCheckboxChange}
              />{' '}
              {opt.label}
            </label>
          ))}
        </div>
      </div>

      <div className={styles.filterGroup}>
        <h3 className={styles.groupTitle}>Стоимость, €</h3>
        <div className={styles.priceInputs}>
          <input
            type="number"
            name="price_min"
            placeholder="от"
            value={filters.price_min}
            onChange={handleInputChange}
          />
          <span>—</span>
          <input
            type="number"
            name="price_max"
            placeholder="до"
            value={filters.price_max}
            onChange={handleInputChange}
          />
        </div>
      </div>

      <div className={styles.filterGroup}>
        <h3 className={styles.groupTitle}>Город</h3>
        <select
          name="city"
          className={styles.select}
          value={filters.city}
          onChange={handleInputChange}
        >
          <option value="roma">Рим</option>
          <option value="milano">Милан</option>
          <option value="firenze">Флоренция</option>
        </select>
      </div>

      <div className={styles.filterGroup}>
        <h3 className={styles.groupTitle}>Общая площадь, м²</h3>
        <div className={styles.priceInputs}>
          <input
            type="number"
            name="min_area"
            placeholder="от"
            value={filters.min_area}
            onChange={handleInputChange}
          />
          <span>—</span>
          <input
            type="number"
            name="max_area"
            placeholder="до"
            value={filters.max_area}
            onChange={handleInputChange}
          />
        </div>
      </div>

      <div className={styles.actions}>
        <button className={styles.applyButton} onClick={handleApplyFilters}>
          Показать объявления
        </button>
        <button className={styles.resetButton} onClick={handleResetFilters}>
          Сбросить
        </button>
      </div>
    </aside>
  );
};

export default FiltersSidebar;
