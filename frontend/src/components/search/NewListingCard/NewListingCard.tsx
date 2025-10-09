import React, { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import { Listing } from "../../../types";
import heartIcon from "../../../designSvg/heart.svg";
import shareIcon from "../../../designSvg/share.svg";
import mapIcon from "../../../designSvg/map.svg";

interface NewListingCardProps {
  listing: Listing;
  onFavoriteToggle?: (id: string) => void;
  onShare?: (id: string) => void;
  onShowMap?: (id: string) => void;
}

const NewListingCard: React.FC<NewListingCardProps> = ({
  listing,
  onFavoriteToggle,
  onShare,
  onShowMap,
}) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isCopyToastVisible, setCopyToastVisible] = useState(false);
  const copyToastTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(
    null
  );
  const isBrowser = typeof window !== "undefined";

  const listingUrl = listing.url || listing.originalUrl || "";

  // ===== Обработка изображений =====
  const getImages = (): string[] => {
    if (listing.photos_urls && listing.photos_urls.length > 0) {
      return listing.photos_urls;
    }
    if (listing.imageUrls && listing.imageUrls.length > 0) {
      return listing.imageUrls;
    }
    return ["https://via.placeholder.com/306x200?text=No+Image"];
  };

  const images = getImages();
  const currentImage = images[currentImageIndex];

  // Обработка движения мыши для смены изображений
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const width = rect.width;
    const imageIndex = Math.floor((x / width) * images.length);
    setCurrentImageIndex(Math.min(imageIndex, images.length - 1));
  };

  const handleMouseLeave = () => {
    setCurrentImageIndex(0);
  };

  const openListing = () => {
    if (!listingUrl) {
      return;
    }

    window.open(listingUrl, "_blank", "noopener,noreferrer");
  };

  const handleCardKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openListing();
    }
  };

  const handleShareClick = async (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    event.stopPropagation();

    if (!listingUrl) {
      return;
    }

    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(listingUrl);
      } else {
        const textarea = document.createElement("textarea");
        textarea.value = listingUrl;
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
      }

      onShare?.(listing.id);
      setCopyToastVisible(true);

      if (copyToastTimeoutRef.current) {
        clearTimeout(copyToastTimeoutRef.current);
      }

      copyToastTimeoutRef.current = setTimeout(() => {
        setCopyToastVisible(false);
      }, 2000);
    } catch (error) {
      console.error("Failed to copy listing link", error);
    }
  };

  useEffect(() => {
    return () => {
      if (copyToastTimeoutRef.current) {
        clearTimeout(copyToastTimeoutRef.current);
      }
    };
  }, []);

  const handleFavoriteClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    onFavoriteToggle?.(listing.id);
  };

  const handleMapClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    onShowMap?.(listing.id);
  };

  // ===== Форматирование заголовка (комнаты, метраж, этаж) =====
  const getTitle = (): string => {
    const parts: string[] = [];

    // Количество комнат
    if (listing.property_type === "studio" || listing.num_rooms === 0) {
      parts.push("Studio");
    } else if (listing.num_rooms) {
      parts.push(`${listing.num_rooms}-room apt.`);
    }

    // Площадь
    const area = listing.area_sqm || listing.area;
    if (area) {
      parts.push(`${area} m²`);
    }

    // Этаж (формат: "5/8 floor" если есть общее количество этажей)
    if (listing.floor) {
      const floorMatch = listing.floor.match(/\d+/);
      if (floorMatch) {
        const currentFloor = floorMatch[0];
        // Если есть информация об общем количестве этажей
        if (listing.floor && typeof listing.floor === "string") {
          const totalFloorsMatch = listing.floor.match(/\/(\d+)/);
          if (totalFloorsMatch) {
            parts.push(`${currentFloor}/${totalFloorsMatch[1]} floor`);
          } else {
            parts.push(`${currentFloor} floor`);
          }
        } else {
          parts.push(`${currentFloor} floor`);
        }
      }
    }

    return parts.join(", ");
  };

  // ===== Форматирование адреса =====
  const getAddress = (): string => {
    // Используем address_text или составляем из частей
    if (listing.address_text) {
      return listing.address_text;
    }

    const parts: string[] = [];
    if (listing.address) parts.push(listing.address);
    if (listing.district) parts.push(listing.district);
    if (listing.city) parts.push(listing.city);

    return parts.join(", ") || "Address not available";
  };

  // ===== Форматирование цены =====
  const getPrice = (): string => {
    if (!listing.price) {
      return "Price not specified";
    }
    return `€ ${listing.price.toLocaleString("en-US")}`;
  };

  // ===== Получение комиссии агента =====
  const getCommission = (): string | null => {
    // Ищем информацию о комиссии в описании или features
    if (listing.commission) {
      return listing.commission;
    }

    // Ищем в features
    if (listing.features) {
      const commissionFeature = listing.features.find(
        (f) =>
          f.toLowerCase().includes("commission") ||
          f.toLowerCase().includes("no deposit") ||
          f.toLowerCase().includes("комиссия")
      );
      if (commissionFeature) {
        return commissionFeature;
      }
    }

    // Ищем в описании
    if (listing.description) {
      const commissionMatch = listing.description.match(
        /commission[:\s]+([^,.\n]+)/i
      );
      if (commissionMatch) {
        return commissionMatch[1].trim();
      }
    }

    return null;
  };

  // ===== Получение иконки транспорта =====
  const getTransportIcon = (
    distance: string
  ): { icon: JSX.Element; type: "walk" | "car" } => {
    // Если в строке есть "min" - извлекаем число минут
    const timeMatch = distance.match(/(\d+)\s*min/i);
    if (timeMatch) {
      const minutes = parseInt(timeMatch[1]);
      // До 15 минут - пешком, больше - на авто
      if (minutes <= 15) {
        return {
          type: "walk",
          icon: (
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M8 3C8.55228 3 9 2.55228 9 2C9 1.44772 8.55228 1 8 1C7.44772 1 7 1.44772 7 2C7 2.55228 7.44772 3 8 3Z"
                fill="#6B7280"
              />
              <path
                d="M6 5L8 4L10 5L9 9L10 15H8.5L8 11L7 15H5.5L6.5 9L6 5Z"
                fill="#6B7280"
              />
            </svg>
          ),
        };
      }
    }

    return {
      type: "car",
      icon: (
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M3 9L4 5H12L13 9M3 9V13H4V14H5V13H11V14H12V13H13V9M3 9H13M5 11H5.01M11 11H11.01"
            stroke="#6B7280"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ),
    };
  };

  // ===== Получение источника =====
  const getSourceName = (): string => {
    const source = listing.source_site || listing.source || "";
    const sourceMap: { [key: string]: string } = {
      idealista: "Idealista",
      immobiliare: "Immobiliare",
      subito: "Subito",
    };
    return sourceMap[source.toLowerCase()] || source;
  };

  const title = getTitle();
  const address = getAddress();
  const price = getPrice();
  const commission = getCommission();
  const sourceName = getSourceName();

  return (
    <div
      className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] w-full overflow-hidden relative cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
      onClick={openListing}
      onKeyDown={handleCardKeyDown}
      role="link"
      tabIndex={listingUrl ? 0 : -1}
    >
      {/* Image container with slider */}
      <div
        className="relative h-[200px] w-full cursor-pointer"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        <img
          src={currentImage}
          alt={title}
          className="w-full h-full object-cover"
        />

        {/* Image indicators (dots) */}
        {images.length > 1 && (
          <div className="absolute bottom-[12px] left-0 right-0 flex justify-center gap-[6px]">
            {images.map((_, index) => (
              <div
                key={index}
                className={`h-[8px] rounded-full transition-all flex-shrink-0 ${
                  index === currentImageIndex
                    ? "bg-blue-600 w-[24px]"
                    : "bg-white/70 w-[8px]"
                }`}
              />
            ))}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-[16px]">
        {/* Title: комнаты, метраж, этаж */}
        <h3 className="font-semibold text-[18px] leading-[24px] text-gray-900 mb-[8px] truncate">
          {title}
        </h3>

        {/* Address */}
        <p className="font-normal text-[14px] leading-[20px] text-gray-600 mb-[12px] truncate">
          {address}
        </p>

        {/* Price */}
        <p className="font-bold text-[24px] leading-[32px] text-gray-900 mb-[8px]">
          {price}
        </p>

        {/* Commission (if available) */}
        {commission && (
          <p className="font-normal text-[14px] leading-[20px] text-gray-600 mb-[12px]">
            Commission: {commission}
          </p>
        )}

        {/* Metro */}
        <div className="mb-[12px] space-y-[6px]">
          {listing.metroStations && listing.metroStations.length > 0 ? (
            listing.metroStations.slice(0, 2).map((station, index) => {
              const transport = getTransportIcon(station.distance);
              return (
                <div key={index} className="flex items-center gap-[8px]">
                  <div className="flex items-center gap-[6px] flex-1">
                    {transport.icon}
                    <p className="font-normal text-[14px] leading-[20px] text-gray-900 truncate">
                      {station.name}
                    </p>
                  </div>
                  <p className="font-normal text-[14px] leading-[20px] text-gray-600">
                    {station.distance}
                  </p>
                </div>
              );
            })
          ) : (
            // Моковые данные для проверки верстки
            <div className="flex items-center gap-[8px]">
              <div className="flex items-center gap-[6px] flex-1">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M8 3C8.55228 3 9 2.55228 9 2C9 1.44772 8.55228 1 8 1C7.44772 1 7 1.44772 7 2C7 2.55228 7.44772 3 8 3Z"
                    fill="#6B7280"
                  />
                  <path
                    d="M6 5L8 4L10 5L9 9L10 15H8.5L8 11L7 15H5.5L6.5 9L6 5Z"
                    fill="#6B7280"
                  />
                </svg>
                <p className="font-normal text-[14px] leading-[20px] text-gray-900 truncate">
                  Nearest metro
                </p>
              </div>
              <p className="font-normal text-[14px] leading-[20px] text-gray-600">
                —
              </p>
            </div>
          )}
        </div>

        {/* Source */}
        <p className="font-normal text-[12px] leading-[16px] text-gray-500 mb-[16px]">
          Source: {sourceName}
        </p>

        {/* Action buttons */}
        <div className="flex items-center justify-between">
          {/* On the map button */}
          <button
            type="button"
            onClick={handleMapClick}
            className="bg-blue-600 px-[16px] py-[8px] rounded-[8px] flex items-center gap-[8px] hover:bg-blue-700 transition-colors"
          >
            <img src={mapIcon} alt="Map" className="w-[20px] h-[20px]" />
            <span className="font-medium text-[14px] text-white">
              On the map
            </span>
          </button>

          {/* Icon buttons */}
          <div className="flex items-center gap-[12px]">
            <button
              type="button"
              onClick={handleFavoriteClick}
              className="w-[20px] h-[20px] hover:opacity-70 transition-opacity"
              aria-label="Добавить в избранное"
            >
              <img
                src={heartIcon}
                alt="Add to favorites"
                className="w-full h-full"
              />
            </button>

            <button
              type="button"
              onClick={handleShareClick}
              className="w-[20px] h-[20px] hover:opacity-70 transition-opacity"
              aria-label="Поделиться объявлением"
            >
              <img
                src={shareIcon}
                alt="Share listing"
                className="w-full h-full"
              />
            </button>
          </div>
        </div>
      </div>
      {isCopyToastVisible &&
        isBrowser &&
        createPortal(
          <div
            className="fixed bottom-[24px] right-[24px] bg-blue-600/80 text-white px-[16px] py-[10px] rounded-[12px] shadow-[0_12px_24px_rgba(37,99,235,0.28)] text-[14px] font-medium"
            role="status"
            aria-live="polite"
          >
            Link copied to clipboard
          </div>,
          document.body
        )}
    </div>
  );
};

export default NewListingCard;
