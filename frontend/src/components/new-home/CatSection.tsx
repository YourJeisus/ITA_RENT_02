import React from "react";
import kittenIcon from "../../designSvg/kitten.svg";

const CatSection: React.FC = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="bg-[#eaf4fd] py-[40px] md:py-[60px]">
      <div className="max-w-[1920px] mx-auto px-4 md:px-8 lg:px-[312px]">
        <div className="bg-[#e0ecff] rounded-[12px] p-[24px] md:p-[48px] text-center">
          <h2 className="font-bold text-[32px] md:text-[48px] leading-[40px] md:leading-[56px] text-gray-900 mb-[16px] md:mb-[24px]">
            Scrolled all<br className="md:hidden" /> the way down?
          </h2>

          <p className="font-medium text-[18px] md:text-[22px] leading-[28px] md:leading-[32px] text-gray-900 mb-[24px] md:mb-[32px]">
            Here's a cute cat for you!
          </p>

          <div className="flex justify-center mb-[24px] md:mb-[32px]">
            <img src={kittenIcon} alt="Cat" className="w-[100px] h-[100px] md:w-[120px] md:h-[120px]" />
          </div>

          <button
            onClick={scrollToTop}
            className="w-full md:w-auto bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
          >
            Return to top
          </button>
        </div>
      </div>
    </div>
  );
};

export default CatSection;
