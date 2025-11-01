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

  return (
    <div className="bg-[#eaf4fd] py-[80px] md:py-[60px]">
      <div className="max-w-[1920px] mx-auto px-[40px] md:px-[312px]">
        <h2 className="font-bold text-[48px] leading-[56px] text-center text-gray-900 mb-[48px] md:mb-[60px]">
          Where I search for apartments
        </h2>

        <div className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] p-[48px]">
          <div className="flex flex-col gap-[48px] md:gap-0">
            <div className="font-medium gap-[24px] grid grid-cols-[repeat(2,_minmax(0px,_1fr))] grid-rows-[repeat(4,_minmax(0px,_1fr))] h-[164px] leading-[32px] text-[18px] text-blue-600 text-center w-full md:flex md:flex-col md:space-y-[12px] md:h-auto">
              {cities.flat().slice(0, 8).map((city, index) => {
                const gridAreas = [
                  '[grid-area:1_/_1]',
                  '[grid-area:1_/_2]',
                  '[grid-area:2_/_1]',
                  '[grid-area:2_/_2]',
                  '[grid-area:3_/_1]',
                  '[grid-area:3_/_2]',
                  '[grid-area:4_/_2]',
                  '[grid-area:4_/_1]'
                ];
                return (
                  <p
                    key={city}
                    className={`font-medium text-[18px] leading-[32px] text-blue-600 text-center relative self-start ${gridAreas[index]} md:static md:w-[196px]`}
                  >
                    {city}
                  </p>
                );
              })}
            </div>
            <button className="border border-slate-300 border-solid px-[24px] py-[8px] rounded-[8px] font-semibold text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors h-[44px] w-full md:w-auto md:mt-0">
              Load more
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CitiesSection;

