import React from "react";
import Hero from "../components/home/Hero/Hero";
import Features from "../components/home/Features/Features";
import HowItWorks from "../components/home/HowItWorks/HowItWorks";
import SocialProof from "../components/home/SocialProof/SocialProof";
import CallToAction from "../components/home/CallToAction/CallToAction";
// import styles from './HomePage.module.scss'; // Если будут специфичные стили для HomePage

const HomePage: React.FC = () => {
  return (
    <main>
      <Hero />
      <Features />
      <HowItWorks />
      <SocialProof />
      <CallToAction />
      {/* 
        Здесь мы продолжим добавлять остальные секции:
        SocialProof
        FounderMessage
        ...etc
      */}
    </main>
  );
};

export default HomePage;
