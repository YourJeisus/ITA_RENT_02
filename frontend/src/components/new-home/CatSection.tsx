import React from 'react';
import catEmoji from '../../assets/new-design/cat-emoji.svg';

const CatSection: React.FC = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="bg-[#eaf4fd] py-[60px]">
      <div className="max-w-[1920px] mx-auto px-[312px]">
        <div className="bg-[#e0ecff] rounded-[12px] p-[48px] text-center">
          <h2 className="font-bold text-[48px] leading-[56px] text-gray-900 mb-[24px]">
            Scrolled all the way down?
          </h2>

          <p className="font-medium text-[22px] leading-[32px] text-gray-900 mb-[32px]">
            Here's a cute cat for you!
          </p>

          <div className="flex justify-center mb-[32px]">
            <img src={catEmoji} alt="Cat" className="w-[120px] h-[120px]" />
          </div>

          <button
            onClick={scrollToTop}
            className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
          >
            Return to top
          </button>
        </div>
      </div>
    </div>
  );
};

export default CatSection;

