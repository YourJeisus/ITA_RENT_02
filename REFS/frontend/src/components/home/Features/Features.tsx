import React from 'react';
import styles from './Features.module.css';

// Импортируем иконки. Предположим, что они у нас есть. 
// Если нет, я временно использую плейсхолдеры.
// import { ReactComponent as NoCommissionIcon } from '@/assets/icons/no-commission.svg';
// import { ReactComponent as QualityIcon } from '@/assets/icons/quality.svg';
// import { ReactComponent as FastIcon } from '@/assets/icons/fast.svg';

const featuresData = [
  {
    // Icon: NoCommissionIcon,
    Icon: () => <>Icon1</>, // Placeholder
    title: 'Без посредников',
    description: 'Мы ищем объявления только от собственников, чтобы вы не переплачивали.',
  },
  {
    // Icon: QualityIcon,
    Icon: () => <>Icon2</>, // Placeholder
    title: 'Хороший ремонт',
    description: 'Алгоритмы отсеивают квартиры с «бабушкиным» ремонтом и плохими фото.',
  },
  {
    // Icon: FastIcon,
    Icon: () => <>Icon3</>, // Placeholder
    title: 'Очень быстро',
    description: 'Получайте уведомления в Telegram в ту же минуту, как объявление появилось.',
  },
];

const Features: React.FC = () => {
  return (
    <section id="features" className={styles.features}>
      <div className={styles.container}>
        {featuresData.map((feature, index) => (
          <div key={index} className={styles.featureCard}>
            <div className={styles.iconWrapper}>
              <feature.Icon />
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