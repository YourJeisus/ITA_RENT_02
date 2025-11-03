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
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {/* Logo and Social Icons */}
          <div>
            <Link to="/" className="font-extrabold text-[48px] text-blue-600 inline-block mb-6">
              RentAg
            </Link>
            <div className="flex gap-4">
              <a href="#" className="w-14 h-14 rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                <img src={instagramIcon} alt="Instagram" className="w-8 h-8" />
              </a>
              <a href="#" className="w-14 h-14 rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                <img src={facebookIcon} alt="Facebook" className="w-8 h-8" />
              </a>
              <a href="#" className="w-14 h-14 rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                <img src={twitterIcon} alt="Twitter" className="w-8 h-8" />
              </a>
            </div>
            <div className="flex gap-4 mt-4">
              <a href="#" className="w-14 h-14 rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                <img src={linkedinIcon} alt="LinkedIn" className="w-8 h-8" />
              </a>
              <a href="#" className="w-14 h-14 rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                <img src={youtubeIcon} alt="YouTube" className="w-8 h-8" />
              </a>
              <a href="#" className="w-14 h-14 rounded-xl bg-[#e0ecff] flex items-center justify-center hover:bg-blue-100 transition">
                <img src={twitchIcon} alt="Twitch" className="w-8 h-8" />
              </a>
            </div>
          </div>

          {/* Navigation Links */}
          <div>
            <nav className="flex flex-col gap-4">
              <Link to="/search" className="font-medium text-[18px] text-gray-900 hover:text-blue-600 transition">
                Search apartament
              </Link>
              <Link to="#how-it-works" className="font-medium text-[18px] text-gray-900 hover:text-blue-600 transition">
                How it works
              </Link>
              <Link to="#contact" className="font-medium text-[18px] text-gray-900 hover:text-blue-600 transition">
                Contact
              </Link>
              <Link to="#faq" className="font-medium text-[18px] text-gray-900 hover:text-blue-600 transition">
                FAQ
              </Link>
            </nav>
          </div>

          {/* Newsletter */}
          <div>
            <h3 className="font-semibold text-[32px] leading-tight text-gray-900 mb-4">
              <span className="text-blue-600">Stay in the loop</span> — new discounts, and tips?
            </h3>
            <p className="font-medium text-[22px] text-gray-900 mb-6">
              Leave your email — I'll keep you posted.
            </p>
            <input
              type="email"
              placeholder="Your email"
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-400 focus:outline-none focus:border-blue-600 transition"
            />
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-gray-200 mt-12 pt-6 text-center">
          <p className="font-normal text-[16px] text-gray-600">
            © 2025 RentAg. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default AuthFooter;

