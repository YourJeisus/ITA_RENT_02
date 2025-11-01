import React from "react";
import { useNavigate } from "react-router-dom";

const SaveTimeSection: React.FC = () => {
  const navigate = useNavigate();

  const platforms = ["Casa", "Idealista", "Immobiliare", "Subito"];

  return (
    <div className="bg-[#eaf4fd] py-[40px] md:py-[60px]">
      <div className="max-w-[1920px] mx-auto px-4 md:px-8 lg:px-12 xl:px-24 2xl:px-[312px]">
        <div className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] p-[24px] md:p-[48px]">
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-[32px]">
            <div>
              <h2 className="font-bold text-[32px] md:text-[48px] leading-[40px] md:leading-[56px] text-gray-900 mb-[24px] md:mb-[32px] max-w-[505px]">
                Save your time —<br />
                I'll find the best place<br className="hidden md:block" />
                for you.
              </h2>
            </div>

            <div className="max-w-full lg:max-w-[461px]">
              <p className="font-medium text-[16px] md:text-[18px] leading-[28px] md:leading-[32px] text-gray-900 mb-[24px]">
                Tell me what you're looking for — your dream place, budget,
                area. I'll find listings on the most popular platforms:
              </p>

              <div className="flex flex-wrap gap-[16px] mb-[24px] md:mb-[28px]">
                {platforms.map((platform) => (
                  <div
                    key={platform}
                    className="bg-gray-100 px-[16px] py-[10px] rounded-[18px]"
                  >
                    <span className="font-medium text-[14px] leading-[20px] text-gray-700">
                      {platform}
                    </span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => navigate("/auth")}
                className="w-full md:w-auto bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
              >
                Let's set things up
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SaveTimeSection;
