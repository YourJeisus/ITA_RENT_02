import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import CityDropdown from "./CityDropdown";
import SimpleDropdown from "./SimpleDropdown";
import RoomsDropdown from "./RoomsDropdown";
import PriceDropdown from "./PriceDropdown";
import FiltersDropdown from "./FiltersDropdown";

const NewHero: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useState({
    city: "City",
    type: "Rent",
    propertyType: "Property type",
    rooms: "Rooms",
    price: "Price",
    neighborhood: "",
  });
  const [filters, setFilters] = useState<string[]>([]);

  const mapFiltersToUrlParams = () => {
    const params = new URLSearchParams();

    // City
    if (searchParams.city !== "City") {
      params.append("city", searchParams.city.toLowerCase());
    }

    // Property Type
    if (searchParams.propertyType !== "Property type") {
      const propertyTypeMap: { [key: string]: string } = {
        Apartment: "apartment",
        House: "house",
        Studio: "studio",
        Room: "room",
        Villa: "house",
        Loft: "apartment",
      };
      const mappedType = propertyTypeMap[searchParams.propertyType];
      if (mappedType) {
        params.append("property_type", mappedType);
      }
    }

    // Rooms
    if (searchParams.rooms !== "Rooms") {
      if (searchParams.rooms === "Studio") {
        params.append("property_type", "studio");
      } else if (searchParams.rooms === "5+") {
        params.append("rooms", "5");
        params.append("rooms", "6");
        params.append("rooms", "7");
      } else {
        params.append("rooms", searchParams.rooms);
      }
    }

    // Price
    if (searchParams.price !== "Price") {
      const priceMatch = searchParams.price.match(/€(\d+)\s*-\s*€(\d+|∞)/);
      if (priceMatch) {
        if (priceMatch[1] !== "0") {
          params.append("price_min", priceMatch[1]);
        }
        if (priceMatch[2] !== "∞") {
          params.append("price_max", priceMatch[2]);
        }
      } else {
        // Quick select format "Up to €1500"
        const quickMatch = searchParams.price.match(/Up to €(\d+)/);
        if (quickMatch) {
          params.append("price_max", quickMatch[1]);
        }
      }
    }

    // Filters - пока не добавляем, так как API не поддерживает большинство из них
    // В будущем можно добавить поддержку этих фильтров

    return params.toString();
  };

  const handleSearch = () => {
    const urlParams = mapFiltersToUrlParams();
    const searchUrl = `/search${urlParams ? `?${urlParams}` : ""}`;
    window.open(searchUrl, "_blank");
  };

  const handleExploreMap = () => {
    const urlParams = mapFiltersToUrlParams();
    const mapUrl = `/map${urlParams ? `?${urlParams}` : ""}`;
    window.open(mapUrl, "_blank");
  };

  return (
    <div className="bg-[#e0ecff] pt-[72px] pb-[68px]">
      <div className="max-w-[1920px] mx-auto px-[312px]">
        {/* Title */}
        <h1 className="font-bold text-[48px] leading-[56px] text-center text-gray-900 mt-[94px] mb-[34px]">
          Apartment search in Italy, 24/7
        </h1>

        {/* Subtitle */}
        <p className="font-medium text-[22px] leading-[32px] text-center text-gray-600 mb-[68px] max-w-[856px] mx-auto">
          AI-powered assistant that finds apartments for you and sends them
          straight
          <br />
          to your WhatsApp.
        </p>

        {/* Manual Search Label */}
        <p className="font-medium text-[18px] leading-[32px] text-blue-600 mb-[10px]">
          Prefer to search manually?
        </p>

        {/* Search Bar */}
        <div className="bg-white h-[64px] rounded-[12px] flex items-center px-[24px] mb-[28px]">
          {/* City */}
          <CityDropdown
            value={searchParams.city}
            onChange={(city) => setSearchParams({ ...searchParams, city })}
          />

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Rent */}
          <SimpleDropdown
            value={searchParams.type}
            options={["Short term rent", "Long term rent"]}
            onChange={(type) => setSearchParams({ ...searchParams, type })}
          />

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Property type */}
          <SimpleDropdown
            value={searchParams.propertyType}
            options={["Apartment", "House", "Studio", "Room", "Villa", "Loft"]}
            onChange={(propertyType) =>
              setSearchParams({ ...searchParams, propertyType })
            }
          />

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Rooms */}
          <RoomsDropdown
            value={searchParams.rooms}
            onChange={(rooms) => setSearchParams({ ...searchParams, rooms })}
          />

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Price */}
          <PriceDropdown
            value={searchParams.price}
            onChange={(price) => setSearchParams({ ...searchParams, price })}
          />

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Filters */}
          <FiltersDropdown value={filters} onChange={setFilters} />

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Neighborhood Input */}
          <input
            type="text"
            placeholder="Neighborhood, Metro"
            className="flex-1 px-[16px] py-[10px] bg-white rounded-[8px] font-normal text-[16px] text-gray-900 leading-[24px] outline-none placeholder:text-gray-400"
            value={searchParams.neighborhood}
            onChange={(e) =>
              setSearchParams({ ...searchParams, neighborhood: e.target.value })
            }
          />
        </div>

        {/* Buttons */}
        <div className="flex items-center justify-end gap-[12px]">
          <button
            onClick={handleExploreMap}
            className="border border-slate-300 border-solid px-[24px] py-[8px] rounded-[8px] font-semibold text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors"
          >
            Explore on map
          </button>
          <button
            onClick={handleSearch}
            className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewHero;
