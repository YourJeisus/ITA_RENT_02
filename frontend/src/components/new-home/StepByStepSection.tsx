import React from "react";
import robotIcon from "../../designSvg/robot.svg";

const StepByStepSection: React.FC = () => {
  return (
    <div className="bg-[#eaf4fd] py-[80px] md:py-[60px]">
      <div className="max-w-[1920px] mx-auto px-[40px] md:px-[312px]">
        <h2 className="font-bold text-[48px] leading-[56px] text-center text-gray-900 mb-[48px] md:mb-[60px]">
          Your apartment hunt – step by step
        </h2>

        <div className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] p-[48px]">
          <div className="flex flex-col gap-[40px] md:space-y-[32px]">
            {/* User Message 1 */}
            <div className="flex justify-end gap-[12px] items-start">
              <div className="bg-[#e7eefa] px-[24px] py-[16px] rounded-bl-[16px] rounded-br-[16px] rounded-tl-[16px] w-[340px] md:max-w-[600px]">
                <p className="font-medium text-[18px] leading-[32px] text-gray-900">
                  Hey! I'm looking for an apartment in Milan, up to 1000€
                </p>
              </div>
              <div className="grid-cols-[max-content] grid-rows-[max-content] inline-grid leading-[0] place-items-start relative shrink-0">
                <div className="[grid-area:1_/_1] ml-0 mt-0 relative size-[64px]">
                  <div className="w-[64px] h-[64px] bg-[#e0ecff] rounded-full"></div>
                </div>
                <p className="[grid-area:1_/_1] font-medium text-[24px] leading-[28px] ml-[24px] mt-[18px] relative text-blue-600 text-nowrap whitespace-pre">
                  U
                </p>
              </div>
            </div>

            {/* Bot Response 1 */}
            <div className="flex justify-start gap-[12px] items-start">
              <div className="relative shrink-0 size-[64px]">
                <img src={robotIcon} alt="Bot" className="w-[64px] h-[64px]" />
              </div>
              <div className="bg-[#f1f5fe] px-[24px] py-[16px] rounded-bl-[22px] rounded-br-[22px] rounded-tr-[22px] max-w-[600px]">
                <p className="font-medium text-[18px] leading-[32px] text-gray-900">
                  Got it! I'll find matching listings for you as soon as they
                  appear.
                </p>
              </div>
            </div>

            {/* User Message 2 */}
            <div className="flex justify-end gap-[12px] items-start">
              <div className="flex flex-col gap-[8px] items-end max-w-[600px]">
                <div className="bg-[#e7eefa] px-[24px] py-[16px] rounded-bl-[16px] rounded-br-[16px] rounded-tl-[16px] w-full">
                  <p className="font-medium text-[18px] leading-[32px] text-gray-900">
                    Nice. How do I get them?
                  </p>
                </div>
                <div className="bg-[#e7eefa] px-[24px] py-[16px] rounded-bl-[16px] rounded-br-[16px] rounded-tl-[16px] w-full">
                  <p className="font-medium text-[18px] leading-[32px] text-gray-900">
                    Do I need to check the sites myself?
                  </p>
                </div>
              </div>
              <div className="grid-cols-[max-content] grid-rows-[max-content] inline-grid leading-[0] place-items-start relative shrink-0">
                <div className="[grid-area:1_/_1] ml-0 mt-0 relative size-[64px]">
                  <div className="w-[64px] h-[64px] bg-[#e0ecff] rounded-full"></div>
                </div>
                <p className="[grid-area:1_/_1] font-medium text-[24px] leading-[28px] ml-[24px] mt-[18px] relative text-blue-600 text-nowrap whitespace-pre">
                  U
                </p>
              </div>
            </div>

            {/* Bot Response 2 */}
            <div className="flex justify-start gap-[12px] items-start">
              <div className="relative shrink-0 size-[64px]">
                <img src={robotIcon} alt="Bot" className="w-[64px] h-[64px]" />
              </div>
              <div className="flex flex-col gap-[8px] items-start max-w-[600px]">
                <div className="bg-[#f1f5fe] px-[24px] py-[16px] rounded-bl-[22px] rounded-br-[22px] rounded-tr-[22px] w-full">
                  <p className="font-medium text-[18px] leading-[32px] text-gray-900 whitespace-pre-wrap">
                    I'll send new listings directly to your WhatsApp :) I'm watching everything 24/7 — you'll be the first to know.
                  </p>
                </div>
                <div className="bg-[#f1f5fe] px-[24px] py-[16px] rounded-bl-[22px] rounded-br-[22px] rounded-tr-[22px] w-full">
                  <p className="font-medium text-[18px] leading-[32px] text-gray-900">
                    Set your filters — and I'll start looking for your place.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-center mt-[48px] md:mt-[48px]">
            <button className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors h-[44px] w-full md:w-[416px]">
              Try free trial
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StepByStepSection;
