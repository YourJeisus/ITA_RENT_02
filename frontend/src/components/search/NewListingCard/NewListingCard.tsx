import React, { useState } from "react";
import { Listing } from "../../../types";

interface NewListingCardProps {
  listing: Listing;
  onFavoriteToggle?: (id: string) => void;
  onFlag?: (id: string) => void;
  onShare?: (id: string) => void;
  onShowMap?: (id: string) => void;
}

const NewListingCard: React.FC<NewListingCardProps> = ({
  listing,
  onFavoriteToggle,
  onFlag,
  onShare,
  onShowMap,
}) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

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
        if (listing.floor && typeof listing.floor === 'string') {
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
    return `€ ${listing.price.toLocaleString('en-US')}`;
  };

  // ===== Получение комиссии агента =====
  const getCommission = (): string | null => {
    // Ищем информацию о комиссии в описании или features
    if (listing.commission) {
      return listing.commission;
    }
    
    // Ищем в features
    if (listing.features) {
      const commissionFeature = listing.features.find(f => 
        f.toLowerCase().includes('commission') || 
        f.toLowerCase().includes('no deposit') ||
        f.toLowerCase().includes('комиссия')
      );
      if (commissionFeature) {
        return commissionFeature;
      }
    }
    
    // Ищем в описании
    if (listing.description) {
      const commissionMatch = listing.description.match(/commission[:\s]+([^,.\n]+)/i);
      if (commissionMatch) {
        return commissionMatch[1].trim();
      }
    }
    
    return null;
  };

  // ===== Получение иконки транспорта =====
  const getTransportIcon = (distance: string): { icon: JSX.Element; type: 'walk' | 'car' } => {
    // Если в строке есть "min" - извлекаем число минут
    const timeMatch = distance.match(/(\d+)\s*min/i);
    if (timeMatch) {
      const minutes = parseInt(timeMatch[1]);
      // До 15 минут - пешком, больше - на авто
      if (minutes <= 15) {
        return {
          type: 'walk',
          icon: (
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 3C8.55228 3 9 2.55228 9 2C9 1.44772 8.55228 1 8 1C7.44772 1 7 1.44772 7 2C7 2.55228 7.44772 3 8 3Z" fill="#6B7280"/>
              <path d="M6 5L8 4L10 5L9 9L10 15H8.5L8 11L7 15H5.5L6.5 9L6 5Z" fill="#6B7280"/>
            </svg>
          )
        };
      }
    }
    
    return {
      type: 'car',
      icon: (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 9L4 5H12L13 9M3 9V13H4V14H5V13H11V14H12V13H13V9M3 9H13M5 11H5.01M11 11H11.01" stroke="#6B7280" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      )
    };
  };

  // ===== Получение источника =====
  const getSourceName = (): string => {
    const source = listing.source_site || listing.source || '';
    const sourceMap: { [key: string]: string } = {
      'idealista': 'Idealista',
      'immobiliare': 'Immobiliare',
      'subito': 'Subito',
    };
    return sourceMap[source.toLowerCase()] || source;
  };

  const title = getTitle();
  const address = getAddress();
  const price = getPrice();
  const commission = getCommission();
  const sourceName = getSourceName();

  return (
    <div className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] w-full overflow-hidden">
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
                className={`w-[8px] h-[8px] rounded-full transition-all ${
                  index === currentImageIndex 
                    ? 'bg-blue-600 w-[24px]' 
                    : 'bg-white/70'
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
        {listing.metroStations && listing.metroStations.length > 0 && (
          <div className="mb-[12px] space-y-[6px]">
            {listing.metroStations.slice(0, 2).map((station, index) => {
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
            })}
          </div>
        )}

        {/* Source */}
        <p className="font-normal text-[12px] leading-[16px] text-gray-500 mb-[16px]">
          Source: {sourceName}
        </p>

        {/* Action buttons */}
        <div className="flex items-center justify-between">
          {/* On the map button */}
          <button
            onClick={() => onShowMap?.(listing.id)}
            className="bg-blue-600 px-[16px] py-[8px] rounded-[8px] flex items-center gap-[8px] hover:bg-blue-700 transition-colors"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M10 11C11.6569 11 13 9.65685 13 8C13 6.34315 11.6569 5 10 5C8.34315 5 7 6.34315 7 8C7 9.65685 8.34315 11 10 11Z"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M10 19C13 16 17 12.4183 17 8C17 4.13401 13.866 1 10 1C6.13401 1 3 4.13401 3 8C3 12.4183 7 16 10 19Z"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span className="font-medium text-[14px] text-white">On the map</span>
          </button>

          {/* Icon buttons */}
          <div className="flex items-center gap-[12px]">
            <button
              onClick={() => onFavoriteToggle?.(listing.id)}
              className="w-[20px] h-[20px] hover:opacity-70 transition-opacity"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M10 18L8.55 16.7C3.4 12.16 0 9.08 0 5.5C0 2.42 2.42 0 5.5 0C7.24 0 8.91 0.81 10 2.09C11.09 0.81 12.76 0 14.5 0C17.58 0 20 2.42 20 5.5C20 9.08 16.6 12.16 11.45 16.7L10 18Z"
                  fill="#9CA3AF"
                />
              </svg>
            </button>

            <button
              onClick={() => onFlag?.(listing.id)}
              className="w-[20px] h-[20px] hover:opacity-70 transition-opacity"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 1V19L18 10L3 1Z" fill="#9CA3AF" />
              </svg>
            </button>

            <button
              onClick={() => onShare?.(listing.id)}
              className="w-[20px] h-[20px] hover:opacity-70 transition-opacity"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="15" cy="5" r="3" fill="#9CA3AF" />
                <circle cx="5" cy="10" r="3" fill="#9CA3AF" />
                <circle cx="15" cy="15" r="3" fill="#9CA3AF" />
                <path d="M7.5 11L12.5 14M12.5 6L7.5 9" stroke="#9CA3AF" strokeWidth="2" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewListingCard;
