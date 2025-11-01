import React from 'react';
import { useNavigate } from 'react-router-dom';

const FAQSection: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="bg-[#eaf4fd] py-[80px] md:py-[60px]">
      <div className="max-w-[1920px] mx-auto px-[40px] md:px-[312px]">
        <div className="bg-white rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] p-[48px]">
          <h2 className="font-bold text-[48px] leading-[56px] text-center text-gray-900 mb-[12px] md:mb-[24px]">
            Any questions left?
          </h2>

          <div className="h-[64px] md:h-auto relative shrink-0 w-full mb-[32px]">
            <p className="absolute font-medium text-[18px] leading-[32px] left-0 right-0 text-center text-gray-900 top-0">
              <span>You can also ask us in the </span>
              <span className="text-blue-600">support chat</span>
              <span>
                {' — '}
                <br aria-hidden="true" />
                {'or write to '}
              </span>
              <span className="text-blue-600">hi@rentag.com</span>
            </p>
          </div>

          <div className="flex flex-col md:flex-row gap-[12px] md:gap-[16px]">
            <button className="flex-1 md:flex-none border border-slate-300 border-solid px-[24px] py-[8px] rounded-[8px] font-semibold text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors">
              Open FAQ
            </button>
            <button
              onClick={() => navigate('/search')}
              className="flex-1 md:flex-none bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
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

