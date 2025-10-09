import React from "react";
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
  // ===== Обработка изображений =====
  const getImageUrl = (): string => {
    if (listing.photos_urls && listing.photos_urls.length > 0) {
      return listing.photos_urls[0];
    }
    if (listing.imageUrls && listing.imageUrls.length > 0) {
      return listing.imageUrls[0];
    }
    return "https://via.placeholder.com/306x200?text=No+Image";
  };

  // ===== Форматирование заголовка =====
  const getTitle = (): string => {
    const parts: string[] = [];
    
    // Проверка на студию
    if (listing.property_type === "studio" || listing.num_rooms === 0) {
      parts.push("Studio");
    } else if (listing.num_rooms) {
      parts.push(`${listing.num_rooms}-room`);
    }
    
    // Тип недвижимости (если не студия)
    if (listing.property_type && listing.property_type !== "studio") {
      parts.push(listing.property_type);
    }
    
    // Площадь
    const area = listing.area_sqm || listing.area;
    if (area) {
      parts.push(`${area} m²`);
    }
    
    // Этажи (если есть и это дом/вилла)
    if (listing.floor && (listing.property_type === "house" || listing.property_type === "villa")) {
      const floorMatch = listing.floor.match(/\d+/);
      if (floorMatch) {
        parts.push(`${floorMatch[0]} floor${parseInt(floorMatch[0]) > 1 ? 's' : ''}`);
      }
    }
    
    return parts.join(", ");
  };

  // ===== Форматирование описания =====
  const getDescription = (): string => {
    if (!listing.description) {
      return "";
    }
    
    // Убираем лишние пробелы и переносы строк
    let text = listing.description.replace(/\s+/g, ' ').trim();
    
    // Обрезаем до 100 символов
    if (text.length > 100) {
      text = text.substring(0, 100);
      // Обрезаем по последнему слову
      const lastSpace = text.lastIndexOf(' ');
      if (lastSpace > 0) {
        text = text.substring(0, lastSpace);
      }
      text += '...';
    }
    
    return text;
  };

  // ===== Форматирование цены =====
  const getPrice = (): string => {
    if (!listing.price) {
      return "Price not specified";
    }
    return `€ ${listing.price.toLocaleString('en-US')}`;
  };

  // ===== Получение features для отображения =====
  const getDisplayFeatures = (): string[] => {
    if (!listing.features || listing.features.length === 0) {
      return [];
    }
    
    // Приоритетные features
    const priority = ["Sea view", "No deposit", "Furnished", "Pet-friendly"];
    
    // Сначала ищем приоритетные
    const priorityFeatures = listing.features.filter(f => 
      priority.some(p => f.toLowerCase().includes(p.toLowerCase()))
    );
    
    // Если есть приоритетные, берем первые 2
    if (priorityFeatures.length > 0) {
      return priorityFeatures.slice(0, 2);
    }
    
    // Иначе берем первые 2 любых
    return listing.features.slice(0, 2);
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

  const imageUrl = getImageUrl();
  const title = getTitle();
  const description = getDescription();
  const price = getPrice();
  const displayFeatures = getDisplayFeatures();
  const sourceName = getSourceName();

  return (
    <div className="bg-white relative rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] w-full h-[448px]">
      {/* Image */}
      <div className="absolute h-[200px] left-0 rounded-tl-[12px] rounded-tr-[12px] top-0 w-full">
        <div className="absolute inset-0 overflow-hidden pointer-events-none rounded-tl-[12px] rounded-tr-[12px]">
          <img 
            alt={title} 
            className="absolute h-full w-full object-cover" 
            src={imageUrl} 
          />
        </div>
      </div>

      {/* Features chips */}
      {displayFeatures.length > 0 && (
        <div className="absolute flex flex-wrap gap-x-[8px] gap-y-[8px] left-[16px] top-[16px]">
          {displayFeatures.map((feature, index) => (
            <div 
              key={index} 
              className="bg-gray-100 box-border flex h-[36px] items-center justify-center px-[16px] py-[10px] rounded-[18px]"
            >
              <p className="font-medium leading-[20px] text-[14px] text-gray-700 text-nowrap whitespace-pre">
                {feature}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Title */}
      <p className="absolute font-medium leading-[32px] left-[16px] text-[16px] text-gray-900 top-[216px] w-[274px]">
        {title}
      </p>

      {/* Description */}
      <p className="absolute font-normal leading-[20px] left-[16px] text-[12px] text-gray-700 top-[248px] w-[274px]">
        {description}
      </p>

      {/* Price */}
      <p className="absolute font-semibold leading-[28px] left-[16px] text-[18px] text-gray-900 text-nowrap top-[304px] whitespace-pre">
        {price}
      </p>

      {/* Metro stations or district */}
      {listing.metroStations && listing.metroStations.length > 0 ? (
        <>
          {listing.metroStations.slice(0, 2).map((station, index) => {
            const transport = getTransportIcon(station.distance);
            return (
              <div 
                key={index}
                className="absolute flex items-center justify-between left-[16px] right-[16px]"
                style={{ top: `${344 + index * 28}px` }}
              >
                <div className="flex items-center gap-[6px]">
                  {transport.icon}
                  <p className="font-normal leading-[20px] text-[14px] text-gray-900">
                    {station.name}
                  </p>
                </div>
                <p className="font-normal leading-[20px] text-[14px] text-gray-700">
                  {station.distance}
                </p>
              </div>
            );
          })}
        </>
      ) : listing.district ? (
        <div className="absolute flex items-center gap-[8px] left-[16px] top-[344px]">
          <p className="font-normal leading-[20px] text-[14px] text-gray-900">
            {listing.district}
          </p>
        </div>
      ) : null}

      {/* Source */}
      <div className="absolute left-[16px] top-[378px]">
        <p className="font-normal leading-[20px] text-[12px] text-gray-500">
          Source: {sourceName}
        </p>
      </div>

      {/* On the map button */}
      <div 
        className="absolute bg-blue-600 flex gap-[8px] items-center justify-center left-[16px] px-[16px] py-[4px] rounded-[8px] top-[404px] cursor-pointer hover:bg-blue-700 transition-colors"
        onClick={() => onShowMap?.(listing.id)}
      >
        <div className="size-[20px]">
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
        </div>
        <p className="font-medium leading-[20px] text-[14px] text-white whitespace-pre">
          On the map
        </p>
      </div>

      {/* Action icons */}
      <div className="absolute flex gap-[12px] items-center right-[16px] top-[408px]">
        {/* Heart icon */}
        <div 
          className="size-[20px] cursor-pointer hover:opacity-70 transition-opacity"
          onClick={() => onFavoriteToggle?.(listing.id)}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M10 18L8.55 16.7C3.4 12.16 0 9.08 0 5.5C0 2.42 2.42 0 5.5 0C7.24 0 8.91 0.81 10 2.09C11.09 0.81 12.76 0 14.5 0C17.58 0 20 2.42 20 5.5C20 9.08 16.6 12.16 11.45 16.7L10 18Z"
              fill="#9CA3AF"
            />
          </svg>
        </div>

        {/* Flag icon */}
        <div 
          className="size-[20px] cursor-pointer hover:opacity-70 transition-opacity"
          onClick={() => onFlag?.(listing.id)}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 1V19L18 10L3 1Z" fill="#9CA3AF" />
          </svg>
        </div>

        {/* Share icon */}
        <div 
          className="size-[20px] cursor-pointer hover:opacity-70 transition-opacity"
          onClick={() => onShare?.(listing.id)}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="15" cy="5" r="3" fill="#9CA3AF" />
            <circle cx="5" cy="10" r="3" fill="#9CA3AF" />
            <circle cx="15" cy="15" r="3" fill="#9CA3AF" />
            <path d="M7.5 11L12.5 14M12.5 6L7.5 9" stroke="#9CA3AF" strokeWidth="2" />
          </svg>
        </div>
      </div>
    </div>
  );
};

export default NewListingCard;
