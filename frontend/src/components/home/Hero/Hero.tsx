import React from 'react';
import styles from './Hero.module.css';
import { Link } from 'react-router-dom';

const Hero: React.FC = () => {
  return (
    <section className={styles.hero}>
      <div className={styles.content}>
        <h1 className={styles.title}>Ищу квартиры в аренду в Италии 24/7</h1>
        <p className={styles.subtitle}>
          Привет! Я — твой персональный помощник. Давай я покажу тебе
          подходящие объявления со всех топовых сайтов? Могу присылать в
          телеграм новые варианты, как только они появляются.
        </p>
        <div className={styles.actions}>
          <Link to="/search" className={`${styles.button} ${styles.primary}`}>
            Найти жилье
          </Link>
          <a href="#features" className={`${styles.button} ${styles.secondary}`}>
            Подробнее
          </a>
        </div>
      </div>
    </section>
  );
};

export default Hero; 