import React, { useState } from "react";
import instIcon from "../../designSvg/inst.svg";
import facebookIcon from "../../designSvg/facebook.svg";
import twitterIcon from "../../designSvg/twitter.svg";
import linkedinIcon from "../../designSvg/in.svg";
import youtubeIcon from "../../designSvg/youtube.svg";
import discordIcon from "../../designSvg/discord.svg";

const NewFooter: React.FC = () => {
  const [email, setEmail] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement email subscription
    console.log("Subscribe email:", email);
  };

  const socialIcons = [
    { icon: instIcon, name: "Instagram" },
    { icon: facebookIcon, name: "Facebook" },
    { icon: twitterIcon, name: "Twitter" },
    { icon: linkedinIcon, name: "LinkedIn" },
    { icon: youtubeIcon, name: "YouTube" },
    { icon: discordIcon, name: "Discord" },
  ];

  return (
    <div className="bg-white py-[64px]">
      <div className="max-w-[1920px] mx-auto px-[312px]">
        <div className="border-t border-gray-200 pt-[32px]">
          <div className="flex justify-between items-start mb-[64px]">
            {/* Left Side - Logo and Social Icons */}
            <div>
              <div className="font-extrabold text-[48px] text-blue-600 leading-[64px] mb-[48px]">
                RentAg
              </div>

              {/* Social Icons */}
              <div className="grid grid-cols-3 gap-[16px] max-w-[216px]">
                {socialIcons.map((social) => (
                  <div
                    key={social.name}
                    className="w-[56px] h-[56px] bg-[#e0ecff] rounded-[12px] flex items-center justify-center cursor-pointer hover:bg-[#d0dcff] transition-colors"
                  >
                    <img
                      src={social.icon}
                      alt={social.name}
                      className="w-[24px] h-[24px]"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Center - Menu Links */}
            <div className="space-y-[16px] font-medium text-[18px] text-gray-900">
              <div className="hover:text-blue-600 cursor-pointer transition-colors">
                Search apartament
              </div>
              <div className="hover:text-blue-600 cursor-pointer transition-colors">
                How it works
              </div>
              <div className="hover:text-blue-600 cursor-pointer transition-colors">
                Contact
              </div>
              <div className="hover:text-blue-600 cursor-pointer transition-colors">
                FAQ
              </div>
            </div>

            {/* Right Side - Newsletter */}
            <div className="max-w-[416px]">
              <h3 className="font-semibold text-[32px] leading-[40px] text-gray-900 mb-[16px]">
                <span className="text-blue-600">Stay in the loop</span> — new
                discounts, and tips?
              </h3>

              <p className="font-medium text-[22px] leading-[32px] text-gray-900 mb-[24px]">
                Leave your email — I'll keep you posted.
              </p>

              <form onSubmit={handleSubmit}>
                <input
                  type="email"
                  placeholder="Your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white border border-gray-200 px-[16px] py-[10px] rounded-[8px] font-normal text-[16px] text-gray-900 leading-[24px] outline-none placeholder:text-gray-400 focus:border-blue-600 transition-colors"
                />
              </form>
            </div>
          </div>

          {/* Copyright */}
          <div className="text-center">
            <p className="font-normal text-[16px] leading-[28px] text-gray-600">
              © 2025 RentAg. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewFooter;
