import React from 'react';

const CitiesSection: React.FC = () => {
  const cities = [
    ['Rome', 'Bologna', 'Messina', 'Amalfi', 'Rimini'],
    ['Milan', 'Florence', 'Padua', 'Sorrento', 'Parma'],
    ['Naples', 'Bari', 'Trieste', 'Taormina', 'Lucca'],
    ['Turin', 'Catania', 'Pisa', 'Lecce', 'Trento'],
    ['Palermo', 'Venice', 'Siena', 'Bergamo', 'Bolzano'],
    ['Genoa', 'Verona', 'Como', 'Cagliari', 'La Spezia'],
  ];

  // Mobile cities - only 8 cities in 2 columns
  const mobileCities = [
    'Rome', 'Bologna', 'Messina', 'Amalfi',
    'Rimini', 'Milan', 'Florence', 'Sorrento'
  ];

  return (
    <div className="bg-[#eaf4fd] py-[40px] md:py-[60px]">
      <div className="max-w-[1920px] mx-auto px-4 md:px-8 lg:px-12 xl:px-24 2xl:px-[312px]">
        <h2 className="font-bold text-[32px] md:text-[48px] leading-[40px] md:leading-[56px] text-center text-gray-900 mb-[40px] md:mb-[60px]">
          Where I search for apartments
        </h2>

        <div className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] p-[24px] md:p-[40px] lg:p-[48px]">
          {/* Mobile view - 2 columns grid */}
          <div className="md:hidden grid grid-cols-2 gap-x-4 gap-y-6">
            {mobileCities.map((city) => (
              <button
                key={city}
                className="font-medium text-[16px] leading-[28px] text-blue-600 hover:underline transition-all text-center"
              >
                {city}
              </button>
            ))}
          </div>

          {/* Mobile "Load more" button */}
          <button className="md:hidden w-full mt-8 border border-slate-300 border-solid px-[24px] py-[8px] rounded-[8px] font-semibold text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors">
            Load more
          </button>

          {/* Tablet view - 3 columns grid */}
          <div className="hidden md:grid lg:hidden grid-cols-3 gap-x-6 gap-y-6">
            {cities.flat().map((city) => (
              <button
                key={city}
                className="font-medium text-[16px] leading-[28px] text-blue-600 hover:underline transition-all text-center"
              >
                {city}
              </button>
            ))}
          </div>

          {/* Desktop view - rows of 5 */}
          <div className="hidden lg:block space-y-[12px]">
            {cities.map((row, rowIndex) => (
              <div key={rowIndex} className="flex justify-between">
                {row.map((city) => (
                  <button
                    key={city}
                    className="font-medium text-[18px] leading-[32px] text-blue-600 hover:underline transition-all w-[196px] text-center"
                  >
                    {city}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CitiesSection;

