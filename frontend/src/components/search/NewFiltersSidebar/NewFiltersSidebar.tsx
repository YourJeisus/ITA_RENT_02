import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useListingStore } from "../../../store/listingStore";
import styles from "./NewFiltersSidebar.module.scss";

type Filters = {
  property_type: string[];
  rooms: string[];
  price_min: string;
  price_max: string;
  city: string;
  min_area: string;
  max_area: string;
  kitchen_area_min: string;
  kitchen_area_max: string;
  no_commission: boolean;
  renovation: string[];
  floor_type: string[];
  floor_min: string;
  floor_max: string;
  floors_in_building_min: string;
  floors_in_building_max: string;
  year_built_min: string;
  year_built_max: string;
  building_type: string[];
  park_nearby: boolean;
  no_noisy_roads: boolean;
  pets_allowed: boolean;
  children_allowed: boolean;
};

const NewFiltersSidebar: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { totalListings } = useListingStore();

  const [filters, setFilters] = useState<Filters>({
    property_type: searchParams.getAll("property_type") || [],
    rooms: searchParams.getAll("rooms") || [],
    price_min: searchParams.get("price_min") || "",
    price_max: searchParams.get("price_max") || "",
    city: searchParams.get("city") || "Rome",
    min_area: searchParams.get("min_area") || "",
    max_area: searchParams.get("max_area") || "",
    kitchen_area_min: searchParams.get("kitchen_area_min") || "",
    kitchen_area_max: searchParams.get("kitchen_area_max") || "",
    no_commission: searchParams.get("no_commission") === "true",
    renovation: searchParams.getAll("renovation") || [],
    floor_type: searchParams.getAll("floor_type") || [],
    floor_min: searchParams.get("floor_min") || "",
    floor_max: searchParams.get("floor_max") || "",
    floors_in_building_min: searchParams.get("floors_in_building_min") || "",
    floors_in_building_max: searchParams.get("floors_in_building_max") || "",
    year_built_min: searchParams.get("year_built_min") || "",
    year_built_max: searchParams.get("year_built_max") || "",
    building_type: searchParams.getAll("building_type") || [],
    park_nearby: searchParams.get("park_nearby") === "true",
    no_noisy_roads: searchParams.get("no_noisy_roads") === "true",
    pets_allowed: searchParams.get("pets_allowed") === "true",
    children_allowed: searchParams.get("children_allowed") === "true",
  });

  const handleButtonToggle = (
    category:
      | "property_type"
      | "rooms"
      | "renovation"
      | "floor_type"
      | "building_type",
    value: string
  ) => {
    setFilters((prev) => {
      const current = prev[category];
      const updated = current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value];
      return { ...prev, [category]: updated };
    });
  };

  const handleCheckboxChange = (field: keyof Filters) => {
    setFilters((prev) => ({ ...prev, [field]: !prev[field] }));
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleApplyFilters = () => {
    const newParams = new URLSearchParams();

    if (filters.city) newParams.set("city", filters.city.toLowerCase());

    filters.property_type.forEach((type) =>
      newParams.append("property_type", type)
    );
    filters.rooms.forEach((room) => newParams.append("rooms", room));
    filters.renovation.forEach((type) => newParams.append("renovation", type));
    filters.floor_type.forEach((type) => newParams.append("floor_type", type));
    filters.building_type.forEach((type) =>
      newParams.append("building_type", type)
    );

    if (filters.price_min) newParams.set("price_min", filters.price_min);
    if (filters.price_max) newParams.set("price_max", filters.price_max);
    if (filters.min_area) newParams.set("min_area", filters.min_area);
    if (filters.max_area) newParams.set("max_area", filters.max_area);
    if (filters.kitchen_area_min)
      newParams.set("kitchen_area_min", filters.kitchen_area_min);
    if (filters.kitchen_area_max)
      newParams.set("kitchen_area_max", filters.kitchen_area_max);
    if (filters.floor_min) newParams.set("floor_min", filters.floor_min);
    if (filters.floor_max) newParams.set("floor_max", filters.floor_max);
    if (filters.floors_in_building_min)
      newParams.set("floors_in_building_min", filters.floors_in_building_min);
    if (filters.floors_in_building_max)
      newParams.set("floors_in_building_max", filters.floors_in_building_max);
    if (filters.year_built_min)
      newParams.set("year_built_min", filters.year_built_min);
    if (filters.year_built_max)
      newParams.set("year_built_max", filters.year_built_max);

    if (filters.no_commission)
      newParams.set("no_commission", filters.no_commission.toString());
    if (filters.park_nearby)
      newParams.set("park_nearby", filters.park_nearby.toString());
    if (filters.no_noisy_roads)
      newParams.set("no_noisy_roads", filters.no_noisy_roads.toString());
    if (filters.pets_allowed)
      newParams.set("pets_allowed", filters.pets_allowed.toString());
    if (filters.children_allowed)
      newParams.set("children_allowed", filters.children_allowed.toString());

    setSearchParams(newParams);
  };

  const propertyTypes = [
    { value: "apartment", label: "Apartment" },
    { value: "room", label: "Room" },
    { value: "house", label: "House" },
  ];

  const roomOptions = [
    { value: "studio", label: "Studio" },
    { value: "1", label: "1" },
    { value: "2", label: "2" },
    { value: "3", label: "3" },
    { value: "4", label: "4" },
    { value: "5", label: "5+" },
  ];

  const renovationTypes = [
    { value: "outdated", label: "Outdated" },
    { value: "budget", label: "Budget" },
    { value: "euro", label: "Euro renovation" },
    { value: "designer", label: "Designer" },
  ];

  const floorTypes = [
    { value: "not_first", label: "Not first" },
    { value: "not_last", label: "Not last" },
    { value: "not_first_not_last", label: "Not first and not last" },
    { value: "only_last", label: "Only last" },
  ];

  const buildingTypes = [
    { value: "monolithic", label: "Monolithic" },
    { value: "brick_monolithic", label: "Brick-monolithic" },
    { value: "brick", label: "Brick" },
    { value: "stalinka", label: "Stalinka" },
    { value: "block", label: "Block" },
    { value: "panel", label: "Panel" },
    { value: "wooden", label: "Wooden" },
  ];

  return (
    <aside className={styles.sidebar}>
      <div className={styles.filtersContent}>
        {/* City */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>City</h3>
          <select
            name="city"
            className={styles.select}
            value={filters.city}
            onChange={handleInputChange}
          >
            <option value="Rome">Rome</option>
            <option value="Milan">Milan</option>
            <option value="Florence">Florence</option>
            <option value="Naples">Naples</option>
            <option value="Turin">Turin</option>
            <option value="Venice">Venice</option>
          </select>
        </div>

        {/* Property Type */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Property type</h3>
          <div className={styles.pillGroup}>
            {propertyTypes.map((type) => (
              <button
                key={type.value}
                className={`${styles.pill} ${
                  filters.property_type.includes(type.value)
                    ? styles.pillActive
                    : ""
                }`}
                onClick={() => handleButtonToggle("property_type", type.value)}
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>

        {/* Rooms */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Rooms</h3>
          <div className={styles.pillGroup}>
            {roomOptions.map((room) => (
              <button
                key={room.value}
                className={`${styles.pill} ${
                  filters.rooms.includes(room.value) ? styles.pillActive : ""
                }`}
                onClick={() => handleButtonToggle("rooms", room.value)}
              >
                {room.label}
              </button>
            ))}
          </div>
        </div>

        {/* Price */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Price, €</h3>
          <div className={styles.rangeInputs}>
            <input
              type="number"
              name="price_min"
              placeholder="From"
              value={filters.price_min}
              onChange={handleInputChange}
              className={styles.input}
            />
            <span className={styles.separator}>—</span>
            <input
              type="number"
              name="price_max"
              placeholder="To"
              value={filters.price_max}
              onChange={handleInputChange}
              className={styles.input}
            />
          </div>
        </div>

        {/* Agent Commission */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Agent commission</h3>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={filters.no_commission}
              onChange={() => handleCheckboxChange("no_commission")}
              className={styles.checkbox}
            />
            <span>No commission</span>
          </label>
        </div>

        {/* Renovation */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Renovation type</h3>
          <div className={styles.pillGroup}>
            {renovationTypes.map((type) => (
              <button
                key={type.value}
                className={`${styles.pill} ${
                  filters.renovation.includes(type.value)
                    ? styles.pillActive
                    : ""
                }`}
                onClick={() => handleButtonToggle("renovation", type.value)}
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>

        {/* Location - Placeholders */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Location</h3>
          <button className={styles.expandButton}>
            <span>Draw on map</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M6 4L10 8L6 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <button className={styles.expandButton}>
            <span>District</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M6 4L10 8L6 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <button className={styles.expandButton}>
            <span>Add metro</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M6 4L10 8L6 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <button className={styles.expandButton}>
            <span>Time to metro</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M6 4L10 8L6 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>

        {/* Parks/Roads */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Parks/Roads</h3>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={filters.park_nearby}
              onChange={() => handleCheckboxChange("park_nearby")}
              className={styles.checkbox}
            />
            <span>Park within walking distance</span>
          </label>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={filters.no_noisy_roads}
              onChange={() => handleCheckboxChange("no_noisy_roads")}
              className={styles.checkbox}
            />
            <span>No noisy roads nearby</span>
          </label>
        </div>

        {/* Total Area */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Total area, m²</h3>
          <div className={styles.rangeInputs}>
            <input
              type="number"
              name="min_area"
              placeholder="From"
              value={filters.min_area}
              onChange={handleInputChange}
              className={styles.input}
            />
            <span className={styles.separator}>—</span>
            <input
              type="number"
              name="max_area"
              placeholder="To"
              value={filters.max_area}
              onChange={handleInputChange}
              className={styles.input}
            />
          </div>
        </div>

        {/* Kitchen Area */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Kitchen area, m²</h3>
          <div className={styles.rangeInputs}>
            <input
              type="number"
              name="kitchen_area_min"
              placeholder="From"
              value={filters.kitchen_area_min}
              onChange={handleInputChange}
              className={styles.input}
            />
            <span className={styles.separator}>—</span>
            <input
              type="number"
              name="kitchen_area_max"
              placeholder="To"
              value={filters.kitchen_area_max}
              onChange={handleInputChange}
              className={styles.input}
            />
          </div>
        </div>

        {/* Floor Type */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Floor</h3>
          <div className={styles.pillGroup}>
            {floorTypes.map((type) => (
              <button
                key={type.value}
                className={`${styles.pill} ${
                  filters.floor_type.includes(type.value)
                    ? styles.pillActive
                    : ""
                }`}
                onClick={() => handleButtonToggle("floor_type", type.value)}
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>

        {/* Floor Range */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Floor - exact range</h3>
          <div className={styles.rangeInputs}>
            <input
              type="number"
              name="floor_min"
              placeholder="From"
              value={filters.floor_min}
              onChange={handleInputChange}
              className={styles.input}
            />
            <span className={styles.separator}>—</span>
            <input
              type="number"
              name="floor_max"
              placeholder="To"
              value={filters.floor_max}
              onChange={handleInputChange}
              className={styles.input}
            />
          </div>
        </div>

        {/* Floors in Building */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Floors in building</h3>
          <div className={styles.rangeInputs}>
            <input
              type="number"
              name="floors_in_building_min"
              placeholder="From"
              value={filters.floors_in_building_min}
              onChange={handleInputChange}
              className={styles.input}
            />
            <span className={styles.separator}>—</span>
            <input
              type="number"
              name="floors_in_building_max"
              placeholder="To"
              value={filters.floors_in_building_max}
              onChange={handleInputChange}
              className={styles.input}
            />
          </div>
        </div>

        {/* Year of Construction */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Year of construction</h3>
          <div className={styles.rangeInputs}>
            <input
              type="number"
              name="year_built_min"
              placeholder="From"
              value={filters.year_built_min}
              onChange={handleInputChange}
              className={styles.input}
            />
            <span className={styles.separator}>—</span>
            <input
              type="number"
              name="year_built_max"
              placeholder="To"
              value={filters.year_built_max}
              onChange={handleInputChange}
              className={styles.input}
            />
          </div>
        </div>

        {/* Building Type */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Building type/material</h3>
          <div className={styles.checkboxGroup}>
            {buildingTypes.map((type) => (
              <label key={type.value} className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.building_type.includes(type.value)}
                  onChange={() =>
                    handleButtonToggle("building_type", type.value)
                  }
                  className={styles.checkbox}
                />
                <span>{type.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Children/Pets */}
        <div className={styles.filterGroup}>
          <h3 className={styles.groupTitle}>Children/Pets</h3>
          <p className={styles.filterNote}>
            Children/Pets — I filter only those listings where the ban is
            explicitly stated in the description text — it's unlikely you'll be
            able to negotiate with such landlords. But if the ban is only
            indicated in the listing parameters and there's nothing in the text,
            it's worth trying. In good apartments, pets and children are often
            prohibited by default, without serious consideration. If you don't
            want to communicate yourself, contact our concierge service — we do
            this professionally.
          </p>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={filters.children_allowed}
              onChange={() => handleCheckboxChange("children_allowed")}
              className={styles.checkbox}
            />
            <span>Without explicit ban on children</span>
          </label>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={filters.pets_allowed}
              onChange={() => handleCheckboxChange("pets_allowed")}
              className={styles.checkbox}
            />
            <span>Without explicit ban on pets</span>
          </label>
        </div>
      </div>

      {/* Sticky Footer with Apply Button */}
      <div className={styles.stickyFooter}>
        <button className={styles.applyButton} onClick={handleApplyFilters}>
          <span className={styles.applyButtonText}>Show result</span>
          <span className={styles.applyButtonSubtext}>
            {totalListings.toLocaleString()} apartments
          </span>
        </button>
      </div>
    </aside>
  );
};

export default NewFiltersSidebar;
