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
    <div className="bg-[#e0ecff] pt-[72px] pb-[40px] md:pb-[68px]">
      <div className="max-w-[1920px] mx-auto px-4 md:px-8 lg:px-12 xl:px-24 2xl:px-[312px]">
        {/* Title */}
        <h1 className="font-bold text-[32px] md:text-[48px] leading-[40px] md:leading-[56px] text-center text-gray-900 mt-[40px] md:mt-[94px] mb-[24px] md:mb-[34px]">
          Apartment search in Italy, 24/7
        </h1>

        {/* Subtitle */}
        <p className="font-medium text-[18px] md:text-[22px] leading-[28px] md:leading-[32px] text-center text-gray-600 mb-[40px] md:mb-[68px] max-w-[856px] mx-auto">
          AI-powered assistant that finds apartments for you and sends them straight to your WhatsApp.
        </p>

        {/* Manual Search Label */}
        <p className="font-medium text-[16px] md:text-[18px] leading-[28px] md:leading-[32px] text-blue-600 mb-[10px]">
          Prefer to search manually?
        </p>

        {/* Search Bar - Desktop - только для очень больших экранов (1280px+) */}
        <div className="hidden xl:flex bg-white h-[64px] rounded-[12px] items-center px-[24px] mb-[28px]">
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

        {/* Search Bar - Mobile and Tablet - для всех экранов меньше 1280px */}
        <div className="xl:hidden bg-white rounded-[12px] p-[24px] mb-[24px] flex flex-col gap-[24px]">
          <div className="flex flex-col gap-[12px]">
            {/* Row 1 */}
            <div className="grid grid-cols-3 h-[44px] md:h-[52px] items-center w-full gap-0">
              <div className="flex gap-[12px] items-center h-full border-r border-slate-300">
                <CityDropdown
                  value={searchParams.city}
                  onChange={(city) => setSearchParams({ ...searchParams, city })}
                />
              </div>
              <div className="flex gap-[12px] items-center justify-center h-full">
                <SimpleDropdown
                  value={searchParams.type}
                  options={["Rent", "Short term", "Long term"]}
                  onChange={(type) => setSearchParams({ ...searchParams, type })}
                />
              </div>
              <div className="flex gap-[12px] items-center justify-end h-full border-l border-slate-300">
                <SimpleDropdown
                  value={searchParams.propertyType}
                  options={["Property type", "Apartment", "House", "Studio"]}
                  onChange={(propertyType) =>
                    setSearchParams({ ...searchParams, propertyType })
                  }
                />
              </div>
            </div>

            {/* Horizontal divider */}
            <div className="w-full h-[1px] bg-slate-300" />

            {/* Row 2 */}
            <div className="grid grid-cols-3 h-[44px] md:h-[52px] items-center w-full gap-0">
              <div className="flex gap-[12px] items-center h-full border-r border-slate-300">
                <RoomsDropdown
                  value={searchParams.rooms}
                  onChange={(rooms) => setSearchParams({ ...searchParams, rooms })}
                />
              </div>
              <div className="flex gap-[12px] items-center justify-center h-full">
                <PriceDropdown
                  value={searchParams.price}
                  onChange={(price) => setSearchParams({ ...searchParams, price })}
                />
              </div>
              <div className="flex gap-[12px] items-center justify-end h-full border-l border-slate-300">
                <FiltersDropdown value={filters} onChange={setFilters} />
              </div>
            </div>
          </div>

          {/* Search Input */}
          <div className="flex gap-[10px] items-start w-full">
            <div className="flex-1 bg-white border border-gray-200 rounded-[8px] px-[16px] py-[10px] h-[44px] md:h-[52px] flex gap-[12px] items-center">
              <svg 
                className="w-5 h-5 text-gray-400 shrink-0"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Neighborhood, Metro"
                className="flex-1 bg-transparent font-normal text-[16px] text-gray-900 leading-[24px] outline-none placeholder:text-gray-400"
                value={searchParams.neighborhood}
                onChange={(e) =>
                  setSearchParams({ ...searchParams, neighborhood: e.target.value })
                }
              />
            </div>
          </div>
        </div>

        {/* Buttons */}
        <div className="flex flex-col md:flex-row items-center justify-end gap-[12px] md:gap-[12px]">
          <button
            onClick={handleExploreMap}
            className="w-full md:w-auto border border-slate-300 border-solid px-[24px] py-[8px] rounded-[8px] font-semibold text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors"
          >
            Explore on map
          </button>
          <button
            onClick={handleSearch}
            className="w-full md:w-auto bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewHero;
