import React from "react";
import { useNavigate } from "react-router-dom";

const SaveTimeSection: React.FC = () => {
  const navigate = useNavigate();

  const platforms = ["Casa", "Idealista", "Immobiliare", "Subito"];

  return (
    <div className="bg-[#eaf4fd] py-[80px] md:py-[60px]">
      <div className="max-w-[1920px] mx-auto px-[40px] md:px-[312px]">
        <div className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] p-[48px]">
          <div className="flex flex-col gap-[12px] md:flex-row md:items-start md:justify-between md:gap-[48px]">
            <div className="flex flex-col gap-[12px] items-start w-full md:max-w-[505px]">
              <h2 className="font-bold text-[48px] leading-[56px] text-gray-900 w-full h-[184px] md:h-auto">
                Save your time —<br />
                I'll find the best place<br />
                for you.
              </h2>
            </div>

            <div className="flex flex-col gap-[24px] items-start w-full md:max-w-[461px]">
              <p className="font-medium text-[18px] leading-[32px] text-gray-900 w-full min-w-full">
                Tell me what you're looking for — your dream place, budget,
                area. I'll find listings on the most<br className="hidden md:block" />
                popular platforms:
              </p>

              <div className="flex flex-wrap gap-[16px] w-full">
                {platforms.map((platform) => (
                  <div
                    key={platform}
                    className="bg-gray-100 px-[16px] py-[10px] rounded-[18px] h-[36px] flex items-center justify-center"
                  >
                    <span className="font-medium text-[14px] leading-[20px] text-gray-700">
                      {platform}
                    </span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => navigate("/auth")}
                className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors h-[44px] w-[180.446px] md:w-auto"
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
