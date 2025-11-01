import React from 'react';
import { useNavigate } from 'react-router-dom';

const FAQSection: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="bg-[#eaf4fd] py-[40px] md:py-[60px]">
      <div className="max-w-[1920px] mx-auto px-4 md:px-8 lg:px-12 xl:px-24 2xl:px-[312px]">
        <div className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] p-[24px] md:p-[48px]">
          <h2 className="font-bold text-[32px] md:text-[48px] leading-[40px] md:leading-[56px] text-center text-gray-900 mb-[16px] md:mb-[24px]">
            Any questions left?
          </h2>

          <p className="font-medium text-[16px] md:text-[18px] leading-[28px] md:leading-[32px] text-center text-gray-900 mb-[24px] md:mb-[32px]">
            You can also ask us in the <span className="text-blue-600 cursor-pointer hover:underline">support chat</span> —<br className="hidden md:block" />
            or write to <span className="text-blue-600 cursor-pointer hover:underline">hi@rentag.com</span>
          </p>

          <div className="flex flex-col md:flex-row justify-center gap-[12px] md:gap-[16px]">
            <button className="w-full md:w-auto border border-slate-300 border-solid px-[24px] py-[8px] rounded-[8px] font-semibold text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors">
              Open FAQ
            </button>
            <button
              onClick={() => navigate('/search')}
              className="w-full md:w-auto bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
            >
              Start searching
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQSection;

