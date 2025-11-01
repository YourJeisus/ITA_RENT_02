import React from "react";
import clockIcon from "../../designSvg/icon_01_clock.svg";
import armsIcon from "../../designSvg/icon_02_arms.svg";
import cleanerIcon from "../../designSvg/icon_03_cleaner.svg";

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
}) => {
  return (
    <div className="bg-white min-h-[224px] w-full lg:w-[416px] rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] p-[24px] flex flex-col">
      <div className="mb-[24px]">
        <img src={icon} alt="" className="w-[56px] h-[56px]" />
      </div>
      <h3 className="font-semibold text-[22px] leading-[32px] text-gray-900 mb-[8px]">
        {title}
      </h3>
      <p className="font-normal text-[16px] leading-[28px] text-gray-600 flex-grow">
        {description}
      </p>
    </div>
  );
};

const FeatureCards: React.FC = () => {
  const features = [
    {
      icon: clockIcon,
      title: "New apartments? I'll text you first",
      description:
        "Great listings get taken in 15 minutes. I'll send you new options instantly — it's up to you to act fast.",
    },
    {
      icon: armsIcon,
      title: "Rent directly — no agents",
      description:
        "If there's a no-fee listing for the place — I'll send you that one, not some sketchy agent ad.",
    },
    {
      icon: cleanerIcon,
      title: "Only places with good renovation",
      description:
        "I use AI to scan apartment photos and filter out those with outdated, old-school interiors.",
    },
  ];

  return (
    <div className="bg-[#eaf4fd] py-[40px] md:py-[60px]">
      <div className="max-w-[1920px] mx-auto px-4 md:px-8 lg:px-[312px]">
        <div className="flex flex-col lg:flex-row gap-[16px] lg:gap-[24px] justify-between">
          {features.map((feature, index) => (
            <FeatureCard key={index} {...feature} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default FeatureCards;
