import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const NewNavbar: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const [menuOpen, setMenuOpen] = useState(false);

  // Блокировка скролла при открытом меню
  useEffect(() => {
    if (menuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [menuOpen]);

  return (
    <>
      <div className="bg-white h-[72px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] fixed top-0 left-0 right-0 z-50">
        <div className="max-w-[1920px] mx-auto px-4 md:px-8 lg:px-12 xl:px-24 2xl:px-[312px] h-full flex items-center justify-between">
          <button 
            onClick={() => navigate('/')}
            className="font-extrabold text-[22px] text-blue-600 leading-[32px] hover:opacity-80 transition-opacity"
          >
            RentAg
          </button>

          {/* Desktop Navigation - показываем на планшетах (md: 768px) и выше */}
          <nav className="hidden md:flex items-center gap-[24px] lg:gap-[48px] xl:gap-[68px] font-medium text-[13px] lg:text-[14px] xl:text-[16px] text-gray-900">
            <button onClick={() => navigate('/search')} className="leading-[24px] hover:text-blue-600 transition-colors whitespace-nowrap">
              Apartment search
            </button>
            <button className="leading-[24px] hover:text-blue-600 transition-colors whitespace-nowrap">
              How it works
            </button>
            <button className="leading-[24px] hover:text-blue-600 transition-colors whitespace-nowrap">
              Contact
            </button>
            <button className="leading-[24px] hover:text-blue-600 transition-colors whitespace-nowrap">
              FAQ
            </button>
          </nav>

          {/* Desktop Auth Buttons - показываем на планшетах (md) и выше */}
          <div className="hidden md:flex items-center gap-[8px]">
            {isAuthenticated ? (
              <button 
                onClick={() => navigate('/settings')}
                className="bg-blue-600 px-[16px] lg:px-[20px] xl:px-[24px] py-[10px] rounded-[8px] font-semibold text-[14px] lg:text-[15px] xl:text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors whitespace-nowrap"
              >
                Settings & Filters
              </button>
            ) : (
              <>
                <button 
                  onClick={() => navigate('/auth/login')}
                  className="border border-gray-200 border-solid px-[16px] lg:px-[20px] xl:px-[24px] py-[8px] rounded-[8px] font-semibold text-[14px] lg:text-[15px] xl:text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors whitespace-nowrap"
                >
                  Log in
                </button>
                <button 
                  onClick={() => navigate('/auth/signup')}
                  className="bg-blue-600 px-[16px] lg:px-[20px] xl:px-[24px] py-[10px] rounded-[8px] font-semibold text-[14px] lg:text-[15px] xl:text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors whitespace-nowrap"
                >
                  Sign up
                </button>
              </>
            )}
          </div>

          {/* Mobile Menu Button - Hamburger - прячем на планшетах */}
          <button 
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden w-[44px] h-[44px] flex flex-col justify-center items-center gap-[6px] relative"
            aria-label="Toggle menu"
          >
            <span className={`w-[24px] h-[2px] bg-gray-900 transition-all duration-300 ${menuOpen ? 'rotate-45 translate-y-[8px]' : ''}`}></span>
            <span className={`w-[24px] h-[2px] bg-gray-900 transition-all duration-300 ${menuOpen ? 'opacity-0' : ''}`}></span>
            <span className={`w-[24px] h-[2px] bg-gray-900 transition-all duration-300 ${menuOpen ? '-rotate-45 -translate-y-[8px]' : ''}`}></span>
          </button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {menuOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black/20 z-40 transition-opacity duration-300"
          onClick={() => setMenuOpen(false)}
        />
      )}

      {/* Mobile Menu - Compact Dropdown - только на мобильных */}
      <div className={`md:hidden fixed top-[72px] left-0 right-0 bg-white rounded-bl-[12px] rounded-br-[12px] shadow-2xl z-50 transition-all duration-300 ease-in-out ${menuOpen ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4 pointer-events-none'}`}>
        <div className="flex flex-col gap-[20px] p-[20px]">
          {/* Navigation Links */}
          <nav className="border-b border-gray-200 pb-[20px] flex flex-col gap-[36px] items-center justify-center">
            <button 
              onClick={() => { navigate('/search'); setMenuOpen(false); }} 
              className="font-medium text-[16px] leading-[24px] text-center text-gray-900 hover:text-blue-600 transition-colors"
            >
              Apartment search
            </button>
            <button 
              onClick={() => setMenuOpen(false)}
              className="font-medium text-[16px] leading-[24px] text-center text-gray-900 hover:text-blue-600 transition-colors"
            >
              How it works
            </button>
            <button 
              onClick={() => setMenuOpen(false)}
              className="font-medium text-[16px] leading-[24px] text-center text-gray-900 hover:text-blue-600 transition-colors"
            >
              Contact
            </button>
            <button 
              onClick={() => setMenuOpen(false)}
              className="font-medium text-[16px] leading-[24px] text-center text-gray-900 hover:text-blue-600 transition-colors"
            >
              FAQ
            </button>
          </nav>

          {/* Auth Buttons */}
          <div className="flex gap-[12px] w-full">
            {isAuthenticated ? (
              <button 
                onClick={() => { navigate('/settings'); setMenuOpen(false); }}
                className="flex-1 bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
              >
                Settings & Filters
              </button>
            ) : (
              <>
                <button 
                  onClick={() => { navigate('/auth/login'); setMenuOpen(false); }}
                  className="flex-1 border border-slate-300 border-solid px-[24px] py-[8px] rounded-[8px] font-semibold text-[16px] text-gray-900 leading-[24px] hover:bg-gray-50 transition-colors"
                >
                  Log in
                </button>
                <button 
                  onClick={() => { navigate('/auth/signup'); setMenuOpen(false); }}
                  className="flex-1 bg-blue-600 px-[24px] py-[10px] rounded-[8px] font-semibold text-[16px] text-white leading-[24px] hover:bg-blue-700 transition-colors"
                >
                  Sign up
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default NewNavbar;

