import React, { useState, useRef, useEffect } from "react";

interface FiltersDropdownProps {
  value: string[];
  onChange: (filters: string[]) => void;
}

const filterOptions = [
  "Furnished",
  "Elevator",
  "Balcony",
  "Terrace",
  "Air conditioning",
  "Heating",
  "Pet-friendly",
  "Parking",
  "Garage",
  "Dishwasher",
  "Washing machine",
  "Available now",
  "Top floor",
  "Ground floor",
  "Private landlord",
  "New building",
];

const FiltersDropdown: React.FC<FiltersDropdownProps> = ({
  value,
  onChange,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

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
    }, 300);
  };

  const toggleFilter = (filter: string) => {
    if (value.includes(filter)) {
      onChange(value.filter((f) => f !== filter));
    } else {
      onChange([...value, filter]);
    }
  };

  const displayValue =
    value.length > 0 ? `Filters (${value.length})` : "Filters";

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-[8px] lg:gap-[12px] lg:px-[16px] lg:py-[10px] cursor-pointer hover:bg-gray-50 lg:rounded-[8px] transition-colors w-full"
      >
        <span className="font-normal text-[16px] text-gray-900 leading-[20px] lg:leading-[24px] lg:whitespace-nowrap flex-1 text-right">
          {displayValue}
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
          className="fixed left-0 right-0 lg:top-1/2 lg:left-1/2 lg:-translate-x-1/2 lg:-translate-y-1/2 lg:right-auto bg-white w-full lg:w-[439px] rounded-t-[24px] lg:rounded-[12px] shadow-[0px_-4px_12px_0px_rgba(0,0,0,0.08)] lg:shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] z-50 p-[24px] max-h-[80vh] overflow-y-auto transition-all duration-300 ease-out"
          style={{ 
            bottom: '0',
            transform: isAnimating ? 'translateY(0)' : 'translateY(100%)'
          }}
        >
          <div className="flex flex-wrap gap-[12px]">
            {filterOptions.map((filter) => (
              <button
                key={filter}
                onClick={() => toggleFilter(filter)}
                className={`px-[16px] py-[10px] rounded-[18px] font-medium text-[14px] leading-[20px] transition-colors ${
                  value.includes(filter)
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {filter}
              </button>
            ))}
          </div>

          {/* Clear All Button */}
          {value.length > 0 && (
            <div className="mt-[16px] pt-[16px] border-t border-gray-200">
              <button
                onClick={() => onChange([])}
                className="w-full px-[16px] py-[8px] rounded-[8px] font-medium text-[14px] text-gray-700 hover:bg-gray-100 transition-colors"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FiltersDropdown;
