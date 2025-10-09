import React from "react";
import styles from "./Features.module.css";
import clockIcon from "../../../designSvg/icon_01_clock.svg";
import armsIcon from "../../../designSvg/icon_02_arms.svg";
import cleanerIcon from "../../../designSvg/icon_03_cleaner.svg";

const featuresData = [
  {
    icon: clockIcon,
    title: "Очень быстро",
    description:
      "Получайте уведомления в Telegram в ту же минуту, как объявление появилось.",
  },
  {
    icon: armsIcon,
    title: "Без посредников",
    description:
      "Мы ищем объявления только от собственников, чтобы вы не переплачивали.",
  },
  {
    icon: cleanerIcon,
    title: "Хороший ремонт",
    description:
      "Алгоритмы отсеивают квартиры с «бабушкиным» ремонтом и плохими фото.",
  },
];

const Features: React.FC = () => {
  return (
    <section id="features" className={styles.features}>
      <div className={styles.container}>
        {featuresData.map((feature, index) => (
          <div key={index} className={styles.featureCard}>
            <div className={styles.iconWrapper}>
              <img src={feature.icon} alt="" className={styles.icon} />
            </div>
            <h3 className={styles.featureTitle}>{feature.title}</h3>
            <p className={styles.featureDescription}>{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Features;
