import React from 'react';
import notificationIcon from '../../assets/new-design/notification-icon.svg';
import noAgentIcon from '../../assets/new-design/no-agent-icon.svg';
import aiScanIcon from '../../assets/new-design/ai-scan-icon.svg';

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ icon, title, description }) => {
  return (
    <div className="bg-white h-[224px] w-[416px] rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.04)] p-[24px]">
      <div className="bg-[#e0ecff] w-[56px] h-[56px] rounded-[12px] flex items-center justify-center mb-[24px]">
        <img src={icon} alt="" className="w-[32px] h-[32px]" />
      </div>
      <h3 className="font-semibold text-[22px] leading-[32px] text-gray-900 mb-[8px]">
        {title}
      </h3>
      <p className="font-normal text-[16px] leading-[28px] text-gray-600">
        {description}
      </p>
    </div>
  );
};

const FeatureCards: React.FC = () => {
  const features = [
    {
      icon: notificationIcon,
      title: "New apartments? I'll text you first",
      description: "Great listings get taken in 15 minutes. I'll send you new options instantly — it's up to you to act fast.",
    },
    {
      icon: noAgentIcon,
      title: "Rent directly — no agents",
      description: "If there's a no-fee listing for the place — I'll send you that one, not some sketchy agent ad.",
    },
    {
      icon: aiScanIcon,
      title: "Only places with good renovation",
      description: "I use AI to scan apartment photos and filter out those with outdated, old-school interiors.",
    },
  ];

  return (
    <div className="bg-[#eaf4fd] py-[60px]">
      <div className="max-w-[1920px] mx-auto px-[312px]">
        <div className="flex gap-[24px] justify-between">
          {features.map((feature, index) => (
            <FeatureCard key={index} {...feature} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default FeatureCards;

