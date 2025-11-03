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
  const [isAnimating, setIsAnimating] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  const filteredCities = cities.filter((city) =>
    city.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Trigger animation
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => setIsAnimating(true), 10);
    } else {
      setIsAnimating(false);
    }
  }, [isOpen]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        handleClose();
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  const handleClose = () => {
    setIsAnimating(false);
    setTimeout(() => {
      setIsOpen(false);
      setSearchQuery("");
    }, 300);
  };

  const handleCitySelect = (city: string) => {
    onChange(city);
    handleClose();
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-[8px] lg:gap-[12px] lg:px-[16px] lg:py-[10px] cursor-pointer hover:bg-gray-50 lg:rounded-[8px] transition-colors w-full"
      >
        <span className="font-normal text-[16px] text-gray-900 leading-[20px] lg:leading-[24px] lg:whitespace-nowrap flex-1 text-left">
          {value}
        </span>
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={`transition-transform shrink-0 ${isOpen ? "rotate-180" : ""}`}
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

      {/* Backdrop - Mobile only */}
      {isOpen && (
        <div 
          className="lg:hidden fixed inset-0 z-40 transition-all duration-300"
          style={{ backgroundColor: isAnimating ? 'rgba(0, 0, 0, 0.4)' : 'rgba(0, 0, 0, 0)' }}
          onClick={handleClose}
        />
      )}

      {/* Dropdown Menu */}
      {isOpen && (
        <div 
          className="fixed left-0 right-0 lg:top-1/2 lg:left-1/2 lg:-translate-x-1/2 lg:-translate-y-1/2 lg:right-auto bg-white w-full lg:w-[233px] rounded-t-[24px] lg:rounded-[12px] shadow-[0px_-4px_12px_0px_rgba(0,0,0,0.08)] lg:shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] z-50 max-h-[80vh] overflow-y-auto transition-all duration-300 ease-out"
          style={{ 
            bottom: '0',
            transform: isAnimating ? 'translateY(0)' : 'translateY(100%)'
          }}
        >
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
