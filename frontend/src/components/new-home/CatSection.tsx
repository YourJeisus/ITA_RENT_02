import React from "react";
import kittenIcon from "../../designSvg/kitten.svg";

const CatSection: React.FC = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="bg-[#eaf4fd] py-[80px] md:py-[60px]">
      <div className="max-w-[1920px] mx-auto px-[40px] md:px-[312px]">
        <div className="bg-[#e0ecff] rounded-[12px] p-[48px]">
          <div className="flex flex-col gap-[48px] items-start w-full">
            <div className="flex flex-col gap-[12px] items-start w-full">
              <h2 className="font-bold text-[48px] leading-[56px] text-center text-gray-900 w-full">
                Scrolled all<br aria-hidden="true" /> the way down?
              </h2>

              <div className="flex gap-[10px] items-center justify-center w-full">
                <p className="font-medium text-[22px] leading-[32px] text-center text-gray-900 w-[464px] md:w-full">
                  Here's a cute cat for you!
                </p>
              </div>
            </div>

            <div className="flex gap-[10px] items-center justify-center w-full">
              <div className="grid-cols-[max-content] grid-rows-[max-content] inline-grid leading-[0] place-items-start relative shrink-0">
                <div className="[grid-area:1_/_1] ml-0 mt-0 relative size-[120px]">
                  <img src={kittenIcon} alt="Cat" className="w-[120px] h-[120px]" />
                </div>
              </div>
            </div>

            <div className="flex gap-[12px] items-center w-full">
              <button
                onClick={scrollToTop}
                className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors h-[44px] w-full md:w-auto"
              >
                Return to top
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CatSection;
