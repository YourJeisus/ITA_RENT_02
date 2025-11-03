import React, { useState, useRef, useEffect } from "react";

interface CityDropdownProps {
  value: string;
  onChange: (city: string) => void;
}

const cities = [
  "Rome",
  "Milan",
  "Naples",
  "Turin",
  "Palermo",
  "Genoa",
  "Bologna",
  "Florence",
];

const CityDropdown: React.FC<CityDropdownProps> = ({ value, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  const filteredCities = cities.filter((city) =>
    city.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSearchQuery("");
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleCitySelect = (city: string) => {
    onChange(city);
    setIsOpen(false);
    setSearchQuery("");
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-[12px] px-[16px] py-[10px] cursor-pointer hover:bg-gray-50 rounded-[8px] transition-colors"
      >
        <span className="font-normal text-[16px] text-gray-900 leading-[24px]">
          {value}
        </span>
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={`transition-transform ${isOpen ? "rotate-180" : ""}`}
        >
          <path
            d="M4 6L8 10L12 6"
            stroke="#111827"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-[60px] left-0 bg-white w-[233px] rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] z-50">
          {/* Search Input */}
          <div className="p-[24px] pb-0">
            <div className="flex items-center gap-[12px] px-[16px] py-[10px] border border-gray-200 rounded-[8px] bg-white">
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M9 17C13.4183 17 17 13.4183 17 9C17 4.58172 13.4183 1 9 1C4.58172 1 1 4.58172 1 9C1 13.4183 4.58172 17 9 17Z"
                  stroke="#9CA3AF"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M19 19L14.65 14.65"
                  stroke="#9CA3AF"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <input
                type="text"
                placeholder="Search City"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="font-normal text-[16px] leading-[24px] outline-none flex-1 placeholder:text-gray-400"
                autoFocus
              />
            </div>
          </div>

          {/* Separator */}
          <div className="h-[1px] bg-gray-200 mt-[24px]" />

          {/* Cities List */}
          <div className="px-[24px] py-[24px] flex flex-col gap-[12px] max-h-[240px] overflow-y-auto">
            {filteredCities.map((city) => (
              <button
                key={city}
                onClick={() => handleCitySelect(city)}
                className="flex items-center gap-[8px] cursor-pointer hover:opacity-80 transition-opacity"
              >
                {/* Radio Button */}
                <div
                  className={`w-[20px] h-[20px] rounded-full border-2 flex items-center justify-center ${
                    value === city ? "border-blue-600" : "border-gray-300"
                  }`}
                >
                  {value === city && (
                    <div className="w-[10px] h-[10px] rounded-full bg-blue-600" />
                  )}
                </div>
                <span
                  className={`font-normal text-[16px] leading-[24px] ${
                    value === city ? "text-gray-900" : "text-gray-400"
                  }`}
                >
                  {city}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CityDropdown;
