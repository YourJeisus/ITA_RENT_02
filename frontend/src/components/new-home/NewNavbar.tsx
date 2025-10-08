import React from 'react';
import { useNavigate } from 'react-router-dom';

const NewNavbar: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="bg-white h-[72px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] fixed top-0 left-0 right-0 z-50">
      <div className="max-w-[1920px] mx-auto px-[312px] h-full flex items-center justify-between">
        <div className="font-extrabold text-[22px] text-blue-600 leading-[32px]">
          RentAg
        </div>

        <nav className="flex items-center gap-[68px] font-medium text-[16px] text-gray-900">
          <button onClick={() => navigate('/search')} className="leading-[24px] hover:text-blue-600 transition-colors">
            Apartment search
          </button>
          <button className="leading-[24px] hover:text-blue-600 transition-colors">
            How it works
          </button>
          <button className="leading-[24px] hover:text-blue-600 transition-colors">
            Contact
          </button>
          <button className="leading-[24px] hover:text-blue-600 transition-colors">
            FAQ
          </button>
        </nav>

        <div className="flex items-center gap-[8px]">
          <button 
            onClick={() => navigate('/auth')}
            className="border border-gray-200 border-solid px-[24px] py-[8px] rounded-[8px] font-semibold text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors"
          >
            Log in
          </button>
          <button 
            onClick={() => navigate('/auth')}
            className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
          >
            Sign up
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewNavbar;

