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
    <div className="bg-[#e0ecff] pt-[72px] pb-[80px] md:h-auto h-[900px] overflow-clip">
      <div className="max-w-[1920px] mx-auto px-[40px] md:px-[312px] flex flex-col gap-[40px] items-center justify-center h-full">
        {/* Title and Subtitle */}
        <div className="flex flex-col gap-[24px] items-center text-center w-full shrink-0">
          <h1 className="font-bold text-[48px] leading-[56px] text-gray-900 w-full">
            Apartment search in Italy, 24/7
          </h1>
          <p className="font-medium text-[22px] leading-[32px] text-gray-600 w-full max-w-[856px]">
            AI-powered assistant that finds apartments for you and sends them straight to your WhatsApp.
          </p>
        </div>

        {/* Manual Search Section */}
        <div className="flex flex-col gap-[12px] items-start w-full">
          <p className="font-medium text-[18px] leading-[32px] text-blue-600 w-full">
            Prefer to search manually?
          </p>

          {/* Search Bar - Desktop */}
          <div className="hidden md:flex bg-white h-[64px] rounded-[12px] items-center px-[24px] mb-[28px] w-full">
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

          {/* Search Bar - Mobile */}
        <div className="md:hidden bg-white rounded-[12px] p-[24px] relative flex flex-col gap-[24px] items-center w-full">
          {/* First Row */}
          <div className="flex h-[44px] items-center justify-between w-full">
            <div className="basis-0 border-[0px_1px_0px_0px] border-slate-300 border-solid flex gap-[12px] grow h-full items-center min-h-px min-w-px relative shrink-0">
              <CityDropdown
                value={searchParams.city}
                onChange={(city) => setSearchParams({ ...searchParams, city })}
              />
            </div>
            <div className="basis-0 flex gap-[12px] grow h-full items-center justify-center min-h-px min-w-px relative shrink-0">
              <SimpleDropdown
                value={searchParams.type}
                options={["Short term rent", "Long term rent"]}
                onChange={(type) => setSearchParams({ ...searchParams, type })}
              />
            </div>
            <div className="basis-0 border-[0px_0px_0px_1px] border-slate-300 border-solid flex gap-[12px] grow h-full items-center justify-end min-h-px min-w-px relative shrink-0">
              <SimpleDropdown
                value={searchParams.propertyType}
                options={["Apartment", "House", "Studio", "Room", "Villa", "Loft"]}
                onChange={(propertyType) =>
                  setSearchParams({ ...searchParams, propertyType })
                }
              />
            </div>
          </div>

          {/* Second Row */}
          <div className="flex h-[44px] items-center justify-between w-full">
            <div className="basis-0 border-[0px_1px_0px_0px] border-slate-300 border-solid flex gap-[12px] grow h-full items-center min-h-px min-w-px relative shrink-0">
              <RoomsDropdown
                value={searchParams.rooms}
                onChange={(rooms) => setSearchParams({ ...searchParams, rooms })}
              />
            </div>
            <div className="basis-0 flex gap-[12px] grow h-full items-center justify-center min-h-px min-w-px relative shrink-0">
              <PriceDropdown
                value={searchParams.price}
                onChange={(price) => setSearchParams({ ...searchParams, price })}
              />
            </div>
            <div className="basis-0 border-[0px_0px_0px_1px] border-slate-300 border-solid flex gap-[12px] grow h-full items-center justify-end min-h-px min-w-px relative shrink-0">
              <FiltersDropdown value={filters} onChange={setFilters} />
            </div>
          </div>

          {/* Search Input */}
          <div className="flex gap-[10px] items-start w-full">
            <div className="basis-0 bg-white border border-gray-200 border-solid flex gap-[12px] grow h-[44px] items-center min-h-px min-w-px px-[16px] py-[10px] relative rounded-[8px] shrink-0">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" className="relative shrink-0 size-[20px]">
                <path d="M9 17C13.4183 17 17 13.4183 17 9C17 4.58172 13.4183 1 9 1C4.58172 1 1 4.58172 1 9C1 13.4183 4.58172 17 9 17Z" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M19 19L14.65 14.65" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <input
                type="text"
                placeholder="Neighborhood, Metro"
                className="font-normal text-[16px] leading-[24px] text-gray-400 text-nowrap whitespace-pre outline-none bg-transparent flex-1"
                value={searchParams.neighborhood}
                onChange={(e) =>
                  setSearchParams({ ...searchParams, neighborhood: e.target.value })
                }
              />
            </div>
          </div>

          {/* Horizontal line separator */}
          <div className="absolute h-0 left-[24px] top-[80px] w-full max-w-[512px]">
            <div className="absolute bottom-0 left-0 right-0 top-[-1px] border-t border-slate-300"></div>
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-[40px] items-start w-full md:justify-end md:gap-[12px]">
          <button
            onClick={handleExploreMap}
            className="basis-0 border border-slate-300 border-solid flex gap-[10px] grow h-[44px] items-center justify-center min-h-px min-w-px px-[24px] py-[8px] relative rounded-[8px] shrink-0 md:flex-none md:h-auto"
          >
            <p className="font-semibold text-[16px] leading-[24px] text-gray-900 text-nowrap whitespace-pre">
              Explore on map
            </p>
          </button>
          <button
            onClick={handleSearch}
            className="basis-0 bg-blue-600 flex gap-[8px] grow h-[44px] items-center justify-center min-h-px min-w-px px-[24px] py-[10px] relative rounded-[8px] shrink-0 md:flex-none md:h-auto"
          >
            <p className="font-semibold text-[16px] leading-[24px] text-white text-nowrap whitespace-pre">
              Search
            </p>
          </button>
        </div>
        </div>
      </div>
    </div>
  );
};

export default NewHero;
