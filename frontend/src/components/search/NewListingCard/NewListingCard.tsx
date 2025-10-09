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
  const imageUrl =
    listing.photos_urls && listing.photos_urls.length > 0
      ? listing.photos_urls[0]
      : listing.imageUrls && listing.imageUrls.length > 0
        ? listing.imageUrls[0]
        : "https://via.placeholder.com/306x200";

  const price = listing.price
    ? `€ ${listing.price.toLocaleString()}`
    : "Цена не указана";

  const rooms = listing.num_rooms ? `${listing.num_rooms}-room` : "";
  const area = listing.area_sqm || listing.area;
  const areaText = area ? `${area} m²` : "";
  const floors = listing.floor ? `${listing.floor} floor` : "";

  const titleParts = [rooms, listing.property_type, areaText, floors]
    .filter(Boolean)
    .join(", ");

  const description =
    listing.description?.substring(0, 100) ||
    `Spacious ${rooms} ${listing.property_type || "property"} with ${areaText} of living space — perfect for a large family or...`;

  return (
    <div className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] w-[306px] h-[448px] relative">
      {/* Image */}
      <div className="relative w-[306px] h-[200px] rounded-t-[12px] overflow-hidden">
        <img
          src={imageUrl}
          alt={listing.title || titleParts}
          className="w-full h-full object-cover"
        />

        {/* Tags */}
        <div className="absolute top-[16px] left-[16px] flex gap-[8px]">
          {listing.property_type === "studio" && (
            <div className="bg-gray-100 px-[16px] py-[10px] rounded-[18px]">
              <p className="font-medium text-[14px] leading-[20px] text-gray-700">
                Studio
              </p>
            </div>
          )}
          {/* Добавьте другие теги по желанию */}
        </div>
      </div>

      {/* Content */}
      <div className="p-[16px]">
        {/* Title */}
        <h3 className="font-medium text-[16px] leading-[32px] text-gray-900 mb-[8px]">
          {titleParts || listing.title}
        </h3>

        {/* Description */}
        <p className="font-normal text-[12px] leading-[20px] text-gray-700 mb-[16px] h-[40px] overflow-hidden">
          {description}
        </p>

        {/* Price */}
        <p className="font-semibold text-[18px] leading-[28px] text-gray-900 mb-[16px]">
          {price}
        </p>

        {/* Metro stations */}
        <div className="mb-[24px] space-y-[8px]">
          {listing.metroStations && listing.metroStations.length > 0
            ? listing.metroStations.slice(0, 2).map((station, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between font-normal text-[14px] leading-[20px]"
                >
                  <span className="text-gray-900">{station.name}</span>
                  <span className="text-gray-700">{station.distance}</span>
                </div>
              ))
            : listing.district && (
                <div className="flex items-center justify-between font-normal text-[14px] leading-[20px]">
                  <span className="text-gray-900">{listing.district}</span>
                </div>
              )}
        </div>

        {/* Action buttons */}
        <div className="flex items-center justify-between">
          {/* On the map button */}
          <button
            onClick={() => onShowMap?.(listing.id)}
            className="bg-blue-600 px-[16px] py-[4px] rounded-[8px] flex items-center gap-[8px] hover:bg-blue-700 transition-colors"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
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
            <p className="font-medium text-[14px] leading-[20px] text-white">
              On the map
            </p>
          </button>

          {/* Icon buttons */}
          <div className="flex items-center gap-[12px]">
            <button
              onClick={() => onFavoriteToggle?.(listing.id)}
              className="w-[20px] h-[20px] hover:opacity-70 transition-opacity"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
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
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M3 19V1L18 10L3 19Z" fill="#9CA3AF" />
              </svg>
            </button>

            <button
              onClick={() => onShare?.(listing.id)}
              className="w-[20px] h-[20px] hover:opacity-70 transition-opacity"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle cx="15" cy="5" r="3" fill="#9CA3AF" />
                <circle cx="5" cy="10" r="3" fill="#9CA3AF" />
                <circle cx="15" cy="15" r="3" fill="#9CA3AF" />
                <path
                  d="M7.5 11L12.5 14M12.5 6L7.5 9"
                  stroke="#9CA3AF"
                  strokeWidth="2"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewListingCard;
