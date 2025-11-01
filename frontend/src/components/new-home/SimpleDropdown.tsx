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

  const handleSelect = (option: string) => {
    onChange(option);
    handleClose();
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-[8px] lg:gap-[12px] lg:px-[16px] lg:py-[10px] cursor-pointer hover:bg-gray-50 lg:rounded-[8px] transition-colors w-full"
      >
        <span className="font-normal text-[16px] text-gray-900 leading-[20px] lg:leading-[24px] lg:whitespace-nowrap text-right flex-1">
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
          className="fixed left-0 right-0 lg:top-1/2 lg:left-1/2 lg:-translate-x-1/2 lg:-translate-y-1/2 lg:right-auto bg-white w-full lg:w-[200px] rounded-t-[24px] lg:rounded-[12px] shadow-[0px_-4px_12px_0px_rgba(0,0,0,0.08)] lg:shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] z-50 py-[12px] max-h-[80vh] overflow-y-auto transition-all duration-300 ease-out"
          style={{ 
            bottom: '0',
            transform: isAnimating ? 'translateY(0)' : 'translateY(100%)'
          }}
        >
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
