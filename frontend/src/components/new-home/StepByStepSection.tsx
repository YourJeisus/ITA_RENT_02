import React from "react";
import robotIcon from "../../designSvg/robot.svg";

const StepByStepSection: React.FC = () => {
  return (
    <div className="bg-[#eaf4fd] py-[40px] md:py-[60px]">
      <div className="max-w-[1920px] mx-auto px-4 md:px-8 lg:px-[312px]">
        <h2 className="font-bold text-[32px] md:text-[48px] leading-[40px] md:leading-[56px] text-center text-gray-900 mb-[40px] md:mb-[60px]">
          Your apartment hunt – step by step
        </h2>

        <div className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] p-[24px] md:p-[48px]">
          <div className="space-y-[24px] md:space-y-[32px]">
            {/* User Message 1 */}
            <div className="flex justify-end">
              <div className="flex items-start gap-[12px] md:gap-[16px]">
                <div className="bg-[#e7eefa] px-[16px] md:px-[24px] py-[12px] md:py-[16px] rounded-bl-[16px] rounded-br-[16px] rounded-tl-[16px] max-w-[340px] md:max-w-[600px]">
                  <p className="font-medium text-[16px] md:text-[18px] leading-[28px] md:leading-[32px] text-gray-900">
                    Hey! I'm looking for an apartment in Milan, up to 1000€
                  </p>
                </div>
                <div className="w-[48px] h-[48px] md:w-[64px] md:h-[64px] bg-[#e0ecff] rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="font-medium text-[20px] md:text-[24px] leading-[24px] md:leading-[28px] text-blue-600">
                    U
                  </span>
                </div>
              </div>
            </div>

            {/* Bot Response 1 */}
            <div className="flex justify-start">
              <div className="flex items-start gap-[12px] md:gap-[16px]">
                <img src={robotIcon} alt="Bot" className="w-[48px] h-[48px] md:w-[64px] md:h-[64px] flex-shrink-0" />
                <div className="bg-[#f1f5fe] px-[16px] md:px-[24px] py-[12px] md:py-[16px] rounded-bl-[22px] rounded-br-[22px] rounded-tr-[22px] max-w-[340px] md:max-w-[600px]">
                  <p className="font-medium text-[16px] md:text-[18px] leading-[28px] md:leading-[32px] text-gray-900">
                    Got it! I'll find matching listings for you as soon as they
                    appear.
                  </p>
                </div>
              </div>
            </div>

            {/* User Message 2 */}
            <div className="flex justify-end">
              <div className="flex items-start gap-[12px] md:gap-[16px]">
                <div className="bg-[#e7eefa] px-[16px] md:px-[24px] py-[12px] md:py-[16px] rounded-bl-[16px] rounded-br-[16px] rounded-tl-[16px] max-w-[340px] md:max-w-[600px]">
                  <p className="font-medium text-[16px] md:text-[18px] leading-[28px] md:leading-[32px] text-gray-900">
                    Nice. How do I get them?
                  </p>
                </div>
                <div className="w-[48px] h-[48px] md:w-[64px] md:h-[64px] bg-[#e0ecff] rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="font-medium text-[20px] md:text-[24px] leading-[24px] md:leading-[28px] text-blue-600">
                    U
                  </span>
                </div>
              </div>
            </div>

            {/* User Message 3 */}
            <div className="flex justify-end">
              <div className="flex items-start gap-[12px] md:gap-[16px]">
                <div className="bg-[#e7eefa] px-[16px] md:px-[24px] py-[12px] md:py-[16px] rounded-bl-[16px] rounded-br-[16px] rounded-tl-[16px] max-w-[340px] md:max-w-[600px]">
                  <p className="font-medium text-[16px] md:text-[18px] leading-[28px] md:leading-[32px] text-gray-900">
                    Do I need to check the sites myself?
                  </p>
                </div>
                <div className="w-[48px] h-[48px] md:w-[64px] md:h-[64px] bg-[#e0ecff] rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="font-medium text-[20px] md:text-[24px] leading-[24px] md:leading-[28px] text-blue-600">
                    U
                  </span>
                </div>
              </div>
            </div>

            {/* Bot Response 2 */}
            <div className="flex justify-start">
              <div className="flex items-start gap-[12px] md:gap-[16px]">
                <img src={robotIcon} alt="Bot" className="w-[48px] h-[48px] md:w-[64px] md:h-[64px] flex-shrink-0" />
                <div className="bg-[#f1f5fe] px-[16px] md:px-[24px] py-[12px] md:py-[16px] rounded-bl-[22px] rounded-br-[22px] rounded-tr-[22px] max-w-[340px] md:max-w-[600px]">
                  <p className="font-medium text-[16px] md:text-[18px] leading-[28px] md:leading-[32px] text-gray-900">
                    I'll send new listings directly to your WhatsApp :)
                    <br />
                    I'm watching everything 24/7 — you'll be the first to know.
                  </p>
                </div>
              </div>
            </div>

            {/* Bot Response 3 */}
            <div className="flex justify-start">
              <div className="flex items-start gap-[12px] md:gap-[16px]">
                <img src={robotIcon} alt="Bot" className="w-[48px] h-[48px] md:w-[64px] md:h-[64px] flex-shrink-0" />
                <div className="bg-[#f1f5fe] px-[16px] md:px-[24px] py-[12px] md:py-[16px] rounded-bl-[22px] rounded-br-[22px] rounded-tr-[22px] max-w-[340px] md:max-w-[600px]">
                  <p className="font-medium text-[16px] md:text-[18px] leading-[28px] md:leading-[32px] text-gray-900">
                    Set your filters — and I'll start looking for your place.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-center mt-[32px] md:mt-[48px]">
            <button className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors w-full md:w-[416px]">
              Try free trial
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StepByStepSection;
