import React, { useState, useRef, useEffect } from "react";

interface PriceDropdownProps {
  value: string;
  onChange: (price: string) => void;
}

const PriceDropdown: React.FC<PriceDropdownProps> = ({ value, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleApply = () => {
    if (minPrice || maxPrice) {
      const priceRange = `€${minPrice || "0"} - €${maxPrice || "∞"}`;
      onChange(priceRange);
      setIsOpen(false);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-[12px] cursor-pointer hover:opacity-80 transition-opacity w-full justify-center"
      >
        <span className="font-normal text-[16px] text-gray-900 leading-[24px] text-nowrap whitespace-pre">
          {value}
        </span>
        <div className="relative shrink-0 size-[16px]">
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
        </div>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-[60px] left-0 bg-white w-[280px] rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] z-50 p-[24px]">
          <div className="mb-[16px]">
            <p className="font-medium text-[14px] text-gray-900 mb-[8px]">
              Price Range (€/month)
            </p>
            <div className="flex gap-[12px] items-center">
              <input
                type="number"
                placeholder="Min"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
                className="w-full px-[12px] py-[8px] border border-gray-200 rounded-[8px] font-normal text-[14px] outline-none focus:border-blue-600"
              />
              <span className="text-gray-400">—</span>
              <input
                type="number"
                placeholder="Max"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                className="w-full px-[12px] py-[8px] border border-gray-200 rounded-[8px] font-normal text-[14px] outline-none focus:border-blue-600"
              />
            </div>
          </div>

          {/* Quick Options */}
          <div className="mb-[16px]">
            <p className="font-medium text-[14px] text-gray-900 mb-[8px]">
              Quick select
            </p>
            <div className="flex flex-wrap gap-[8px]">
              {["500", "1000", "1500", "2000", "2500"].map((price) => (
                <button
                  key={price}
                  onClick={() => {
                    onChange(`Up to €${price}`);
                    setIsOpen(false);
                  }}
                  className="px-[12px] py-[6px] border border-gray-200 rounded-[8px] font-normal text-[14px] text-gray-700 hover:bg-blue-50 hover:border-blue-600 transition-colors"
                >
                  €{price}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleApply}
            className="w-full bg-blue-600 px-[16px] py-[8px] rounded-[8px] font-semibold text-[14px] text-white hover:bg-blue-700 transition-colors"
          >
            Apply
          </button>
        </div>
      )}
    </div>
  );
};

export default PriceDropdown;
