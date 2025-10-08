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
    <div className="bg-[#eaf4fd] py-[60px]">
      <div className="max-w-[1920px] mx-auto px-[312px]">
        <h2 className="font-bold text-[48px] leading-[56px] text-center text-gray-900 mb-[60px]">
          Where I search for apartments
        </h2>

        <div className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] p-[48px]">
          <div className="space-y-[12px]">
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

