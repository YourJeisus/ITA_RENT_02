import React from 'react';
import { Link } from 'react-router-dom';
import instagramIcon from '../../designSvg/instagram.svg';
import facebookIcon from '../../designSvg/facebook.svg';
import twitterIcon from '../../designSvg/twitter.svg';
import linkedinIcon from '../../designSvg/linkedin.svg';
import youtubeIcon from '../../designSvg/youtube.svg';
import twitchIcon from '../../designSvg/twitch.svg';

const AuthFooter: React.FC = () => {
  return (
    <footer className="bg-[#eaf4fd] border-t border-gray-200">
      <div className="max-w-[1920px] mx-auto px-4 md:px-8 lg:px-12 xl:px-24 2xl:px-[40px] py-[40px] md:py-[80px]">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-[80px] mb-[40px] md:mb-[80px]">
          {/* Newsletter Section - First on mobile */}
          <div className="order-1">
            <h3 className="font-semibold text-[24px] md:text-[32px] leading-tight text-gray-900 mb-3 md:mb-4">
              <span className="text-blue-600">Stay in the loop</span> — new discounts, and tips?
            </h3>
            <p className="font-medium text-[18px] md:text-[22px] text-gray-900 mb-4 md:mb-6">
              Leave your email — I'll keep you posted.
            </p>
            <input
              type="email"
              placeholder="Your email"
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-400 focus:outline-none focus:border-blue-600 transition bg-white"
            />
          </div>

          {/* Navigation and Social - Second on mobile */}
          <div className="order-2 grid grid-cols-2 gap-8">
            {/* Navigation Links */}
            <div>
              <nav className="flex flex-col gap-3 md:gap-4">
                <Link to="/search" className="font-medium text-[16px] md:text-[18px] text-gray-900 hover:text-blue-600 transition">
                  Search apartament
                </Link>
                <Link to="#how-it-works" className="font-medium text-[16px] md:text-[18px] text-gray-900 hover:text-blue-600 transition">
                  How it works
                </Link>
                <Link to="#contact" className="font-medium text-[16px] md:text-[18px] text-gray-900 hover:text-blue-600 transition">
                  Contact
                </Link>
                <Link to="#faq" className="font-medium text-[16px] md:text-[18px] text-gray-900 hover:text-blue-600 transition">
                  FAQ
                </Link>
              </nav>
            </div>

            {/* Social Icons */}
            <div>
              <div className="flex flex-wrap gap-4 md:gap-6">
                <a href="#" className="w-10 h-10 md:w-14 md:h-14 rounded-lg md:rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                  <img src={instagramIcon} alt="Instagram" className="w-5 h-5 md:w-8 md:h-8" />
                </a>
                <a href="#" className="w-10 h-10 md:w-14 md:h-14 rounded-lg md:rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                  <img src={facebookIcon} alt="Facebook" className="w-5 h-5 md:w-8 md:h-8" />
                </a>
                <a href="#" className="w-10 h-10 md:w-14 md:h-14 rounded-lg md:rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                  <img src={twitterIcon} alt="Twitter" className="w-5 h-5 md:w-8 md:h-8" />
                </a>
                <a href="#" className="w-10 h-10 md:w-14 md:h-14 rounded-lg md:rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                  <img src={linkedinIcon} alt="LinkedIn" className="w-5 h-5 md:w-8 md:h-8" />
                </a>
                <a href="#" className="w-10 h-10 md:w-14 md:h-14 rounded-lg md:rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                  <img src={youtubeIcon} alt="YouTube" className="w-5 h-5 md:w-8 md:h-8" />
                </a>
                <a href="#" className="w-10 h-10 md:w-14 md:h-14 rounded-lg md:rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                  <img src={twitchIcon} alt="Twitch" className="w-5 h-5 md:w-8 md:h-8" />
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Logo */}
        <div className="mb-[40px] md:mb-[80px]">
          <Link to="/" className="font-extrabold text-[40px] md:text-[48px] text-blue-600 inline-block">
            RentAg
          </Link>
        </div>

        {/* Copyright */}
        <div className="border-t border-gray-200 pt-6 text-center">
          <p className="font-normal text-[14px] md:text-[16px] text-gray-600">
            © 2025 RentAg. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default AuthFooter;

