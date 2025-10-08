import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import arrowDown from '../../assets/new-design/arrow-down.svg';

const NewHero: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useState({
    city: 'City',
    type: 'Rent',
    propertyType: 'Property type',
    rooms: 'Rooms',
    price: 'Price',
    filters: 'Filters',
    neighborhood: '',
  });

  const handleSearch = () => {
    navigate('/search');
  };

  const handleExploreMap = () => {
    navigate('/map');
  };

  return (
    <div className="bg-[#e0ecff] pt-[72px] pb-[68px]">
      <div className="max-w-[1920px] mx-auto px-[312px]">
        {/* Title */}
        <h1 className="font-bold text-[48px] leading-[56px] text-center text-gray-900 mt-[94px] mb-[34px]">
          Apartment search in Italy, 24/7
        </h1>

        {/* Subtitle */}
        <p className="font-medium text-[22px] leading-[32px] text-center text-gray-600 mb-[68px] max-w-[856px] mx-auto">
          AI-powered assistant that finds apartments for you and sends them straight
          <br />
          to your WhatsApp.
        </p>

        {/* Manual Search Label */}
        <p className="font-medium text-[18px] leading-[32px] text-blue-600 mb-[10px]">
          Prefer to search manually?
        </p>

        {/* Search Bar */}
        <div className="bg-white h-[64px] rounded-[12px] flex items-center px-[24px] mb-[28px]">
          {/* City */}
          <div className="flex items-center gap-[12px] px-[16px] py-[10px] cursor-pointer hover:bg-gray-50 rounded-[8px] transition-colors">
            <span className="font-normal text-[16px] text-gray-900 leading-[24px]">{searchParams.city}</span>
            <img src={arrowDown} alt="" className="w-[16px] h-[16px]" />
          </div>

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Rent */}
          <div className="flex items-center gap-[12px] px-[16px] py-[10px] cursor-pointer hover:bg-gray-50 rounded-[8px] transition-colors">
            <span className="font-normal text-[16px] text-gray-900 leading-[24px]">{searchParams.type}</span>
            <img src={arrowDown} alt="" className="w-[16px] h-[16px]" />
          </div>

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Property type */}
          <div className="flex items-center gap-[12px] px-[16px] py-[10px] cursor-pointer hover:bg-gray-50 rounded-[8px] transition-colors">
            <span className="font-normal text-[16px] text-gray-900 leading-[24px]">{searchParams.propertyType}</span>
            <img src={arrowDown} alt="" className="w-[16px] h-[16px]" />
          </div>

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Rooms */}
          <div className="flex items-center gap-[12px] px-[16px] py-[10px] cursor-pointer hover:bg-gray-50 rounded-[8px] transition-colors">
            <span className="font-normal text-[16px] text-gray-900 leading-[24px]">{searchParams.rooms}</span>
            <img src={arrowDown} alt="" className="w-[16px] h-[16px]" />
          </div>

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Price */}
          <div className="flex items-center gap-[12px] px-[16px] py-[10px] cursor-pointer hover:bg-gray-50 rounded-[8px] transition-colors">
            <span className="font-normal text-[16px] text-gray-900 leading-[24px]">{searchParams.price}</span>
            <img src={arrowDown} alt="" className="w-[16px] h-[16px]" />
          </div>

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Filters */}
          <div className="flex items-center gap-[12px] px-[16px] py-[10px] cursor-pointer hover:bg-gray-50 rounded-[8px] transition-colors">
            <span className="font-normal text-[16px] text-gray-900 leading-[24px]">{searchParams.filters}</span>
            <img src={arrowDown} alt="" className="w-[16px] h-[16px]" />
          </div>

          <div className="w-[1px] h-[64px] bg-gray-200" />

          {/* Neighborhood Input */}
          <input
            type="text"
            placeholder="Neighborhood, Metro"
            className="flex-1 px-[16px] py-[10px] bg-white rounded-[8px] font-normal text-[16px] text-gray-900 leading-[24px] outline-none placeholder:text-gray-400"
            value={searchParams.neighborhood}
            onChange={(e) => setSearchParams({ ...searchParams, neighborhood: e.target.value })}
          />
        </div>

        {/* Buttons */}
        <div className="flex items-center justify-end gap-[12px]">
          <button 
            onClick={handleExploreMap}
            className="border border-slate-300 border-solid px-[24px] py-[8px] rounded-[8px] font-semibold text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors"
          >
            Explore on map
          </button>
          <button 
            onClick={handleSearch}
            className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewHero;

