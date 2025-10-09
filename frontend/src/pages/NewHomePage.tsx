import React from "react";
import NewNavbar from "../components/new-home/NewNavbar";
import NewHero from "../components/new-home/NewHero";
import FeatureCards from "../components/new-home/FeatureCards";
import SaveTimeSection from "../components/new-home/SaveTimeSection";
import StepByStepSection from "../components/new-home/StepByStepSection";
import CitiesSection from "../components/new-home/CitiesSection";
import FAQSection from "../components/new-home/FAQSection";
import CatSection from "../components/new-home/CatSection";
import AuthFooter from "../components/auth/AuthFooter";

const NewHomePage: React.FC = () => {
  return (
    <div className="font-['Manrope',sans-serif]">
      <NewNavbar />
      <NewHero />
      <FeatureCards />
      <SaveTimeSection />
      <StepByStepSection />
      <CitiesSection />
      <FAQSection />
      <CatSection />
      <AuthFooter />
    </div>
  );
};

export default NewHomePage;
