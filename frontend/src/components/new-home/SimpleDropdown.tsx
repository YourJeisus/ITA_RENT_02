import React, { useState, useRef, useEffect } from "react";

interface SimpleDropdownProps {
  value: string;
  options: string[];
  onChange: (value: string) => void;
  placeholder?: string;
}

const SimpleDropdown: React.FC<SimpleDropdownProps> = ({
  value,
  options,
  onChange,
  placeholder = "Select",
}) => {
  const [isOpen, setIsOpen] = useState(false);
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

  const handleSelect = (option: string) => {
    onChange(option);
    setIsOpen(false);
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
        <div className="absolute top-[60px] left-0 bg-white w-[200px] rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] z-50 py-[12px]">
          <div className="flex flex-col gap-[4px]">
            {options.map((option) => (
              <button
                key={option}
                onClick={() => handleSelect(option)}
                className={`flex items-center gap-[8px] px-[24px] py-[10px] cursor-pointer hover:bg-gray-50 transition-colors ${
                  value === option ? "bg-blue-50" : ""
                }`}
              >
                {/* Radio Button */}
                <div
                  className={`w-[20px] h-[20px] rounded-full border-2 flex items-center justify-center ${
                    value === option ? "border-blue-600" : "border-gray-300"
                  }`}
                >
                  {value === option && (
                    <div className="w-[10px] h-[10px] rounded-full bg-blue-600" />
                  )}
                </div>
                <span
                  className={`font-normal text-[16px] leading-[24px] ${
                    value === option ? "text-gray-900" : "text-gray-400"
                  }`}
                >
                  {option}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SimpleDropdown;
