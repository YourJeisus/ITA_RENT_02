import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const NewNavbar: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="bg-white h-[72px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] fixed top-0 left-0 right-0 z-50">
      <div className="max-w-[1920px] mx-auto px-[312px] md:px-[40px] h-full flex items-center justify-between">
        <button 
          onClick={() => navigate('/')}
          className="font-extrabold text-[22px] text-blue-600 leading-[32px] hover:opacity-80 transition-opacity"
        >
          RentAg
        </button>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-[68px] font-medium text-[16px] text-gray-900">
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

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden w-[24px] h-[24px] flex flex-col justify-center gap-[4px]"
        >
          <span className={`w-full h-[2px] bg-gray-900 transition-all ${mobileMenuOpen ? 'rotate-45 translate-y-[6px]' : ''}`} />
          <span className={`w-full h-[2px] bg-gray-900 transition-all ${mobileMenuOpen ? 'opacity-0' : ''}`} />
          <span className={`w-full h-[2px] bg-gray-900 transition-all ${mobileMenuOpen ? '-rotate-45 -translate-y-[6px]' : ''}`} />
        </button>

        {/* Desktop Auth Buttons */}
        <div className="hidden md:flex items-center gap-[8px]">
          {isAuthenticated ? (
            <button 
              onClick={() => navigate('/settings')}
              className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
            >
              Settings & Filters
            </button>
          ) : (
            <>
              <button 
                onClick={() => navigate('/auth/login')}
                className="border border-gray-200 border-solid px-[24px] py-[8px] rounded-[8px] font-semibold text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors"
              >
                Log in
              </button>
              <button 
                onClick={() => navigate('/auth/signup')}
                className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
              >
                Sign up
              </button>
            </>
          )}
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-200 shadow-lg">
          <nav className="flex flex-col p-[16px] gap-[16px]">
            <button 
              onClick={() => { navigate('/search'); setMobileMenuOpen(false); }}
              className="text-left font-medium text-[16px] text-gray-900 leading-[24px] hover:text-blue-600 transition-colors"
            >
              Apartment search
            </button>
            <button className="text-left font-medium text-[16px] text-gray-900 leading-[24px] hover:text-blue-600 transition-colors">
              How it works
            </button>
            <button className="text-left font-medium text-[16px] text-gray-900 leading-[24px] hover:text-blue-600 transition-colors">
              Contact
            </button>
            <button className="text-left font-medium text-[16px] text-gray-900 leading-[24px] hover:text-blue-600 transition-colors">
              FAQ
            </button>
            <div className="border-t border-gray-200 pt-[16px] mt-[8px] flex flex-col gap-[8px]">
              {isAuthenticated ? (
                <button 
                  onClick={() => { navigate('/settings'); setMobileMenuOpen(false); }}
                  className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors w-full"
                >
                  Settings & Filters
                </button>
              ) : (
                <>
                  <button 
                    onClick={() => { navigate('/auth/login'); setMobileMenuOpen(false); }}
                    className="border border-gray-200 border-solid px-[24px] py-[8px] rounded-[8px] font-semibold text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors w-full"
                  >
                    Log in
                  </button>
                  <button 
                    onClick={() => { navigate('/auth/signup'); setMobileMenuOpen(false); }}
                    className="bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors w-full"
                  >
                    Sign up
                  </button>
                </>
              )}
            </div>
          </nav>
        </div>
      )}
    </div>
  );
};

export default NewNavbar;

